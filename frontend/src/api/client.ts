import axios from 'axios';

// 末尾スラッシュを除去して二重スラッシュになるのを防ぐ。
// 本番では VITE_API_BASE_URL を空にして同一オリジンで配信する想定。
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
