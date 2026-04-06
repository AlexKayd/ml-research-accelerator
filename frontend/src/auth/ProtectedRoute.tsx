import { Box, Button, Paper, Typography } from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) return <>{children}</>

  return (
    <Box sx={{ maxWidth: 560, mx: 'auto', mt: 4, px: 2 }}>
      <Paper elevation={0} variant="outlined" sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Нужна авторизация
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 2 }}>
          Войдите в аккаунт или зарегистрируйтесь, чтобы пользоваться этим разделом.
        </Typography>
        <Button component={RouterLink} to="/auth" variant="contained">
          Регистрация / вход
        </Button>
      </Paper>
    </Box>
  )
}