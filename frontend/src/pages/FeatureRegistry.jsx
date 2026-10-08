import { useState, useEffect } from 'react';
import {
  List, Sliders, CheckCircle2, Search, Filter,
  Mountain, Droplet, CloudRain, TreePine, MapPin, Compass, Info, ToggleLeft, ToggleRight
} from 'lucide-react';
import { features } from '../api';

const DEFAULT_FEATURES = [
  { id: 1, name: 'slope', display_name: 'Slope Gradient', category: 'terrain', unit: 'degrees', data_type: 'numerical', is_required: true, is_enabled: true, description: 'Steepness of terrain derived from DEM. Higher slopes produce increased shear stress.' },
  { id: 2, name: 'aspect', display_name: 'Slope Aspect', category: 'terrain', unit: 'degrees', data_type: 'numerical', is_required: true, is_enabled: true, description: 'Compass orientation of slopes. Regulates sunlight, moisture retention, and vegetative shelter.' },
  { id: 3, name: 'elevation', display_name: 'Elevation (DEM)', category: 'terrain', unit: 'meters', data_type: 'numerical', is_required: true, is_enabled: true, description: 'Altitude above sea level. Modulates orographic rainfall and freeze-thaw weathering.' },
  { id: 4, name: 'plan_curvature', display_name: 'Plan Curvature', category: 'terrain', unit: '1/m', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Horizontal surface contour curvature. Drives surface water convergence or divergence.' },
  { id: 5, name: 'profile_curvature', display_name: 'Profile Curvature', category: 'terrain', unit: '1/m', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Vertical gradient curvature indicating flow acceleration and deceleration zones.' },
  { id: 6, name: 'tpi', display_name: 'Topographic Position Index (TPI)', category: 'terrain', unit: 'index', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Elevation relative to surrounding landscape to identify ridges, slopes, and valley floors.' },
  { id: 7, name: 'tri', display_name: 'Terrain Ruggedness Index (TRI)', category: 'terrain', unit: 'meters', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Quantifies local topographic heterogeneity and surface roughness.' },
  { id: 8, name: 'twi', display_name: 'Topographic Wetness Index (TWI)', category: 'hydrology', unit: 'index', data_type: 'numerical', is_required: false, is_enabled: true, description: 'ln(a/tanβ) combining drainage catchment area with slope to model pore-water pressure.' },
  { id: 9, name: 'spi', display_name: 'Stream Power Index (SPI)', category: 'hydrology', unit: 'index', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Estimates erosive power of overland sheet and channelized flow.' },
  { id: 10, name: 'distance_rivers', display_name: 'Proximity to Drainage Network', category: 'hydrology', unit: 'meters', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Euclidean distance to perennial and seasonal streams causing toe undercutting.' },
  { id: 11, name: 'rainfall', display_name: 'Annual Precipitation', category: 'climate', unit: 'mm/year', data_type: 'numerical', is_required: true, is_enabled: true, description: 'Cumulative monsoon precipitation serving as primary hydrodynamic trigger.' },
  { id: 12, name: 'soil_type', display_name: 'Soil Texture Class', category: 'soil', unit: 'category', data_type: 'categorical', is_required: false, is_enabled: true, description: 'Soil cohesion, grain size distribution, and hydraulic conductivity.' },
  { id: 13, name: 'ndvi', display_name: 'Vegetation Cover (NDVI)', category: 'vegetation', unit: 'index', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Root mechanical cohesion and canopy interception dampening splash erosion.' },
  { id: 14, name: 'distance_roads', display_name: 'Proximity to Roads', category: 'human', unit: 'meters', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Anthropogenic cut-slope toe excavation, blasting damage, and inadequate culverts.' },
  { id: 15, name: 'distance_faults', display_name: 'Proximity to Geological Faults', category: 'geology', unit: 'meters', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Shear fracturing, joint density, and seismically weakened rock mass.' },
  { id: 16, name: 'lithology', display_name: 'Bedrock Lithology', category: 'geology', unit: 'category', data_type: 'categorical', is_required: false, is_enabled: true, description: 'Rock type resistance: Phyllites, Schists, Quartzite, and Gneiss formations.' },
  { id: 17, name: 'distance_settlements', display_name: 'Proximity to Settlements', category: 'human', unit: 'meters', data_type: 'numerical', is_required: false, is_enabled: true, description: 'Distance to urban nodes, agricultural terraces, and infrastructure.' },
  { id: 18, name: 'slope_length', display_name: 'Slope Length Factor', category: 'terrain', unit: 'meters', data_type: 'numerical', is_required: false, is_enabled: false, description: 'Downslope length of uninterrupted surface flow contributing to shear runoff.' }
];

export default function FeatureRegistry() {
  const [featureList, setFeatureList] = useState(DEFAULT_FEATURES);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchFeatures = async () => {
      try {
        const res = await features.list();
        if (res.data && res.data.length > 0) {
          setFeatureList(res.data);
        }
      } catch {
        // Fallback to rich default features
      }
    };
    fetchFeatures();
  }, []);

  const toggleFeature = (id) => {
    setFeatureList((prev) =>
      prev.map((f) => {
        if (f.id === id && !f.is_required) {
          return { ...f, is_enabled: !f.is_enabled };
        }
        return f;
      })
    );
  };

  const categories = ['all', 'terrain', 'hydrology', 'climate', 'soil', 'vegetation', 'geology', 'human'];

  const filteredFeatures = featureList.filter((f) => {
    const matchesCategory = selectedCategory === 'all' || f.category.toLowerCase() === selectedCategory;
    const matchesSearch =
      f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.display_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const activeCount = featureList.filter((f) => f.is_enabled).length;

  return (
    <div className="feature-registry-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Feature Registry & Factor Configuration</h2>
          <p>Configure candidate conditioning factors, inspect scientific relevance, and select active feature subsets for machine learning.</p>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(198, 93%, 55%, 0.12)', color: 'var(--accent-primary)' }}>
            <Sliders size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Candidate Factors</div>
            <div className="stat-value">{featureList.length}</div>
            <div className="stat-change positive">Registered in system</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(152, 69%, 48%, 0.12)', color: 'var(--accent-success)' }}>
            <CheckCircle2 size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Active for Training</div>
            <div className="stat-value">{activeCount}</div>
            <div className="stat-change positive">{Math.round((activeCount / featureList.length) * 100)}% feature inclusion</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(263, 70%, 60%, 0.12)', color: 'var(--accent-secondary)' }}>
            <Mountain size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Mandatory Core Factors</div>
            <div className="stat-value">{featureList.filter((f) => f.is_required).length}</div>
            <div className="stat-change">Slope, Aspect, Elevation, Rain</div>
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="card" style={{ marginBottom: '1.5rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          {/* Category Tabs */}
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`btn btn-sm ${selectedCategory === cat ? 'btn-primary' : 'btn-secondary'}`}
                style={{ textTransform: 'capitalize' }}
              >
                {cat}
              </button>
            ))}
          </div>

          {/* Search box */}
          <div style={{ position: 'relative', width: '280px' }}>
            <Search size={16} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Search features..."
              className="form-input"
              style={{ paddingLeft: '32px' }}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Features Grid */}
      <div className="grid-3">
        {filteredFeatures.map((f) => (
          <div
            key={f.id}
            className="card"
            style={{
              borderColor: f.is_enabled ? 'var(--border-default)' : 'var(--border-subtle)',
              opacity: f.is_enabled ? 1 : 0.6,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              transition: 'all 0.2s ease',
            }}
          >
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.5rem' }}>
                <span className="badge badge-primary" style={{ textTransform: 'uppercase', fontSize: '0.68rem' }}>
                  {f.category}
                </span>

                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  {f.is_required && (
                    <span className="badge badge-warning" style={{ fontSize: '0.65rem' }}>Required</span>
                  )}
                  <label className="toggle" title={f.is_required ? 'Required feature' : 'Toggle feature'}>
                    <input
                      type="checkbox"
                      checked={f.is_enabled}
                      disabled={f.is_required}
                      onChange={() => toggleFeature(f.id)}
                    />
                    <span className="toggle-slider"></span>
                  </label>
                </div>
              </div>

              <h4 style={{ fontSize: '1.02rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.3rem' }}>
                {f.display_name}
              </h4>
              <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--accent-primary)', marginBottom: '0.6rem' }}>
                {f.name}
              </p>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4, marginBottom: '1rem' }}>
                {f.description}
              </p>
            </div>

            <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '0.75rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              <span>Unit: <strong style={{ color: 'var(--text-secondary)' }}>{f.unit}</strong></span>
              <span>Type: <strong style={{ color: 'var(--text-secondary)' }}>{f.data_type}</strong></span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
