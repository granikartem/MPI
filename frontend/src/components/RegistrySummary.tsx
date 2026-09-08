import { RegistrySummary as Summary } from '../api'
import { statusColor, statusLabel } from './StatusBadge'

interface Props {
  summary: Summary
  scope: string
  scopeLabel: string
  disabled?: boolean
  onScope: (scope: string) => void
}

export const STATUS_ORDER = [
  'DRAFT',
  'READY',
  'EN_ROUTE',
  'DELAYED',
  'DELIVERED',
  'CLOSED',
  'CANCELLED',
]

export const RISK_LEVEL_ORDER = ['UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']

const RISK_LEVEL_COLORS: Record<string, string> = {
  UNKNOWN: '#888',
  LOW: '#33ff66',
  MEDIUM: '#ffd633',
  HIGH: '#ff9800',
  CRITICAL: '#ff4444',
}

const RISK_LEVEL_LABELS: Record<string, string> = {
  UNKNOWN: 'Н/Д',
  LOW: 'Низкий',
  MEDIUM: 'Средний',
  HIGH: 'Высокий',
  CRITICAL: 'Критический',
}

const ATTENTION_LABELS: Record<string, string> = {
  DELAYED: 'Задержка',
  AWAITING_CLOSURE: 'Ждёт закрытия',
  RISK_RECALCULATION_REQUIRED: 'Требует пересчёта risk_score',
  RISK_DATA_STALE: 'risk_score по устаревшим данным',
}

const ATTENTION_ORDER = [
  'DELAYED',
  'AWAITING_CLOSURE',
  'RISK_RECALCULATION_REQUIRED',
  'RISK_DATA_STALE',
]

export function riskLevelColor(level: string): string {
  return RISK_LEVEL_COLORS[level] ?? '#888'
}

export function riskLevelLabel(level: string): string {
  return RISK_LEVEL_LABELS[level] ?? level
}

export default function RegistrySummary({ summary, scope, scopeLabel, disabled, onScope }: Props) {
  const statuses = STATUS_ORDER.filter((s) => s in summary.byStatus)

  return (
    <>
      <div className="scope-tabs">
        <button
          className={scope === 'ACTIVE' ? 'active' : ''}
          disabled={disabled === true}
          onClick={() => onScope('ACTIVE')}
        >
          Активные ({summary.active})
        </button>
        <button
          className={scope === 'COMPLETED' ? 'active' : ''}
          disabled={disabled === true}
          onClick={() => onScope('COMPLETED')}
        >
          Архив ({summary.completed})
        </button>
      </div>

      <div className="summary-tiles">
        <div className="summary-tile">
          <div className="tile-head">Срез «{scopeLabel}»</div>
          <div className="tile-value">{summary.scopeTotal}</div>
          <div className="muted small">рейсов в срезе</div>
        </div>

        <div className="summary-tile">
          <div className="tile-head">По статусам</div>
          <div className="tile-marks">
            {statuses.map((s) => (
              <span
                key={s}
                className="summary-mark"
                style={{ borderColor: statusColor(s), color: statusColor(s) }}
              >
                {statusLabel(s)} · {summary.byStatus[s]}
              </span>
            ))}
          </div>
        </div>

        <div className="summary-tile">
          <div className="tile-head">По уровню риска</div>
          <div className="tile-marks">
            {RISK_LEVEL_ORDER.map((level) => (
              <span
                key={level}
                className="summary-mark"
                style={{ borderColor: riskLevelColor(level), color: riskLevelColor(level) }}
              >
                {riskLevelLabel(level)} · {summary.byRiskLevel[level] ?? 0}
              </span>
            ))}
          </div>
        </div>

        <div className="summary-tile">
          <div className="tile-head">Требуют внимания</div>
          <div className="tile-value">{summary.attentionTotal}</div>
          <div className="tile-marks">
            {ATTENTION_ORDER.map((code) => (
              <span key={code} className="summary-mark attention">
                {ATTENTION_LABELS[code] ?? code} · {summary.byAttention[code] ?? 0}
              </span>
            ))}
          </div>
        </div>
      </div>

      <div className="registry-hint muted small">
        Сводка считается по срезу и не зависит от применённых фильтров и ограничения выборки.
      </div>
    </>
  )
}
