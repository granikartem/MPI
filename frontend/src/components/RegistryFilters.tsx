import { RegistryQuery } from '../api'
import { RISK_LEVEL_ORDER, riskLevelColor, riskLevelLabel } from './RegistrySummary'
import { statusColor, statusLabel } from './StatusBadge'

interface Props {
  scopeStatuses: string[]
  query: RegistryQuery
  disabled?: boolean
  onChange: (patch: RegistryQuery) => void
  onReset: () => void
}

const SORTS = [
  { value: 'CREATED_DESC', label: 'Сначала новые' },
  { value: 'DEPARTURE_ASC', label: 'По дате отправки' },
  { value: 'RISK_DESC', label: 'По risk_score' },
  { value: 'STATUS_CHANGED_DESC', label: 'По последнему изменению статуса' },
]

function toggled(selected: string[], value: string): string[] {
  return selected.includes(value)
    ? selected.filter((v) => v !== value)
    : [...selected, value]
}

export default function RegistryFilters({ scopeStatuses, query, disabled, onChange, onReset }: Props) {
  const statuses = query.status ?? []
  const levels = query.riskLevel ?? []
  const attentionOnly = query.attentionOnly === true
  const filtered = statuses.length > 0 || levels.length > 0 || attentionOnly

  return (
    <div className="filter-bar">
      <div className="filter-group">
        <span className="filter-title">Статус</span>
        <div className="chips">
          {scopeStatuses.map((s) => {
            const active = statuses.includes(s)
            return (
              <button
                key={s}
                className={active ? 'chip active' : 'chip'}
                style={{ borderColor: statusColor(s), color: statusColor(s) }}
                disabled={disabled === true}
                onClick={() => onChange({ status: toggled(statuses, s) })}
                title={`Показывать только рейсы в статусе «${statusLabel(s)}»`}
              >
                {statusLabel(s)}
              </button>
            )
          })}
        </div>
      </div>

      <div className="filter-group">
        <span className="filter-title">Уровень риска</span>
        <div className="chips">
          {RISK_LEVEL_ORDER.map((level) => {
            const active = levels.includes(level)
            return (
              <button
                key={level}
                className={active ? 'chip active' : 'chip'}
                style={{ borderColor: riskLevelColor(level), color: riskLevelColor(level) }}
                disabled={disabled === true}
                onClick={() => onChange({ riskLevel: toggled(levels, level) })}
                title={`Показывать только рейсы с уровнем риска «${riskLevelLabel(level)}»`}
              >
                {riskLevelLabel(level)}
              </button>
            )
          })}
        </div>
      </div>

      <div className="filter-group">
        <label className="check-row">
          <input
            type="checkbox"
            checked={attentionOnly}
            disabled={disabled === true}
            onChange={(e) => onChange({ attentionOnly: e.target.checked })}
          />
          только требующие внимания
        </label>
      </div>

      <div className="filter-group">
        <label className="sort-select">
          Порядок
          <select
            value={query.sort ?? 'CREATED_DESC'}
            disabled={disabled === true}
            onChange={(e) => onChange({ sort: e.target.value })}
          >
            {SORTS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
      </div>

      <div className="filter-group filter-actions">
        <button onClick={onReset} disabled={!filtered || disabled === true}>
          Сбросить фильтры
        </button>
      </div>
    </div>
  )
}
