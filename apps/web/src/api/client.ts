import catalogFixture from '../../../../contracts/fixtures/catalog-synthetic.json'
import profileFixture from '../../../../contracts/fixtures/profile-synthetic.json'
import successFixture from '../../../../contracts/fixtures/search-success-synthetic.json'
import emptyFixture from '../../../../contracts/fixtures/search-empty-synthetic.json'
import noDataFixture from '../../../../contracts/fixtures/search-no-data-synthetic.json'
import hotspotFixture from '../../../../contracts/fixtures/search-hotspot-synthetic.json'
import distinctAreasFixture from '../../../../contracts/fixtures/search-distinct-areas-synthetic.json'
import unavailableFixture from '../../../../contracts/fixtures/error-dataset-unavailable-synthetic.json'
import mapHotspotFixture from '../../../../contracts/fixtures/map-hotspot-synthetic.json'
import pixelHotspotFixture from '../../../../contracts/fixtures/pixel-hotspot-synthetic.json'
import type {
  CatalogResponse,
  DataMode,
  DemoScenario,
  ErrorResponse,
  MapResponse,
  PixelDetailsResponse,
  ProfileResponse,
  SearchRequest,
  SearchResponse,
} from './types'

export const demoScenarios: Array<{ id: DemoScenario; label: string; description: string }> = [
  { id: 'success', label: 'Successful ranking', description: 'Two synthetic pixels with measured example values.' },
  { id: 'empty', label: 'Empty scope', description: 'No cells intersect the selected synthetic scope.' },
  { id: 'no-data', label: 'No eligible measurements', description: 'Cells exist, but active measurements are missing.' },
  { id: 'hotspot', label: 'Isolated hotspot', description: 'One excellent pixel inside a weaker display cell.' },
  { id: 'distinct-areas', label: 'Distinct areas', description: 'Separate representatives selected with an explicit distance.' },
  { id: 'dataset-unavailable', label: 'API error', description: 'A synthetic DATASET_UNAVAILABLE error response.' },
]

const searchFixtures: Record<Exclude<DemoScenario, 'dataset-unavailable'>, unknown> = {
  success: successFixture,
  empty: emptyFixture,
  'no-data': noDataFixture,
  hotspot: hotspotFixture,
  'distinct-areas': distinctAreasFixture,
}

export class ApiError extends Error {
  readonly payload: ErrorResponse | null
  readonly status: number | null

