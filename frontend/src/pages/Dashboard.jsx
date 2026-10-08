import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  MapPin, Database, Brain, Map, TrendingUp, AlertTriangle,
  Mountain, Layers, Activity, ChevronRight, Zap
} from 'lucide-react';
import { studyAreas, features, models, health } from '../api';

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [areasRes, featRes, modelsRes] = await Promise.allSettled([
          studyAreas.list(),
          features.list(),
          models.list(),
        ]);
        setStats({
          areas:    areasRes.status === 'fulfilled' ? areasRes.value.data.length : 0,
          features: featRes.status === 'fulfilled' ? featRes.value.data.length : 0,
          models:   modelsRes.status === 'fulfilled' ? modelsRes.value.data.length : 0,
          bestAcc:  modelsRes.status === 'fulfilled' && modelsRes.value.data.length > 0
            ? Math.max(...modelsRes.value.data.map(m => m.accuracy || 0))
            : 0,
          bestModel: modelsRes.status === 'fulfilled' && modelsRes.value.data.length > 0
            ? modelsRes.value.data.find(m => m.is_best)?.model_name || 'N/A'
            : 'N/A',
        });
      } catch {
        setStats({ areas: 0, features: 0, models: 0, bestAcc: 0, bestModel: 'N/A' });
      }
      setLoading(false);
    })();
  }, []);

  if (loading) return (
    <div className="loading-screen">
      <div className="spinner spinner-lg" />
      <p>Loading dashboard…</p>
    </div>
  );

  const s = stats || {};

  const statCards = [
    { label: 'Study Areas', value: s.areas, icon: MapPin,   color: 'hsl(198, 93%, 55%)', bg: 'hsla(198, 93%, 55%, 0.1)' },
    { label: 'Features',    value: s.features, icon: Layers, color: 'hsl(263, 70%, 60%)', bg: 'hsla(263, 70%, 60%, 0.1)' },
    { label: 'ML Models',   value: s.models, icon: Brain,    color: 'hsl(152, 69%, 48%)', bg: 'hsla(152, 69%, 48%, 0.1)' },
    { label: 'Best Accuracy', value: `${(s.bestAcc * 100).toFixed(1)}%`, icon: TrendingUp, color: 'hsl(38, 92%, 55%)', bg: 'hsla(38, 92%, 55%, 0.1)' },
  ];

  const workflow = [
    { step: 1, title: 'Define Study Area',  desc: 'Select your region of interest on the interactive map', link: '/study-areas', icon: MapPin, done: s.areas > 0 },
    { step: 2, title: 'Load GIS Data',      desc: 'Upload or generate terrain, proximity, and climate layers', link: '/data', icon: Database, done: true },
    { step: 3, title: 'Configure Features',  desc: 'Select and weight 18+ geomorphological features', link: '/features', icon: Layers, done: s.features > 0 },
    { step: 4, title: 'Train ML Models',     desc: 'Train 5 classifiers with stratified k-fold cross-validation', link: '/training', icon: Brain, done: s.models > 0 },
    { step: 5, title: 'Generate Map',        desc: 'Click-to-predict or generate area-wide susceptibility grid', link: '/predict', icon: Map, done: false },
    { step: 6, title: 'Analyze Risk',        desc: 'Identify exposed roads, settlements, and infrastructure', link: '/risk', icon: AlertTriangle, done: false },
  ];

  return (
    <div className="animate-fade-in">
      {/* Hero Banner */}
      <div className="card" style={{ marginBottom: 'var(--sp-xl)', background: 'linear-gradient(135deg, hsla(198, 93%, 55%, 0.08), hsla(263, 70%, 60%, 0.08))', border: '1px solid hsla(198, 93%, 55%, 0.15)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-lg)' }}>
          <div style={{ width: 56, height: 56, background: 'var(--gradient-brand)', borderRadius: 'var(--radius-lg)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px hsla(198, 93%, 55%, 0.3)' }}>
            <Mountain size={28} color="#fff" />
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, marginBottom: 4 }}>
              <span className="gradient-text">LandSense AI</span>
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              Landslide Susceptibility & Risk Analysis — Machine Learning Platform
            </p>
          </div>
          <div className="badge badge-success"><Zap size={12} /> Demo Ready</div>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        {statCards.map((card, i) => (
          <div key={card.label} className={`stat-card animate-slide-up stagger-${i + 1}`}
               style={{ '--stat-color': card.color, '--stat-bg': card.bg }}>
            <div className="stat-icon" style={{ background: card.bg }}>
              <card.icon size={20} style={{ color: card.color }} />
            </div>
            <div className="stat-info">
              <div className="stat-label">{card.label}</div>
              <div className="stat-value">{card.value}</div>
            </div>
          </div>
        ))}
      </div>

      {/* Workflow Steps */}
      <div className="card animate-slide-up stagger-5" style={{ marginBottom: 'var(--sp-xl)' }}>
        <div className="card-header">
          <div className="card-title"><Activity size={18} /> Analysis Workflow Pipeline</div>
          <div className="badge badge-info">6 Phases</div>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 'var(--sp-md)' }}>
          {workflow.map((w) => (
            <Link key={w.step} to={w.link} style={{ textDecoration: 'none' }}>
              <div style={{
                display: 'flex', gap: 'var(--sp-sm)', padding: 'var(--sp-md)',
                borderRadius: 'var(--radius-md)', border: `1px solid ${w.done ? 'hsla(152, 69%, 48%, 0.2)' : 'var(--border-subtle)'}`,
                background: w.done ? 'hsla(152, 69%, 48%, 0.04)' : 'var(--bg-secondary)',
                transition: 'all 0.2s', cursor: 'pointer',
              }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--accent-primary)'; e.currentTarget.style.transform = 'translateY(-2px)'; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = w.done ? 'hsla(152, 69%, 48%, 0.2)' : 'var(--border-subtle)'; e.currentTarget.style.transform = 'none'; }}
              >
                <div style={{
                  width: 32, height: 32, borderRadius: 'var(--radius-md)', flexShrink: 0,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  background: w.done ? 'hsla(152, 69%, 48%, 0.15)' : 'hsla(198, 93%, 55%, 0.1)',
                  color: w.done ? 'var(--accent-success)' : 'var(--accent-primary)',
                  fontSize: '0.75rem', fontWeight: 700,
                }}>
                  {w.done ? '✓' : w.step}
                </div>
                <div>
                  <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: 2 }}>{w.title}</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{w.desc}</div>
                </div>
                <ChevronRight size={16} style={{ marginLeft: 'auto', alignSelf: 'center', color: 'var(--text-muted)' }} />
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* Best Model Info */}
      {s.bestModel !== 'N/A' && (
        <div className="card animate-slide-up stagger-6">
          <div className="card-header">
            <div className="card-title"><Brain size={18} /> Best Performing Model</div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--sp-lg)' }}>
            <div style={{ padding: 'var(--sp-md) var(--sp-lg)', background: 'hsla(152, 69%, 48%, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid hsla(152, 69%, 48%, 0.15)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4 }}>Model</div>
              <div style={{ fontSize: '1rem', fontWeight: 700 }}>{s.bestModel.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}</div>
            </div>
            <div style={{ padding: 'var(--sp-md) var(--sp-lg)', background: 'hsla(198, 93%, 55%, 0.08)', borderRadius: 'var(--radius-md)', border: '1px solid hsla(198, 93%, 55%, 0.15)' }}>
              <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginBottom: 4 }}>Accuracy</div>
              <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--accent-success)' }}>{(s.bestAcc * 100).toFixed(1)}%</div>
            </div>
            <Link to="/models" className="btn btn-secondary" style={{ marginLeft: 'auto' }}>
              View Comparison <ChevronRight size={16} />
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}
