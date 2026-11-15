import type {
  CatalogDataset,
  CatalogResponse,
  DataMode,
  ProfileFeature,
  ProfileResponse,
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

/** Select only the dataset role intended for this mode; never rely on catalog ordering. */
export function selectDatasetForMode(mode: DataMode, catalog: CatalogResponse): CatalogDataset {
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
  if (candidates.length > 1) {
    throw new Error(`The ${mode} catalog contains multiple ${role} Earth datasets; selection is ambiguous.`)
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

/** Build the versioned global Earth request from selected features; map display visibility is not scoring state. */
export function buildSearchRequest(
  profile: ProfileResponse['profile'],
  datasetVersion: string,
  features: readonly ProfileFeature[],
  settings: CriteriaSettings,
): SearchRequest {
  if (!datasetVersion.trim()) throw new Error('An Earth dataset version is required.')
  if (!profile.profile_id.trim()) throw new Error('A reference profile is required.')

  const validationError = getCriteriaValidationError(features, settings)
  if (validationError) throw new Error(validationError)

  const criteria = getActiveCriteria(features, settings).map(({ feature, weight }) => ({
    feature_id: feature.feature_id,
    weight,
  }))

  return {
    contract_version: '1.0.0',
    body: profile.body,
    profile_id: profile.profile_id,
    dataset_version: datasetVersion,
    scope: { type: 'global' },
    criteria,
    result_mode: 'pixels',
    top_k: 10,
  }
}
