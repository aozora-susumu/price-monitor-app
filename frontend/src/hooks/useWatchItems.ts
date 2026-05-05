import { useEffect, useState } from 'react';
import { checkNow, fetchItems } from '../api/items';
import type { CheckSummary, WatchItem } from '../types';

interface SnackbarState {
  open: boolean;
  message: string;
  severity: 'success' | 'error' | 'info';
}

export function useWatchItems() {
  const [items, setItems] = useState<WatchItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkRunning, setCheckRunning] = useState(false);
  const [snackbar, setSnackbar] = useState<SnackbarState>({
    open: false,
    message: '',
    severity: 'info',
  });

  useEffect(() => {
    fetchItems()
      .then(setItems)
      .catch(() =>
        setSnackbar({
          open: true,
          message: '商品一覧の取得に失敗しました',
          severity: 'error',
        })
      )
      .finally(() => setLoading(false));
  }, []);

  const addItem = (item: WatchItem) => {
    setItems((prev) => [item, ...prev]);
    setSnackbar({
      open: true,
      message: `「${item.title}」を追加しました`,
      severity: 'success',
    });
  };

  const updateItem = (updated: WatchItem) => {
    setItems((prev) =>
      prev.map((i) => (i.item_code === updated.item_code ? updated : i))
    );
  };

  const deleteItem = (itemCode: string) => {
    setItems((prev) => prev.filter((i) => i.item_code !== itemCode));
    setSnackbar({ open: true, message: '商品を削除しました', severity: 'info' });
  };

  const runCheckNow = async () => {
    setCheckRunning(true);
    try {
      const summary: CheckSummary = await checkNow();
      const msg = `チェック完了: ${summary.checked_count}件チェック, ${summary.notified_count}件通知`;
      setSnackbar({ open: true, message: msg, severity: 'success' });
      const refreshed = await fetchItems();
      setItems(refreshed);
    } catch {
      setSnackbar({
        open: true,
        message: '価格チェックに失敗しました',
        severity: 'error',
      });
    } finally {
      setCheckRunning(false);
    }
  };

  const closeSnackbar = () => setSnackbar((s) => ({ ...s, open: false }));

  return {
    items,
    loading,
    checkRunning,
    snackbar,
    addItem,
    updateItem,
    deleteItem,
    runCheckNow,
    closeSnackbar,
  };
}
