import { useState } from 'react'
import { Box, Button, Divider, Link, Paper, Stack, Typography } from '@mui/material'
import FavoriteIcon from '@mui/icons-material/Favorite'
import FavoriteBorderIcon from '@mui/icons-material/FavoriteBorder'
import type { DatasetFile, DatasetWithFiles } from '../types/api'
import { DateOnly } from './DateOnly'
import { getDatasetNonDataFiles, addFavorite, removeFavorite, UserServiceError } from '../api/user_service'
import { formatDatasetDescription } from '../utils/dataset_display'

export function DatasetCard({
  dataset: initial,
  mode,
  onReportReadyForFile,
  onGenerateReport,
}: {
  dataset: DatasetWithFiles
  mode: 'catalog' | 'favorites'
  onReportReadyForFile?: (datasetId: number, fileId: number) => void
  onGenerateReport: (fileId: number) => Promise<
    { ok: true; reportUrl: string } | { ok: false; error: string }
  >
}) {
  const [dataset, setDataset] = useState(initial)
  const [favoriteAdded, setFavoriteAdded] = useState(false)
  const [favoriteRemoved, setFavoriteRemoved] = useState(false)
  const [favoriteError, setFavoriteError] = useState<string | null>(null)
  const [extraFiles, setExtraFiles] = useState<
    { file_id: number; file_name: string; file_size_kb: number | null; file_updated_at: string }[] | null
  >(null)
  const [extraOpen, setExtraOpen] = useState(false)
  const [extraLoading, setExtraLoading] = useState(false)
  const [extraError, setExtraError] = useState<string | null>(null)
  const [genByFile, setGenByFile] = useState<Record<number, 'idle' | 'processing' | 'ready' | 'error'>>({})
  const [filesWithReport, setFilesWithReport] = useState<number[]>(() =>
    initial.files.filter((f) => f.has_user_report).map((f) => f.file_id),
  )
  const [genError, setGenError] = useState<string | null>(null)

  const showAddFavorite = mode === 'catalog' && !dataset.is_favorite && !favoriteAdded
  const showRemoveFavorite = mode === 'favorites' && !favoriteRemoved

  async function loadExtraFiles() {
    setExtraLoading(true)
    setExtraError(null)
    try {
      const res = await getDatasetNonDataFiles(dataset.dataset_id)
      setExtraFiles(res.files)
      setExtraOpen(true)
    } catch (e) {
      setExtraError(e instanceof UserServiceError ? e.message : 'Не удалось загрузить файлы')
    } finally {
      setExtraLoading(false)
    }
  }

  async function addToFavorites() {
    setFavoriteError(null)
    try {
      await addFavorite(dataset.dataset_id)
      setFavoriteAdded(true)
      setDataset((d) => ({ ...d, is_favorite: true }))
    } catch (e) {
      setFavoriteError(e instanceof UserServiceError ? e.message : 'Ошибка')
    }
  }

  async function removeFromFavorites() {
    setFavoriteError(null)
    try {
      await removeFavorite(dataset.dataset_id)
      setFavoriteRemoved(true)
    } catch (e) {
      setFavoriteError(e instanceof UserServiceError ? e.message : 'Ошибка')
    }
  }

  async function generateForFile(file: DatasetFile) {
    setGenError(null)
    setGenByFile((m) => ({ ...m, [file.file_id]: 'processing' }))
    try {
      const r = await onGenerateReport(file.file_id)
      if (r.ok) {
        setGenByFile((m) => ({ ...m, [file.file_id]: 'ready' }))
        setFilesWithReport((prev) => (prev.includes(file.file_id) ? prev : [...prev, file.file_id]))
        onReportReadyForFile?.(dataset.dataset_id, file.file_id)
        window.setTimeout(() => {
          window.open(r.reportUrl, '_blank', 'noopener,noreferrer')
        }, 1000)
      } else {
        setGenByFile((m) => ({ ...m, [file.file_id]: 'error' }))
        setGenError(r.error)
      }
    } catch (e) {
      setGenByFile((m) => ({ ...m, [file.file_id]: 'error' }))
      setGenError(e instanceof Error ? e.message : 'Ошибка генерации отчёта')
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, mb: 2 }}>
      <Stack spacing={1}>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
          {showAddFavorite && (
            <Button
              size="small"
              color="error"
              startIcon={<FavoriteBorderIcon />}
              onClick={() => void addToFavorites()}
            >
              Добавить в избранное
            </Button>
          )}
          {mode === 'catalog' && dataset.is_favorite && !favoriteAdded && (
            <Stack direction="row" alignItems="center" gap={0.5} sx={{ color: 'error.main' }}>
              <FavoriteIcon sx={{ fontSize: 18 }} />
              <Typography variant="body2" color="inherit">
                В избранном
              </Typography>
            </Stack>
          )}
          {favoriteAdded &&
            (mode === 'catalog' ? (
              <Stack direction="row" alignItems="center" gap={0.5} sx={{ color: 'error.main' }}>
                <FavoriteIcon sx={{ fontSize: 18 }} />
                <Typography variant="body2" color="inherit">
                  Датасет добавлен в избранное
                </Typography>
              </Stack>
            ) : (
              <Typography variant="body2" color="success.main">
                Датасет добавлен в избранное
              </Typography>
            ))}
          {showRemoveFavorite && (
            <Button size="small" color="error" startIcon={<FavoriteIcon />} onClick={() => void removeFromFavorites()}>
              Удалить из избранного
            </Button>
          )}
          {favoriteRemoved && (
            <Typography variant="body2" color="text.secondary">
              Датасет удалён из избранного
            </Typography>
          )}
        </Box>
        {favoriteError && (
          <Typography color="error" variant="body2">
            {favoriteError}
          </Typography>
        )}

        <Typography variant="body2">
          <strong>Статус:</strong> {dataset.status}
          {'  '}
          <strong>Обновлён:</strong> <DateOnly value={dataset.source_updated_at} />
        </Typography>
        <Typography variant="body2">
          <strong>Ресурс:</strong> {dataset.source}
          {'  '}
          {dataset.repository_url ? (
            <Link href={dataset.repository_url} target="_blank" rel="noopener noreferrer">
              Репозиторий
            </Link>
          ) : (
            '—'
          )}
        </Typography>
        <Typography variant="h6">{dataset.title}</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
          {formatDatasetDescription(dataset.title, dataset.description)}
        </Typography>
        <Typography variant="body2">
          <strong>Теги:</strong> {dataset.tags.length ? dataset.tags.join(', ') : '—'}
        </Typography>
        <Typography variant="body2">
          <strong>Формат:</strong> {dataset.dataset_format ?? '—'}
          {'  '}
          <strong>Размер:</strong> {dataset.dataset_size_kb != null ? `${dataset.dataset_size_kb} КБ` : '—'}
        </Typography>
        <Typography variant="body2">
          {dataset.download_url ? (
            <Link href={dataset.download_url} target="_blank" rel="noopener noreferrer">
              Скачать датасет
            </Link>
          ) : (
            'Ссылка на скачивание недоступна'
          )}
        </Typography>

        <Divider sx={{ my: 1 }} />
        <Typography variant="subtitle2">Файлы для генерации отчета</Typography>
        {dataset.files.map((file) => {
          const st = genByFile[file.file_id] ?? 'idle'
          const hasReport = filesWithReport.includes(file.file_id)
          return (
            <Box key={file.file_id} sx={{ pl: 1, borderLeft: 2, borderColor: 'divider', py: 0.5 }}>
              <Typography variant="body2">{file.file_name}</Typography>
              <Typography variant="caption" color="text.secondary" display="block">
                {file.file_size_kb != null ? `${file.file_size_kb} КБ` : '—'} <DateOnly value={file.file_updated_at} />
              </Typography>
              {st === 'processing' && (
                <Typography variant="body2" color="primary">
                  В процессе…
                </Typography>
              )}
              {st === 'ready' && (
                <Typography variant="body2" color="success.main">
                  Отчёт готов!
                </Typography>
              )}
              {st === 'error' && (
                <Typography variant="body2" color="error">
                  Ошибка генерации
                </Typography>
              )}
              {hasReport && st === 'idle' && (
                <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
                  Отчёт в истории.
                </Typography>
              )}
              {!hasReport && st === 'idle' && (
                <Button size="small" variant="outlined" sx={{ mt: 0.5 }} onClick={() => void generateForFile(file)}>
                  Сгенерировать отчёт
                </Button>
              )}
            </Box>
          )
        })}

        {!extraOpen && (
          <Button size="small" disabled={extraLoading} onClick={() => void loadExtraFiles()}>
            {extraLoading ? 'Загрузка…' : 'Получить остальные файлы'}
          </Button>
        )}
        {extraError && (
          <Typography color="error" variant="body2">
            {extraError}
          </Typography>
        )}
        {extraOpen && extraFiles && extraFiles.length > 0 && (
          <>
            <Typography variant="subtitle2">Прочие файлы</Typography>
            {extraFiles.map((f) => (
              <Box key={f.file_id} sx={{ pl: 1, borderLeft: 2, borderColor: 'divider' }}>
                <Typography variant="body2">{f.file_name}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {f.file_size_kb != null ? `${f.file_size_kb} КБ` : '—'} <DateOnly value={f.file_updated_at} />
                </Typography>
              </Box>
            ))}
            <Button size="small" onClick={() => setExtraOpen(false)}>
              Скрыть файлы
            </Button>
          </>
        )}
        {extraOpen && extraFiles && extraFiles.length === 0 && (
          <>
            <Typography variant="body2" color="text.secondary">
              Нет дополнительных файлов
            </Typography>
            <Button size="small" onClick={() => setExtraOpen(false)}>
              Скрыть файлы
            </Button>
          </>
        )}

        {genError && (
          <Typography color="error" variant="body2">
            {genError}
          </Typography>
        )}
      </Stack>
    </Paper>
  )
}