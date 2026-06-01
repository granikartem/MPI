interface Props {
  score: number | null
  status: string
  onClick?: () => void
}

function color(score: number | null, status: string): string {
  if (status === 'NA' || score === null) return '#888'
  if (score >= 80) return '#ff4444'
  if (score >= 60) return '#ff9800'
  if (score >= 30) return '#ffd633'
  return '#33ff66'
}

function label(score: number | null, status: string): string {
  if (status === 'NA' || score === null) return 'Н/Д'
  const suffix = status === 'STALE' ? ' (устар.)' : ''
  return `${score}${suffix}`
}

export default function RiskBadge({ score, status, onClick }: Props) {
  const c = color(score, status)
  return (
    <button
      className="risk-badge"
      style={{ borderColor: c, color: c }}
      onClick={onClick}
      title="Показать, как получен risk_score"
    >
      risk {label(score, status)} ⓘ
    </button>
  )
}
