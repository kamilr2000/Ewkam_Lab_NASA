import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { after, before, test } from 'node:test'
import { resolve } from 'node:path'
import { createServer } from 'vite'

const appRoot = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repositoryRoot = resolve(appRoot, '../..')
const searchSuccess = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/search-success-synthetic.json'), 'utf8'))
const searchDistinct = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/search-distinct-areas-synthetic.json'), 'utf8'))
const mapHotspot = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/map-hotspot-synthetic.json'), 'utf8'))
const pixelHotspot = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/pixel-hotspot-synthetic.json'), 'utf8'))
const unavailableError = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/error-dataset-unavailable-synthetic.json'), 'utf8'))

const pixelRequest = {
  contract_version: '1.0.0',
  body: 'mars',
  profile_id: 'synthetic-mars-reference',
  dataset_version: 'synthetic-earth-v1',
  scope: { type: 'regional', region_id: 'synthetic-region-1' },
  criteria: [
    { feature_id: 'slope_deg', weight: 1 },
    { feature_id: 'roughness_m', weight: 1 },
  ],
  result_mode: 'pixels',
  top_k: 10,
}

const distinctRequest = {
  contract_version: '1.0.0',
  body: 'mars',
  profile_id: 'synthetic-mars-reference',
  dataset_version: 'synthetic-earth-v1',
  scope: { type: 'global' },
  criteria: [{ feature_id: 'slope_deg', weight: 1 }],
  result_mode: 'distinct_areas',
  top_k: 2,
  min_distance_km: 25,
}

let server
let client

before(async () => {
  server = await createServer({
    configFile: false,
    root: appRoot,
    server: { middlewareMode: true, hmr: false, ws: false },
    appType: 'custom',
  })
  client = await server.ssrLoadModule('/src/api/client.ts')
})

after(async () => {
  await server?.close()
})

function liveSearchResponse() {
  const response = structuredClone(searchSuccess)
  response.is_synthetic = false
  return response
}

function installFetch(payload, status = 200) {
  const originalFetch = globalThis.fetch
  const calls = []
  globalThis.fetch = async (input, init) => {
    calls.push({ url: String(input), init })
    return new Response(JSON.stringify(payload), {
      status,
      headers: { 'Content-Type': 'application/json' },
    })
  }
  return {
    calls,
    restore() {
      globalThis.fetch = originalFetch
    },
  }
}

async function rejectsLiveSearch(payload, request, expectedMessage) {
  const stub = installFetch(payload)
  try {
    await assert.rejects(
      client.runSearch('live', request, 'success'),
      (error) => error instanceof client.ApiError && error.message.includes(expectedMessage),
    )
    assert.equal(stub.calls.length, 1, 'a rejected live response must not trigger a fixture fallback request')
    assert.equal(payload.is_synthetic, false)
  } finally {
    stub.restore()
  }
}

test('accepts a live search whose dataset and query match, regardless of criteria order', async () => {
  const payload = liveSearchResponse()
  payload.query.criteria.reverse()
  const stub = installFetch(payload)
  try {
    const result = await client.runSearch('live', pixelRequest, 'success')
    assert.equal(result.is_synthetic, false)
    assert.equal(result.analysis_id, 'synthetic-analysis-success')
    assert.deepEqual(JSON.parse(stub.calls[0].init.body), pixelRequest)
  } finally {
    stub.restore()
  }
})

test('rejects a live search for a different dataset', async () => {
  const payload = liveSearchResponse()
  payload.dataset_version = 'unexpected-dataset'
  await rejectsLiveSearch(payload, pixelRequest, 'dataset_version')
})

test('rejects a live search for a different planetary body', async () => {
  const payload = liveSearchResponse()
  payload.query.body = 'moon'
  await rejectsLiveSearch(payload, pixelRequest, 'planetary body')
})

test('rejects a live search for a different profile', async () => {
  const payload = liveSearchResponse()
  payload.query.profile_id = 'unexpected-profile'
  await rejectsLiveSearch(payload, pixelRequest, 'profile')
})

test('rejects a live search with a different scope type', async () => {
  const payload = liveSearchResponse()
  payload.query.scope = { type: 'global' }
  await rejectsLiveSearch(payload, pixelRequest, 'scope')
})

