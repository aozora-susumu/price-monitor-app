import {
  Alert,
  Box,
  CircularProgress,
  Container,
  Divider,
  Paper,
  Snackbar,
  Typography,
} from '@mui/material';
import AddItemForm from './components/AddItemForm';
import AppHeader from './components/AppHeader';
import ItemList from './components/ItemList';
import { useWatchItems } from './hooks/useWatchItems';

function App() {
  const {
    items,
    loading,
    checkRunning,
    snackbar,
    addItem,
    updateItem,
    deleteItem,
    runCheckNow,
    closeSnackbar,
  } = useWatchItems();

  return (
    <>
      <AppHeader checkRunning={checkRunning} onCheckNow={runCheckNow} />

      <Container maxWidth="md">
        <Paper sx={{ p: 2, mb: 3 }} elevation={1}>
          <Typography variant="subtitle1" gutterBottom sx={{ fontWeight: 'bold' }}>
            商品を追加
          </Typography>
          <AddItemForm onAdded={addItem} />
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
          <ItemList items={items} onUpdated={updateItem} onDeleted={deleteItem} />
        )}
      </Container>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={closeSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity={snackbar.severity} onClose={closeSnackbar}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </>
  );
}

export default App;
