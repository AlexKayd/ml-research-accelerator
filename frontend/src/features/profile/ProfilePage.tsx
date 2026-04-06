import { useEffect, useState } from 'react'
import { Alert, Box, Paper, Typography } from '@mui/material'
import { getProfile, UserServiceError } from '../../api/user_service'
import { useAuth } from '../../auth/AuthContext'
import { LoadingBox } from '../../components/LoadingBox'
import { formatDateOnly } from '../../utils/dates'

export function ProfilePage() {
  const { isAuthenticated, accessToken } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [login, setLogin] = useState<string | null>(null)
  const [created, setCreated] = useState<string | null>(null)

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      setLogin(null)
      setCreated(null)
      return
    }
    setLoading(true)
    setError(null)
    void getProfile()
      .then((p) => {
        setLogin(p.login)
        setCreated(p.created_at)
      })
      .catch((e) => {
        setError(e instanceof UserServiceError ? e.message : 'Ошибка загрузки профиля')
      })
      .finally(() => setLoading(false))
  }, [isAuthenticated, accessToken])

  if (!isAuthenticated) {
    return (
      <Box sx={{ maxWidth: 560, mx: 'auto', mt: 4, px: 2 }}>
        <Typography>Вы не авторизованы.</Typography>
      </Box>
    )
  }

  if (loading) return <LoadingBox message="Загрузка профиля…" />

  return (
    <Box sx={{ maxWidth: 560, mx: 'auto', py: 3, px: 2 }}>
      <Typography variant="h5" gutterBottom>
        Профиль
      </Typography>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Paper variant="outlined" sx={{ p: 2 }}>
        <Typography>
          <strong>Логин:</strong> {login ?? '—'}
        </Typography>
        <Typography sx={{ mt: 1 }}>
          <strong>Дата регистрации:</strong> {created ? formatDateOnly(created) : '—'}
        </Typography>
      </Paper>
    </Box>
  )
}