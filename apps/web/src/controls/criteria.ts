import type {
  CatalogDataset,
  CatalogResponse,
  DataMode,
  ProfileFeature,
  ProfileResponse,
  ResultMode,
  SearchRegion,
  SearchRequest,
} from '../api/types'

export const MIN_CRITERION_WEIGHT = 0.1
export const MAX_CRITERION_WEIGHT = 10
export const CRITERION_WEIGHT_STEP = 0.1
export const MAX_ACTIVE_CRITERIA = 16

export interface CriterionSetting {
  enabled: boolean
  weight: number
}

export type CriteriaSettings = Record<string, CriterionSetting>

export interface ActiveCriterion {
  feature: ProfileFeature
  weight: number
  normalizedWeight: number | null
}

function expectedAvailability(mode: DataMode): 'available' | 'synthetic_only' {
  return mode === 'synthetic' ? 'synthetic_only' : 'available'
}

/** Return only catalog regions backed by the dataset role used in this mode. */
export function getAvailableSearchRegions(mode: DataMode, catalog: CatalogResponse): SearchRegion[] {
  const role = mode === 'synthetic' ? 'fixture_only' : 'earth_search'
  const availability = expectedAvailability(mode)
  const datasetVersions = new Set(catalog.datasets
    .filter((dataset) => dataset.body === 'earth' && dataset.role === role && dataset.availability === availability)
    .map((dataset) => dataset.dataset_version))
  return catalog.search_regions.filter((region) =>
    region.availability === availability && datasetVersions.has(region.dataset_version),
  )
}

/** Select the immutable dataset mapped to an explicitly chosen live region. */
export function selectDatasetForMode(mode: DataMode, catalog: CatalogResponse, regionId?: string): CatalogDataset {
  const role = mode === 'synthetic' ? 'fixture_only' : 'earth_search'
  const availability = expectedAvailability(mode)
  const candidates = catalog.datasets.filter((dataset) =>
    dataset.body === 'earth' && dataset.role === role && dataset.availability === availability,
  )

  if (candidates.length === 0) {
    throw new Error(mode === 'synthetic'
      ? 'The synthetic catalog does not include a fixture-only Earth dataset.'
      : 'No available Earth search dataset is listed in the live catalog.')
  }

  if (mode === 'live') {
    if (!regionId) throw new Error('Choose an available Earth search region from the live catalog.')
    const regions = catalog.search_regions.filter((region) =>
      region.region_id === regionId && region.availability === availability,
    )
    if (regions.length !== 1) {
      throw new Error('The selected Earth search region is missing or ambiguous in the live catalog.')
    }
    const regionalDatasets = candidates.filter((dataset) => dataset.dataset_version === regions[0].dataset_version)
    if (regionalDatasets.length !== 1) {
      throw new Error('The selected Earth region does not map to exactly one available search dataset.')
    }
    return regionalDatasets[0]
  }

  if (candidates.length > 1) {
    throw new Error('The synthetic catalog contains multiple fixture-only Earth datasets; selection is ambiguous.')
  }
  return candidates[0]
}

function findDuplicate(values: readonly string[]): string | null {
  const seen = new Set<string>()
  for (const value of values) {
    if (seen.has(value)) return value
    seen.add(value)
  }
  return null
}

/** Return profile measurements that are both declared by the catalog and selectable in this mode. */
export function getAvailableProfileFeatures(
  mode: DataMode,
  catalog: CatalogResponse,
  profile: ProfileResponse,
): ProfileFeature[] {
  const expected = expectedAvailability(mode)
  const profileEntry = catalog.profiles.find((item) =>
    item.profile_id === profile.profile.profile_id &&
    item.body === profile.profile.body &&
    item.availability === expected,
  )
  if (!profileEntry) {
    throw new Error('The selected profile is not available in the current catalog.')
  }

  const duplicateProfileFeature = findDuplicate(profile.profile.features.map((feature) => feature.feature_id))
  if (duplicateProfileFeature) {
    throw new Error(`The profile lists feature “${duplicateProfileFeature}” more than once.`)
  }
  const duplicateCatalogFeature = findDuplicate(profileEntry.feature_ids)
  if (duplicateCatalogFeature) {
    throw new Error(`The catalog lists feature “${duplicateCatalogFeature}” more than once for this profile.`)
  }

  const profileFeatureIds = new Set(profileEntry.feature_ids)
  const selectableCatalogIds = new Set(catalog.features
    .filter((feature) => feature.availability === expected)
    .map((feature) => feature.feature_id))

  return profile.profile.features.filter((feature) =>
    profileFeatureIds.has(feature.feature_id) && selectableCatalogIds.has(feature.feature_id),
  )
}

