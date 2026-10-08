"""
LandSense AI — PDF Report Generator.

Generates a downloadable PDF analysis report using ReportLab.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from pathlib import Path

from app.config import settings

logger = logging.getLogger("landsense.reports.pdf")


def generate_pdf_report(
    area, training_run, model_results: list, title: str = ""
) -> str:
    """Generate a PDF report and return the file path.

    Uses ReportLab to build a structured analysis report including:
    - Study area info
    - Training configuration
    - Model comparison table
    - Feature importance
    - Disclaimer
    """
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import inch, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak,
    )

    out_dir = Path(settings.output_dir) / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"report_{area.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = out_dir / filename

    doc = SimpleDocTemplate(str(filepath), pagesize=A4,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle", parent=styles["Title"],
        fontSize=20, spaceAfter=20,
    )
    heading_style = ParagraphStyle(
        "ReportHeading", parent=styles["Heading2"],
        fontSize=14, spaceAfter=10, spaceBefore=15,
    )
    body_style = styles["BodyText"]

    story = []

    # ── Title ────────────────────────────────────────────────────────────
    story.append(Paragraph(title or "Landslide Susceptibility Analysis Report", title_style))
    story.append(Paragraph(f"<b>Study Area:</b> {area.name}", body_style))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", body_style))
    story.append(Spacer(1, 20))

    # ── Study Area Details ───────────────────────────────────────────────
    story.append(Paragraph("Study Area Details", heading_style))
    story.append(Paragraph(f"Area: {area.area_sqkm or 'N/A'} sq km", body_style))
    story.append(Paragraph(f"Bounding Box: ({area.bbox_minlat}, {area.bbox_minlng}) to ({area.bbox_maxlat}, {area.bbox_maxlng})", body_style))
    story.append(Spacer(1, 15))

    # ── Training Configuration ───────────────────────────────────────────
    story.append(Paragraph("Training Configuration", heading_style))
    story.append(Paragraph(f"Run ID: {training_run.run_id}", body_style))
    story.append(Paragraph(f"CV Folds: {training_run.cv_folds}", body_style))
    story.append(Paragraph(f"Random Seed: {training_run.random_seed}", body_style))
    story.append(Paragraph(f"Balancing: {training_run.balancing_method or 'None'}", body_style))
    story.append(Paragraph(f"Features Used: {training_run.n_features}", body_style))
    story.append(Paragraph(f"Samples: {training_run.n_samples}", body_style))
    story.append(Spacer(1, 15))

    # ── Model Comparison Table ───────────────────────────────────────────
    story.append(Paragraph("Model Comparison", heading_style))

    table_data = [
        ["Model", "Accuracy", "Precision", "Recall", "F1", "ROC-AUC", "Best"]
    ]
    for m in model_results:
        table_data.append([
            m.model_name,
            f"{m.accuracy:.4f}" if m.accuracy else "N/A",
            f"{m.precision_score:.4f}" if m.precision_score else "N/A",
            f"{m.recall:.4f}" if m.recall else "N/A",
            f"{m.f1_score:.4f}" if m.f1_score else "N/A",
            f"{m.roc_auc:.4f}" if m.roc_auc else "N/A",
            "★" if m.is_best else "",
        ])

    t = Table(table_data, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
        ("ALIGN", (1, 0), (-1, -1), "CENTER"),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))

    # ── Best Model Feature Importance ────────────────────────────────────
    best = next((m for m in model_results if m.is_best), None)
    if best and best.feature_importance:
        story.append(Paragraph("Feature Importance (Best Model)", heading_style))
        fi = json.loads(best.feature_importance)[:10]
        fi_data = [["Feature", "Importance"]]
        for item in fi:
            fi_data.append([
                item["feature"],
                f"{item['importance']:.4f}",
            ])
        ft = Table(fi_data, repeatRows=1)
        ft.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
        ]))
        story.append(ft)
        story.append(Spacer(1, 15))

    # ── Limitations ──────────────────────────────────────────────────────
    story.append(Paragraph("Limitations", heading_style))
    story.append(Paragraph(
        "Results depend on the quality and completeness of the historical "
        "landslide inventory, spatial resolution of input data, and the "
        "characteristics of the selected study area. The model is trained "
        "on available features and may not capture all relevant factors.",
        body_style,
    ))
    story.append(Spacer(1, 15))

    # ── Disclaimer ───────────────────────────────────────────────────────
    story.append(Paragraph("Disclaimer", heading_style))
    story.append(Paragraph(settings.report_disclaimer, body_style))

    # Build PDF
    doc.build(story)
    logger.info("Generated PDF report: %s", filepath)
    return str(filepath)
