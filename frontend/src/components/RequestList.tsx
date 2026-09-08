import { useEffect, useState } from 'react'
import { CaravanRequest, recalcRisk, RegistryRow } from '../api'
import RiskBadge from './RiskBadge'
import RiskModal from './RiskModal'
import StatusBadge from './StatusBadge'
import StatusModal from './StatusModal'

interface Props {
  organizationId: string
  rows: RegistryRow[]
  onChanged: () => void
}

function formatEta(hours: number | null): string {
  if (hours === null) return '—'
  const days = Math.floor(hours / 24)
  const rest = Math.round(hours % 24)
  return days > 0 ? `${days} д ${rest} ч` : `${rest} ч`
}

function formatMoment(value: string | null): string {
  if (value === null) return '—'
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString('ru-RU')
}

function errorText(e: unknown): string {
  const message = (e as { response?: { data?: { message?: string } } })?.response?.data?.message
  return message ?? 'Не удалось пересчитать risk_score'
}

function actorOf(row: RegistryRow): string {
  const role = row.lastStatusActorRoleLabel
  if (role === null) return '—'
  return row.lastStatusActorName ? `${role} · ${row.lastStatusActorName}` : role
}

function toRequest(row: RegistryRow, organizationId: string): CaravanRequest {
  return {
    id: row.id,
    organizationId,
    origin: row.origin,
    destination: row.destination,
    departureDate: row.departureDate,
    cargoDescription: row.cargoDescription,
    cargoValueCaps: row.cargoValueCaps,
    routeCode: row.routeCode,
    routeName: row.routeName,
    etaHours: row.etaHours,
    riskScore: row.riskScore,
    riskStatus: row.riskStatus,
    recommendation: row.recommendation,
    status: row.status,
    statusLabel: row.statusLabel,
    createdAt: row.createdAt,
  }
}

export default function RequestList({ organizationId, rows, onChanged }: Props) {
  const [riskFor, setRiskFor] = useState<CaravanRequest | null>(null)
  const [statusFor, setStatusFor] = useState<CaravanRequest | null>(null)
  const [busy, setBusy] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => setError(null), [rows])

  async function recalc(id: string) {
    setBusy(id)
    setError(null)
    try {
      await recalcRisk(id)
      onChanged()
    } catch (e) {
      setError(errorText(e))
    } finally {
      setBusy(null)
    }
  }

  return (
    <>
      {error && (
        <div className="card">
          <div className="error">{error}</div>
        </div>
      )}

      {rows.length > 0 && (
        <div className="card">
          <div className="registry-table">
            <table>
              <thead>
                <tr>
                  <th>Маршрут (id · название)</th>
                  <th>Откуда → Куда</th>
                  <th>Отправка</th>
                  <th>Груз</th>
                  <th>ETA</th>
                  <th>risk_score</th>
                  <th>Статус</th>
                  <th>Внимание</th>
                  <th>Изменение статуса</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.id} className={r.attention.length > 0 ? 'row-attention' : ''}>
                    <td>
                      {r.routeCode && <span className="route-code">{r.routeCode}</span>}
                      {r.routeName ?? '—'}
                    </td>
                    <td>
                      {r.origin} → {r.destination}
                    </td>
                    <td>{r.departureDate}</td>
                    <td>
                      {r.cargoDescription || '—'}
                      <div className="muted small">{r.cargoValueCaps} крышек</div>
                    </td>
                    <td>{formatEta(r.etaHours)}</td>
                    <td>
                      <RiskBadge
                        score={r.riskScore}
                        status={r.riskStatus}
                        onClick={() => setRiskFor(toRequest(r, organizationId))}
                      />
                      <div className="muted small">{r.riskLevelLabel}</div>
                      {r.recommendation && <div className="rec">{r.recommendation}</div>}
                    </td>
                    <td>
                      <StatusBadge
                        status={r.status}
                        label={r.statusLabel}
                        onClick={() => setStatusFor(toRequest(r, organizationId))}
                      />
                    </td>
                    <td>
                      {r.attention.length === 0 ? (
                        <span className="muted small">—</span>
                      ) : (
                        <div className="attention-marks">
                          {r.attention.map((a) => (
                            <span key={a.code} className="attention-mark">
                              {a.label}
                            </span>
                          ))}
                        </div>
                      )}
                    </td>
                    <td>
                      <div className="small">{formatMoment(r.lastStatusChangeAt)}</div>
                      <div className="muted small">{actorOf(r)}</div>
                      {r.lastStatusReason && <div className="muted small">{r.lastStatusReason}</div>}
                    </td>
                    <td>
                      <button
                        className="link"
                        disabled={busy === r.id}
                        onClick={() => recalc(r.id)}
                      >
                        {busy === r.id ? '...' : 'Пересчитать риск'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {riskFor && (
        <RiskModal
          request={riskFor}
          onClose={() => setRiskFor(null)}
          onUpdated={() => onChanged()}
        />
      )}

      {statusFor && (
        <StatusModal
          request={statusFor}
          onClose={() => setStatusFor(null)}
          onUpdated={(updated) => {
            setStatusFor(updated)
            onChanged()
          }}
        />
      )}
    </>
  )
}
