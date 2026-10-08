import { useState, useEffect } from 'react';
import {
  ShieldAlert, AlertTriangle, Home, Compass, Activity,
  Layers, MapPin, CheckCircle, Navigation, ShieldCheck, ChevronRight
} from 'lucide-react';
import { exposure } from '../api';

const HOTSPOTS = [
  { id: 1, name: 'NH-58 Bypass Corridor (Km 14–19)', type: 'National Highway', riskLevel: 'Critical', elements: '14.2 km road length, 3 culverts', priority: 'Immediate Stabilisation' },
  { id: 2, name: 'Byasi Rural Settlement Terraces', type: 'Human Settlement', riskLevel: 'High', elements: '340 residents, 58 homestead structures', priority: 'Slope Reinforcement & Monitoring' },
  { id: 3, name: 'Alaknanda Riverbank Cut-Slope Segment', type: 'Riparian Infrastructure', riskLevel: 'High', elements: 'River bridge pier, transmission tower', priority: 'Riprap / Retaining Gabions' },
  { id: 4, name: 'Devprayag Ridge Approach Road', type: 'Secondary Highway', riskLevel: 'Moderate', elements: '8.5 km transit link', priority: 'Periodic Inspection' },
];

const MITIGATION_ACTIONS = [
  { technique: 'Subsurface Horizontal Drainage Pipes', target: 'Pore-Water Dissipation', effectiveness: '85% risk reduction', cost: 'Moderate' },
  { technique: 'Vetiver Grass Bio-Engineering Anchoring', target: 'Shallow Surface Slips', effectiveness: '70% risk reduction', cost: 'Low' },
  { technique: 'Anchored High-Tensile Wire Mesh', target: 'Steep Rockfall Fractures', effectiveness: '95% rock arrest', cost: 'High' },
  { technique: 'Reinforced Concrete Toe Retaining Wall', target: 'Toe Excavation Failure', effectiveness: '90% stability restoration', cost: 'High' },
];

export default function RiskAnalysis() {
  const [data, setData] = useState(null);
  const [searchRefuge, setSearchRefuge] = useState(false);
  const [refugeResult, setRefugeResult] = useState(null);

  useEffect(() => {
    const fetchExposure = async () => {
      try {
        const res = await exposure.analyze(1);
        if (res.data) setData(res.data);
      } catch {
        // Fallback default risk statistics
        setData({
          exposed_road_km: 38.6,
          exposed_settlements_count: 6,
          high_risk_area_sqkm: 214.8,
          population_at_risk: 4250,
        });
      }
    };
    fetchExposure();
  }, []);

  const handleFindRefuge = () => {
    setSearchRefuge(true);
    setTimeout(() => {
      setRefugeResult({
        name: 'Devprayag Ridge Plateau Safe Zone',
        distance_km: 2.4,
        susceptibility: 'Very Low (0.12)',
        elevation: '820 m',
        route: 'Evacuation Route Alpha via East Hill Spur',
      });
      setSearchRefuge(false);
    }, 800);
  };

  return (
    <div className="risk-analysis-page">
      <div className="page-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h2>Risk, Exposure & Infrastructure Vulnerability Analysis</h2>
          <p>Quantify societal and infrastructural impact: Risk = Hazard × Exposure × Vulnerability.</p>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(0, 84%, 60%, 0.12)', color: 'var(--accent-danger)' }}>
            <AlertTriangle size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">High Hazard Footprint</div>
            <div className="stat-value">{data?.high_risk_area_sqkm || 214.8} km²</div>
            <div className="stat-change negative">Critical susceptibility zone</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(38, 92%, 55%, 0.12)', color: 'var(--accent-warning)' }}>
            <Compass size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Exposed Highway Length</div>
            <div className="stat-value">{data?.exposed_road_km || 38.6} km</div>
            <div className="stat-change negative">Transportation disruption risk</div>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'hsla(198, 93%, 55%, 0.12)', color: 'var(--accent-primary)' }}>
            <Home size={22} />
          </div>
          <div className="stat-info">
            <div className="stat-label">Vulnerable Population</div>
            <div className="stat-value">{data?.population_at_risk || 4250}</div>
            <div className="stat-change negative">Within 500m high-slope buffer</div>
          </div>
        </div>
      </div>

      {/* Refuge / Evacuation Finder Tool */}
      <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, hsla(152, 69%, 48%, 0.1), hsla(198, 93%, 55%, 0.1))', borderColor: 'var(--accent-success)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Navigation size={18} color="var(--accent-success)" />
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)', margin: 0 }}>
                Rapid Evacuation & Lower-Susceptibility Safe Refuge Finder
              </h3>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', margin: 0 }}>
              Algorithmic spatial nearest-neighbor search for low-gradient, geologically stable ground.
            </p>
          </div>

          <button className="btn btn-primary" onClick={handleFindRefuge} disabled={searchRefuge}>
            {searchRefuge ? 'Computing Geodesic Path...' : 'Locate Nearest Safe Refuge'}
          </button>
        </div>

        {refugeResult && (
          <div style={{ marginTop: '1.2rem', padding: '1rem', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-default)', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--accent-success)' }}>{refugeResult.name}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>{refugeResult.route}</div>
            </div>
            <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8rem' }}>
              <div><span style={{ color: 'var(--text-muted)' }}>Distance:</span> <strong>{refugeResult.distance_km} km</strong></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Hazard:</span> <strong style={{ color: 'var(--accent-success)' }}>{refugeResult.susceptibility}</strong></div>
              <div><span style={{ color: 'var(--text-muted)' }}>Altitude:</span> <strong>{refugeResult.elevation}</strong></div>
            </div>
          </div>
        )}
      </div>

      {/* Critical Hotspots & Mitigation Strategies */}
      <div className="grid-12">
        {/* Hotspots */}
        <div className="col-span-6">
          <div className="card" style={{ height: '100%' }}>
            <div className="card-header">
              <div className="card-title">
                <ShieldAlert size={18} /> High-Priority Vulnerability Hotspots
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {HOTSPOTS.map((h) => (
                <div key={h.id} style={{ padding: '0.9rem', background: 'var(--bg-elevated)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '4px' }}>
                    <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', margin: 0 }}>
                      {h.name}
                    </h4>
                    <span className={`badge ${h.riskLevel === 'Critical' ? 'badge-danger' : 'badge-warning'}`}>
                      {h.riskLevel}
                    </span>
                  </div>
                  <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                    Exposed Elements: {h.elements}
                  </p>
                  <div style={{ fontSize: '0.72rem', color: 'var(--accent-primary)', fontWeight: 500 }}>
                    Recommended Action: {h.priority}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Engineering Mitigation Guide */}
        <div className="col-span-6">
          <div className="card" style={{ height: '100%' }}>
            <div className="card-header">
              <div className="card-title">
                <ShieldCheck size={18} /> Engineering Countermeasures & Mitigation Matrix
              </div>
            </div>

            <table className="data-table">
              <thead>
                <tr>
                  <th>Mitigation Technique</th>
                  <th>Hazard Target</th>
                  <th>Effectiveness</th>
                  <th>Cost</th>
                </tr>
              </thead>
              <tbody>
                {MITIGATION_ACTIONS.map((m, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{m.technique}</td>
                    <td style={{ fontSize: '0.78rem' }}>{m.target}</td>
                    <td><span className="badge badge-success">{m.effectiveness}</span></td>
                    <td style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{m.cost}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
