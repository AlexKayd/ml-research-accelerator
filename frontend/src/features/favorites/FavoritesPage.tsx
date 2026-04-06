import { useEffect, useState } from 'react'
import { Box, Typography } from '@mui/material'
import { listFavorites, UserServiceError } from '../../api/user_service'
import type { DatasetWithFiles } from '../../types/api'
import { DatasetCard } from '../../components/DatasetCard'
import { LoadingBox } from '../../components/LoadingBox'
import { useReportGeneration } from '../../hooks/use_report_generation'

export function FavoritesPage() {
  const { startGeneration } = useReportGeneration()
  const [datasets, setDatasets] = useState<DatasetWithFiles[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setLoading(true)
    setError(null)
    listFavorites()
      .then(setDatasets)
      .catch((e) => setError(e instanceof UserServiceError ? e.message : 'Ошибка загрузки'))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingBox message="Загрузка избранного…" />

  return (
    <Box sx={{ p: 2, maxWidth: 900, mx: 'auto' }}>
      <Typography variant="h5" gutterBottom>
        Избранные датасеты
      </Typography>
      {error && (
        <Typography color="error" sx={{ mb: 2 }}>
          {error}
        </Typography>
      )}
      {datasets.map((d) => (
        <DatasetCard
          key={d.dataset_id}
          dataset={d}
          mode="favorites"
          onGenerateReport={(fileId) => startGeneration(fileId)}
          onReportReadyForFile={(datasetId, fileId) => {
            setDatasets((prev) =>
              prev.map((row) =>
                row.dataset_id !== datasetId
                  ? row
                  : {
                      ...row,
                      files: row.files.map((f) =>
                        f.file_id === fileId ? { ...f, has_user_report: true } : f,
                      ),
                    },
              ),
            )
          }}
        />
      ))}
      {!error && datasets.length === 0 && (
        <Typography color="text.secondary">У вас пока нет избранных датасетов.</Typography>
      )}
    </Box>
  )
}