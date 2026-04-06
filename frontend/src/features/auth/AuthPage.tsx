import { useState } from 'react'
import { Alert, Box, Button, Paper, Stack, TextField, Typography } from '@mui/material'
import { loginUser, registerUser, UserServiceError } from '../../api/user_service'
import { useAuth } from '../../auth/AuthContext'
import { useNavigate } from 'react-router-dom'

export function AuthPage() {
  const { login, isAuthenticated } = useAuth()
  const navigate = useNavigate()
  const [regLogin, setRegLogin] = useState('')
  const [regPassword, setRegPassword] = useState('')
  const [logLogin, setLogLogin] = useState('')
  const [logPassword, setLogPassword] = useState('')
  const [regError, setRegError] = useState<string | null>(null)
  const [regOk, setRegOk] = useState<string | null>(null)
  const [logError, setLogError] = useState<string | null>(null)
  const [regLoading, setRegLoading] = useState(false)
  const [logLoading, setLogLoading] = useState(false)

  if (isAuthenticated) {
    return (
      <Box sx={{ maxWidth: 480, mx: 'auto', mt: 4, px: 2 }}>
        <Alert severity="info">Вы уже вошли в систему.</Alert>
        <Button sx={{ mt: 2 }} onClick={() => navigate('/catalog')}>
          Перейти в каталог
        </Button>
      </Box>
    )
  }

  async function handleRegister() {
    setRegError(null)
    setRegOk(null)
    setRegLoading(true)
    try {
      await registerUser(regLogin.trim(), regPassword)
      setRegOk('Регистрация успешна. Теперь выполните вход.')
    } catch (e) {
      setRegError(e instanceof UserServiceError ? e.message : 'Не удалось зарегистрироваться')
    } finally {
      setRegLoading(false)
    }
  }

  async function handleLogin() {
    setLogError(null)
    setLogLoading(true)
    try {
      const data = await loginUser(logLogin.trim(), logPassword)
      login(data.access_token, data.refresh_token, data.user)
      navigate('/catalog')
    } catch (e) {
      setLogError(e instanceof UserServiceError ? e.message : 'Не удалось войти')
    } finally {
      setLogLoading(false)
    }
  }

  return (
    <Box sx={{ maxWidth: 720, mx: 'auto', py: 3, px: 2 }}>
      <Typography variant="h5" gutterBottom>
        Регистрация и вход
      </Typography>
      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Зарегистрируйтесь, затем осуществите вход в свой аккаунт.
      </Typography>
      <Stack spacing={3} direction={{ xs: 'column', md: 'row' }}>
        <Paper variant="outlined" sx={{ p: 2, flex: 1 }}>
          <Typography variant="subtitle1" gutterBottom>
            Регистрация
          </Typography>
          <Stack spacing={2}>
            <TextField
              label="Логин"
              value={regLogin}
              onChange={(e) => setRegLogin(e.target.value)}
              fullWidth
              autoComplete="username"
            />
            <TextField
              label="Пароль"
              type="password"
              value={regPassword}
              onChange={(e) => setRegPassword(e.target.value)}
              fullWidth
              autoComplete="new-password"
            />
            {regOk && <Alert severity="success">{regOk}</Alert>}
            {regError && <Alert severity="error">{regError}</Alert>}
            <Button variant="contained" disabled={regLoading} onClick={() => void handleRegister()}>
              Регистрация
            </Button>
          </Stack>
        </Paper>
        <Paper variant="outlined" sx={{ p: 2, flex: 1 }}>
          <Typography variant="subtitle1" gutterBottom>
            Вход
          </Typography>
          <Stack spacing={2}>
            <TextField
              label="Логин"
              value={logLogin}
              onChange={(e) => setLogLogin(e.target.value)}
              fullWidth
              autoComplete="username"
            />
            <TextField
              label="Пароль"
              type="password"
              value={logPassword}
              onChange={(e) => setLogPassword(e.target.value)}
              fullWidth
              autoComplete="current-password"
            />
            {logError && <Alert severity="error">{logError}</Alert>}
            <Button variant="contained" disabled={logLoading} onClick={() => void handleLogin()}>
              Вход
            </Button>
          </Stack>
        </Paper>
      </Stack>
    </Box>
  )
}