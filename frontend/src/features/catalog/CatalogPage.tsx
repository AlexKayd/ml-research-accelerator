import { useRef, useState } from 'react'
import {
  Box,
  Button,
  Checkbox,
  FormControlLabel,
  FormGroup,
  Paper,
  TextField,
  Typography,
} from '@mui/material'
import { searchDatasets, UserServiceError } from '../../api/user_service'
import type { DatasetWithFiles } from '../../types/api'
import { DatasetCard } from '../../components/DatasetCard'
import { LoadingBox } from '../../components/LoadingBox'
import { useReportGeneration } from '../../hooks/use_report_generation'

const LIMIT_MIN = 1
const MB_MIN = 0.005

function sanitizeMbInput(value: string): string {
  const s = value.replace(/[^\d.]/g, '')
  const i = s.indexOf('.')
  if (i === -1) return s
  return s.slice(0, i + 1) + s.slice(i + 1).replace(/\./g, '')
}

function sanitizeLimitInput(value: string): string {
  return value.replace(/\D/g, '')
}

export function CatalogPage() {
  const { startGeneration } = useReportGeneration()
  const [query, setQuery] = useState('')
  const [sources, setSources] = useState({ kaggle: true, uci: true })
  const [formats, setFormats] = useState({ csv: true, json: true })
  const [maxSizeMb, setMaxSizeMb] = useState('')
  const [tagsRaw, setTagsRaw] = useState('')
  const [limit, setLimit] = useState('100')
  const [datasets, setDatasets] = useState<DatasetWithFiles[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [maxSizeFieldError, setMaxSizeFieldError] = useState<string | null>(null)
  const [limitFieldError, setLimitFieldError] = useState<string | null>(null)
  const [searched, setSearched] = useState(false)
  const requestIdRef = useRef(0)

  async function handleSearch() {
    setError(null)
    setMaxSizeFieldError(null)
    setLimitFieldError(null)

    let maxN: number | undefined = undefined
    const maxT = maxSizeMb.trim()
    if (maxT !== '') {
      maxN = Number.parseFloat(maxT)
      if (!Number.isFinite(maxN)) {
        setMaxSizeFieldError('Введите число, МБ')
        return
      }
      if (maxN < MB_MIN) {
        setMaxSizeFieldError(`Минимум ${MB_MIN} МБ`)
        return
      }
    }

    let limN: number | undefined = undefined
    const limT = limit.trim()
    if (limT !== '') {
      if (!/^\d+$/.test(limT)) {
        setLimitFieldError('Только целое число')
        return
      }
      limN = Number.parseInt(limT, 10)
      if (limN < LIMIT_MIN) {
        setLimitFieldError(`От ${LIMIT_MIN}`)
        return
      }
    }

    const myId = ++requestIdRef.current
    setLoading(true)
    setSearched(true)
    const src: string[] = []
    if (sources.kaggle) src.push('kaggle')
    if (sources.uci) src.push('uci')
    const fmt: string[] = []
    if (formats.csv) fmt.push('csv')
    if (formats.json) fmt.push('json')
    const tags = tagsRaw
      .split(/[,;\s]+/)
      .map((t) => t.trim())
      .filter(Boolean)

    try {
      const list = await searchDatasets({
        query: query.trim() || undefined,
        sources: src.length ? src : undefined,
        file_formats: fmt.length ? fmt : undefined,
        max_size_mb: maxN,
        tags: tags.length ? tags : undefined,
        limit: limN,
        offset: 0,
      })
      if (requestIdRef.current === myId) setDatasets(list)
    } catch (e) {
      if (requestIdRef.current === myId) {
        setError(e instanceof UserServiceError ? e.message : 'Ошибка поиска')
        setDatasets([])
      }
    } finally {
      if (requestIdRef.current === myId) setLoading(false)
    }
  }

  return (
    <Box sx={{ display: 'flex', flexDirection: { xs: 'column', md: 'row' }, gap: 2, p: 2, alignItems: 'flex-start' }}>
      <Paper variant="outlined" sx={{ p: 2, width: { xs: '100%', md: 280 }, flexShrink: 0 }}>
        <Typography variant="subtitle2" gutterBottom>
          Фильтры
        </Typography>
        <FormGroup>
          <Typography variant="caption" color="text.secondary">
            Ресурс
          </Typography>
          <FormControlLabel
            control={
              <Checkbox
                checked={sources.kaggle}
                onChange={(e) => setSources((s) => ({ ...s, kaggle: e.target.checked }))}
              />
            }
            label="kaggle"
          />
          <FormControlLabel
            control={
              <Checkbox checked={sources.uci} onChange={(e) => setSources((s) => ({ ...s, uci: e.target.checked }))} />
            }
            label="uci"
          />
          <Typography variant="caption" color="text.secondary" sx={{ mt: 1 }}>
            Формат файлов
          </Typography>
          <FormControlLabel
            control={
              <Checkbox checked={formats.csv} onChange={(e) => setFormats((s) => ({ ...s, csv: e.target.checked }))} />
            }
            label="csv"
          />
          <FormControlLabel
            control={
              <Checkbox checked={formats.json} onChange={(e) => setFormats((s) => ({ ...s, json: e.target.checked }))} />
            }
            label="json"
          />
        </FormGroup>
        <TextField
          label="Макс. размер датасета, МБ"
          type="text"
          inputMode="decimal"
          size="small"
          fullWidth
          sx={{ mt: 2 }}
          value={maxSizeMb}
          error={Boolean(maxSizeFieldError)}
          helperText={maxSizeFieldError ?? undefined}
          onChange={(e) => {
            setMaxSizeFieldError(null)
            setMaxSizeMb(sanitizeMbInput(e.target.value))
          }}
        />
        <TextField
          label="Теги (через запятую)"
          size="small"
          fullWidth
          sx={{ mt: 2 }}
          value={tagsRaw}
          onChange={(e) => setTagsRaw(e.target.value)}
        />
        <TextField
          label="Количество датасетов"
          type="text"
          inputMode="numeric"
          size="small"
          fullWidth
          sx={{ mt: 2 }}
          value={limit}
          error={Boolean(limitFieldError)}
          onChange={(e) => {
            setLimitFieldError(null)
            setLimit(sanitizeLimitInput(e.target.value))
          }}
        />
        <Button variant="contained" fullWidth sx={{ mt: 2 }} onClick={() => void handleSearch()} disabled={loading}>
          Найти датасеты
        </Button>
      </Paper>
      <Box sx={{ flex: 1, minWidth: 0 }}>
        <TextField
          label="Поиск по названию и описанию"
          fullWidth
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          sx={{ mb: 2 }}
        />
        {!searched && !loading && (
          <Typography color="text.secondary" sx={{ mb: 2 }}>
            Для поиска датасетов используйте поисковую строку и фильтры.
          </Typography>
        )}
        {loading && <LoadingBox />}
        {error && (
          <Typography color="error" sx={{ mb: 2 }}>
            {error}
          </Typography>
        )}
        {!loading &&
          searched &&
          !error &&
          datasets.map((d) => (
            <DatasetCard
              key={d.dataset_id}
              dataset={d}
              mode="catalog"
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
        {!loading && searched && !error && datasets.length === 0 && (
          <Typography color="text.secondary">Ничего не найдено.</Typography>
        )}
      </Box>
    </Box>
  )
}