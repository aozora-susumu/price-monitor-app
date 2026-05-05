import type {
  AddItemRequest,
  CheckSummary,
  UpdateItemRequest,
  WatchItem,
} from '../types';
import apiClient from './client';

export const fetchItems = (): Promise<WatchItem[]> =>
  apiClient.get<WatchItem[]>('/api/items').then((r) => r.data);

export const addItem = (payload: AddItemRequest): Promise<WatchItem> =>
  apiClient.post<WatchItem>('/api/items', payload).then((r) => r.data);

export const updateItem = (
  itemCode: string,
  payload: UpdateItemRequest
): Promise<WatchItem> =>
  apiClient.patch<WatchItem>(`/api/items/${itemCode}`, payload).then((r) => r.data);

export const deleteItem = (itemCode: string): Promise<void> =>
  apiClient.delete(`/api/items/${itemCode}`).then(() => undefined);

export const checkNow = (): Promise<CheckSummary> =>
  apiClient.post<CheckSummary>('/api/check-now').then((r) => r.data);
