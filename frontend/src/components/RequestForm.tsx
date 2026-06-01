import { useState } from 'react'
import {
  createRequest,
  CaravanRequest,
  Checkpoint,
  RouteOption,
  SegmentInput,
} from '../api'

interface Props {
  routes: RouteOption[]
  checkpoints: Checkpoint[]
  onCreated: (request: CaravanRequest) => void
}

type Mode = 'template' | 'manual'

export default function RequestForm({ routes, checkpoints, onCreated }: Props) {
  const [origin, setOrigin] = useState('Goodsprings')
  const [destination, setDestination] = useState('New Vegas')
  const [departureDate, setDepartureDate] = useState('2287-10-21')
  const [cargoDescription, setCargoDescription] = useState('')
  const [cargoValueCaps, setCargoValueCaps] = useState(5000)
  const [mode, setMode] = useState<Mode>('template')
  const [routeId, setRouteId] = useState(routes[0]?.id ?? '')
  const [segments, setSegments] = useState<SegmentInput[]>([
    { fromCode: checkpoints[0]?.code ?? '', toCode: checkpoints[1]?.code ?? '', distanceKm: 40 },
  ])
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  function updateSegment(i: number, patch: Partial<SegmentInput>) {
    setSegments((prev) => prev.map((s, idx) => (idx === i ? { ...s, ...patch } : s)))
  }
  function addSegment() {
    setSegments((prev) => [
      ...prev,
      { fromCode: checkpoints[0]?.code ?? '', toCode: checkpoints[1]?.code ?? '', distanceKm: 40 },
    ])
  }
  function removeSegment(i: number) {
    setSegments((prev) => prev.filter((_, idx) => idx !== i))
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    try {
      const base = { origin, destination, departureDate, cargoDescription, cargoValueCaps }
      const body =
        mode === 'template' ? { ...base, routeId } : { ...base, segments }
      const created = await createRequest(body)
      onCreated(created)
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Ошибка создания заявки')
    } finally {
      setBusy(false)
    }
  }

  return (
    <form className="card" onSubmit={submit}>
      <h2>Новая заявка на перевозку</h2>
      <label>
        Пункт отправления
        <input value={origin} onChange={(e) => setOrigin(e.target.value)} required />
      </label>
      <label>
        Пункт назначения
        <input value={destination} onChange={(e) => setDestination(e.target.value)} required />
      </label>
      <label>
        Дата отправки
        <input value={departureDate} onChange={(e) => setDepartureDate(e.target.value)} required />
      </label>

      <div className="mode-toggle">
        <button
          type="button"
          className={mode === 'template' ? 'active' : ''}
          onClick={() => setMode('template')}
        >
          Шаблон маршрута
        </button>
        <button
          type="button"
          className={mode === 'manual' ? 'active' : ''}
          onClick={() => setMode('manual')}
        >
          Ручной маршрут
        </button>
      </div>

      {mode === 'template' ? (
        <label>
          Маршрут
          <select value={routeId} onChange={(e) => setRouteId(e.target.value)}>
            {routes.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </label>
      ) : (
        <div className="segments">
          <div className="muted small">Участки маршрута (по порядку)</div>
          {segments.map((s, i) => (
            <div className="segment-row" key={i}>
              <select value={s.fromCode} onChange={(e) => updateSegment(i, { fromCode: e.target.value })}>
                {checkpoints.map((c) => (
                  <option key={c.code} value={c.code}>{c.name}</option>
                ))}
              </select>
              <span>→</span>
              <select value={s.toCode} onChange={(e) => updateSegment(i, { toCode: e.target.value })}>
                {checkpoints.map((c) => (
                  <option key={c.code} value={c.code}>{c.name}</option>
                ))}
              </select>
              <input
                type="number"
                value={s.distanceKm}
                onChange={(e) => updateSegment(i, { distanceKm: Number(e.target.value) })}
                min={1}
                title="км"
              />
              <button type="button" className="link" onClick={() => removeSegment(i)} disabled={segments.length === 1}>
                ✕
              </button>
            </div>
          ))}
          <button type="button" className="link" onClick={addSegment}>
            + участок
          </button>
        </div>
      )}

      <label>
        Описание груза
        <input
          value={cargoDescription}
          onChange={(e) => setCargoDescription(e.target.value)}
          placeholder="Медикаменты, патроны..."
        />
      </label>
      <label>
        Ценность груза (крышек)
        <input
          type="number"
          value={cargoValueCaps}
          onChange={(e) => setCargoValueCaps(Number(e.target.value))}
          min={0}
        />
      </label>
      {error && <div className="error">{error}</div>}
      <button type="submit" disabled={busy}>
        {busy ? 'Создание...' : 'Создать заявку'}
      </button>
    </form>
  )
}
