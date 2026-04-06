export type UserResponse = {
  user_id: number
  login: string
  created_at: string
}

export type TokenResponse = {
  access_token: string
  refresh_token: string
  user: UserResponse
}

export type DatasetFile = {
  file_id: number
  file_name: string
  file_size_kb: number | null
  file_updated_at: string
  has_user_report: boolean
}

export type DatasetWithFiles = {
  dataset_id: number
  source: string
  title: string
  description: string | null
  tags: string[]
  dataset_format: string | null
  dataset_size_kb: number | null
  status: string
  download_url: string | null
  repository_url: string | null
  source_updated_at: string | null
  is_favorite: boolean
  files: DatasetFile[]
}

export type DatasetNonDataFiles = {
  dataset_id: number
  files: Array<{
    file_id: number
    file_name: string
    file_size_kb: number | null
    file_updated_at: string
  }>
}

export type UserReportListItem = {
  report_id: number
  status: string
  updated_at: string | null
  report_url: string | null
  file_id: number
  file_name: string
  dataset_id: number
  source: string
  title: string
  repository_url: string | null
  dataset_status: string
  dataset_updated_at: string | null
}

export type GenerateReportResponse = {
  report_id: number
  status: string
  report_url: string | null
  error_message: string | null
}

export type ReportSseEvent =
  | { event: 'report_ready'; report_id: number; report_url: string }
  | { event: 'report_failed'; report_id: number; error_message: string }
  | { event: 'report_deleting'; report_id: number }
  | { event: 'report_deleted'; report_id: number }