export function createInitialCriteriaSettings(features: readonly ProfileFeature[]): CriteriaSettings {
  return Object.fromEntries(features.map((feature) => [feature.feature_id, { enabled: true, weight: 1 }]))
}

export function setCriterionEnabled(
  settings: CriteriaSettings,
  featureId: string,
  enabled: boolean,
): CriteriaSettings {
  const current = settings[featureId] ?? { enabled: false, weight: 1 }
  return { ...settings, [featureId]: { ...current, enabled } }
}

export function setCriterionWeight(
  settings: CriteriaSettings,
  featureId: string,
  weight: number,
): CriteriaSettings {
  const current = settings[featureId] ?? { enabled: false, weight: 1 }
  return { ...settings, [featureId]: { ...current, weight } }
}

export function getCriteriaValidationError(
  features: readonly ProfileFeature[],
  settings: CriteriaSettings,
): string | null {
  const active = features.filter((feature) => settings[feature.feature_id]?.enabled)
  if (active.length === 0) return 'Select at least one available measurement before running an analysis.'
  if (active.length > MAX_ACTIVE_CRITERIA) return `Select no more than ${MAX_ACTIVE_CRITERIA} measurements.`

  const ids = active.map((feature) => feature.feature_id)
  const duplicateId = findDuplicate(ids)
  if (duplicateId) return `The selected profile contains duplicate feature “${duplicateId}”.`

  const invalidWeight = active.find((feature) => {
    const weight = settings[feature.feature_id]?.weight
    return typeof weight !== 'number' || !Number.isFinite(weight) || weight <= 0 || weight > 1_000_000
  })
  if (invalidWeight) return `Enter a finite positive weight for ${invalidWeight.name}.`
  return null
}

export function getActiveCriteria(
  features: readonly ProfileFeature[],
  settings: CriteriaSettings,
): ActiveCriterion[] {
  const active = features
    .filter((feature) => settings[feature.feature_id]?.enabled)
    .map((feature) => ({ feature, weight: settings[feature.feature_id]?.weight ?? Number.NaN }))
  const totalWeight = active.reduce((total, criterion) => total + criterion.weight, 0)
  const hasValidTotal = Number.isFinite(totalWeight) && totalWeight > 0
  return active.map((criterion) => ({
    ...criterion,
    normalizedWeight: hasValidTotal && Number.isFinite(criterion.weight) && criterion.weight > 0
      ? criterion.weight / totalWeight
      : null,
  }))
}

export const MAX_AREA_DISTANCE_KM = 10_000

export interface SearchRequestOptions {
  scope?: SearchRequest['scope']
  resultMode?: ResultMode
  minDistanceKm?: number
}

/** Build a versioned request from the chosen profile, criteria, and declared search scope. */
export function buildSearchRequest(
  profile: ProfileResponse['profile'],
  datasetVersion: string,
  features: readonly ProfileFeature[],
  settings: CriteriaSettings,
  options: SearchRequestOptions = {},
): SearchRequest {
  if (!datasetVersion.trim()) throw new Error('An Earth dataset version is required.')
  if (!profile.profile_id.trim()) throw new Error('A reference profile is required.')

  const validationError = getCriteriaValidationError(features, settings)
  if (validationError) throw new Error(validationError)

  const resultMode = options.resultMode ?? 'pixels'
  if (resultMode === 'distinct_areas') {
    const distance = options.minDistanceKm
    if (typeof distance !== 'number' || !Number.isFinite(distance) || distance <= 0 || distance > MAX_AREA_DISTANCE_KM) {
      throw new Error('Enter a minimum distance greater than 0 and no more than 10,000 km for distinct areas.')
    }
  } else if (options.minDistanceKm !== undefined) {
    throw new Error('A minimum distance can only be set for distinct areas.')
  }

  const scope = options.scope ?? { type: 'global' as const }
  if (scope.type === 'regional' && !scope.region_id.trim()) {
    throw new Error('An Earth region is required for a regional search.')
  }
  const criteria = getActiveCriteria(features, settings).map(({ feature, weight }) => ({
    feature_id: feature.feature_id,
    weight,
  }))

  const request: SearchRequest = {
    contract_version: '1.0.0',
    body: profile.body,
    profile_id: profile.profile_id,
    dataset_version: datasetVersion,
    scope,
    criteria,
    result_mode: resultMode,
    top_k: 10,
  }
  if (resultMode === 'distinct_areas') request.min_distance_km = options.minDistanceKm
  return request
}
