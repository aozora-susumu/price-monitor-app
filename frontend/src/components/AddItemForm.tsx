import AddIcon from '@mui/icons-material/Add';
import { Box, Button, CircularProgress, TextField, Typography } from '@mui/material';
import { useState } from 'react';
import { addItem } from '../api/items';
import type { WatchItem } from '../types';

interface Props {
  onAdded: (item: WatchItem) => void;
}

export default function AddItemForm({ onAdded }: Props) {
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    setLoading(true);
    setError(null);
    try {
      const item = await addItem({ keyword: keyword.trim() });
      onAdded(item);
      setKeyword('');
    } catch (err: unknown) {
      if (
        err &&
        typeof err === 'object' &&
        'response' in err &&
        err.response &&
        typeof err.response === 'object' &&
        'status' in err.response &&
        err.response.status === 409
      ) {
        setError('この商品はすでに監視リストに追加されています');
      } else {
        setError('商品の追加に失敗しました。キーワードを確認してください');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}
    >
      <TextField
        label="キーワードで商品を追加"
        placeholder="例: Fire TV Stick"
        value={keyword}
        onChange={(e) => setKeyword(e.target.value)}
        size="small"
        sx={{ flex: 1 }}
        error={!!error}
        helperText={error}
        disabled={loading}
      />
      <Button
        type="submit"
        variant="contained"
        startIcon={
          loading ? <CircularProgress size={16} color="inherit" /> : <AddIcon />
        }
        disabled={loading || !keyword.trim()}
        sx={{ mt: 0.25 }}
      >
        追加
      </Button>
      {loading && (
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1.5 }}>
          楽天から商品情報を取得中...
        </Typography>
      )}
    </Box>
  );
}
