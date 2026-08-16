export interface Software {
  id: number
  name: string
  version: string
  platform: string
  description?: string
  file_size: number
  download_count: number
  is_active?: boolean
  created_at?: string
}

export const PLATFORM_OPTIONS = [
  { label: 'Windows', value: 'Windows' },
  { label: 'macOS', value: 'macOS' },
  { label: 'Linux', value: 'Linux' },
  { label: 'Android', value: 'Android' },
]

export function formatFileSize(bytes: number): string {
  if (!bytes || bytes <= 0) return '-'
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unit = 0
  while (size >= 1024 && unit < units.length - 1) {
    size /= 1024
    unit += 1
  }
  return `${size.toFixed(unit === 0 ? 0 : 1)} ${units[unit]}`
}