test('rejects a live search with a different regional scope id', async () => {
  const payload = liveSearchResponse()
  payload.query.scope.region_id = 'unexpected-region'
  await rejectsLiveSearch(payload, pixelRequest, 'scope')
})

test('rejects a live search with a different top-level regional scope id', async () => {
  const payload = liveSearchResponse()
  payload.scope.region_id = 'unexpected-region'
  await rejectsLiveSearch(payload, pixelRequest, 'top-level scope')
})

test('rejects a live search with a different top-level scope type', async () => {
  const payload = liveSearchResponse()
  payload.scope.type = 'global'
  await rejectsLiveSearch(payload, pixelRequest, 'top-level scope')
})

test('rejects a live search that omits the null distance echo', async () => {
  const payload = liveSearchResponse()
  delete payload.query.min_distance_km
  await rejectsLiveSearch(payload, pixelRequest, 'min_distance_km')
})

test('rejects a live search with a different feature', async () => {
  const payload = liveSearchResponse()
  payload.query.criteria[0].feature_id = 'wrong-feature'
  await rejectsLiveSearch(payload, pixelRequest, 'criteria')
})

test('rejects a live search with a different raw feature weight', async () => {
  const payload = liveSearchResponse()
  payload.query.criteria[0].weight = 2
  await rejectsLiveSearch(payload, pixelRequest, 'criteria')
})

test('rejects a live search with a different normalized feature weight', async () => {
  const payload = liveSearchResponse()
  payload.query.criteria[0].normalized_weight = 0.6
  await rejectsLiveSearch(payload, pixelRequest, 'criteria')
})

test('rejects a live search with a different top_k', async () => {
  const payload = liveSearchResponse()
  payload.query.top_k = 9
  await rejectsLiveSearch(payload, pixelRequest, 'top_k')
})

test('rejects a live search with a different result mode', async () => {
  const payload = liveSearchResponse()
  payload.query.result_mode = 'distinct_areas'
  payload.query.min_distance_km = 25
  payload.query.area_selection_rule = 'greedy_geodesic_representatives'
  payload.area_ranking = []
  delete payload.ranking
  await rejectsLiveSearch(payload, pixelRequest, 'result_mode')
})

test('rejects a live pixel search that echoes a distance', async () => {
  const payload = liveSearchResponse()
  payload.query.min_distance_km = 25
  await rejectsLiveSearch(payload, pixelRequest, 'min_distance_km')
})

test('accepts a live distinct-area search with its requested distance', async () => {
  const payload = structuredClone(searchDistinct)
  payload.is_synthetic = false
  const stub = installFetch(payload)
  try {
    const result = await client.runSearch('live', distinctRequest, 'distinct-areas')
    assert.equal(result.is_synthetic, false)
    assert.equal(result.query.min_distance_km, distinctRequest.min_distance_km)
  } finally {
    stub.restore()
  }
})

test('rejects a global response scope that invents a regional id', async () => {
  const payload = structuredClone(searchDistinct)
  payload.is_synthetic = false
  payload.scope.region_id = 'unexpected-region'
  await rejectsLiveSearch(payload, distinctRequest, 'top-level scope')
})

test('rejects a global response scope with a non-null region name', async () => {
  const payload = structuredClone(searchDistinct)
  payload.is_synthetic = false
  payload.scope.region_name = 'Unexpected region'
  await rejectsLiveSearch(payload, distinctRequest, 'top-level scope')
})

test('rejects a live distinct-area search with a different distance', async () => {
  const payload = structuredClone(searchDistinct)
  payload.is_synthetic = false
  payload.query.min_distance_km = 50
  await rejectsLiveSearch(payload, distinctRequest, 'min_distance_km')
})

test('keeps live HTTP errors explicit and does not switch to a synthetic search fixture', async () => {
  const payload = structuredClone(unavailableError)
  payload.is_synthetic = false
  const stub = installFetch(payload, 503)
  try {
    await assert.rejects(
      client.runSearch('live', pixelRequest, 'success'),
      (error) => error instanceof client.ApiError && error.status === 503 && error.message.includes('DATASET_UNAVAILABLE'),
    )
    assert.equal(stub.calls.length, 1)
  } finally {
    stub.restore()
  }
})

