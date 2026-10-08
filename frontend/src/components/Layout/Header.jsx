import { useLocation } from 'react-router-dom';
import { ChevronRight, Wifi } from 'lucide-react';

export default function Header({ pageMap }) {
  const { pathname } = useLocation();
  const page = pageMap[pathname] || { title: 'LandSense AI', sub: '' };

  return (
    <header className="header">
      <div className="header-left">
        <div>
          <div className="header-title">{page.title}</div>
          <div className="header-breadcrumb">
            LandSense AI <ChevronRight size={12} /> <span>{page.sub}</span>
          </div>
        </div>
      </div>
      <div className="header-right">
        <div className="header-status">
          <div className="header-status-dot" />
          <Wifi size={14} />
          <span>Backend Online</span>
        </div>
      </div>
    </header>
  );
}
