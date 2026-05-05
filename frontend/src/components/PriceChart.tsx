import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import type { PricePoint } from '../types';

interface Props {
  history: PricePoint[];
}

export default function PriceChart({ history }: Props) {
  if (history.length === 0) {
    return null;
  }

  const data = history.map((p) => ({
    date: new Date(p.timestamp).toLocaleDateString('ja-JP', {
      month: 'short',
      day: 'numeric',
    }),
    price: p.price,
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" tick={{ fontSize: 11 }} />
        <YAxis
          tick={{ fontSize: 11 }}
          tickFormatter={(value) => `¥${Number(value).toLocaleString()}`}
          width={72}
        />
        <Tooltip
          formatter={(value) => [`¥${Number(value ?? 0).toLocaleString()}`, '価格']}
        />
        <Line
          type="monotone"
          dataKey="price"
          stroke="#1976d2"
          dot={false}
          strokeWidth={2}
        />
      </LineChart>
    </ResponsiveContainer>
  );
}
