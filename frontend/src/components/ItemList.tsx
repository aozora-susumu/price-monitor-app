import { Box, Typography } from '@mui/material';
import type { WatchItem } from '../types';
import ItemCard from './ItemCard';

interface Props {
  items: WatchItem[];
  onUpdated: (item: WatchItem) => void;
  onDeleted: (itemCode: string) => void;
}

export default function ItemList({ items, onUpdated, onDeleted }: Props) {
  if (items.length === 0) {
    return (
      <Box sx={{ textAlign: 'center', py: 6 }}>
        <Typography color="text.secondary">
          監視中の商品はまだありません。キーワードで商品を追加してください。
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
      {items.map((item) => (
        <ItemCard
          key={item.item_code}
          item={item}
          onUpdated={onUpdated}
          onDeleted={onDeleted}
        />
      ))}
    </Box>
  );
}
