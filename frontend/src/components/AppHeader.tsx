import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import { Box, Button, CircularProgress, Container, Typography } from '@mui/material';

interface Props {
  checkRunning: boolean;
  onCheckNow: () => void;
}

export default function AppHeader({ checkRunning, onCheckNow }: Props) {
  return (
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
            onClick={onCheckNow}
            disabled={checkRunning}
            sx={{ color: 'primary.main', bgcolor: 'white' }}
          >
            今すぐチェック
          </Button>
        </Box>
      </Container>
    </Box>
  );
}
