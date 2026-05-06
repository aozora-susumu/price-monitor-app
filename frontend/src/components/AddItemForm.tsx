import AddIcon from '@mui/icons-material/Add';
import { Box, Button, CircularProgress, TextField, Typography } from '@mui/material';
import axios from 'axios';
import { useState } from 'react';
import { addItem } from '../api/items';
import type { WatchItem } from '../types';

interface Props {
  onAdded: (item: WatchItem) => void;
}

const MIN_KEYWORD_LENGTH = 1;
const MAX_KEYWORD_LENGTH = 100;

export default function AddItemForm({ onAdded }: Props) {
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleKeywordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    if (value.length <= MAX_KEYWORD_LENGTH) {
      setKeyword(value);
      setError(null);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = keyword.trim();

    if (trimmed.length < MIN_KEYWORD_LENGTH) {
      setError('1文字以上入力してください');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const item = await addItem({ keyword: trimmed });
      onAdded(item);
      setKeyword('');
    } catch (err: unknown) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        setError('この商品はすでに監視リストに追加されています');
      } else if (axios.isAxiosError(err) && err.response?.status === 422) {
        setError('キーワードは1～100文字で入力してください');
      } else {
        setError('商品の追加に失敗しました。キーワードを確認してください');
      }
    } finally {
      setLoading(false);
    }
  };

  const helperText = error || `${keyword.length}/${MAX_KEYWORD_LENGTH}文字`;

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{ display: 'flex', gap: 1, alignItems: 'flex-start' }}
    >
      <TextField
        label="キーワードで商品を追加"
        placeholder="例: Fire TV Stick (1～100文字)"
        value={keyword}
        onChange={handleKeywordChange}
        size="small"
        sx={{ flex: 1 }}
        error={!!error}
        helperText={helperText}
        disabled={loading}
      />
      <Button
        type="submit"
        variant="contained"
        startIcon={
          loading ? <CircularProgress size={16} color="inherit" /> : <AddIcon />
        }
        disabled={loading || keyword.trim().length === 0}
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
