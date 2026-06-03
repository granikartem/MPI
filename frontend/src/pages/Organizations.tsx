import { useEffect, useMemo, useState } from 'react'
import {
  createOrganization,
  getHealth,
  getOrganizations,
  HealthResponse,
  Organization,
} from '../api'
import { navigate } from '../router'

const TIERS = [
  {
    id: 'BASIC',
    name: 'BASIC',
    price: '200 caps / мес.',
    features: ['до 3 диспетчеров', 'до 50 рейсов / мес', 'Intel: базовый'],
  },
  {
    id: 'STANDARD',
    name: 'STANDARD',
    price: '600 caps / мес.',
    features: ['до 10 диспетчеров', 'до 300 рейсов / мес', 'Intel: расширенный'],
  },
  {
    id: 'PRO',
    name: 'PRO',
    price: '1 500 caps / мес.',
    features: ['без лимита', 'SLA 99.5%', 'Intel: live-feed + API'],
  },
]

function tierPrice(tier: string) {
  return TIERS.find((t) => t.id === tier)?.price ?? '—'
}

export default function Organizations() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [organizations, setOrganizations] = useState<Organization[]>([])
  const [name, setName] = useState('Crimson Caravan Company')
  const [subscriptionTier, setSubscriptionTier] = useState('STANDARD')
  const [legalAddress, setLegalAddress] = useState('Freeside, North Gate, Block 4, Unit 7 / NCR-registered / New Vegas')
  const [primaryContact, setPrimaryContact] = useState('Alice Hawthorne')
  const [contactChannel, setContactChannel] = useState('a.hawthorne@crimson.cvn')
  const [region, setRegion] = useState('Mojave · NV')
  const [skipDispatcher, setSkipDispatcher] = useState(false)
  const [dispatcherName, setDispatcherName] = useState('Alice Hawthorne')
  const [dispatcherLogin, setDispatcherLogin] = useState('disp.hawthorne')
  const [dispatcherPassword, setDispatcherPassword] = useState('change-me-2281')
  const [dispatcherContact, setDispatcherContact] = useState('disp.hawthorne@crimson.cvn')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [created, setCreated] = useState<Organization | null>(null)

  useEffect(() => {
    getHealth().then(setHealth).catch(() => setHealth(null))
    getOrganizations().then(setOrganizations).catch(() => setOrganizations([]))
  }, [])

  const activeUsers = useMemo(
    () => organizations.reduce((sum, org) => sum + org.userCount, 0),
    [organizations],
  )

  const canCreate =
    name.trim().length > 0 &&
    subscriptionTier.trim().length > 0 &&
    (skipDispatcher ||
      (dispatcherName.trim().length > 0 &&
        dispatcherLogin.trim().length > 0 &&
        dispatcherPassword.trim().length > 0))

  async function submit(e: React.FormEvent) {
    e.preventDefault()
    setBusy(true)
    setError(null)
    setCreated(null)
    try {
      const organization = await createOrganization({
        name,
        subscriptionTier,
        legalAddress,
        primaryContact,
        contactChannel,
        region,
        firstDispatcher: skipDispatcher
          ? undefined
          : {
              fullName: dispatcherName,
              login: dispatcherLogin,
              initialPassword: dispatcherPassword,
              contactChannel: dispatcherContact,
            },
      })
      setOrganizations((prev) => [organization, ...prev])
      setCreated(organization)
    } catch (err: any) {
      setError(err?.response?.data?.message ?? 'Ошибка создания организации')
    } finally {
      setBusy(false)
    }
  }

  const conflict = error?.toLowerCase().includes('существ')

  return (
    <div className="admin-console">
      <header className="admin-header">
        <div>
          <h1>ROBCO PLATFORM // SUPERUSER CONSOLE</h1>
          <div className="admin-sub">PLATFORM v4.21.07 · TENANT OPS</div>
        </div>
        <div className="admin-mode">SUPERUSER MODE</div>
        <div className="admin-user">
          ROLE :: PLATFORM OPERATOR
          <br />
          {health ? `API ${health.status} · PG ${health.postgres} · Mongo ${health.mongo}` : 'API недоступен'}
        </div>
      </header>

      <div className="admin-grid">
        <aside className="admin-nav">
          <div className="nav-title">-- PLATFORM --</div>
          <button className="nav-item active">[&gt;] ORGANIZATIONS</button>
          <button className="nav-item">[ ] SUBSCRIPTIONS</button>
          <button className="nav-item">[ ] AUDIT LOG</button>
          <button className="nav-item" onClick={() => navigate('/requests')}>[ ] DISPATCH</button>
          <div className="nav-foot">
            TENANTS: {organizations.length}
            <br />
            ACTIVE USERS: {activeUsers}
            <br />
            STATUS: {health?.status ?? 'offline'}
          </div>
        </aside>

        <main className="admin-main">
          <form className="admin-panel" onSubmit={submit}>
            <div className="admin-panel-title">
              <span>CREATE ORGANIZATION</span>
              <span>WIZARD · STEP 1 / 2</span>
            </div>

            <div className="admin-info">
              Tenant-scope создаётся в PostgreSQL, пользователи привязываются к `organization_id`, событие создания
              фиксируется в Audit Log.
            </div>

            <div className="admin-stepper">
              <div className="admin-step active">1 · ДАННЫЕ ОРГАНИЗАЦИИ</div>
              <div className={`admin-step ${skipDispatcher ? '' : 'active'}`}>2 · ПЕРВЫЙ ДИСПЕТЧЕР</div>
            </div>

            {error && (
              <div className="admin-error">
                ✕ {error}
                {conflict && <span> · выберите другое имя или логин</span>}
              </div>
            )}
            {created && (
              <div className="admin-success">
                ◆ Организация {created.name} создана · tenant {created.tenantKey}
              </div>
            )}

            <section className="admin-block">
              <h2>STEP 1 · ДАННЫЕ ОРГАНИЗАЦИИ</h2>
              <label className="full">
                NAME · НАЗВАНИЕ ОРГАНИЗАЦИИ
                <input
                  className={conflict ? 'input-error' : ''}
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                />
              </label>

              <div className="full">
                <div className="field-title">SUBSCRIPTION TIER · УРОВЕНЬ ПОДПИСКИ</div>
                <div className="tier-grid">
                  {TIERS.map((tier) => (
                    <button
                      type="button"
                      key={tier.id}
                      className={`tier-card ${subscriptionTier === tier.id ? 'selected' : ''}`}
                      onClick={() => setSubscriptionTier(tier.id)}
                    >
                      <b>{tier.name}</b>
                      <span>{tier.price}</span>
                      {tier.features.map((feature) => (
                        <small key={feature}>· {feature}</small>
                      ))}
                    </button>
                  ))}
                </div>
              </div>

              <label className="full">
                LEGAL ADDRESS · ЮРИДИЧЕСКИЙ АДРЕС
                <textarea value={legalAddress} onChange={(e) => setLegalAddress(e.target.value)} />
              </label>
              <label>
                PRIMARY CONTACT · ОСНОВНОЙ КОНТАКТ
                <input value={primaryContact} onChange={(e) => setPrimaryContact(e.target.value)} />
              </label>
              <label>
                HOLOPHONE / EMAIL
                <input value={contactChannel} onChange={(e) => setContactChannel(e.target.value)} />
              </label>
              <label>
                REGION
                <input value={region} onChange={(e) => setRegion(e.target.value)} />
              </label>
            </section>

            <section className={`admin-block ${skipDispatcher ? 'muted-block' : ''}`}>
              <h2>STEP 2 · ПЕРВЫЙ ДИСПЕТЧЕР</h2>
              <label className="check-row full">
                <input
                  type="checkbox"
                  checked={skipDispatcher}
                  onChange={(e) => setSkipDispatcher(e.target.checked)}
                />
                SKIP · Пропустить назначение диспетчера
              </label>
              <label>
                FULL NAME · ФИО
                <input
                  value={dispatcherName}
                  onChange={(e) => setDispatcherName(e.target.value)}
                  disabled={skipDispatcher}
                  required={!skipDispatcher}
                />
              </label>
              <label>
                LOGIN · ЛОГИН
                <input
                  value={dispatcherLogin}
                  onChange={(e) => setDispatcherLogin(e.target.value)}
                  disabled={skipDispatcher}
                  required={!skipDispatcher}
                />
              </label>
              <label>
                INITIAL PASSWORD
                <input
                  value={dispatcherPassword}
                  onChange={(e) => setDispatcherPassword(e.target.value)}
                  disabled={skipDispatcher}
                  required={!skipDispatcher}
                />
              </label>
              <label>
                EMAIL / HOLOPHONE
                <input
                  value={dispatcherContact}
                  onChange={(e) => setDispatcherContact(e.target.value)}
                  disabled={skipDispatcher}
                />
              </label>
            </section>

            <div className="admin-actions">
              <button type="button" onClick={() => navigate('/')}>BACK</button>
              <button className="create-button" type="submit" disabled={busy || !canCreate}>
                {busy ? 'PROVISIONING...' : 'CREATE ORGANIZATION'}
              </button>
            </div>
          </form>

          <section className="admin-panel org-list">
            <div className="admin-panel-title">
              <span>ORGANIZATION REGISTRY</span>
              <span>{organizations.length} TENANTS</span>
            </div>
            {organizations.length === 0 ? (
              <div className="muted">Организаций пока нет.</div>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Tenant</th>
                    <th>Название</th>
                    <th>Подписка</th>
                    <th>Контакт</th>
                    <th>Пользователи</th>
                    <th>Статус</th>
                  </tr>
                </thead>
                <tbody>
                  {organizations.map((org) => (
                    <tr key={org.id}>
                      <td>{org.tenantKey}</td>
                      <td>{org.name}</td>
                      <td>{org.subscriptionTier}</td>
                      <td>{org.primaryContact ?? org.contactChannel ?? '—'}</td>
                      <td>{org.userCount}</td>
                      <td>{org.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </section>
        </main>

        <aside className="admin-summary">
          <h2>SUMMARY</h2>
          <div className="sum-sec">
            <div className="sum-head">-- ORGANIZATION --</div>
            <div className="sum-row"><span>Name:</span><b>{name || '—'}</b></div>
            <div className="sum-row"><span>Tier:</span><b>{subscriptionTier}</b></div>
            <div className="sum-row"><span>Billing:</span><b>{tierPrice(subscriptionTier)}</b></div>
            <div className="sum-row"><span>Region:</span><b>{region || '—'}</b></div>
          </div>
          <div className="sum-sec">
            <div className="sum-head">-- FIRST DISPATCHER --</div>
            <div className="sum-row"><span>Status:</span><b>{skipDispatcher ? 'SKIPPED' : 'READY'}</b></div>
            <div className="sum-row"><span>Login:</span><b>{skipDispatcher ? '—' : dispatcherLogin || '—'}</b></div>
            <div className="sum-row"><span>Access:</span><b>{skipDispatcher ? '—' : 'DISPATCHER'}</b></div>
          </div>
          <div className="sum-effect">
            <b>БУДЕТ СОЗДАНО</b>
            <span>+ TENANT scope</span>
            <span>+ ORG catalog row</span>
            <span>+ USER account {skipDispatcher ? '(later)' : ''}</span>
            <span>+ AUDIT event</span>
          </div>
        </aside>
      </div>
    </div>
  )
}
