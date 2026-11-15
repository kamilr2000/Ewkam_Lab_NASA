import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { Map as MapLibreMap, Marker, setWorkerUrl, type GeoJSONSource, type LngLatBounds, type StyleSpecification } from 'maplibre-gl'
import maplibreWorkerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url'
import { getAnalysisMap } from '../api/client'
import type { DataMode, Geometry, SearchMapCell, SearchPixel, SearchResponse } from '../api/types'
import { boundsForCoordinates, splitGeometryAtAntimeridian, type GeographicBounds, type LonLat, type MapGeometry } from './geometry'

const EMPTY_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: 'background', type: 'background', paint: { 'background-color': '#10191b' } }],
  projection: { type: 'globe' },
}

setWorkerUrl(maplibreWorkerUrl)

const EMPTY_COLLECTION = { type: 'FeatureCollection', features: [] } as const
const MAX_VIEWPORT_CELLS = 1000

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

type MapFeature<G = MapGeometry | { type: 'Point'; coordinates: LonLat }> = {
  type: 'Feature'
  id?: string | number
  geometry: G
  properties: Record<string, unknown>
}
type FeatureCollection<G = MapGeometry | { type: 'Point'; coordinates: LonLat }> = { type: 'FeatureCollection'; features: Array<MapFeature<G>> }

function formatNumber(value: number | null, maximumFractionDigits = 2): string {
  if (value === null || !Number.isFinite(value)) return 'Not available'
  return value.toLocaleString('en-US', { maximumFractionDigits })
}

function getCoordinates(geometry: MapGeometry): LonLat[] {
  const coordinates: LonLat[] = []
  const visit = (value: unknown): void => {
    if (!Array.isArray(value)) return
    if (value.length >= 2 && typeof value[0] === 'number' && typeof value[1] === 'number') {
      coordinates.push([value[0], value[1]])
      return
    }
    value.forEach(visit)
  }
  visit(geometry.coordinates)
  return coordinates
}

function boundsForGeometry(geometry: Geometry | null | undefined): GeographicBounds | null {
  if (!geometry) return null
  const normalized = splitGeometryAtAntimeridian(geometry)
  return normalized ? boundsForCoordinates(getCoordinates(normalized)) : null
}

function boundsForCells(cells: SearchMapCell[]): GeographicBounds | null {
  const coordinates = cells.flatMap((cell) => {
    const geometry = splitGeometryAtAntimeridian(cell.geometry)
    return geometry ? getCoordinates(geometry) : []
  })
  return boundsForCoordinates(coordinates)
}

function boundsForPixel(pixel: SearchPixel | null): GeographicBounds | null {
  return pixel ? boundsForGeometry(pixel.geometry) : null
}

