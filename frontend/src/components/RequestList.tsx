import { useState } from 'react'
import { CaravanRequest, recalcRisk } from '../api'
import RiskBadge from './RiskBadge'
import RiskModal from './RiskModal'
import StatusBadge from './StatusBadge'
import StatusModal from './StatusModal'

interface Props {
  requests: CaravanRequest[]
  onUpdated: (request: CaravanRequest) => void
}

function formatEta(hours: number | null): string {
  if (hours === null) return '—'
  const days = Math.floor(hours / 24)
  const rest = Math.round(hours % 24)
  return days > 0 ? `${days} д ${rest} ч` : `${rest} ч`
}

export default function RequestList({ requests, onUpdated }: Props) {
  const [riskFor, setRiskFor] = useState<CaravanRequest | null>(null)
  const [statusFor, setStatusFor] = useState<CaravanRequest | null>(null)

  async function recalc(id: string) {
    const updated = await recalcRisk(id)
    onUpdated(updated)
  }

  if (requests.length === 0) {
    return <div className="card muted">Заявок пока нет.</div>
  }

  return (
    <div className="card">
      <h2>Реестр заявок</h2>
      <table>
        <thead>
          <tr>
            <th>Маршрут (id · название)</th>
            <th>Откуда → Куда</th>
            <th>Груз</th>
            <th>Ценность</th>
            <th>ETA</th>
            <th>risk_score</th>
            <th>Статус</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {requests.map((r) => (
            <tr key={r.id}>
              <td>
                {r.routeCode && <span className="route-code">{r.routeCode}</span>}
                {r.routeName ?? '—'}
              </td>
              <td>
                {r.origin} → {r.destination}
              </td>
              <td>{r.cargoDescription || '—'}</td>
              <td>{r.cargoValueCaps}</td>
              <td>{formatEta(r.etaHours)}</td>
              <td>
                <RiskBadge score={r.riskScore} status={r.riskStatus} onClick={() => setRiskFor(r)} />
                {r.recommendation && <div className="rec">{r.recommendation}</div>}
              </td>
              <td>
                <StatusBadge status={r.status} label={r.statusLabel} onClick={() => setStatusFor(r)} />
              </td>
              <td>
                <button className="link" onClick={() => recalc(r.id)}>
                  Пересчитать риск
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {riskFor && (
        <RiskModal
          request={riskFor}
          onClose={() => setRiskFor(null)}
          onUpdated={onUpdated}
        />
      )}

      {statusFor && (
        <StatusModal
          request={statusFor}
          onClose={() => setStatusFor(null)}
          onUpdated={(updated) => {
            onUpdated(updated)
            setStatusFor(updated)
          }}
        />
      )}
    </div>
  )
}
