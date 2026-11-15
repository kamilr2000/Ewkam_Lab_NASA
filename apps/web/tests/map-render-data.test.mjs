import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { after, before, test } from 'node:test'
import { resolve } from 'node:path'
import { createServer } from 'vite'

const appRoot = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repositoryRoot = resolve(appRoot, '../..')
const hotspotFixture = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/search-hotspot-synthetic.json'), 'utf8'))
const noDataFixture = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/search-no-data-synthetic.json'), 'utf8'))

let server
let renderData
let layerVisibility

before(async () => {
  server = await createServer({
    configFile: false,
    root: appRoot,
    server: { middlewareMode: true, hmr: false, ws: false },
    appType: 'custom',
  })
  renderData = await server.ssrLoadModule('/src/map/renderData.ts')
  layerVisibility = await server.ssrLoadModule('/src/map/layerVisibility.ts')
})

after(async () => {
  await server?.close()
})

test('cell source receives a GeoJSON FeatureCollection with numeric and null results', () => {
  const cells = [hotspotFixture.map_cells[0], noDataFixture.map_cells[0]]
  const result = renderData.makeCellCollection(cells)
  let sourceData = null

  renderData.applyCellCollectionData({ setData(value) { sourceData = value } }, result)

  assert.equal(result.invalidCount, 0)
  assert.equal(sourceData.type, 'FeatureCollection')
  assert.equal(sourceData.features.length, 2)
  assert.notStrictEqual(sourceData, result)
  assert.deepEqual(sourceData.features.map((feature) => feature.properties.score), [100, null])
  assert.equal(sourceData.features[1].properties.missing_reason, 'missing_feature_value')
})

test('map context labels identify synthetic global fixtures as a test universe', () => {
  assert.equal(renderData.formatMapContextLabel('global', 1, true), 'SYNTHETIC TEST FIXTURE · 1 TEST CELL')
  assert.equal(renderData.formatMapContextLabel('regional', 2), 'REGIONAL ANALYSIS · 2 REGIONAL DISPLAY CELLS')
})

test('map visibility switches affect presentation only and preserve independent overlays', () => {
  const layoutChanges = []
  const markers = [{ element: { hidden: false, style: { display: '' } } }, { element: { hidden: false, style: { display: '' } } }]
  const map = { setLayoutProperty(layerId, property, value) { layoutChanges.push([layerId, property, value]) } }
  const markerTargets = markers.map(({ element }) => ({ getElement() { return element } }))

  layerVisibility.applyLayerVisibility(map, markerTargets, { basemap: false, cells: true, markers: false })

  assert.deepEqual(layoutChanges[0], ['osm-basemap', 'visibility', 'none'])
  assert.deepEqual(layoutChanges.slice(1).map(([, , value]) => value), ['visible', 'visible', 'visible', 'visible', 'visible'])
  assert.ok(markers.every(({ element }) => element.hidden))
  assert.ok(markers.every(({ element }) => element.style.display === 'none'))
  assert.equal(layoutChanges.length, 6)

  layerVisibility.applyLayerVisibility(map, markerTargets, { basemap: true, cells: false, markers: true })
  assert.ok(markers.every(({ element }) => !element.hidden && element.style.display === ''))
  assert.equal(layoutChanges[6][2], 'visible')
  assert.ok(layoutChanges.slice(7).every(([, , value]) => value === 'none'))
})

test('new ranked markers inherit a currently hidden marker layer', () => {
  const recreatedMarkers = [
    { element: { hidden: false, style: { display: '' } } },
    { element: { hidden: false, style: { display: '' } } },
  ]
  const targets = recreatedMarkers.map(({ element }) => ({ getElement() { return element } }))
  const map = { setLayoutProperty() {} }

  layerVisibility.applyLayerVisibility(map, targets, { basemap: true, cells: true, markers: false })

  assert.ok(recreatedMarkers.every(({ element }) => element.hidden && element.style.display === 'none'))
})

test('map layer settings retain independent values across unrelated analysis updates', () => {
  const initial = { basemap: true, cells: true, markers: true }
  const afterHidingMarkers = layerVisibility.updateMapLayerVisibility(initial, 'markers', false)
  const afterHidingCells = layerVisibility.updateMapLayerVisibility(afterHidingMarkers, 'cells', false)

  assert.deepEqual(afterHidingCells, { basemap: true, cells: false, markers: false })
  assert.deepEqual(initial, { basemap: true, cells: true, markers: true })
})
