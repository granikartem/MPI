import { useEffect, useState } from 'react'
import {
  CaravanRequest,
  Checkpoint,
  getCheckpoints,
  getHealth,
  getRequests,
  getRoutes,
  HealthResponse,
  RouteOption,
} from '../api'
import RequestForm from '../components/RequestForm'
import RequestList from '../components/RequestList'
import { navigate } from '../router'

export default function Console() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [routes, setRoutes] = useState<RouteOption[]>([])
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([])
  const [requests, setRequests] = useState<CaravanRequest[]>([])

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
    getRoutes().then(setRoutes).catch(() => setRoutes([]))
    getCheckpoints().then(setCheckpoints).catch(() => setCheckpoints([]))
    getRequests().then(setRequests).catch(() => setRequests([]))
  }, [])

  function onCreated(request: CaravanRequest) {
    setRequests((prev) => [request, ...prev])
  }

  function onUpdated(request: CaravanRequest) {
    setRequests((prev) => prev.map((r) => (r.id === request.id ? request : r)))
  }

  return (
    <div className="app">
      <header>
        <div className="header-top">
          <h1>CARAVAN // DISPATCH TERMINAL</h1>
          <button className="link" onClick={() => navigate('/')}>← на главную</button>
        </div>
        <div className="health">
          {health ? (
            <>
              <span className={`dot ${health.status === 'ok' ? 'ok' : 'bad'}`} />
              сервер: {health.status} · PG: {health.postgres} · Mongo: {health.mongo}
            </>
          ) : (
            <>
              <span className="dot bad" /> сервер недоступен
            </>
          )}
        </div>
      </header>

      <main>
        {routes.length > 0 && checkpoints.length > 0 && (
          <RequestForm routes={routes} checkpoints={checkpoints} onCreated={onCreated} />
        )}
        <RequestList requests={requests} onUpdated={onUpdated} />
      </main>
    </div>
  )
}