const mapRequest = {
  analysisId: 'analysis-live',
  bbox: [12.5, -8.25, 20, 4],
  level: 3,
  limit: 16,
}

function liveMapResponse() {
  return {
    ...structuredClone(mapHotspot),
    analysis_id: mapRequest.analysisId,
    is_synthetic: false,
    query: { bbox: [...mapRequest.bbox], level: mapRequest.level, limit: mapRequest.limit },
  }
}

async function rejectsLiveMap(payload, expectedMessage) {
  const stub = installFetch(payload)
  try {
    await assert.rejects(
      client.getAnalysisMap('live', mapRequest.analysisId, mapRequest.bbox, mapRequest.level, mapRequest.limit),
      (error) => error instanceof client.ApiError && error.message.includes(expectedMessage),
    )
    assert.equal(stub.calls.length, 1, 'a rejected live response must not trigger a fixture fallback request')
    assert.equal(payload.is_synthetic, false)
  } finally {
    stub.restore()
  }
}

test('accepts a live map that echoes its bbox, level, and limit', async () => {
  const stub = installFetch(liveMapResponse())
  try {
    const result = await client.getAnalysisMap('live', mapRequest.analysisId, mapRequest.bbox, mapRequest.level, mapRequest.limit)
    assert.equal(result.is_synthetic, false)
    assert.deepEqual(result.query, { bbox: mapRequest.bbox, level: mapRequest.level, limit: mapRequest.limit })
  } finally {
    stub.restore()
  }
})

test('rejects a live map with a different bbox despite a matching analysis id', async () => {
  const payload = liveMapResponse()
  payload.query.bbox[0] += 1
  await rejectsLiveMap(payload, 'bbox')
})

test('rejects a live map with a different level', async () => {
  const payload = liveMapResponse()
  payload.query.level += 1
  await rejectsLiveMap(payload, 'bbox, level, or limit')
})

test('rejects a live map with a different limit', async () => {
  const payload = liveMapResponse()
  payload.query.limit += 1
  await rejectsLiveMap(payload, 'bbox, level, or limit')
})

test('retains analysis id validation for live maps', async () => {
  const payload = liveMapResponse()
  payload.analysis_id = 'unexpected-analysis'
  await rejectsLiveMap(payload, 'analysis')
})

test('accepts the synthetic map fixture with its recorded bbox, level, and limit', async () => {
  const result = await client.getAnalysisMap('synthetic', 'synthetic-analysis-hotspot', [3, 3, 3.04, 3.02], 0, 1000)
  assert.equal(result.is_synthetic, true)
  assert.equal(result.analysis_id, 'synthetic-analysis-hotspot')
})

test('synthetic maps reject a fixture with a different requested bbox', async () => {
  await assert.rejects(
    client.getAnalysisMap('synthetic', 'synthetic-analysis-hotspot', [3, 3, 3.05, 3.02], 0, 1000),
    (error) => error instanceof client.ApiError && error.message.includes('bbox, level, or limit'),
  )
})

test('retains analysis id and pixel id validation for live pixel details', async () => {
  const payload = {
    ...structuredClone(pixelHotspot),
    analysis_id: 'analysis-live',
    is_synthetic: false,
  }
  const stub = installFetch(payload)
  try {
    const result = await client.getPixelDetails('live', 'analysis-live', 'synthetic-hotspot-p001')
    assert.equal(result.is_synthetic, false)
    assert.equal(result.pixel.pixel_id, 'synthetic-hotspot-p001')
  } finally {
    stub.restore()
  }

  await rejectsLivePixelDetails({ ...payload, analysis_id: 'unexpected-analysis' }, 'analysis-live', 'synthetic-hotspot-p001', 'analysis')
  await rejectsLivePixelDetails({ ...payload, pixel: { ...payload.pixel, pixel_id: 'unexpected-pixel' } }, 'analysis-live', 'synthetic-hotspot-p001', 'pixel')
})

async function rejectsLivePixelDetails(payload, analysisId, pixelId, expectedMessage) {
  const stub = installFetch(payload)
  try {
    await assert.rejects(
      client.getPixelDetails('live', analysisId, pixelId),
      (error) => error instanceof client.ApiError && error.message.includes(expectedMessage),
    )
    assert.equal(stub.calls.length, 1)
  } finally {
    stub.restore()
  }
}
