import { AppBar, Box, Button, Toolbar, Typography, useMediaQuery, useTheme } from '@mui/material'
import { Link as RouterLink, useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

const links = [
  { to: '/auth', label: 'Регистрация / вход' },
  { to: '/profile', label: 'Профиль' },
  { to: '/info', label: 'Информация' },
  { to: '/catalog', label: 'Каталог датасетов' },
  { to: '/favorites', label: 'Избранные датасеты' },
  { to: '/reports', label: 'История отчётов' },
]

export function AppBarNav() {
  const { pathname } = useLocation()
  const { isAuthenticated, user } = useAuth()
  const theme = useTheme()
  const narrow = useMediaQuery(theme.breakpoints.down('md'))

  const toolbarSx = {
    flexWrap: narrow ? ('wrap' as const) : ('nowrap' as const),
    gap: narrow ? 0.5 : 1,
    py: narrow ? 1 : 0,
    minHeight: narrow ? 56 : 48,
  }

  return (
    <AppBar position="sticky" color="default" elevation={1} sx={{ borderBottom: 1, borderColor: 'divider' }}>
      <Toolbar variant="dense" sx={toolbarSx}>
        <Typography
          variant="subtitle2"
          sx={{ mr: narrow ? 0 : 2, fontWeight: 600, width: narrow ? '100%' : 'auto' }}
        >
          ML Research Accelerator
        </Typography>
        <Box
          sx={{
            display: 'flex',
            flexWrap: narrow ? 'wrap' : 'nowrap',
            alignItems: 'center',
            gap: 0.5,
            flexGrow: 1,
            justifyContent: narrow ? 'flex-start' : 'flex-end',
          }}
        >
          {links.map((item) => (
            <Button
              key={item.to}
              component={RouterLink}
              to={item.to}
              size="small"
              color={pathname === item.to ? 'primary' : 'inherit'}
              variant={pathname === item.to ? 'outlined' : 'text'}
              sx={{ textTransform: 'none', minWidth: 'auto', px: 1 }}
            >
              {item.label}
            </Button>
          ))}
          {isAuthenticated && user && (
            <Typography variant="caption" color="text.secondary" sx={{ ml: narrow ? 0 : 1, px: 0.5 }}>
              {user.login}
            </Typography>
          )}
        </Box>
      </Toolbar>
    </AppBar>
  )
}