import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Header from './components/Layout/Header';
import Dashboard from './pages/Dashboard';
import StudyAreas from './pages/StudyAreas';
import DataManagement from './pages/DataManagement';
import FeatureRegistry from './pages/FeatureRegistry';
import HistoricalLandslides from './pages/HistoricalLandslides';
import Training from './pages/Training';
import ModelComparison from './pages/ModelComparison';
import PredictionMap from './pages/PredictionMap';
import RiskAnalysis from './pages/RiskAnalysis';
import Reports from './pages/Reports';
import Settings from './pages/Settings';
import './App.css';

const pageMap = {
  '/':                    { title: 'Dashboard',              sub: 'Overview' },
  '/study-areas':         { title: 'Study Areas',            sub: 'Region Management' },
  '/data':                { title: 'Data Management',        sub: 'GIS Layers' },
  '/features':            { title: 'Feature Registry',       sub: 'ML Features' },
  '/historical':          { title: 'Historical Landslides',  sub: 'Inventory' },
  '/training':            { title: 'Model Training',         sub: 'ML Pipeline' },
  '/models':              { title: 'Model Comparison',       sub: 'Evaluation' },
  '/predict':             { title: 'Susceptibility Map',     sub: 'Prediction' },
  '/risk':                { title: 'Risk Analysis',          sub: 'Exposure' },
  '/reports':             { title: 'Reports',                sub: 'PDF Export' },
  '/settings':            { title: 'Settings',               sub: 'Configuration' },
};

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <div className="app-main">
          <Header pageMap={pageMap} />
          <main className="app-content">
            <Routes>
              <Route path="/"           element={<Dashboard />} />
              <Route path="/study-areas" element={<StudyAreas />} />
              <Route path="/data"       element={<DataManagement />} />
              <Route path="/features"   element={<FeatureRegistry />} />
              <Route path="/historical" element={<HistoricalLandslides />} />
              <Route path="/training"   element={<Training />} />
              <Route path="/models"     element={<ModelComparison />} />
              <Route path="/predict"    element={<PredictionMap />} />
              <Route path="/risk"       element={<RiskAnalysis />} />
              <Route path="/reports"    element={<Reports />} />
              <Route path="/settings"   element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}
