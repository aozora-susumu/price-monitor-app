import axios from 'axios';

const rawApiBaseUrl = import.meta.env.VITE_API_BASE_URL?.trim();
const normalizedApiBaseUrl = rawApiBaseUrl
  ? rawApiBaseUrl.replace(/\/+$/, '')
  : import.meta.env.DEV
    ? 'http://localhost:8000'
    : '';

const apiClient = axios.create({
  baseURL: normalizedApiBaseUrl,
  headers: { 'Content-Type': 'application/json' },
});

export default apiClient;