function makeCellCollection(cells: SearchMapCell[]): { collection: FeatureCollection; invalidCount: number } {
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

function makeGeometryCollection(geometry: Geometry | null | undefined): FeatureCollection {
  const normalized = geometry ? splitGeometryAtAntimeridian(geometry) : null
  return normalized
    ? { type: 'FeatureCollection', features: [{ type: 'Feature', geometry: normalized, properties: {} }] }
    : { type: 'FeatureCollection', features: [] }
}

function makeGraticule(): FeatureCollection<{ type: 'LineString'; coordinates: LonLat[] }> {
  const features: Array<MapFeature<{ type: 'LineString'; coordinates: LonLat[] }>> = []
  for (let longitude = -180; longitude < 180; longitude += 30) {
    const coordinates: LonLat[] = []
    for (let latitude = -88; latitude <= 88; latitude += 4) coordinates.push([longitude, latitude])
    features.push({ type: 'Feature', geometry: { type: 'LineString', coordinates }, properties: { kind: 'meridian' } })
  }
  for (let latitude = -60; latitude <= 60; latitude += 30) {
    const coordinates: LonLat[] = []
    for (let longitude = -180; longitude <= 180; longitude += 4) coordinates.push([longitude, latitude])
    features.push({ type: 'Feature', geometry: { type: 'LineString', coordinates }, properties: { kind: latitude === 0 ? 'equator' : 'parallel' } })
  }
  return { type: 'FeatureCollection', features }
}

function splitViewportBounds(bounds: LngLatBounds): Array<[number, number, number, number]> {
  let south = Math.max(-90, bounds.getSouth())
  let north = Math.min(90, bounds.getNorth())
  if (north - south < 1e-5) {
    if (north >= 90) south = 89.999
    else north = Math.min(90, south + 1e-5)
  }
  const rawWest = bounds.getWest()
  const rawEast = bounds.getEast()
  if (rawEast - rawWest >= 359.999) return [[-180, south, 180, north]]

  const west = ((rawWest + 180) % 360 + 360) % 360 - 180
  const east = west + (rawEast - rawWest)
  if (east <= 180) return [[west, south, east, north]]
  return [[west, south, 180, north], [-180, south, east - 360, north]]
}

function fitMapToBounds(map: MapLibreMap, bounds: GeographicBounds | null, maxZoom: number): void {
  if (!bounds) {
    map.easeTo({ center: [0, 0], zoom: 0.7, duration: 500 })
    return
  }
  const longitudeSpan = Math.max(0, bounds.east - bounds.west)
  if (longitudeSpan > 350) {
    map.easeTo({ center: [0, 0], zoom: 0.7, duration: 500 })
    return
  }
  const minimumSpan = 0.005
  const west = bounds.west - Math.max(0, minimumSpan - longitudeSpan) / 2
  const east = bounds.east + Math.max(0, minimumSpan - longitudeSpan) / 2
  const south = Math.max(-89.5, Math.min(bounds.south, bounds.north - minimumSpan / 2))
  const north = Math.min(89.5, Math.max(bounds.north, bounds.south + minimumSpan / 2))
  map.fitBounds([[west, south], [east, north]], {
    padding: { top: 86, right: 45, bottom: 148, left: 45 },
    maxZoom,
    duration: 650,
  })
}

interface AnalysisMapProps {
  analysis: SearchResponse | null
  mode: DataMode
  pixels: SearchPixel[]
  selectedPixel: SearchPixel | null
  selectedPixelId: string | null
  zoomRequest: number
  emptyMessage: string
  searchError: string | null
  onSelectPixel: (pixelId: string) => void
  onRetry: () => void
}

export default function AnalysisMap({ analysis, mode, pixels, selectedPixel, selectedPixelId, zoomRequest, emptyMessage, searchError, onSelectPixel, onRetry }: AnalysisMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null)
  const mapRef = useRef<MapLibreMap | null>(null)
  const modeRef = useRef(mode)
  const analysisRef = useRef(analysis)
  const cellsRef = useRef(new Map<string, SearchMapCell>())
  const pixelsRef = useRef(new Map(pixels.map((pixel) => [pixel.pixel_id, pixel])))
  const markersRef = useRef(new Map<string, Marker>())
  const onSelectPixelRef = useRef(onSelectPixel)
  const requestRef = useRef<AbortController | null>(null)
  const requestEpochRef = useRef(0)
  const debounceRef = useRef<number | null>(null)
  const firstFitRef = useRef<string | null>(null)
  const lastZoomRequestRef = useRef(0)
  const [mapReady, setMapReady] = useState(false)
  const [viewportCells, setViewportCells] = useState<SearchMapCell[] | null>(null)
  const [mapError, setMapError] = useState<string | null>(null)
  const [mapLoading, setMapLoading] = useState(false)
  const [rendererError, setRendererError] = useState<string | null>(null)
  const [selectedCellId, setSelectedCellId] = useState<string | null>(null)

  modeRef.current = mode
  analysisRef.current = analysis
  onSelectPixelRef.current = onSelectPixel
  pixelsRef.current = new Map(pixels.map((pixel) => [pixel.pixel_id, pixel]))

  const displayCells = viewportCells ?? analysis?.map_cells ?? []
  const collection = useMemo(() => makeCellCollection(displayCells), [displayCells])
  const selectionCollection = useMemo(() => makeGeometryCollection(selectedPixel?.geometry), [selectedPixel])
  const scopeCollection = useMemo(() => makeGeometryCollection(analysis?.scope.geometry), [analysis?.scope.geometry])
  const cellsById = useMemo(() => new Map(displayCells.map((cell) => [cell.cell_id, cell])), [displayCells])
  const selectedCell = selectedCellId ? cellsById.get(selectedCellId) ?? null : null
  cellsRef.current = cellsById

  const fitResults = useCallback(() => {
    const map = mapRef.current
    const currentAnalysis = analysisRef.current
    if (!map || !currentAnalysis) return
    const bounds = boundsForGeometry(currentAnalysis.scope.geometry) ?? boundsForCells(currentAnalysis.map_cells)
    fitMapToBounds(map, bounds, 9)
  }, [])

  const refreshViewport = useCallback(() => {
    const map = mapRef.current
    const currentAnalysis = analysisRef.current
    if (!map || !currentAnalysis || modeRef.current !== 'live') return
    const bboxes = splitViewportBounds(map.getBounds())
    if (bboxes.length === 0 || bboxes.some((bbox) => bbox[0] >= bbox[2] || bbox[1] >= bbox[3])) return
    const level = Math.max(0, Math.min(30, Math.floor(map.getZoom())))
    const limit = Math.max(1, Math.floor(MAX_VIEWPORT_CELLS / bboxes.length))
    const epoch = ++requestEpochRef.current
    requestRef.current?.abort()
    const controller = new AbortController()
    requestRef.current = controller
    setMapLoading(true)
    setMapError(null)

    void Promise.all(bboxes.map((bbox) => getAnalysisMap('live', currentAnalysis.analysis_id, bbox, level, limit, controller.signal)))
      .then((responses) => {
        if (epoch !== requestEpochRef.current || controller.signal.aborted) return
        const cells = new Map<string, SearchMapCell>()
        responses.forEach((response) => response.map_cells.forEach((cell) => cells.set(cell.cell_id, cell)))
        setViewportCells([...cells.values()])
      })
      .catch((error: unknown) => {
        if (epoch !== requestEpochRef.current || (error instanceof DOMException && error.name === 'AbortError')) return
        setMapError(error instanceof Error ? error.message : 'Map cells for this view could not be loaded.')
      })
      .finally(() => {
        if (epoch === requestEpochRef.current) setMapLoading(false)
      })
  }, [])

  useEffect(() => {
    const container = containerRef.current
    if (!container) return
    let map: MapLibreMap
    try {
      map = new MapLibreMap({
        container,
        style: EMPTY_STYLE,
        center: [0, 0],
        zoom: 0.7,
        minZoom: 0,
        maxZoom: 18,
        attributionControl: false,
        dragRotate: false,
        pitchWithRotate: false,
        renderWorldCopies: true,
        canvasContextAttributes: { antialias: true },
      })
    } catch (error) {
      setRendererError(error instanceof Error ? error.message : 'WebGL map renderer could not be initialized.')
      return
    }

    mapRef.current = map
    map.on('load', () => {
      map.setProjection({ type: 'globe' })
      map.addSource('graticule', { type: 'geojson', data: makeGraticule() as never })
      map.addSource('analysis-cells', { type: 'geojson', data: EMPTY_COLLECTION as never })
      map.addSource('selected-pixel', { type: 'geojson', data: EMPTY_COLLECTION as never })
      map.addSource('analysis-scope', { type: 'geojson', data: EMPTY_COLLECTION as never })
      map.addLayer({
        id: 'graticule-lines', type: 'line', source: 'graticule',
        paint: { 'line-color': '#729087', 'line-opacity': 0.28, 'line-width': 0.6 },
      })
      map.addLayer({
        id: 'analysis-cells-fill', type: 'fill', source: 'analysis-cells',
        paint: {
          'fill-color': ['case', ['==', ['get', 'score'], null], '#7c8585', ['interpolate', ['linear'], ['to-number', ['get', 'score']], 0, '#3b528b', 25, '#21918c', 50, '#5ec962', 75, '#b9de4f', 100, '#fde725']],
          'fill-opacity': 0.83,
        },
      })
      map.addLayer({
        id: 'analysis-cells-outline', type: 'line', source: 'analysis-cells',
        paint: { 'line-color': '#13201e', 'line-opacity': 0.82, 'line-width': 1.15 },
      })
      map.addLayer({
        id: 'analysis-scope-outline', type: 'line', source: 'analysis-scope',
        paint: { 'line-color': '#d0d9be', 'line-opacity': 0.72, 'line-width': 1.2, 'line-dasharray': [2, 2] },
      })
      map.addLayer({
        id: 'selected-pixel-fill', type: 'fill', source: 'selected-pixel',
        paint: { 'fill-color': '#f8f2c2', 'fill-opacity': 0.12 },
      })
      map.addLayer({
        id: 'selected-pixel-outline', type: 'line', source: 'selected-pixel',
        paint: { 'line-color': '#fff2ab', 'line-width': 2.4, 'line-opacity': 1 },
      })
      map.on('click', 'analysis-cells-fill', (event) => {
        const cellId = event.features?.[0]?.properties?.cell_id
        if (typeof cellId !== 'string') return
        const cell = cellsRef.current.get(cellId)
        if (!cell) return
        setSelectedCellId(cell.cell_id)
        fitMapToBounds(map, boundsForGeometry(cell.geometry), 12)
      })
      map.on('mouseenter', 'analysis-cells-fill', () => { map.getCanvas().style.cursor = 'pointer' })
      map.on('mouseleave', 'analysis-cells-fill', () => { map.getCanvas().style.cursor = '' })
      map.on('moveend', () => {
        if (debounceRef.current !== null) window.clearTimeout(debounceRef.current)
        debounceRef.current = window.setTimeout(refreshViewport, 240)
      })
      setMapReady(true)
    })
    map.on('error', (event) => {
      if (!map.isStyleLoaded()) setRendererError(event.error.message || 'Map style could not be loaded.')
    })

    return () => {
      if (debounceRef.current !== null) window.clearTimeout(debounceRef.current)
      requestRef.current?.abort()
      markersRef.current.forEach((marker) => marker.remove())
      markersRef.current.clear()
      map.remove()
      mapRef.current = null
      setMapReady(false)
    }
  }, [refreshViewport])

  useEffect(() => {
    if (!mapReady) return
    const map = mapRef.current
    if (!map || !map.isStyleLoaded()) return
    const cellsSource = map.getSource('analysis-cells') as GeoJSONSource | undefined
    const selectionSource = map.getSource('selected-pixel') as GeoJSONSource | undefined
    const scopeSource = map.getSource('analysis-scope') as GeoJSONSource | undefined
    cellsSource?.setData(collection as never)
    selectionSource?.setData(selectionCollection as never)
    scopeSource?.setData(scopeCollection as never)
  }, [collection, mapReady, scopeCollection, selectionCollection])

  useEffect(() => {
    const map = mapRef.current
    if (!mapReady || !map) return
    markersRef.current.forEach((marker) => marker.remove())
    markersRef.current.clear()
    pixels.forEach((pixel, index) => {
      const [longitude, latitude] = pixel.center
      if (!Number.isFinite(longitude) || !Number.isFinite(latitude) || latitude < -90 || latitude > 90) return
      const rank = pixel.rank ?? index + 1
      const element = document.createElement('button')
      element.type = 'button'
      element.className = `rank-map-marker ${pixel.pixel_id === selectedPixelId ? 'is-selected' : ''}`
      element.textContent = String(rank).padStart(2, '0')
      element.setAttribute('aria-label', `Rank ${rank}, pixel ${pixel.pixel_id}, ${pixel.score_pct === null ? 'score not available' : `${formatNumber(pixel.score_pct)} percent similarity`}. Select and zoom to this pixel.`)
      element.title = `${pixel.pixel_id} · ${pixel.score_pct === null ? 'score not available' : `${formatNumber(pixel.score_pct)}%`}`
      element.addEventListener('click', (event) => {
        event.stopPropagation()
        if (pixelsRef.current.has(pixel.pixel_id)) onSelectPixelRef.current(pixel.pixel_id)
      })
      const marker = new Marker({ element, anchor: 'center' }).setLngLat([longitude, latitude]).addTo(map)
      markersRef.current.set(pixel.pixel_id, marker)
    })
    return () => {
      markersRef.current.forEach((marker) => marker.remove())
      markersRef.current.clear()
    }
  }, [mapReady, pixels, selectedPixelId])

  useEffect(() => {
    if (!analysis) {
      setViewportCells(null)
      setSelectedCellId(null)
      setMapError(null)
      return
    }
    setViewportCells(null)
    setSelectedCellId(null)
    setMapError(null)
    setMapLoading(false)
    requestRef.current?.abort()
    requestEpochRef.current += 1
    firstFitRef.current = null
  }, [analysis?.analysis_id])

  useEffect(() => {
    if (!mapReady || !analysis || firstFitRef.current === analysis.analysis_id) return
    const map = mapRef.current
    if (!map) return
    firstFitRef.current = analysis.analysis_id
    fitMapToBounds(map, boundsForGeometry(analysis.scope.geometry) ?? boundsForCells(analysis.map_cells), 9)
  }, [analysis, mapReady])

  useEffect(() => {
    if (!mapReady || zoomRequest === 0 || zoomRequest === lastZoomRequestRef.current) return
    const map = mapRef.current
    if (!map || !selectedPixel) return
    lastZoomRequestRef.current = zoomRequest
    fitMapToBounds(map, boundsForPixel(selectedPixel), 13)
  }, [mapReady, selectedPixel, zoomRequest])

  const selectedCellSummary = selectedCell
    ? selectedCell.max_score_pct === null
      ? `No eligible pixel scores. Missing reason: ${selectedCell.missing_reason ?? 'not supplied'}.`
      : `Cell maximum ${formatNumber(selectedCell.max_score_pct)}%; mean ${formatNumber(selectedCell.mean_score_pct)}% is context only.`
    : null

  return (
    <div className={`map-frame ${analysis ? 'has-analysis' : ''}`} role="region" aria-label="Interactive analysis map">
      <div className="map-viewport" ref={containerRef} aria-label="Globe map with analysis cells and ranked pixel markers" />
      {rendererError && <div className="map-renderer-error" role="status">Interactive map unavailable: {rendererError} The ranking and pixel details remain available below.</div>}
      <div className="map-hud map-hud-top">
        <div className="map-context">
          <span className="map-globe-icon" aria-hidden="true">◉</span>
          <div>
            <p className="eyebrow">{analysis ? `${analysis.scope.type.toUpperCase()} ANALYSIS · ${analysis.map_cells.length} GLOBAL DISPLAY CELLS` : 'GLOBAL SPATIAL VIEW'}</p>
            <strong>{analysis?.scope.region_name ?? 'Earth terrain analogs'}</strong>
          </div>
        </div>
        <div className="map-actions" aria-label="Map controls">
          <button type="button" onClick={() => mapRef.current?.zoomIn({ duration: 220 })} aria-label="Zoom in">+</button>
          <button type="button" onClick={() => mapRef.current?.zoomOut({ duration: 220 })} aria-label="Zoom out">−</button>
          <button type="button" onClick={fitResults} disabled={!analysis}>Fit scope</button>
        </div>
      </div>

      {!analysis && (
        <div className={`map-empty-overlay ${searchError ? 'has-error' : ''}`}>
          <p className="eyebrow">{searchError ? 'REQUEST ERROR · NO DEMO FALLBACK' : 'YOUR NEXT FIELD SITE STARTS HERE'}</p>
          <h2>{searchError ? 'Analysis could not be loaded.' : 'Explore a world of terrain.'}</h2>
          <p>{searchError ?? emptyMessage}</p>
          {searchError && <button className="secondary-button" type="button" onClick={onRetry}>Try again</button>}
        </div>
      )}

      <div className="map-hud map-hud-bottom">
        <section className="map-legend" aria-label="Map legend">
          <p className="map-legend-title">{analysis?.query.result_mode === 'distinct_areas' ? 'Display cell maximum · similarity index' : 'Display cell maximum · similarity index'}</p>
          <div className="score-ramp" aria-hidden="true" />
          <div className="score-ramp-labels"><span>0%</span><span>25</span><span>50</span><span>75</span><span>100%</span></div>
          <div className="map-legend-keys">
            <span><i className="no-data-swatch" aria-hidden="true" />No eligible measurements (null)</span>
            <span><i className="rank-swatch" aria-hidden="true">01</i>{analysis?.query.result_mode === 'distinct_areas' ? 'Selected area representative' : 'Top 10 pixel'}</span>
          </div>
        </section>
        <div className="map-footnote">
          <span>{analysis ? `${displayCells.length.toLocaleString('en-US')} visible cells · ${pixels.length} ranked markers` : 'No map results loaded'}</span>
          <span>Globe projection includes polar regions · zoom changes view, not data resolution.</span>
          <span>No external basemap or tile license dependency.</span>
        </div>
      </div>

      {selectedCell && (
        <section className="map-cell-inspector" aria-live="polite" aria-label="Selected display cell details">
          <button className="map-inspector-close" type="button" onClick={() => setSelectedCellId(null)} aria-label="Close display cell details">×</button>
          <p className="eyebrow">DISPLAY CELL · {selectedCell.valid_pixel_count}/{selectedCell.total_pixel_count} ELIGIBLE PIXELS</p>
          <strong>{selectedCell.cell_id}</strong>
          <p>{selectedCellSummary}</p>
          {selectedCell.max_pixel_id && <small>Maximum pixel: {selectedCell.max_pixel_id}</small>}
        </section>
      )}

      {analysis && collection.invalidCount > 0 && <p className="map-status map-warning" role="status">{collection.invalidCount} invalid cell footprint(s) were omitted from the map.</p>}
      {analysis && mode === 'live' && (mapLoading || mapError) && (
        <p className={`map-status ${mapError ? 'map-warning' : ''}`} role="status" aria-live="polite">
          {mapLoading ? `Loading up to ${MAX_VIEWPORT_CELLS.toLocaleString('en-US')} cells for this map view…` : `Map view update failed: ${mapError} Existing ranking and markers are unchanged.`}
        </p>
      )}
      {analysis && mode === 'synthetic' && <p className="map-status" role="status">Synthetic fixture geometry only. Zoom and pan do not request unstored fixture cells.</p>}
    </div>
  )
}

