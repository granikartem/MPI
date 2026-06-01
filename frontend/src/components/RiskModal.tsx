import { useEffect, useState } from 'react'
import { CaravanRequest, deleteRisk, getRisk, RiskAssessment } from '../api'

interface Props {
  request: CaravanRequest
  onClose: () => void
  onUpdated: (request: CaravanRequest) => void
}

function cargoTier(caps: number): string {
  if (caps >= 20000) return '≥ 20 000 → +30'
  if (caps >= 5000) return '5 000–19 999 → +20'
  if (caps >= 1000) return '1 000–4 999 → +10'
  return '< 1 000 → +0'
}

function statusNote(status: string): string {
  if (status === 'STALE') return 'Данные Wasteland Intel старше 24 ч — оценка приблизительная.'
  if (status === 'NA') return 'Wasteland Intel недоступен — risk_score не рассчитан.'
  return 'Данные актуальны.'
}

export default function RiskModal({ request, onClose, onUpdated }: Props) {
  const [risk, setRisk] = useState<RiskAssessment | null>(null)
  const [loading, setLoading] = useState(true)
  const [deleting, setDeleting] = useState(false)

  useEffect(() => {
    getRisk(request.id)
      .then(setRisk)
      .catch(() => setRisk(null))
      .finally(() => setLoading(false))
  }, [request.id])

  async function onDelete() {
    setDeleting(true)
    try {
      const updated = await deleteRisk(request.id)
      onUpdated(updated)
      onClose()
    } finally {
      setDeleting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-head">
          <h3>Как получен risk_score</h3>
          <button className="link" onClick={onClose}>✕</button>
        </div>
        <div className="muted small">
          {request.origin} → {request.destination} · {request.routeName}
        </div>

        {loading ? (
          <div className="muted">Загрузка...</div>
        ) : !risk ? (
          <div className="muted">Оценка ещё не рассчитана.</div>
        ) : (
          <>
            <div className="muted small modal-asof">
              Источник: Wasteland Intel, данные на {risk.asOf ?? '—'}
            </div>

            <table className="inner">
              <thead>
                <tr>
                  <th>Участок</th>
                  <th>Угроза</th>
                  <th>Уровень</th>
                </tr>
              </thead>
              <tbody>
                {risk.segments.map((s) => (
                  <tr key={s.segment}>
                    <td>{s.segment}</td>
                    <td>{s.threats.join(', ') || '—'}</td>
                    <td>{s.threatLevel}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="derivation">
              <div className="step">
                <span>Сумма уровней угроз</span>
                <b>{risk.threatSum}</b>
              </div>
              <div className="step">
                <span>База = сумма × 6 (макс. 100)</span>
                <b>{risk.base}</b>
              </div>
              <div className="step">
                <span>Ценность груза {request.cargoValueCaps} крышек ({cargoTier(request.cargoValueCaps)})</span>
                <b>+{risk.cargoFactor}</b>
              </div>
              <div className="step total">
                <span>Итог = min(100, база + коэф. груза)</span>
                <b>{risk.score ?? '—'}</b>
              </div>
            </div>

            <div className="rec modal-rec">{risk.recommendation}</div>
            <div className="muted small">{statusNote(risk.status)}</div>

            <div className="modal-actions">
              <button className="danger" onClick={onDelete} disabled={deleting}>
                {deleting ? 'Удаление...' : 'Удалить оценку'}
              </button>
              <span className="muted small">
                после удаления нажмите «Пересчитать риск» в реестре — оценка появится заново
              </span>
            </div>
          </>
        )}
      </div>
    </div>
  )
}
