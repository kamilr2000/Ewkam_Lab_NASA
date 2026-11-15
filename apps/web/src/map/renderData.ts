import type { GeoJSONSource } from 'maplibre-gl'
import type { Geometry, SearchMapCell } from '../api/types'
import { splitGeometryAtAntimeridian, type LonLat, type MapGeometry } from './geometry'

export type MapFeature<G = MapGeometry | { type: 'Point'; coordinates: LonLat }> = {
  type: 'Feature'
  id?: string | number
  geometry: G
  properties: Record<string, unknown>
}

export type FeatureCollection<G = MapGeometry | { type: 'Point'; coordinates: LonLat }> = {
  type: 'FeatureCollection'
  features: Array<MapFeature<G>>
}

type CellProperties = {
  cell_id: string
  score: number | null
  mean: number | null
  max_pixel_id: string | null
  valid_pixel_count: number
  total_pixel_count: number
  coverage_fraction: number
  missing_reason: string | null
}

export type CellCollectionResult = {
  collection: FeatureCollection
  invalidCount: number
}

export function makeCellCollection(cells: SearchMapCell[]): CellCollectionResult {
  let invalidCount = 0
  const features = cells.flatMap((cell) => {
    const geometry = splitGeometryAtAntimeridian(cell.geometry)
    if (!geometry) {
      invalidCount += 1
      return []
    }
    const properties: CellProperties = {
      cell_id: cell.cell_id,
      score: cell.max_score_pct,
      mean: cell.mean_score_pct,
      max_pixel_id: cell.max_pixel_id,
      valid_pixel_count: cell.valid_pixel_count,
      total_pixel_count: cell.total_pixel_count,
      coverage_fraction: cell.coverage_fraction,
      missing_reason: cell.missing_reason,
    }
    return [{ type: 'Feature' as const, id: cell.cell_id, geometry, properties }]
  })
  return { collection: { type: 'FeatureCollection', features }, invalidCount }
}

/** Pass the GeoJSON FeatureCollection itself to MapLibre, never its QA wrapper. */
export function applyCellCollectionData(
  source: Pick<GeoJSONSource, 'setData'>,
  result: CellCollectionResult,
): void {
  source.setData(result.collection as never)
}

export function formatMapContextLabel(
  scopeType: 'global' | 'regional',
  cellCount: number,
  isSynthetic = false,
): string {
  const cellLabel = cellCount === 1 ? 'CELL' : 'CELLS'
  if (scopeType === 'global' && isSynthetic) {
    return 'SYNTHETIC TEST FIXTURE · ' + cellCount + ' TEST ' + cellLabel
  }
  const scopeLabel = scopeType.toUpperCase()
  return scopeLabel + ' ANALYSIS · ' + cellCount + ' ' + scopeLabel + ' DISPLAY ' + cellLabel
}

export function makeGeometryCollection(geometry: Geometry | null | undefined): FeatureCollection {
  const normalized = geometry ? splitGeometryAtAntimeridian(geometry) : null
  return normalized
    ? { type: 'FeatureCollection', features: [{ type: 'Feature', geometry: normalized, properties: {} }] }
    : { type: 'FeatureCollection', features: [] }
}