  constructor(message: string, payload: ErrorResponse | null = null, status: number | null = null) {
    super(message)
    this.name = 'ApiError'
    this.payload = payload
    this.status = status
  }
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function assertVersionedEnvelope(value: unknown, operation: string): asserts value is Record<string, unknown> {
  if (!isRecord(value) || value.contract_version !== '1.0.0' || typeof value.is_synthetic !== 'boolean') {
    throw new ApiError(`${operation} returned a payload that does not match contract 1.0.0.`)
  }
}

function parseCatalog(value: unknown): CatalogResponse {
  assertVersionedEnvelope(value, 'Catalog')
  if (!Array.isArray(value.datasets) || !Array.isArray(value.features) || !Array.isArray(value.profiles) || !Array.isArray(value.search_regions)) {
    throw new ApiError('Catalog response is missing datasets, features, profiles, or search regions.')
  }
  return value as unknown as CatalogResponse
}

function parseProfile(value: unknown, expectedProfileId: string): ProfileResponse {
  assertVersionedEnvelope(value, 'Profile')
  if (!isRecord(value.profile) || value.profile.profile_id !== expectedProfileId || !Array.isArray(value.profile.features)) {
    throw new ApiError(`Profile response did not contain the requested profile “${expectedProfileId}”.`)
  }
  return value as unknown as ProfileResponse
}

function parseSearch(value: unknown, expected?: SearchRequest): SearchResponse {
  assertVersionedEnvelope(value, 'Search')
  if (
    typeof value.analysis_id !== 'string' || value.analysis_id.length === 0 ||
    !isRecord(value.query) || !isRecord(value.coverage) ||
    !Array.isArray(value.map_cells) || !Array.isArray(value.warnings) ||
    (value.query.result_mode === 'pixels' && !Array.isArray(value.ranking)) ||
    (value.query.result_mode === 'distinct_areas' && !Array.isArray(value.area_ranking))
  ) {
    throw new ApiError('Search response is missing required contract fields or an analysis_id.')
  }
  if (value.query.result_mode !== 'pixels' && value.query.result_mode !== 'distinct_areas') {
    throw new ApiError('Search response has an unsupported result_mode.')
  }
  if (expected && (value.query.profile_id !== expected.profile_id || value.query.body !== expected.body || value.query.result_mode !== expected.result_mode)) {
    throw new ApiError('Search response does not match the requested profile, body, or result mode.')
  }
  const response = value as unknown as SearchResponse
  const rankedPixels = value.query.result_mode === 'pixels'
    ? value.ranking as Array<{ score_pct: number | null }>
    : (value.area_ranking as Array<{ representative_pixel: { score_pct: number | null } }>).map((entry) => entry.representative_pixel)
  if (rankedPixels.some((pixel) => pixel.score_pct !== null && (!Number.isFinite(pixel.score_pct) || pixel.score_pct < 0 || pixel.score_pct > 100))) {
    throw new ApiError('Search response includes a score outside the 0–100% range.')
  }
  return response
}

function parseError(value: unknown, status: number): ApiError {
  if (
    isRecord(value) && value.contract_version === '1.0.0' && typeof value.is_synthetic === 'boolean' &&
    typeof value.request_id === 'string' && isRecord(value.error) &&
    typeof value.error.code === 'string' && typeof value.error.message === 'string'
  ) {
    const payload = value as unknown as ErrorResponse
    return new ApiError(`${payload.error.code}: ${payload.error.message}`, payload, status)
  }
  return new ApiError(`The API returned HTTP ${status} without a valid contract 1.0.0 error payload.`, null, status)
}

function apiUrl(path: string): string {
  const base = import.meta.env.VITE_API_BASE_URL?.trim()
  if (!base) return path
  return new URL(path, base.endsWith('/') ? base : `${base}/`).toString()
}

async function requestJson(path: string, init: RequestInit = {}): Promise<unknown> {
  let response: Response
  try {
    response = await fetch(apiUrl(path), {
      ...init,
      headers: { Accept: 'application/json', ...init.headers },
    })
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') throw error
    throw new ApiError(error instanceof Error ? `API connection failed: ${error.message}` : 'API connection failed.')
  }

  let payload: unknown
  try {
    payload = await response.json()
  } catch {
    if (!response.ok) throw new ApiError(`The API returned HTTP ${response.status} with no JSON error response.`, null, response.status)
    throw new ApiError('The API returned a response that is not valid JSON.', null, response.status)
  }
  if (!response.ok) throw parseError(payload, response.status)
  return payload
}

export async function getCatalog(mode: DataMode, signal?: AbortSignal): Promise<CatalogResponse> {
  if (mode === 'synthetic') return parseCatalog(catalogFixture)
  return parseCatalog(await requestJson('/api/v1/catalog', { signal }))
}

export async function getProfile(mode: DataMode, profileId: string, signal?: AbortSignal): Promise<ProfileResponse> {
  if (mode === 'synthetic') return parseProfile(profileFixture, profileId)
  return parseProfile(await requestJson(`/api/v1/catalog/profiles/${encodeURIComponent(profileId)}`, { signal }), profileId)
}

export async function runSearch(
  mode: DataMode,
  request: SearchRequest,
  scenario: DemoScenario,
  signal?: AbortSignal,
): Promise<SearchResponse> {
  if (mode === 'synthetic') {
    if (scenario === 'dataset-unavailable') {
      const error = parseError(unavailableFixture, 503)
      throw new ApiError(error.message, unavailableFixture as ErrorResponse, 503)
    }
    return parseSearch(searchFixtures[scenario])
  }
  return parseSearch(await requestJson('/api/v1/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
    signal,
  }), request)
}

export async function getAnalysisMap(
  mode: DataMode,
  analysisId: string,
  bbox: [number, number, number, number],
  level: number,
  limit: number,
  signal?: AbortSignal,
): Promise<MapResponse> {
  const query = new URLSearchParams({ bbox: bbox.join(','), level: String(level), limit: String(limit) })
  const response: unknown = mode === 'synthetic'
    ? mapHotspotFixture
    : await requestJson(`/api/v1/analyses/${encodeURIComponent(analysisId)}/map?${query}`, { signal })
  assertVersionedEnvelope(response, 'Map')
  if (response.analysis_id !== analysisId || !Array.isArray(response.map_cells)) {
    throw new ApiError(`Map response does not belong to analysis “${analysisId}”.`)
  }
  if (mode === 'synthetic' && isRecord(response.query)) {
    const fixtureQuery = response.query
    if (
      !Array.isArray(fixtureQuery.bbox) || fixtureQuery.bbox.some((value, index) => value !== bbox[index]) ||
      fixtureQuery.level !== level || fixtureQuery.limit !== limit
    ) {
      throw new ApiError('The synthetic map fixture only represents its recorded bbox, level, and limit.')
    }
  }
  return response as unknown as MapResponse
}

export async function getPixelDetails(
  mode: DataMode,
  analysisId: string,
  pixelId: string,
  signal?: AbortSignal,
): Promise<PixelDetailsResponse> {
  const response: unknown = mode === 'synthetic'
    ? pixelHotspotFixture
    : await requestJson(`/api/v1/analyses/${encodeURIComponent(analysisId)}/pixels/${encodeURIComponent(pixelId)}`, { signal })
  assertVersionedEnvelope(response, 'Pixel details')
  if (response.analysis_id !== analysisId || !isRecord(response.pixel) || response.pixel.pixel_id !== pixelId) {
    throw new ApiError(`Pixel details do not match analysis “${analysisId}” and pixel “${pixelId}”.`)
  }
  return response as unknown as PixelDetailsResponse
}
