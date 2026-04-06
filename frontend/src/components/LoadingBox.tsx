import { Box, CircularProgress, Typography } from '@mui/material'

type Props = { message?: string }

export function LoadingBox({ message = 'Загрузка…' }: Props) {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2, py: 6 }}>
      <CircularProgress />
      <Typography color="text.secondary">{message}</Typography>
    </Box>
  )
}