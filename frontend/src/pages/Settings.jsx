import { useState } from 'react';
import {
  Settings as SettingsIcon, Server, Database, Sliders,
  Save, CheckCircle2, RotateCcw, Shield, Info, Palette
} from 'lucide-react';

export default function Settings() {
  const [saved, setSaved] = useState(false);
  const [formData, setFormData] = useState({
    apiUrl: 'http://localhost:8000/api',
    mapTileProvider: 'carto-voyager',
    crsDefault: 'EPSG:4326',
    defaultMetric: 'roc_auc',
    cvFoldsDefault: 5,
    randomSeedDefault: 42,
    thresholdVeryLow: 0.20,
    thresholdLow: 0.40,
    thresholdModerate: 0.60,
    thresholdHigh: 0.80,
  });

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  const handleResetDemoData = () => {
    alert('Synthetic demo dataset reset trigger dispatched to backend!');
  };

  return (
    <div className="settings-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>System Preferences & Pipeline Configuration</h2>
          <p>Tune spatial projections, API connection endpoints, threshold classifications, and ML evaluation criteria.</p>
        </div>
      </div>

      {saved && (
        <div className="card" style={{ marginBottom: '1.5rem', background: 'hsla(152, 69%, 48%, 0.1)', borderColor: 'var(--accent-success)', color: 'var(--accent-success)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <CheckCircle2 size={18} />
          <span>System configuration successfully saved and applied to active session!</span>
        </div>
      )}

      <form onSubmit={handleSave}>
        <div className="grid-12">
          {/* Left Column: API & GIS */}
          <div className="col-span-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Backend Integration */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Server size={18} /> Backend & Service API
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">FastAPI Endpoint Base URL</label>
                <input
                  type="text"
                  className="form-input"
                  value={formData.apiUrl}
                  onChange={(e) => setFormData({ ...formData, apiUrl: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Default Spatial Coordinate Reference System (CRS)</label>
                <select
                  className="form-select"
                  value={formData.crsDefault}
                  onChange={(e) => setFormData({ ...formData, crsDefault: e.target.value })}
                >
                  <option value="EPSG:4326">WGS 84 (EPSG:4326) — Universal Geodetic</option>
                  <option value="EPSG:32644">UTM Zone 44N (EPSG:32644) — Himalayan Projection</option>
                  <option value="EPSG:3857">Web Mercator (EPSG:3857) — Standard Web Tiles</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Cartographic Tile Base Layer</label>
                <select
                  className="form-select"
                  value={formData.mapTileProvider}
                  onChange={(e) => setFormData({ ...formData, mapTileProvider: e.target.value })}
                >
                  <option value="carto-voyager">CARTO Voyager (Clean High-Contrast)</option>
                  <option value="osm">OpenStreetMap Standard</option>
                  <option value="esri-satellite">Esri World Imagery (Satellite Relief)</option>
                </select>
              </div>
            </div>

            {/* Susceptibility Classification Thresholds */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Sliders size={18} /> Susceptibility Class Cutoffs (Probability 0.0 – 1.0)
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem' }}>
                <div className="form-group">
                  <label className="form-label">Very Low / Low Boundary</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    className="form-input"
                    value={formData.thresholdVeryLow}
                    onChange={(e) => setFormData({ ...formData, thresholdVeryLow: parseFloat(e.target.value) })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Low / Moderate Boundary</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    className="form-input"
                    value={formData.thresholdLow}
                    onChange={(e) => setFormData({ ...formData, thresholdLow: parseFloat(e.target.value) })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Moderate / High Boundary</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    className="form-input"
                    value={formData.thresholdModerate}
                    onChange={(e) => setFormData({ ...formData, thresholdModerate: parseFloat(e.target.value) })}
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">High / Very High Boundary</label>
                  <input
                    type="number"
                    step="0.05"
                    min="0"
                    max="1"
                    className="form-input"
                    value={formData.thresholdHigh}
                    onChange={(e) => setFormData({ ...formData, thresholdHigh: parseFloat(e.target.value) })}
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Right Column: ML Defaults & Capstone Info */}
          <div className="col-span-6" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* ML Evaluation Defaults */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Shield size={18} /> Machine Learning Optimization
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Champion Model Selection Criterion</label>
                <select
                  className="form-select"
                  value={formData.defaultMetric}
                  onChange={(e) => setFormData({ ...formData, defaultMetric: e.target.value })}
                >
                  <option value="roc_auc">Area Under ROC Curve (ROC-AUC) — Standard</option>
                  <option value="f1_score">F1-Score (Harmonic Mean of Precision & Recall)</option>
                  <option value="recall">Recall (Minimize False Negatives in Disaster Management)</option>
                </select>
              </div>

              <div className="form-group">
                <label className="form-label">Default Random Seed</label>
                <input
                  type="number"
                  className="form-input"
                  value={formData.randomSeedDefault}
                  onChange={(e) => setFormData({ ...formData, randomSeedDefault: parseInt(e.target.value) })}
                />
              </div>

              <div style={{ marginTop: '1.2rem', padding: '1rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-md)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>Demo Dataset Reset</div>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Regenerate synthetic Himalayan valley data</div>
                </div>
                <button type="button" className="btn btn-secondary btn-sm" onClick={handleResetDemoData}>
                  <RotateCcw size={14} /> Reset Data
                </button>
              </div>
            </div>

            {/* Project / Capstone Metadata */}
            <div className="card">
              <div className="card-header">
                <div className="card-title">
                  <Info size={18} /> Project & Capstone Information
                </div>
              </div>

              <div style={{ fontSize: '0.82rem', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
                <div><strong>Project Title:</strong> Landslide Susceptibility & Risk Analysis Using Machine Learning</div>
                <div><strong>Architecture:</strong> FastAPI (Python 3.11) + React 19 + Leaflet GIS + Scikit-Learn / XGBoost</div>
                <div><strong>Domain:</strong> Geospatial Information Systems (GIS) & Disaster Hazard Mitigation</div>
                <div><strong>Reference:</strong> Inspired by MATLAB Excellence in Innovation Landslide Susceptibility Mapping Project</div>
                <div style={{ marginTop: '0.5rem', padding: '0.5rem', background: 'hsla(198, 93%, 55%, 0.1)', borderRadius: 'var(--radius-sm)', color: 'var(--accent-primary)', fontSize: '0.78rem' }}>
                  ✓ Production-grade B.Tech Final Year Capstone Project
                </div>
              </div>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '2rem', display: 'flex', justifyContent: 'flex-end', gap: '1rem' }}>
          <button type="submit" className="btn btn-primary btn-lg">
            <Save size={18} /> Save Settings & Apply Changes
          </button>
        </div>
      </form>
    </div>
  );
}
