import axios from 'axios'

const api = axios.create({ baseURL: '/' })

export interface HealthResponse {
  service: string
  timestamp: string
  postgres: string
  mongo: string
  status: string
}

export interface RouteOption {
  id: string
  code: string
  name: string
}

export interface Checkpoint {
  code: string
  name: string
}

export interface CaravanRequest {
  id: string
  organizationId: string | null
  origin: string
  destination: string
  departureDate: string
  cargoDescription: string | null
  cargoValueCaps: number
  routeCode: string | null
  routeName: string | null
  etaHours: number | null
  riskScore: number | null
  riskStatus: string
  recommendation: string | null
  status: string
  statusLabel: string
  createdAt: string
}

export interface SegmentInput {
  fromCode: string
  toCode: string
  distanceKm: number
}

export interface CreateRequestBody {
  organizationId: string
  origin: string
  destination: string
  departureDate: string
  cargoDescription: string
  cargoValueCaps: number
  routeId?: string
  routeName?: string
  segments?: SegmentInput[]
}

export interface SegmentRisk {
  segment: string
  threatLevel: number
  threats: string[]
}

export interface RiskAssessment {
  requestId: string
  score: number | null
  status: string
  recommendation: string | null
  asOf: string | null
  computedAt: string
  threatSum: number
  base: number
  cargoFactor: number
  segments: SegmentRisk[]
}

export interface StatusTransition {
  to: string
  toLabel: string
  action: string
  roles: string[]
  reasonRequired: boolean
  blockedReason: string | null
}

export interface RequestStatusInfo {
  requestId: string
  status: string
  statusLabel: string
  terminal: boolean
  transitions: StatusTransition[]
}

export interface StatusHistoryEntry {
  id: string
  fromStatus: string | null
  fromLabel: string | null
  toStatus: string
  toLabel: string
  actorRole: string
  actorRoleLabel: string
  actorName: string | null
  reason: string | null
  occurredAt: string
}

export interface ChangeStatusBody {
  targetStatus: string
  actorRole: string
  actorName?: string
  reason?: string
}

export interface AttentionMark {
  code: string
  label: string
}

export interface RegistryRow {
  id: string
  routeCode: string | null
  routeName: string | null
  origin: string
  destination: string
  departureDate: string
  cargoDescription: string | null
  cargoValueCaps: number
  etaHours: number | null
  riskScore: number | null
  riskStatus: string
  riskLevel: string
  riskLevelLabel: string
  recommendation: string | null
  status: string
  statusLabel: string
  terminal: boolean
  lastStatusChangeAt: string | null
  lastStatusActorRole: string | null
  lastStatusActorRoleLabel: string | null
  lastStatusActorName: string | null
  lastStatusReason: string | null
  attention: AttentionMark[]
  createdAt: string
}

export interface RegistrySummary {
  active: number
  completed: number
  scopeTotal: number
  byStatus: Record<string, number>
  byRiskLevel: Record<string, number>
  byAttention: Record<string, number>
  attentionTotal: number
}

export interface TripRegistry {
  organizationId: string
  scope: string
  scopeLabel: string
  sort: string
  limit: number
  shown: number
  truncated: boolean
  generatedAt: string
  summary: RegistrySummary
  rows: RegistryRow[]
}

export interface RegistryQuery {
  scope?: string
  status?: string[]
  riskLevel?: string[]
  attentionOnly?: boolean
  sort?: string
  limit?: number
}

export interface FirstDispatcher {
  id: string
  fullName: string
  login: string
  role: string
  contactChannel: string | null
  active: boolean
  createdAt: string
}

export interface Organization {
  id: string
  tenantKey: string
  name: string
  subscriptionTier: string
  legalAddress: string | null
  primaryContact: string | null
  contactChannel: string | null
  region: string | null
  status: string
  createdAt: string
  userCount: number
  firstDispatcher: FirstDispatcher | null
}

export interface CreateFirstDispatcherBody {
  fullName: string
  login: string
  initialPassword: string
  contactChannel: string
}

export interface CreateOrganizationBody {
  name: string
  subscriptionTier: string
  legalAddress: string
  primaryContact: string
  contactChannel: string
  region: string
  firstDispatcher?: CreateFirstDispatcherBody
}

export const getHealth = () =>
  api.get<HealthResponse>('/api/health').then((r) => r.data)

export const getRoutes = () =>
  api.get<RouteOption[]>('/api/routes').then((r) => r.data)

export const getCheckpoints = () =>
  api.get<Checkpoint[]>('/api/checkpoints').then((r) => r.data)

export const getRequests = (organizationId?: string) =>
  api
    .get<CaravanRequest[]>('/api/requests', {
      params: organizationId ? { organizationId } : {},
    })
    .then((r) => r.data)

export const createRequest = (body: CreateRequestBody) =>
  api.post<CaravanRequest>('/api/requests', body).then((r) => r.data)

export const recalcRisk = (id: string) =>
  api.post<CaravanRequest>(`/api/requests/${id}/risk-score`).then((r) => r.data)

export const getRisk = (id: string) =>
  api.get<RiskAssessment>(`/api/requests/${id}/risk`).then((r) => r.data)

export const deleteRisk = (id: string) =>
  api.delete<CaravanRequest>(`/api/requests/${id}/risk`).then((r) => r.data)

export const getStatusInfo = (id: string) =>
  api.get<RequestStatusInfo>(`/api/requests/${id}/status`).then((r) => r.data)

export const getStatusHistory = (id: string) =>
  api.get<StatusHistoryEntry[]>(`/api/requests/${id}/status-history`).then((r) => r.data)

export const changeStatus = (id: string, body: ChangeStatusBody) =>
  api.post<CaravanRequest>(`/api/requests/${id}/status`, body).then((r) => r.data)

export const getRegistry = (organizationId: string, q: RegistryQuery = {}) =>
  api
    .get<TripRegistry>('/api/requests/registry', {
      params: { organizationId, ...q },
      paramsSerializer: { indexes: null },
    })
    .then((r) => r.data)

export const getOrganizations = () =>
  api.get<Organization[]>('/api/organizations').then((r) => r.data)

export const createOrganization = (body: CreateOrganizationBody) =>
  api.post<Organization>('/api/organizations', body).then((r) => r.data)
