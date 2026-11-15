export type PlanetaryBody = 'mars' | 'moon'
export type ResultMode = 'pixels' | 'distinct_areas'
export type MeasurementScale = 'ratio' | 'interval' | 'ordinal' | 'nominal'
export type DataMode = 'synthetic' | 'live'
export type DemoScenario = 'success' | 'empty' | 'no-data' | 'hotspot' | 'distinct-areas' | 'dataset-unavailable'
export type CatalogDatasetRole = 'earth_search' | 'planetary_reference' | 'validation' | 'fixture_only'

export interface CatalogFeature {
  feature_id: string
  name: string
  description: string
  unit: string
  measurement_scale: MeasurementScale
  domain_id: string
  domain_label: string
  availability: 'available' | 'planned' | 'unavailable' | 'synthetic_only'
  is_proxy: boolean
  proxy_description: string | null
  source_ids: string[]
}

export interface CatalogProfile {
  profile_id: string
  name: string
  body: PlanetaryBody
  region_name: string
  profile_version: string
  availability: 'available' | 'planned' | 'unavailable' | 'synthetic_only'
  feature_ids: string[]
  source_ids: string[]
}

export interface CatalogDataset {
  dataset_version: string
  role: CatalogDatasetRole
  body: 'earth'
  grid_version: string
  model_version: string
  availability: 'available' | 'planned' | 'unavailable' | 'synthetic_only'
  coverage_description: string
  manifest_path: string | null
}

export interface SearchRegion {
  region_id: string
  name: string
  dataset_version: string
  availability: 'available' | 'planned' | 'unavailable' | 'synthetic_only'
  geometry: Geometry
  mask_id: string | null
  description: string
}

export interface CatalogResponse {
  contract_version: '1.0.0'
  catalog_version: string
  generated_at: string
  is_synthetic: boolean
  datasets: CatalogDataset[]
  features: CatalogFeature[]
  profiles: CatalogProfile[]
  search_regions: SearchRegion[]
  warnings: Array<{ code: string; message: string }>
  limitations: string[]
}

export interface Geometry {
  type: 'Polygon' | 'MultiPolygon'
  coordinates: unknown[]
}

export interface SearchRequest {
  contract_version: '1.0.0'
  body: PlanetaryBody
  profile_id: string
  dataset_version: string
  scope: { type: 'global' } | { type: 'regional'; region_id: string }
  criteria: Array<{ feature_id: string; weight: number }>
  result_mode: ResultMode
  top_k: number
  min_distance_km?: number
}

export interface ProfileFeature {
  feature_id: string
  name: string
  description: string
  unit: string
  measurement_scale: MeasurementScale
  reference_interval: [number, number]
  tolerance: {
    value: number
    unit: string
    basis: 'physical' | 'measurement' | 'assumption'
    rationale: string
    source_ids: string[]
  }
  spatial_support: {
    source_resolution_m: number | null
    analysis_cell_resolution_m: number | null
    window_radius_m: number | null
    description: string
    missing_reason: string | null
  }
  is_proxy: boolean
  proxy_description: string | null
  source_ids: string[]
  limitations: string[]
}

export interface ProfileResponse {
  contract_version: '1.0.0'
  is_synthetic: boolean
  profile: {
    profile_id: string
    name: string
    body: PlanetaryBody
    profile_version: string
    region: {
      region_id: string
      name: string
      geometry: Geometry | null
      geometry_missing_reason: string | null
      coordinate_system: {
        coordinate_system_id: string
        body: PlanetaryBody
        name: string
        longitude_direction: 'east' | 'west' | 'not_applicable'
        longitude_domain: '-180_180' | '0_360' | 'not_applicable'
        latitude_type: string
        vertical_reference: string | null
        vertical_reference_missing_reason: string | null
      }
    }
    features: ProfileFeature[]
    source_ids: string[]
    limitations: string[]
  }
}

export interface SearchFeatureResult {
  feature_id: string
  value: number | null
  unit: string
  measurement_scale: MeasurementScale
  similarity_pct: number | null
  normalized_weight: number
  contribution_pct: number | null
  reference_interval: [number, number]
  tolerance: number
  source_ids: string[]
  quality_flags?: string[]
  missing_reason?: string | null
}

export interface SearchPixel {
  rank?: number
  pixel_id: string
  score_pct: number | null
  center: [number, number]
  geometry: Geometry
  pixel_area_km2: number
  coverage_fraction: number
  quality_flags: string[]
  missing_reasons?: string[]
  features: SearchFeatureResult[]
}

export interface SearchMapCell {
  cell_id: string
  level: number
  geometry: Geometry
  max_score_pct: number | null
  mean_score_pct: number | null
  max_pixel_id: string | null
  valid_pixel_count: number
  total_pixel_count: number
  coverage_fraction: number
  missing_reason: string | null
}

export interface SearchQuery {
  body: PlanetaryBody
  profile_id: string
  criteria: Array<{ feature_id: string; weight: number; normalized_weight: number }>
  scope: { type: 'global' } | { type: 'regional'; region_id: string }
  result_mode: ResultMode
  top_k: number
  min_distance_km: number | null
  area_selection_rule: string
}

interface SearchResponseBase {
  contract_version: '1.0.0'
  dataset_version: string
  grid_version: string
  model_version: string
  profile_version: string
  analysis_id: string
  is_synthetic: boolean
  query: SearchQuery
  elapsed_ms: number
  scope: {
    type: 'global' | 'regional'
    region_id: string | null
    region_name: string | null
    geometry: Geometry | null
    mask_id: string | null
    grid_version: string
    description: string
  }
  coverage: {
    total_pixels: number
    eligible_pixels: number
    excluded_by_reason: Record<string, number>
    total_area_km2: number
    eligible_area_km2: number
    eligible_area_fraction: number | null
    no_data_reason: string | null
  }
  map_cells: SearchMapCell[]
  warnings: Array<{ code: string; message: string }>
}

export type SearchResponse = SearchResponseBase & (
  | {
      query: SearchQuery & { result_mode: 'pixels' }
      ranking: SearchPixel[]
      area_ranking?: never
    }
  | {
      query: SearchQuery & { result_mode: 'distinct_areas' }
      area_ranking: Array<{
        rank: number
        candidate_id: string
        representative_pixel: SearchPixel
        nearest_selected_distance_km: number | null
      }>
      ranking?: never
    }
)

export interface PixelDetailsResponse {
  contract_version: '1.0.0'
  dataset_version: string
  grid_version: string
  model_version: string
  profile_version: string
  analysis_id: string
  is_synthetic: boolean
  result_mode: ResultMode
  pixel: SearchPixel
}

export interface MapResponse {
  contract_version: '1.0.0'
  dataset_version: string
  grid_version: string
  model_version: string
  profile_version: string
  analysis_id: string
  is_synthetic: boolean
  query: { bbox: [number, number, number, number]; level: number; limit: number }
  map_cells: SearchMapCell[]
  next_cursor: string | null
}

export interface ErrorResponse {
  contract_version: '1.0.0'
  is_synthetic: boolean
  request_id: string
  error: {
    code: string
    message: string
    details?: Record<string, unknown>
  }
}
