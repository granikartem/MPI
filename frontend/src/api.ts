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

export const getOrganizations = () =>
  api.get<Organization[]>('/api/organizations').then((r) => r.data)

export const createOrganization = (body: CreateOrganizationBody) =>
  api.post<Organization>('/api/organizations', body).then((r) => r.data)
