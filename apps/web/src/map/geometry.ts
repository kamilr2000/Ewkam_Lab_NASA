import type { Geometry } from '../api/types'

export type LonLat = [number, number]
export type LinearRing = LonLat[]
export type PolygonCoordinates = LinearRing[]
export type MapGeometry =
  | { type: 'Polygon'; coordinates: PolygonCoordinates }
  | { type: 'MultiPolygon'; coordinates: PolygonCoordinates[] }

const EPSILON = 1e-9

function parseRing(value: unknown): LinearRing | null {
  if (!Array.isArray(value) || value.length < 4) return null
  const ring: LinearRing = []
  for (const position of value) {
    if (!Array.isArray(position) || position.length < 2) return null
    const longitude = Number(position[0])
    const latitude = Number(position[1])
    if (!Number.isFinite(longitude) || !Number.isFinite(latitude) || latitude < -90 || latitude > 90) return null
    ring.push([longitude, latitude])
  }
  const first = ring[0]
  const last = ring[ring.length - 1]
  if (Math.abs(first[0] - last[0]) > EPSILON || Math.abs(first[1] - last[1]) > EPSILON) ring.push([...first])
  return ring.length >= 4 ? ring : null
}

function parsePolygon(value: unknown): PolygonCoordinates | null {
  if (!Array.isArray(value) || value.length === 0) return null
  const rings = value.map(parseRing)
  if (rings.some((ring) => ring === null)) return null
  return rings as PolygonCoordinates
}

function wrapLongitude(longitude: number): number {
  const wrapped = ((longitude + 180) % 360 + 360) % 360 - 180
  return Math.abs(wrapped + 180) < EPSILON && longitude > 0 ? 180 : wrapped
}

function unwrapRing(ring: LinearRing, anchor?: number): LinearRing {
  const open = ring.slice(0, -1)
  if (open.length < 3) return ring
  const firstLongitude = wrapLongitude(open[0][0])
  const unwrapped: LinearRing = [[firstLongitude, open[0][1]]]
  for (const [rawLongitude, latitude] of open.slice(1)) {
    let longitude = wrapLongitude(rawLongitude)
    const previous = unwrapped[unwrapped.length - 1][0]
    while (longitude - previous > 180) longitude -= 360
    while (longitude - previous < -180) longitude += 360
    unwrapped.push([longitude, latitude])
  }
  if (anchor !== undefined) {
    const mean = unwrapped.reduce((sum, point) => sum + point[0], 0) / unwrapped.length
    const shift = 360 * Math.round((anchor - mean) / 360)
    for (const point of unwrapped) point[0] += shift
  }
  unwrapped.push([...unwrapped[0]])
  return unwrapped
}

function clipRing(ring: LinearRing, boundary: number, keepGreater: boolean): LinearRing {
  const points = ring.slice(0, -1)
  const clipped: LonLat[] = []
  if (points.length < 3) return []
  const inside = (point: LonLat) => keepGreater ? point[0] >= boundary - EPSILON : point[0] <= boundary + EPSILON
  const intersection = (start: LonLat, end: LonLat): LonLat => {
    const delta = end[0] - start[0]
    const t = Math.abs(delta) < EPSILON ? 0 : (boundary - start[0]) / delta
    return [boundary, start[1] + t * (end[1] - start[1])]
  }

  let previous = points[points.length - 1]
  for (const current of points) {
    const previousInside = inside(previous)
    const currentInside = inside(current)
    if (currentInside) {
      if (!previousInside) clipped.push(intersection(previous, current))
      clipped.push(current)
    } else if (previousInside) {
      clipped.push(intersection(previous, current))
    }
    previous = current
  }

  if (clipped.length < 3) return []
  const closed = [...clipped, [...clipped[0]] as LonLat]
  return closed
}

function clipToStrip(ring: LinearRing, west: number, east: number): LinearRing {
  return clipRing(clipRing(ring, west, true), east, false)
}

