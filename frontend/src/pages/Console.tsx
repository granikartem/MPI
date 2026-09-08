import { useEffect, useState } from 'react'
import {
  Checkpoint,
  getCheckpoints,
  getHealth,
  getOrganizations,
  getRoutes,
  HealthResponse,
  Organization,
  RouteOption,
} from '../api'
import RequestForm from '../components/RequestForm'
import RequestRegistry from '../components/RequestRegistry'
import { navigate, subscribeRouter } from '../router'

function selectedOrgId(): string | null {
  return new URLSearchParams(window.location.search).get('org')
}

export default function Console() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [orgId, setOrgId] = useState<string | null>(selectedOrgId())

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
    getOrganizations().then(setOrganizations).catch(() => setOrganizations([]))
    return subscribeRouter(() => setOrgId(selectedOrgId()))
  }, [])

  const org = organizations.find((o) => o.id === orgId) ?? null

  return (
    <div className="app">
      <header>
        <div className="header-top">
          <h1>CARAVAN // DISPATCH TERMINAL</h1>
          <div className="header-actions">
            <button className="link" onClick={() => navigate('/organizations')}>консоль организаций</button>
            <button className="link" onClick={() => navigate('/')}>← на главную</button>
          </div>
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
        {orgId ? (
          <OrgDispatch org={org} orgId={orgId} />
        ) : (
          <OrgPicker organizations={organizations} />
        )}
      </main>
    </div>
  )
}

function OrgPicker({ organizations }: { organizations: Organization[] }) {
  return (
    <div className="card">
      <h2>Организации</h2>
      <p className="muted small">Выберите организацию, чтобы работать с её рейсами.</p>
      {organizations.length === 0 ? (
        <div className="muted">
          Организаций пока нет. Создайте в{' '}
          <button className="link" onClick={() => navigate('/organizations')}>консоли организаций</button>.
        </div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Организация</th>
              <th>Подписка</th>
              <th>Пользователи</th>
              <th>Статус</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {organizations.map((o) => (
              <tr key={o.id}>
                <td>{o.name}</td>
                <td>{o.subscriptionTier}</td>
                <td>{o.userCount}</td>
                <td>{o.status}</td>
                <td>
                  <button onClick={() => navigate(`/requests?org=${o.id}`)}>Рейсы →</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  )
}

function OrgDispatch({ org, orgId }: { org: Organization | null; orgId: string }) {
  const [routes, setRoutes] = useState<RouteOption[]>([])
  const [checkpoints, setCheckpoints] = useState<Checkpoint[]>([])
  const [created, setCreated] = useState(0)

  useEffect(() => {
    getRoutes().then(setRoutes).catch(() => setRoutes([]))
    getCheckpoints().then(setCheckpoints).catch(() => setCheckpoints([]))
  }, [orgId])

  return (
    <>
      <div className="card org-banner">
        <button className="link" onClick={() => navigate('/requests')}>← все организации</button>
        <h2>Рейсы · {org?.name ?? 'организация'}</h2>
        {org && <span className="muted small">{org.subscriptionTier} · tenant {org.tenantKey}</span>}
      </div>
      {routes.length > 0 && checkpoints.length > 0 && (
        <RequestForm
          organizationId={orgId}
          routes={routes}
          checkpoints={checkpoints}
          onCreated={() => setCreated((n) => n + 1)}
        />
      )}
      <RequestRegistry organizationId={orgId} reloadToken={created} />
    </>
  )
}
