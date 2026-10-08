import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard, MapPin, Database, List, History,
  Brain, BarChart3, Map, Shield, FileText, Settings,
  Mountain
} from 'lucide-react';

const NAV_SECTIONS = [
  {
    title: 'Overview',
    items: [
      { to: '/',            icon: LayoutDashboard, label: 'Dashboard' },
      { to: '/study-areas', icon: MapPin,          label: 'Study Areas' },
    ],
  },
  {
    title: 'Data Pipeline',
    items: [
      { to: '/data',       icon: Database, label: 'Data Management' },
      { to: '/features',   icon: List,     label: 'Feature Registry' },
      { to: '/historical', icon: History,  label: 'Landslide Inventory' },
    ],
  },
  {
    title: 'Machine Learning',
    items: [
      { to: '/training', icon: Brain,    label: 'Model Training' },
      { to: '/models',   icon: BarChart3, label: 'Model Comparison' },
    ],
  },
  {
    title: 'Analysis',
    items: [
      { to: '/predict', icon: Map,    label: 'Susceptibility Map' },
      { to: '/risk',    icon: Shield, label: 'Risk Analysis' },
    ],
  },
  {
    title: 'Output',
    items: [
      { to: '/reports',  icon: FileText, label: 'Reports' },
      { to: '/settings', icon: Settings, label: 'Settings' },
    ],
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="sidebar-logo-icon"><Mountain size={20} color="#fff" /></div>
        <h1>Land<span>Sense</span> AI</h1>
      </div>

      <nav className="sidebar-nav">
        {NAV_SECTIONS.map((section) => (
          <div className="sidebar-section" key={section.title}>
            <div className="sidebar-section-title">{section.title}</div>
            {section.items.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                end={item.to === '/'}
                className={({ isActive }) =>
                  `sidebar-link${isActive ? ' active' : ''}`
                }
              >
                <item.icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>

      <div className="sidebar-footer">
        <div className="sidebar-footer-text">
          B.Tech Final Year Project<br />
          Landslide Susceptibility & Risk Analysis
        </div>
      </div>
    </aside>
  );
}
