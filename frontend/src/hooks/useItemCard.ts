import { useEffect, useState } from 'react';
import { deleteItem, updateItem } from '../api/items';
import type { WatchItem } from '../types';

interface UseItemCardProps {
  item: WatchItem;
  onUpdated: (item: WatchItem) => void;
  onDeleted: (itemCode: string) => void;
}

export function useItemCard({ item, onUpdated, onDeleted }: UseItemCardProps) {
  const [loading, setLoading] = useState(false);
  const [thresholdPct, setThresholdPct] = useState(
    Math.round(item.drop_rate_threshold * 100)
  );
  const [thresholdInput, setThresholdInput] = useState(
    String(Math.round(item.drop_rate_threshold * 100))
  );

  // drop_rate_threshold は「今すぐチェック」実行後に親が items を再フェッチして更新する。
  // useState の初期値はマウント時にしか評価されないため、item の変化を useEffect で明示的に同期する。
  useEffect(() => {
    const pct = Math.round(item.drop_rate_threshold * 100);
    setThresholdPct(pct);
    setThresholdInput(String(pct));
  }, [item.drop_rate_threshold]);

  const handleNotifyToggle = async () => {
    setLoading(true);
    try {
      const updated = await updateItem(item.item_code, { notify: !item.notify });
      onUpdated(updated);
    } finally {
      setLoading(false);
    }
  };

  const handleThresholdChange = (_: Event, value: number | number[]) => {
    setThresholdPct(value as number);
  };

  const handleThresholdCommit = async (
    _: React.SyntheticEvent | Event,
    value: number | number[]
  ) => {
    const pct = value as number;
    setThresholdPct(pct);
    setLoading(true);
    try {
      const updated = await updateItem(item.item_code, {
        drop_rate_threshold: pct / 100,
      });
      onUpdated(updated);
    } finally {
      setLoading(false);
    }
  };

  const handleThresholdInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    setThresholdInput(e.target.value);
  };

  const commitThresholdInput = async () => {
    const raw = parseInt(thresholdInput, 10);
    const pct = isNaN(raw) ? thresholdPct : Math.min(50, Math.max(1, raw));
    setThresholdPct(pct);
    setThresholdInput(String(pct));
    setLoading(true);
    try {
      const updated = await updateItem(item.item_code, {
        drop_rate_threshold: pct / 100,
      });
      onUpdated(updated);
    } finally {
      setLoading(false);
    }
  };

  const handleThresholdKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') commitThresholdInput();
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

  return {
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
  };
}
