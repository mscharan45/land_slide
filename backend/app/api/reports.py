"""Report generation endpoints."""
from __future__ import annotations
import logging
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Report, TrainingRun, ModelResult, StudyArea
from app.schemas.report import ReportGenerateRequest, ReportOut

logger = logging.getLogger("landsense.api.reports")
router = APIRouter()


@router.get("/", response_model=list[ReportOut])
def list_reports(db: Session = Depends(get_db)):
    """List all generated reports."""
    return db.query(Report).order_by(Report.generated_at.desc()).all()


@router.post("/generate", response_model=ReportOut, status_code=201)
def generate_report(body: ReportGenerateRequest, db: Session = Depends(get_db)):
    """Generate a PDF analysis report for a study area + training run."""
    from app.reports.pdf_generator import generate_pdf_report

    area = db.query(StudyArea).filter(StudyArea.id == body.study_area_id).first()
    if not area:
        raise HTTPException(404, "Study area not found")

    run = db.query(TrainingRun).filter(
        TrainingRun.id == body.training_run_id
    ).first()
    if not run:
        raise HTTPException(404, "Training run not found")

    models = (
        db.query(ModelResult)
        .filter(ModelResult.training_run_id == run.id)
        .order_by(ModelResult.roc_auc.desc())
        .all()
    )

    file_path = generate_pdf_report(
        area=area,
        training_run=run,
        model_results=models,
        title=body.title or "Landslide Susceptibility Analysis Report",
    )

    report = Report(
        study_area_id=body.study_area_id,
        training_run_id=body.training_run_id,
        title=body.title,
        file_path=file_path,
    )
    db.add(report)
    db.commit()
    db.refresh(report)

    logger.info("Generated report id=%s path=%s", report.id, file_path)
    return report


@router.get("/download/{report_id}")
def download_report(report_id: int, db: Session = Depends(get_db)):
    """Download a generated PDF report."""
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    if not report.file_path or not os.path.exists(report.file_path):
        raise HTTPException(404, "Report file not found on disk")
    return FileResponse(
        report.file_path,
        media_type="application/pdf",
        filename=f"landsense_report_{report.id}.pdf",
    )
