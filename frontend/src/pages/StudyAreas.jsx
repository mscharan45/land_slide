import { useState, useEffect, useRef } from 'react';
import {
  MapPin, Plus, Trash2, Globe, Layers, CheckCircle2,
  AlertCircle, RefreshCw, Compass, ArrowUpRight
} from 'lucide-react';
import { studyAreas } from '../api';
import L, { createCustomIcon } from '../utils/leafletConfig';

const DEFAULT_DEMO_AREAS = [
  {
    id: 1,
    name: 'Rishikesh-Devprayag Valley (Western Himalayas)',
    description: 'High-altitude mountainous terrain prone to rainfall-triggered debris flows along NH-58 and Ganges gorge.',
    bbox_minlat: 30.08,
    bbox_minlng: 78.25,
    bbox_maxlat: 30.25,
    bbox_maxlng: 78.60,
    area_sqkm: 1285.5,
    created_at: '2026-03-01T10:00:00Z',
    status: 'Ready for Analysis',
  },
  {
    id: 2,
    name: 'Wayanad Western Ghats Slope Sector',
    description: 'Steep plantation-covered slopes with fragile lateritic soils subject to high-intensity monsoon saturation.',
    bbox_minlat: 11.50,
    bbox_minlng: 76.00,
    bbox_maxlat: 11.75,
    bbox_maxlng: 76.25,
    area_sqkm: 840.2,
    created_at: '2026-03-05T14:30:00Z',
    status: 'Ready for Analysis',
  }
];

