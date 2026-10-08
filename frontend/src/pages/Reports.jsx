import { useState } from 'react';
import {
  FileText, Download, Printer, CheckCircle2, FileCheck,
  Calendar, Layers, ShieldAlert, Award, Sparkles, RefreshCw
} from 'lucide-react';
import { reports } from '../api';

const GENERATED_REPORTS = [
  {
    id: 1,
    title: 'Comprehensive Landslide Susceptibility & Risk Audit — Rishikesh Valley',
    generated_at: '2026-03-08T14:30:00Z',
    pages: 14,
    size_mb: '3.4 MB',
    format: 'PDF',
    status: 'Ready',
  },
  {
    id: 2,
    title: 'Model Evaluation & Feature Explanations Report (5-Fold CV Benchmark)',
    generated_at: '2026-03-07T17:15:00Z',
    pages: 8,
    size_mb: '2.1 MB',
    format: 'PDF',
    status: 'Ready',
  }
];

export default function Reports() {
  const [reportList, setReportList] = useState(GENERATED_REPORTS);
  const [isGenerating, setIsGenerating] = useState(false);
  const [selectedReport, setSelectedReport] = useState(GENERATED_REPORTS[0]);
  const [config, setConfig] = useState({
    includeExecutiveSummary: true,
    includeGISFactors: true,
    includeModelMetrics: true,
    includeRiskExposure: true,
    includeMitigationPlan: true,
  });

  const handleGenerate = () => {
    setIsGenerating(true);
    setTimeout(() => {
      const newReport = {
        id: Date.now(),
        title: `Technical Hazard & Susceptibility Synthesis — ${new Date().toLocaleDateString()}`,
        generated_at: new Date().toISOString(),
        pages: 12,
        size_mb: '2.8 MB',
        format: 'PDF',
        status: 'Ready',
      };
      setReportList([newReport, ...reportList]);
      setSelectedReport(newReport);
      setIsGenerating(false);
    }, 1500);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="reports-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Technical Reports & Documentation Export</h2>
          <p>Synthesize GIS terrain analyses, machine learning validation metrics, and disaster risk plans into standardized engineering reports.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={handlePrint}>
            <Printer size={16} /> Print Document
          </button>
          <button className="btn btn-primary" onClick={handleGenerate} disabled={isGenerating}>
            <FileText size={16} /> {isGenerating ? 'Compiling PDF...' : 'Generate New PDF Report'}
          </button>
        </div>
      </div>

      <div className="grid-12">
        {/* Left: Report Configuration & Past Reports */}
        <div className="col-span-5" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Configuration Card */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <FileCheck size={18} /> Report Sections & Modules
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.includeExecutiveSummary}
                  onChange={(e) => setConfig({ ...config, includeExecutiveSummary: e.target.checked })}
                />
                <span>Executive Summary & ROI Boundary Coordinates</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.includeGISFactors}
                  onChange={(e) => setConfig({ ...config, includeGISFactors: e.target.checked })}
                />
                <span>GIS Conditioning Factors & Multicollinearity Assessment</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.includeModelMetrics}
                  onChange={(e) => setConfig({ ...config, includeModelMetrics: e.target.checked })}
                />
                <span>5-Model CV Benchmark Scorecard (ROC-AUC / F1 / Recall)</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.includeRiskExposure}
                  onChange={(e) => setConfig({ ...config, includeRiskExposure: e.target.checked })}
                />
                <span>Infrastructure Exposure & Demographic Vulnerability</span>
              </label>

              <label style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={config.includeMitigationPlan}
                  onChange={(e) => setConfig({ ...config, includeMitigationPlan: e.target.checked })}
                />
                <span>Site-Specific Mitigation Guidelines & Engineering Specs</span>
              </label>
            </div>
          </div>

          {/* Past Generated Reports List */}
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <Calendar size={18} /> Generated Report Archives
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {reportList.map((r) => {
                const isSelected = selectedReport?.id === r.id;
                return (
                  <div
                    key={r.id}
                    onClick={() => setSelectedReport(r)}
                    style={{
                      padding: '0.9rem',
                      borderRadius: 'var(--radius-md)',
                      border: `1px solid ${isSelected ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
                      background: isSelected ? 'hsla(198, 93%, 55%, 0.08)' : 'var(--bg-elevated)',
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                      <h4 style={{ fontSize: '0.85rem', fontWeight: 600, color: isSelected ? 'var(--accent-primary)' : 'var(--text-primary)', margin: 0 }}>
                        {r.title}
                      </h4>
                      <span className="badge badge-success">{r.format}</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                      <span>{new Date(r.generated_at).toLocaleDateString()}</span>
                      <span>{r.pages} Pages • {r.size_mb}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right: Interactive Report Document Preview */}
        <div className="col-span-7">
          <div className="card" style={{ height: '100%', background: '#ffffff', color: '#1e293b', padding: '2.5rem', borderRadius: 'var(--radius-lg)', boxShadow: '0 12px 36px rgba(0,0,0,0.4)', overflowY: 'auto', maxHeight: '820px' }}>
            {/* Header Document */}
            <div style={{ borderBottom: '2px solid #0284c7', paddingBottom: '1.2rem', marginBottom: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#0284c7', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                  LandSense AI — Spatial Geological Audit
                </span>
                <h1 style={{ fontSize: '1.4rem', fontWeight: 800, color: '#0f172a', margin: '4px 0 0 0' }}>
                  Landslide Susceptibility & Disaster Risk Report
                </h1>
                <p style={{ fontSize: '0.8rem', color: '#64748b', margin: '2px 0 0 0' }}>
                  Target Scope: Rishikesh-Devprayag Valley • Coordinate Bounds: 30.08°N–30.25°N, 78.25°E–78.60°E
                </p>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0', fontSize: '0.72rem', fontWeight: 700, padding: '3px 8px', borderRadius: '4px' }}>
                  AUDITED DOCUMENT
                </span>
                <div style={{ fontSize: '0.72rem', color: '#94a3b8', marginTop: '4px' }}>
                  Generated: {selectedReport ? new Date(selectedReport.generated_at).toLocaleDateString() : 'Today'}
                </div>
              </div>
            </div>

            {/* Document Content */}
            <div style={{ fontSize: '0.85rem', lineHeight: 1.6, color: '#334155' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px', marginBottom: '8px' }}>
                1. Executive Overview & Terrain Background
              </h3>
              <p style={{ margin: '0 0 1rem 0' }}>
                This technical report details quantitative landslide susceptibility modeling within the Western Himalayas. Using an ensemble of multi-spectral remote sensing imagery, 30m SRTM digital elevation data, and Geological Survey of India inventory points, a machine learning risk matrix was derived to aid disaster mitigation planning.
              </p>

              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px', marginBottom: '8px' }}>
                2. Model Evaluation & Benchmark Summary
              </h3>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.8rem', marginBottom: '1.2rem', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: '#f8fafc', borderBottom: '2px solid #cbd5e1' }}>
                    <th style={{ padding: '6px 8px', color: '#475569' }}>Algorithm</th>
                    <th style={{ padding: '6px 8px', color: '#475569' }}>ROC-AUC</th>
                    <th style={{ padding: '6px 8px', color: '#475569' }}>F1-Score</th>
                    <th style={{ padding: '6px 8px', color: '#475569' }}>Recall</th>
                    <th style={{ padding: '6px 8px', color: '#475569' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  <tr style={{ borderBottom: '1px solid #e2e8f0', background: '#f0fdf4' }}>
                    <td style={{ padding: '6px 8px', fontWeight: 700, color: '#0f172a' }}>Random Forest</td>
                    <td style={{ padding: '6px 8px', fontWeight: 700, color: '#059669' }}>0.948</td>
                    <td style={{ padding: '6px 8px' }}>0.911</td>
                    <td style={{ padding: '6px 8px' }}>0.928</td>
                    <td style={{ padding: '6px 8px', fontWeight: 700, color: '#0284c7' }}>Champion</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '6px 8px' }}>XGBoost</td>
                    <td style={{ padding: '6px 8px' }}>0.941</td>
                    <td style={{ padding: '6px 8px' }}>0.903</td>
                    <td style={{ padding: '6px 8px' }}>0.920</td>
                    <td style={{ padding: '6px 8px' }}>High Precision</td>
                  </tr>
                  <tr style={{ borderBottom: '1px solid #e2e8f0' }}>
                    <td style={{ padding: '6px 8px' }}>CatBoost</td>
                    <td style={{ padding: '6px 8px' }}>0.934</td>
                    <td style={{ padding: '6px 8px' }}>0.895</td>
                    <td style={{ padding: '6px 8px' }}>0.912</td>
                    <td style={{ padding: '6px 8px' }}>Balanced</td>
                  </tr>
                </tbody>
              </table>

              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px', marginBottom: '8px' }}>
                3. Critical Exposure & Risk Quantities
              </h3>
              <ul style={{ margin: '0 0 1rem 0', paddingLeft: '1.2rem' }}>
                <li><strong>Exposed Highway Length:</strong> 38.6 km of NH-58 traversing slopes exceeding 32°.</li>
                <li><strong>High-Hazard Footprint:</strong> 214.8 km² designated as Very High or High susceptibility.</li>
                <li><strong>Primary Trigger Factors:</strong> Slope gradient (28% weight), Monsoon precipitation (22%), Cut-slope proximity (11%).</li>
              </ul>

              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #e2e8f0', paddingBottom: '4px', marginBottom: '8px' }}>
                4. Engineering Countermeasures
              </h3>
              <p style={{ margin: 0 }}>
                Immediate installation of horizontal perforated pore-pressure dissipation drains, followed by deep steel soil nails and hydroseeding on exposed slope faces. Real-time tiltmeter and piezometer telemetry should be deployed on road Km 14–19.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
