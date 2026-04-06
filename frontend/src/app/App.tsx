import { Box, Container } from '@mui/material'
import { Navigate, Route, Routes } from 'react-router-dom'
import { AppBarNav } from '../components/AppBarNav'
import { ProtectedRoute } from '../auth/ProtectedRoute'
import { InfoPage } from '../features/info/InfoPage'
import { AuthPage } from '../features/auth/AuthPage'
import { ProfilePage } from '../features/profile/ProfilePage'
import { CatalogPage } from '../features/catalog/CatalogPage'
import { FavoritesPage } from '../features/favorites/FavoritesPage'
import { ReportsPage } from '../features/reports/ReportsPage'

const needLogin = [
  { path: '/catalog', El: CatalogPage },
  { path: '/favorites', El: FavoritesPage },
  { path: '/reports', El: ReportsPage },
]

export function App() {
  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
      <AppBarNav />
      <Container maxWidth={false} component="main" sx={{ flex: 1, py: 1 }}>
        <Routes>
          <Route path="/" element={<Navigate to="/info" replace />} />
          <Route path="/info" element={<InfoPage />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          {needLogin.map(({ path, El }) => (
            <Route
              key={path}
              path={path}
              element={
                <ProtectedRoute>
                  <El />
                </ProtectedRoute>
              }
            />
          ))}
          <Route path="*" element={<Navigate to="/info" replace />} />
        </Routes>
      </Container>
    </Box>
  )
}