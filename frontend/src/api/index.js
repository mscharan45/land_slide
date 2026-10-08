/**
 * LandSense AI — API Service Layer
 * Centralized Axios client for all backend communication.
 */
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Study Areas ──────────────────────────────────────────────────────────
export const studyAreas = {
  list:   ()       => api.get('/study-areas/'),
  get:    (id)     => api.get(`/study-areas/${id}`),
  create: (data)   => api.post('/study-areas/', data),
};

// ── Datasets ─────────────────────────────────────────────────────────────
export const datasets = {
  list:   (areaId) => api.get('/datasets/', { params: { study_area_id: areaId } }),
  upload: (areaId, file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post(`/datasets/upload?study_area_id=${areaId}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ── Features ─────────────────────────────────────────────────────────────
export const features = {
  list:         ()           => api.get('/features/'),
  toggle:       (id, body)   => api.put(`/features/${id}`, body),
  availability: (areaId)     => api.get(`/features/availability/${areaId}`),
};

// ── Historical Landslides ────────────────────────────────────────────────
export const landslides = {
  list:   (areaId) => api.get('/historical-landslides/', { params: { study_area_id: areaId } }),
  stats:  (areaId) => api.get(`/historical-landslides/stats/${areaId}`),
  upload: (areaId, file) => {
    const form = new FormData();
    form.append('file', file);
    return api.post(`/historical-landslides/upload?study_area_id=${areaId}`, form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
};

// ── Training ─────────────────────────────────────────────────────────────
export const training = {
  createDataset: (body) => api.post('/training/dataset', body),
  startRun:      (body) => api.post('/training/run', body),
  listRuns:      (areaId) => api.get('/training/runs', { params: { study_area_id: areaId } }),
};

// ── Models ───────────────────────────────────────────────────────────────
export const models = {
  list:    ()       => api.get('/models/'),
  get:     (id)     => api.get(`/models/${id}`),
  compare: (runId)  => api.get(`/models/compare/${runId}`),
};

// ── Predictions ──────────────────────────────────────────────────────────
export const predictions = {
  location: (body)  => api.post('/predict/location', body),
  area:     (body)  => api.post('/predict/area', body),
  history:  (areaId)=> api.get('/predict/history', { params: { study_area_id: areaId } }),
};

// ── Exposure / Risk ──────────────────────────────────────────────────────
export const exposure = {
  analyze:   (areaId) => api.get(`/exposure/${areaId}`),
  nearbyLow: (lat, lng, areaId) =>
    api.get('/exposure/nearby-lower', { params: { lat, lng, study_area_id: areaId } }),
};

// ── Reports ──────────────────────────────────────────────────────────────
export const reports = {
  generate: (body) => api.post('/reports/generate', body),
  download: (id)   => `${API_BASE}/reports/download/${id}`,
};

// ── Health ───────────────────────────────────────────────────────────────
export const health = {
  check: () => api.get('/health'),
};

export default api;
