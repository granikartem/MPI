import { useCallback, useEffect, useState } from 'react'
import {
  CaravanRequest,
  changeStatus,
  getStatusHistory,
  getStatusInfo,
  RequestStatusInfo,
  StatusHistoryEntry,
  StatusTransition,
} from '../api'
import StatusBadge from './StatusBadge'

interface Props {
  request: CaravanRequest
  onClose: () => void
  onUpdated: (request: CaravanRequest) => void
}

const ROLES = [
  { value: 'DISPATCHER', label: 'Диспетчер караванов' },
  { value: 'CARAVAN_MASTER', label: 'Караван-мастер' },
]

function formatMoment(value: string): string {
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString('ru-RU')
}

function errorText(e: unknown): string {
  const message = (e as { response?: { data?: { message?: string } } })?.response?.data?.message
  return message ?? 'Не удалось выполнить переход статуса'
}

export default function StatusModal({ request, onClose, onUpdated }: Props) {
  const [info, setInfo] = useState<RequestStatusInfo | null>(null)
  const [history, setHistory] = useState<StatusHistoryEntry[]>([])
  const [role, setRole] = useState('DISPATCHER')
  const [actorName, setActorName] = useState('')
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState<string | null>(null)

  const reload = useCallback(() => {
    getStatusInfo(request.id).then(setInfo).catch(() => setInfo(null))
    getStatusHistory(request.id).then(setHistory).catch(() => setHistory([]))
  }, [request.id])

  useEffect(reload, [reload])

  function blockerFor(t: StatusTransition): string | null {
    if (t.blockedReason) return t.blockedReason
    if (!t.roles.includes(role)) {
      const allowed = t.roles.map((r) => ROLES.find((x) => x.value === r)?.label ?? r).join(', ')
      return `Действие доступно роли: ${allowed}`
    }
    if (t.reasonRequired && reason.trim() === '') return 'Укажите причину перехода'
    return null
  }

  async function apply(t: StatusTransition) {
    setError(null)
    setBusy(t.to)
    try {
      const updated = await changeStatus(request.id, {
        targetStatus: t.to,
        actorRole: role,
        actorName: actorName.trim() || undefined,
        reason: reason.trim() || undefined,
      })
      onUpdated(updated)
      setReason('')
      reload()
    } catch (e) {
      setError(errorText(e))
    } finally {
      setBusy(null)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>Статус рейса</h3>
          <button className="link" onClick={onClose}>✕</button>
        </div>
        <div className="muted small">
          {request.origin} → {request.destination} · {request.routeName ?? 'маршрут не задан'}
        </div>

        <div className="status-current">
          <span className="muted small">Текущий статус:</span>
          <StatusBadge status={info?.status ?? request.status} label={info?.statusLabel} />
        </div>

        {error && <div className="error">{error}</div>}

        {info?.terminal ? (
          <div className="muted small">
            Статус финальный — дальнейшие переходы статусной моделью не предусмотрены.
          </div>
        ) : (
          <>
            <div className="actor-row">
              <label>
                Роль актора
                <select value={role} onChange={(e) => setRole(e.target.value)}>
                  {ROLES.map((r) => (
                    <option key={r.value} value={r.value}>{r.label}</option>
                  ))}
                </select>
              </label>
              <label>
                ФИО (для журнала)
                <input value={actorName} onChange={(e) => setActorName(e.target.value)} placeholder="Например, Кэсседи" />
              </label>
            </div>

            <label>
              Причина перехода
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder="Обязательна при фиксации задержки"
              />
            </label>

            <div className="transitions">
              {(info?.transitions ?? []).map((t) => {
                const blocked = blockerFor(t)
                return (
                  <div className="transition" key={t.to}>
                    <div className="transition-head">
                      <button
                        disabled={blocked !== null || busy !== null}
                        title={blocked ?? ''}
                        onClick={() => apply(t)}
                      >
                        {busy === t.to ? '...' : t.action}
                      </button>
                      <StatusBadge status={t.to} label={`→ ${t.toLabel}`} />
                    </div>
                    {blocked && <div className="muted small">{blocked}</div>}
                  </div>
                )
              })}
            </div>
          </>
        )}

        <div className="derivation">
          <div className="muted small">История изменений статуса (FR-3)</div>
          <table className="inner">
            <thead>
              <tr>
                <th>Когда</th>
                <th>Переход</th>
                <th>Кто</th>
                <th>Причина</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id}>
                  <td className="small">{formatMoment(h.occurredAt)}</td>
                  <td className="small">
                    {h.fromLabel ? `${h.fromLabel} → ` : ''}
                    <b>{h.toLabel}</b>
                  </td>
                  <td className="small">
                    {h.actorRoleLabel}
                    {h.actorName ? ` · ${h.actorName}` : ''}
                  </td>
                  <td className="small">{h.reason ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
