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
  Switch,
  Tooltip,
  Typography,
} from '@mui/material';
import { useItemCard } from '../hooks/useItemCard';
import type { WatchItem } from '../types';
import PriceChart from './PriceChart';
import ThresholdControl from './ThresholdControl';

interface Props {
  item: WatchItem;
  onUpdated: (item: WatchItem) => void;
  onDeleted: (itemCode: string) => void;
}

export default function ItemCard({ item, onUpdated, onDeleted }: Props) {
  const {
    loading,
    thresholdPct,
    thresholdInput,
    handleNotifyToggle,
    handleThresholdChange,
    handleThresholdCommit,
    handleThresholdInput,
    commitThresholdInput,
    handleThresholdKeyDown,
    handleDelete,
  } = useItemCard({ item, onUpdated, onDeleted });

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

          <ThresholdControl
            value={thresholdPct}
            inputValue={thresholdInput}
            disabled={loading || !item.notify}
            onChange={handleThresholdChange}
            onChangeCommitted={handleThresholdCommit}
            onInputChange={handleThresholdInput}
            onInputBlur={commitThresholdInput}
            onInputKeyDown={handleThresholdKeyDown}
          />

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
