interface Props {
  status: string
  label?: string
  onClick?: () => void
}

const COLORS: Record<string, string> = {
  DRAFT: '#7aa888',
  READY: '#ffd633',
  EN_ROUTE: '#33ccff',
  DELAYED: '#ff9800',
  DELIVERED: '#33ff66',
  CLOSED: '#55aa77',
  CANCELLED: '#ff4444',
}

const LABELS: Record<string, string> = {
  DRAFT: 'Черновик',
  READY: 'Готов к отправке',
  EN_ROUTE: 'В пути',
  DELAYED: 'Задержка',
  DELIVERED: 'Доставлен',
  CLOSED: 'Закрыт',
  CANCELLED: 'Отменён',
}

export function statusLabel(status: string): string {
  return LABELS[status] ?? status
}

export function statusColor(status: string): string {
  return COLORS[status] ?? '#888'
}

export default function StatusBadge({ status, label, onClick }: Props) {
  const color = statusColor(status)
  const text = label ?? statusLabel(status)

  if (!onClick) {
    return (
      <span className="status-badge" style={{ borderColor: color, color }}>
        {text}
      </span>
    )
  }

  return (
    <button
      className="status-badge"
      style={{ borderColor: color, color }}
      onClick={onClick}
      title="Открыть управление статусом и историю переходов"
    >
      {text} ⓘ
    </button>
  )
}