function ringMeanLongitude(ring: LinearRing): number {
  const points = ring.slice(0, -1)
  return points.reduce((sum, point) => sum + point[0], 0) / Math.max(points.length, 1)
}

function splitPolygon(rings: PolygonCoordinates): PolygonCoordinates[] {
  const outer = unwrapRing(rings[0])
  const outerLongitudes = outer.map((point) => point[0])
  const west = Math.min(...outerLongitudes)
  const east = Math.max(...outerLongitudes)
  const firstStrip = Math.floor((west + 180 + EPSILON) / 360)
  const lastStrip = Math.floor((east + 180 - EPSILON) / 360)
  const unwrappedRings = [outer, ...rings.slice(1).map((ring) => unwrapRing(ring, ringMeanLongitude(outer)))]
  const pieces: PolygonCoordinates[] = []

  for (let strip = firstStrip; strip <= lastStrip; strip += 1) {
    const stripWest = -180 + 360 * strip
    const stripEast = 180 + 360 * strip
    const clippedOuter = clipToStrip(unwrappedRings[0], stripWest, stripEast)
    if (clippedOuter.length < 4) continue
    const offset = 360 * strip
    const piece: PolygonCoordinates = [clippedOuter.map(([longitude, latitude]) => [wrapLongitude(longitude - offset), latitude])]

    for (const hole of unwrappedRings.slice(1)) {
      const clippedHole = clipToStrip(hole, stripWest, stripEast)
      if (clippedHole.length >= 4) {
        piece.push(clippedHole.map(([longitude, latitude]) => [wrapLongitude(longitude - offset), latitude]))
      }
    }
    pieces.push(piece)
  }
  return pieces
}

/** Convert valid WGS84 polygon geometry to RFC 7946 pieces at the antimeridian. */
export function splitGeometryAtAntimeridian(geometry: Geometry): MapGeometry | null {
  const polygons = geometry.type === 'Polygon'
    ? [parsePolygon(geometry.coordinates)]
    : geometry.type === 'MultiPolygon' && Array.isArray(geometry.coordinates)
      ? geometry.coordinates.map(parsePolygon)
      : []
  if (polygons.length === 0 || polygons.some((polygon) => polygon === null)) return null

  const pieces = polygons.flatMap((polygon) => splitPolygon(polygon as PolygonCoordinates))
  if (pieces.length === 0) return null
  if (geometry.type === 'Polygon' && pieces.length === 1) return { type: 'Polygon', coordinates: pieces[0] }
  return { type: 'MultiPolygon', coordinates: pieces }
}

export interface GeographicBounds {
  west: number
  south: number
  east: number
  north: number
}

/** Find the shortest longitude interval that contains all positions, including dateline crossings. */
export function boundsForCoordinates(coordinates: LonLat[]): GeographicBounds | null {
  if (coordinates.length === 0) return null
  const latitudes = coordinates.map((point) => point[1]).filter(Number.isFinite)
  const longitudes = coordinates.map((point) => ((point[0] % 360) + 360) % 360).sort((a, b) => a - b)
  if (latitudes.length === 0 || longitudes.length === 0) return null

  let largestGap = -1
  let gapIndex = 0
  for (let index = 0; index < longitudes.length; index += 1) {
    const next = index === longitudes.length - 1 ? longitudes[0] + 360 : longitudes[index + 1]
    const gap = next - longitudes[index]
    if (gap > largestGap) {
      largestGap = gap
      gapIndex = index
    }
  }

  const arcStart = longitudes[(gapIndex + 1) % longitudes.length]
  const span = 360 - largestGap
  const west = wrapLongitude(arcStart)
  const clampLatitude = (latitude: number) => Math.max(-89.5, Math.min(89.5, latitude))
  const south = clampLatitude(Math.min(...latitudes))
  const north = clampLatitude(Math.max(...latitudes))
  return { west, south, east: west + span, north }
}

