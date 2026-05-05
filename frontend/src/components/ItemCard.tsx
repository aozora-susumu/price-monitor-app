import DeleteIcon from '@mui/icons-material/Delete';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import OpenInNewIcon from '@mui/icons-material/OpenInNew';
import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Chip,
  FormControlLabel,
  IconButton,
  Slider,
  Switch,
  Tooltip,
  Typography,
} from '@mui/material';
import { useState } from 'react';
import { deleteItem, updateItem } from '../api/items';
import type { WatchItem } from '../types';
import PriceChart from './PriceChart';

interface Props {
  item: WatchItem;
  onUpdated: (item: WatchItem) => void;
  onDeleted: (itemCode: string) => void;
}

export default function ItemCard({ item, onUpdated, onDeleted }: Props) {
  const [loading, setLoading] = useState(false);

  const handleNotifyToggle = async () => {
    setLoading(true);
    try {
      const updated = await updateItem(item.item_code, {
        notify: !item.notify,
      });
      onUpdated(updated);
    } finally {
      setLoading(false);
    }
  };

  const handleThresholdChange = async (_: Event, value: number | number[]) => {
    const threshold = (value as number) / 100;
    setLoading(true);
    try {
      const updated = await updateItem(item.item_code, {
        drop_rate_threshold: threshold,
      });
      onUpdated(updated);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`「${item.title}」を削除しますか？`)) return;
    setLoading(true);
    try {
      await deleteItem(item.item_code);
      onDeleted(item.item_code);
    } finally {
      setLoading(false);
    }
  };

  const lastChecked = item.last_checked
    ? new Date(item.last_checked).toLocaleString('ja-JP')
    : '未チェック';

  return (
    <Accordion disableGutters>
      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flex: 1, mr: 1 }}>
          {item.image && (
            <Box
              component="img"
              src={item.image}
              alt={item.title}
              sx={{ width: 48, height: 48, objectFit: 'contain', flexShrink: 0 }}
            />
          )}
          <Box sx={{ flex: 1, minWidth: 0 }}>
            <Typography
              variant="body2"
              sx={{
                fontWeight: 'bold',
                overflow: 'hidden',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
              }}
            >
              {item.title}
            </Typography>
            <Typography variant="h6" color="primary">
              ¥{item.current_price.toLocaleString()}
            </Typography>
          </Box>
          <Chip
            label={item.notify ? '通知ON' : '通知OFF'}
            color={item.notify ? 'success' : 'default'}
            size="small"
          />
        </Box>
      </AccordionSummary>

      <AccordionDetails>
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          <PriceChart history={item.price_history} />

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={item.notify}
                  onChange={handleNotifyToggle}
                  disabled={loading}
                />
              }
              label="価格下落通知"
            />
          </Box>

          <Box>
            <Typography variant="body2" gutterBottom>
              通知閾値: {(item.drop_rate_threshold * 100).toFixed(0)}% 以上の下落
            </Typography>
            <Slider
              value={item.drop_rate_threshold * 100}
              min={1}
              max={50}
              step={1}
              marks={[
                { value: 5, label: '5%' },
                { value: 10, label: '10%' },
                { value: 20, label: '20%' },
                { value: 30, label: '30%' },
              ]}
              onChange={handleThresholdChange}
              disabled={loading || !item.notify}
              sx={{ maxWidth: 400 }}
            />
          </Box>

          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            <Typography variant="caption" color="text.secondary">
              最終チェック: {lastChecked}
            </Typography>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Tooltip title="楽天で開く">
                <IconButton
                  size="small"
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  component="a"
                >
                  <OpenInNewIcon fontSize="small" />
                </IconButton>
              </Tooltip>
              <Tooltip title="削除">
                <IconButton
                  size="small"
                  color="error"
                  onClick={handleDelete}
                  disabled={loading}
                >
                  <DeleteIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Box>
      </AccordionDetails>
    </Accordion>
  );
}
