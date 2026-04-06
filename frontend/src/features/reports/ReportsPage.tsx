import { useEffect, useState } from 'react'
import { Box, Button, Link, Paper, Stack, Typography } from '@mui/material'
import { deleteReport, listReports, UserServiceError } from '../../api/user_service'
import type { UserReportListItem } from '../../types/api'
import { LoadingBox } from '../../components/LoadingBox'
import { DateOnly } from '../../components/DateOnly'

export function ReportsPage() {
  const [reports, setReports] = useState<UserReportListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [removedIds, setRemovedIds] = useState<number[]>([])

  useEffect(() => {
    setLoading(true)
    setError(null)
    listReports()
      .then(setReports)
      .catch((e) => setError(e instanceof UserServiceError ? e.message : 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [])

  async function handleDelete(reportId: number) {
    try {
      await deleteReport(reportId)
      setRemovedIds((prev) => [...prev, reportId])
    } catch (e) {
      setError(e instanceof UserServiceError ? e.message : 'Не удалось удалить')
    }
  }

  if (loading) return <LoadingBox message="Загрузка истории отчётов…" />

  return (
    <Box sx={{ p: 2, maxWidth: 900, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        История отчётов
      </Typography>
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      <Stack spacing={2}>
        {reports.map((r) => {
          const removed = removedIds.includes(r.report_id)
          return (
            <Paper key={r.report_id} variant="outlined" sx={{ p: 2 }}>
              <Stack spacing={1}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 1 }}>
                  {removed ? (
                    <Typography variant="body2" color="text.secondary">
                      Отчёт удалён из истории
                    </Typography>
                  ) : (
                    <Button size="small" color="error" onClick={() => void handleDelete(r.report_id)}>
                      Удалить отчёт
                    </Button>
                  )}
                </Box>
                <Typography variant="body2">
                  <strong>Статус датасета:</strong> {r.dataset_status}
                  {'  '}
                  <strong>Обновлён:</strong> <DateOnly value={r.dataset_updated_at} />
                </Typography>
                <Typography variant="body2">
                  <strong>Ресурс:</strong> {r.source}
                  {'  '}
                  {r.repository_url ? (
                    <Link href={r.repository_url} target="_blank" rel="noopener noreferrer">
                      Репозиторий
                    </Link>
                  ) : (
                    '—'
                  )}
                </Typography>
                <Typography variant="h6">{r.title}</Typography>
                <Typography variant="body2">
                  <strong>Файл:</strong> {r.file_name}
                </Typography>
                <Typography variant="body2">
                  <strong>Статус отчёта:</strong> {r.status}
                  {'  '}
                  <strong>Обновлён:</strong> <DateOnly value={r.updated_at} />
                </Typography>
                {r.report_url && !removed && (
                  <Button
                    component="a"
                    href={r.report_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    variant="outlined"
                    size="small"
                    sx={{ alignSelf: 'flex-start' }}
                  >
                    Открыть отчёт
                  </Button>
                )}
              </Stack>
            </Paper>
          )
        })}
      </Stack>
      {!error && reports.length === 0 && (
        <Typography color="text.secondary">История отчётов пуста.</Typography>
      )}
    </Box>
  )
}