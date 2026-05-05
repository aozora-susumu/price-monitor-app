import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import {
  Alert,
  Box,
  Button,
  CircularProgress,
  Container,
  Divider,
  Paper,
  Snackbar,
  Typography,
} from '@mui/material';
import { useEffect, useState } from 'react';
import { checkNow, fetchItems } from './api/items';
import AddItemForm from './components/AddItemForm';
import ItemList from './components/ItemList';
import type { CheckSummary, WatchItem } from './types';

function App() {
  const [items, setItems] = useState<WatchItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [checkRunning, setCheckRunning] = useState(false);
  const [snackbar, setSnackbar] = useState<{
    open: boolean;
    message: string;
    severity: 'success' | 'error' | 'info';
  }>({ open: false, message: '', severity: 'info' });

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

  const handleAdded = (item: WatchItem) => {
    setItems((prev) => [item, ...prev]);
    setSnackbar({
      open: true,
      message: `「${item.title}」を追加しました`,
      severity: 'success',
    });
  };

  const handleUpdated = (updated: WatchItem) => {
    setItems((prev) =>
      prev.map((i) => (i.item_code === updated.item_code ? updated : i))
    );
  };

  const handleDeleted = (itemCode: string) => {
    setItems((prev) => prev.filter((i) => i.item_code !== itemCode));
    setSnackbar({ open: true, message: '商品を削除しました', severity: 'info' });
  };

  const handleCheckNow = async () => {
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

  return (
    <>
      <Box sx={{ bgcolor: 'primary.main', color: 'white', py: 2, mb: 3 }}>
        <Container maxWidth="md">
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Box>
              <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                価格モニター
              </Typography>
              <Typography variant="caption" sx={{ opacity: 0.8 }}>
                楽天市場の価格を自動監視
              </Typography>
            </Box>
            <Button
              variant="contained"
              color="inherit"
              startIcon={
                checkRunning ? (
                  <CircularProgress size={16} color="primary" />
                ) : (
                  <PlayArrowIcon />
                )
              }
              onClick={handleCheckNow}
              disabled={checkRunning}
              sx={{ color: 'primary.main', bgcolor: 'white' }}
            >
              今すぐチェック
            </Button>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="md">
        <Paper sx={{ p: 2, mb: 3 }} elevation={1}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
            商品を追加
          </Typography>
          <AddItemForm onAdded={handleAdded} />
        </Paper>

        <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
          監視中の商品 ({items.length})
        </Typography>
        <Divider sx={{ mb: 2 }} />

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
            <CircularProgress />
          </Box>
        ) : (
          <ItemList items={items} onUpdated={handleUpdated} onDeleted={handleDeleted} />
        )}
      </Container>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert
          severity={snackbar.severity}
          onClose={() => setSnackbar((s) => ({ ...s, open: false }))}
        >
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}

export default App;
