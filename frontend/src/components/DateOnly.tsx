import { Typography } from '@mui/material'
import { formatDateOnly } from '../utils/dates'

export function DateOnly({ value }: { value: string | null | undefined }) {
  return (
    <Typography component="span" variant="body2">
      {formatDateOnly(value)}
    </Typography>
  )
}