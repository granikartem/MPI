import { useCallback, useEffect, useRef, useState } from 'react'
import { getRegistry, RegistryQuery, TripRegistry } from '../api'
import RegistryFilters from './RegistryFilters'
import RegistrySummary, { STATUS_ORDER } from './RegistrySummary'
import RequestList from './RequestList'

interface Props {
  organizationId: string
  reloadToken?: number
}

const DEFAULT_QUERY: RegistryQuery = {
  scope: 'ACTIVE',
  status: [],
  riskLevel: [],
  attentionOnly: false,
  sort: 'CREATED_DESC',
  limit: 200,
}

function errorText(e: unknown): string {
  const message = (e as { response?: { data?: { message?: string } } })?.response?.data?.message
  return message ?? 'Не удалось загрузить реестр рейсов — сервер недоступен'
}

function formatMoment(value: string): string {
  const d = new Date(value)
  return Number.isNaN(d.getTime()) ? value : d.toLocaleString('ru-RU')
}

function isFiltered(query: RegistryQuery): boolean {
  return (query.status ?? []).length > 0
    || (query.riskLevel ?? []).length > 0
    || query.attentionOnly === true
}

export default function RequestRegistry({ organizationId, reloadToken }: Props) {
  const [query, setQuery] = useState<RegistryQuery>(DEFAULT_QUERY)
  const [registry, setRegistry] = useState<TripRegistry | null>(null)
  const [appliedFiltered, setAppliedFiltered] = useState(false)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const issued = useRef(0)

  const load = useCallback(() => {
    const ticket = ++issued.current
    setLoading(true)
    setError(null)
    return getRegistry(organizationId, query)
      .then((data) => {
        if (ticket !== issued.current) return
        setRegistry(data)
        setAppliedFiltered(isFiltered(query))
        setError(null)
      })
      .catch((e) => {
        if (ticket !== issued.current) return
        setRegistry(null)
        setError(errorText(e))
      })
      .finally(() => {
        if (ticket === issued.current) setLoading(false)
      })
  }, [organizationId, query])

  useEffect(() => {
    load()
  }, [load, reloadToken])

  function changeScope(scope: string) {
    if (scope === query.scope) return
    setRegistry(null)
    setQuery((prev) => ({ ...prev, scope, status: [] }))
  }

  function changeQuery(patch: RegistryQuery) {
    setQuery((prev) => ({ ...prev, ...patch }))
  }

  function resetFilters() {
    setQuery((prev) => ({ ...prev, status: [], riskLevel: [], attentionOnly: false }))
  }

  function resetAll() {
    setRegistry(null)
    setQuery({ ...DEFAULT_QUERY, status: [], riskLevel: [] })
  }

  const summary = registry?.summary ?? null
  const organizationEmpty = summary !== null && summary.active === 0 && summary.completed === 0

  return (
    <>
      <div className="card">
        <div className="registry-head">
          <h2>Реестр рейсов</h2>
          <div className="registry-meta">
            {registry && (
              <span className="muted small">
                данные на {formatMoment(registry.generatedAt)} · показано {registry.shown} ·
                {' '}в срезе {registry.summary.scopeTotal}
                {registry.truncated && ` · выборка усечена до ${registry.limit}`}
              </span>
            )}
            {loading && <span className="muted small">обновление...</span>}
            <button className="link" disabled={loading} onClick={load}>
              Обновить
            </button>
          </div>
        </div>

        {error !== null ? (
          <div className="registry-state">
            <div className="error">{error}</div>
            <div className="muted small">
              Частичные данные не показываются — повторите загрузку реестра.
            </div>
            <div className="registry-state-actions">
              <button disabled={loading} onClick={load}>Повторить</button>
              <button disabled={loading} onClick={resetAll}>Сбросить отбор и срез</button>
            </div>
          </div>
        ) : registry === null || summary === null ? (
          <div className="muted">Загрузка реестра рейсов...</div>
        ) : organizationEmpty ? (
          <div className="registry-state">
            <div className="muted">В организации ещё нет заявок на перевозку.</div>
            <div className="muted small">
              Создайте первый рейс формой «Новая заявка на перевозку» выше — это прецедент UC-1.
            </div>
          </div>
        ) : (
          <>
            <RegistrySummary
              summary={summary}
              scope={registry.scope}
              scopeLabel={registry.scopeLabel}
              disabled={loading}
              onScope={changeScope}
            />
            <RegistryFilters
              scopeStatuses={STATUS_ORDER.filter((s) => s in summary.byStatus)}
              query={query}
              disabled={loading}
              onChange={changeQuery}
              onReset={resetFilters}
            />
            {registry.rows.length === 0 && (
              appliedFiltered ? (
                <div className="registry-state">
                  <div className="muted">
                    Под выбранные фильтры не подошёл ни один рейс среза «{registry.scopeLabel}».
                  </div>
                  <div className="muted small">Сводка по срезу выше сохраняется без изменений.</div>
                  <button onClick={resetFilters}>Сбросить фильтры</button>
                </div>
              ) : (
                <div className="registry-state">
                  <div className="muted">В срезе «{registry.scopeLabel}» пока нет рейсов.</div>
                  <div className="muted small">
                    Рейсы попадают сюда по мере изменения статуса — это прецедент UC-2.
                  </div>
                </div>
              )
            )}
          </>
        )}
      </div>

      {error === null && registry !== null && (
        <RequestList organizationId={organizationId} rows={registry.rows} onChanged={load} />
      )}
    </>
  )
}