export default function StudyAreas() {
  const [areas, setAreas] = useState([]);
  const [selectedArea, setSelectedArea] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    bbox_minlat: 30.10,
    bbox_minlng: 78.30,
    bbox_maxlat: 30.22,
    bbox_maxlng: 78.55,
    area_sqkm: 550.0,
  });
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const polygonLayer = useRef(null);

  const fetchAreas = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await studyAreas.list();
      if (res.data && res.data.length > 0) {
        setAreas(res.data);
        setSelectedArea(res.data[0]);
      } else {
        setAreas(DEFAULT_DEMO_AREAS);
        setSelectedArea(DEFAULT_DEMO_AREAS[0]);
      }
    } catch {
      // Fallback to demo areas if backend is offline
      setAreas(DEFAULT_DEMO_AREAS);
      setSelectedArea(DEFAULT_DEMO_AREAS[0]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAreas();
  }, []);

  // Initialize and update Leaflet map
  useEffect(() => {
    if (!mapRef.current) return;

    if (!mapInstance.current) {
      mapInstance.current = L.map(mapRef.current).setView([30.15, 78.40], 11);
      L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO',
        maxZoom: 18,
      }).addTo(mapInstance.current);
    }

    if (selectedArea && mapInstance.current) {
      if (polygonLayer.current) {
        mapInstance.current.removeLayer(polygonLayer.current);
      }

      const bounds = [
        [selectedArea.bbox_minlat, selectedArea.bbox_minlng],
        [selectedArea.bbox_maxlat, selectedArea.bbox_maxlng]
      ];

      polygonLayer.current = L.rectangle(bounds, {
        color: '#0284c7',
        weight: 2,
        fillColor: '#38bdf8',
        fillOpacity: 0.25,
        dashArray: '4, 4'
      }).addTo(mapInstance.current);

      polygonLayer.current.bindPopup(`<b>${selectedArea.name}</b><br/>Area: ${selectedArea.area_sqkm} km²`);
      mapInstance.current.fitBounds(bounds, { padding: [30, 30] });
    }
  }, [selectedArea]);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);

    const payload = {
      name: formData.name,
      description: formData.description,
      bbox_minlat: parseFloat(formData.bbox_minlat),
      bbox_minlng: parseFloat(formData.bbox_minlng),
      bbox_maxlat: parseFloat(formData.bbox_maxlat),
      bbox_maxlng: parseFloat(formData.bbox_maxlng),
      area_sqkm: parseFloat(formData.area_sqkm) || 500,
    };

    try {
      const res = await studyAreas.create(payload);
      setSuccess(`Study area "${res.data.name}" created successfully!`);
      setIsCreating(false);
      fetchAreas();
    } catch {
      // Mock creation locally if backend offline
      const mockNew = {
        ...payload,
        id: Date.now(),
        created_at: new Date().toISOString(),
      };
      setAreas([mockNew, ...areas]);
      setSelectedArea(mockNew);
      setSuccess(`Study area "${payload.name}" created in session!`);
      setIsCreating(false);
    }
  };

  return (
    <div className="study-areas-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Study Areas & Region of Interest</h2>
          <p>Define spatial bounding boxes, inspect terrain footprints, and manage GIS regional scopes for landslide modeling.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button className="btn btn-secondary" onClick={fetchAreas} title="Refresh study areas">
            <RefreshCw size={16} /> Refresh
          </button>
          <button className="btn btn-primary" onClick={() => setIsCreating(!isCreating)}>
            <Plus size={16} /> {isCreating ? 'Cancel' : 'New Study Area'}
          </button>
        </div>
      </div>

      {success && (
        <div className="card" style={{ marginBottom: '1.5rem', background: 'hsla(152, 69%, 48%, 0.1)', borderColor: 'var(--accent-success)', color: 'var(--accent-success)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <CheckCircle2 size={18} />
          <span>{success}</span>
        </div>
      )}

      {error && (
        <div className="card" style={{ marginBottom: '1.5rem', background: 'hsla(0, 84%, 60%, 0.1)', borderColor: 'var(--accent-danger)', color: 'var(--accent-danger)', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Stats Summary */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(198, 93%, 55%, 0.12)', color: 'var(--accent-primary)' }}>
            <Globe size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Total Study Areas</div>
            <div className="stat-value">{areas.length}</div>
            <div className="stat-change positive">Active spatial scopes</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(152, 69%, 48%, 0.12)', color: 'var(--accent-success)' }}>
            <Layers size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Selected Area Bounds</div>
            <div className="stat-value">{selectedArea ? `${selectedArea.area_sqkm} km²` : '---'}</div>
            <div className="stat-change positive">Coverage area</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(263, 70%, 60%, 0.12)', color: 'var(--accent-secondary)' }}>
            <Compass size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">CRS Projection</div>
            <div className="stat-value" style={{ fontSize: '1.3rem' }}>WGS84 / EPSG:4326</div>
            <div className="stat-change">Geodetic Coordinates</div>
          </div>
        </div>
      </div>

      {/* Modal / Creation Drawer */}
      {isCreating && (
        <div className="card" style={{ marginBottom: '2rem', borderColor: 'var(--accent-primary)', animation: 'fadeIn 0.3s ease-out' }}>
          <div className="card-header">
            <div className="card-title">
              <Plus size={18} /> Define New Study Area Bounds
            </div>
            <span className="badge badge-primary">Spatial BBox</span>
          </div>
          <form onSubmit={handleCreateSubmit}>
            <div className="grid-2">
              <div className="form-group">
                <label className="form-label">Study Area Name *</label>
                <input
                  type="text"
                  className="form-input"
                  required
                  placeholder="e.g. Uttarkashi District Mountain Sector"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Approx Area (km²)</label>
                <input
                  type="number"
                  className="form-input"
                  placeholder="e.g. 750"
                  value={formData.area_sqkm}
                  onChange={(e) => setFormData({ ...formData, area_sqkm: e.target.value })}
                />
              </div>
            </div>

            <div className="form-group">
              <label className="form-label">Geological / Geographic Description</label>
              <textarea
                className="form-input"
                rows="2"
                placeholder="Description of terrain, tectonic features, and monsoon precipitation patterns..."
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', marginBottom: '1.2rem' }}>
              <div className="form-group">
                <label className="form-label">Min Lat (South) *</label>
                <input
                  type="number"
                  step="0.0001"
                  className="form-input"
                  required
                  value={formData.bbox_minlat}
                  onChange={(e) => setFormData({ ...formData, bbox_minlat: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Min Lng (West) *</label>
                <input
                  type="number"
                  step="0.0001"
                  className="form-input"
                  required
                  value={formData.bbox_minlng}
                  onChange={(e) => setFormData({ ...formData, bbox_minlng: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Max Lat (North) *</label>
                <input
                  type="number"
                  step="0.0001"
                  className="form-input"
                  required
                  value={formData.bbox_maxlat}
                  onChange={(e) => setFormData({ ...formData, bbox_maxlat: e.target.value })}
                />
              </div>
              <div className="form-group">
                <label className="form-label">Max Lng (East) *</label>
                <input
                  type="number"
                  step="0.0001"
                  className="form-input"
                  required
                  value={formData.bbox_maxlng}
                  onChange={(e) => setFormData({ ...formData, bbox_maxlng: e.target.value })}
                />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button type="button" className="btn btn-secondary" onClick={() => setIsCreating(false)}>
                Cancel
              </button>
              <button type="submit" className="btn btn-primary">
                Save & Register Area
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Main Content Layout: List on Left, Map on Right */}
      <div className="grid-12">
        {/* Left: Study Area Cards */}
        <div className="col-span-5" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div className="card">
            <div className="card-header">
              <div className="card-title">
                <MapPin size={18} /> Available Study Scopes ({areas.length})
              </div>
            </div>

            {loading ? (
              <div className="loading-screen" style={{ padding: '2rem' }}>
                <div className="spinner"></div>
                <span>Loading study areas...</span>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {areas.map((area) => {
                  const isSelected = selectedArea?.id === area.id;
                  return (
                    <div
                      key={area.id}
                      onClick={() => setSelectedArea(area)}
                      style={{
                        padding: '1rem',
                        borderRadius: 'var(--radius-md)',
                        border: `1px solid ${isSelected ? 'var(--accent-primary)' : 'var(--border-subtle)'}`,
                        background: isSelected ? 'hsla(198, 93%, 55%, 0.08)' : 'var(--bg-elevated)',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.35rem' }}>
                        <h4 style={{ fontSize: '0.95rem', fontWeight: 600, color: isSelected ? 'var(--accent-primary)' : 'var(--text-primary)' }}>
                          {area.name}
                        </h4>
                        <span className="badge badge-success">Active</span>
                      </div>
                      <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '0.6rem', lineHeight: 1.4 }}>
                        {area.description}
                      </p>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        <span>Area: <strong style={{ color: 'var(--text-primary)' }}>{area.area_sqkm} km²</strong></span>
                        <span>Bounds: {area.bbox_minlat?.toFixed(2)}°N to {area.bbox_maxlat?.toFixed(2)}°N</span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right: Map Preview */}
        <div className="col-span-7">
          <div className="card" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
            <div className="card-header">
              <div className="card-title">
                <Globe size={18} /> Spatial Footprint & Bounding Box
              </div>
              {selectedArea && (
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Selected: <strong style={{ color: 'var(--accent-primary)' }}>{selectedArea.name}</strong>
                </div>
              )}
            </div>

            <div
              ref={mapRef}
              className="map-container"
              style={{ flex: 1, minHeight: '480px', width: '100%', borderRadius: 'var(--radius-md)' }}
            />

            {selectedArea && (
              <div style={{ marginTop: '1rem', padding: '0.75rem', background: 'var(--bg-input)', borderRadius: 'var(--radius-sm)', display: 'flex', justifyContent: 'space-around', fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                <div><span style={{ color: 'var(--text-muted)' }}>South (Min Lat):</span> {selectedArea.bbox_minlat}°</div>
                <div><span style={{ color: 'var(--text-muted)' }}>West (Min Lng):</span> {selectedArea.bbox_minlng}°</div>
                <div><span style={{ color: 'var(--text-muted)' }}>North (Max Lat):</span> {selectedArea.bbox_maxlat}°</div>
                <div><span style={{ color: 'var(--text-muted)' }}>East (Max Lng):</span> {selectedArea.bbox_maxlng}°</div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
