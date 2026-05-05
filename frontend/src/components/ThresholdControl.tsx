import { InputAdornment, Slider, TextField, Box, Typography } from '@mui/material';

interface Props {
  value: number;
  inputValue: string;
  disabled: boolean;
  onChange: (_: Event, value: number | number[]) => void;
  onChangeCommitted: (
    _: React.SyntheticEvent | Event,
    value: number | number[]
  ) => void;
  onInputChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onInputBlur: () => void;
  onInputKeyDown: (e: React.KeyboardEvent) => void;
}

export default function ThresholdControl({
  value,
  inputValue,
  disabled,
  onChange,
  onChangeCommitted,
  onInputChange,
  onInputBlur,
  onInputKeyDown,
}: Props) {
  return (
    <Box>
      <Typography variant="body2" gutterBottom>
        通知閾値: {value}% 以上の下落
      </Typography>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
        <Slider
          value={value}
          min={1}
          max={50}
          step={1}
          marks={[
            { value: 5, label: '5%' },
            { value: 10, label: '10%' },
            { value: 20, label: '20%' },
            { value: 30, label: '30%' },
          ]}
          onChange={onChange}
          onChangeCommitted={onChangeCommitted}
          disabled={disabled}
          sx={{ flex: 1, maxWidth: 340 }}
        />
        <TextField
          type="number"
          size="small"
          value={inputValue}
          onChange={onInputChange}
          onBlur={onInputBlur}
          onKeyDown={onInputKeyDown}
          disabled={disabled}
          slotProps={{
            input: {
              endAdornment: <InputAdornment position="end">%</InputAdornment>,
              inputProps: { min: 1, max: 50 },
            },
          }}
          sx={{ width: 88 }}
        />
      </Box>
    </Box>
  );
}
