import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import { after, before, test } from 'node:test'
import { resolve } from 'node:path'
import { createServer } from 'vite'

const appRoot = resolve(fileURLToPath(new URL('..', import.meta.url)))
const repositoryRoot = resolve(appRoot, '../..')
const catalogFixture = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/catalog-synthetic.json'), 'utf8'))
const profileFixture = JSON.parse(await readFile(resolve(repositoryRoot, 'contracts/fixtures/profile-synthetic.json'), 'utf8'))

let server
let criteria

before(async () => {
  server = await createServer({
    configFile: false,
    root: appRoot,
    server: { middlewareMode: true },
    appType: 'custom',
  })
  criteria = await server.ssrLoadModule('/src/controls/criteria.ts')
})

after(async () => {
  await server?.close()
})

function liveProfileFixtures() {
  const catalog = structuredClone(catalogFixture)
  const profile = structuredClone(profileFixture)
  const reliefFeature = {
    ...profile.profile.features[1],
    feature_id: 'relief_m',
    name: 'Local relief',
    description: 'Synthetic local relief interval.',
  }

  catalog.catalog_version = 'live-catalog-test-v1'
  catalog.features.forEach((feature) => { feature.availability = 'available' })
  catalog.profiles = [{
    profile_id: 'mars-jezero-v1',
    name: 'Jezero reference',
    body: 'mars',
    region_name: 'Jezero crater',
    profile_version: 'jezero-v1',
    availability: 'available',
    feature_ids: ['slope_deg', 'roughness_m', 'relief_m'],
    source_ids: ['synthetic-fixture'],
  }]
  profile.profile.profile_id = 'mars-jezero-v1'
  profile.profile.name = 'Jezero reference'
  profile.profile.profile_version = 'jezero-v1'
  profile.profile.region.name = 'Jezero crater'
  profile.profile.features.push(reliefFeature)
  return { catalog, profile }
}

test('one active measurement creates a one-feature global request with no hidden criteria', () => {
  const { catalog, profile } = liveProfileFixtures()
  const available = criteria.getAvailableProfileFeatures('live', catalog, profile)
  let settings = criteria.createInitialCriteriaSettings(available)
  settings = criteria.setCriterionEnabled(settings, 'roughness_m', false)
  settings = criteria.setCriterionEnabled(settings, 'relief_m', false)
  settings = criteria.setCriterionWeight(settings, 'slope_deg', 2.4)

  const request = criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, settings)
  assert.equal(request.body, 'mars')
  assert.equal(request.profile_id, 'mars-jezero-v1')
  assert.deepEqual(request.scope, { type: 'global' })
  assert.deepEqual(request.criteria, [{ feature_id: 'slope_deg', weight: 2.4 }])
  assert.equal(criteria.getActiveCriteria(available, settings)[0].normalizedWeight, 1)
})

test('live request selects earth_search when an available validation dataset comes first', () => {
  const { catalog, profile } = liveProfileFixtures()
  const template = catalog.datasets[0]
  catalog.datasets = [
    { ...template, dataset_version: 'validation-earth-v1', role: 'validation', availability: 'available' },
    { ...template, dataset_version: 'earth-search-v2', role: 'earth_search', availability: 'available' },
  ]

  const dataset = criteria.selectDatasetForMode('live', catalog)
  const features = criteria.getAvailableProfileFeatures('live', catalog, profile)
  const settings = criteria.createInitialCriteriaSettings(features)
  const request = criteria.buildSearchRequest(profile.profile, dataset.dataset_version, features, settings)

  assert.equal(request.dataset_version, 'earth-search-v2')
})

test('dataset selection reports missing or ambiguous intended roles', () => {
  const { catalog } = liveProfileFixtures()
  catalog.datasets = [
    { ...catalog.datasets[0], dataset_version: 'validation-earth-v1', role: 'validation', availability: 'available' },
  ]
  assert.throws(() => criteria.selectDatasetForMode('live', catalog), /No available Earth search dataset/)

  catalog.datasets.push({
    ...catalog.datasets[0],
    dataset_version: 'earth-search-v2',
    role: 'earth_search',
    availability: 'available',
  })
  catalog.datasets.push({
    ...catalog.datasets[0],
    dataset_version: 'earth-search-v3',
    role: 'earth_search',
    availability: 'available',
  })
  assert.throws(() => criteria.selectDatasetForMode('live', catalog), /multiple earth_search Earth datasets/)
})

test('synthetic request selection requires the fixture_only role', () => {
  const catalog = structuredClone(catalogFixture)
  catalog.datasets.unshift({
    ...catalog.datasets[0],
    dataset_version: 'available-validation-v1',
    role: 'validation',
    availability: 'synthetic_only',
  })

  assert.equal(criteria.selectDatasetForMode('synthetic', catalog).dataset_version, 'synthetic-earth-v1')
})

test('three active measurements retain raw positive weights and show normalized shares', () => {
  const { catalog, profile } = liveProfileFixtures()
  const available = criteria.getAvailableProfileFeatures('live', catalog, profile)
  let settings = criteria.createInitialCriteriaSettings(available)
  settings = criteria.setCriterionWeight(settings, 'slope_deg', 1)
  settings = criteria.setCriterionWeight(settings, 'roughness_m', 2)
  settings = criteria.setCriterionWeight(settings, 'relief_m', 3)

  const request = criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, settings)
  assert.deepEqual(request.criteria, [
    { feature_id: 'slope_deg', weight: 1 },
    { feature_id: 'roughness_m', weight: 2 },
    { feature_id: 'relief_m', weight: 3 },
  ])
  assert.deepEqual(criteria.getActiveCriteria(available, settings).map((item) => item.normalizedWeight), [1 / 6, 1 / 3, 1 / 2])
})

test('zero selected measurements are rejected before a request can be built', () => {
  const { catalog, profile } = liveProfileFixtures()
  const available = criteria.getAvailableProfileFeatures('live', catalog, profile)
  let settings = criteria.createInitialCriteriaSettings(available)
  for (const feature of available) settings = criteria.setCriterionEnabled(settings, feature.feature_id, false)

  assert.match(criteria.getCriteriaValidationError(available, settings), /at least one/)
  assert.throws(() => criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, settings), /at least one/)
})

test('features unavailable in the selected catalog never enter the request', () => {
  const { catalog, profile } = liveProfileFixtures()
  catalog.features.find((feature) => feature.feature_id === 'relief_m').availability = 'planned'
  const available = criteria.getAvailableProfileFeatures('live', catalog, profile)
  let settings = criteria.createInitialCriteriaSettings(available)
  settings.relief_m = { enabled: true, weight: 9 }

  const request = criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, settings)
  assert.deepEqual(available.map((feature) => feature.feature_id), ['slope_deg', 'roughness_m'])
  assert.deepEqual(request.criteria.map((item) => item.feature_id), ['slope_deg', 'roughness_m'])
})

test('non-positive and over-limit weights are rejected before the request is built', () => {
  const { catalog, profile } = liveProfileFixtures()
  const available = criteria.getAvailableProfileFeatures('live', catalog, profile)
  const settings = criteria.createInitialCriteriaSettings(available)
  settings.slope_deg = { enabled: true, weight: 0 }

  assert.match(criteria.getCriteriaValidationError(available, settings), /positive weight/)
  assert.throws(() => criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, settings), /positive weight/)
  settings.slope_deg = { enabled: true, weight: 1_000_001 }
  assert.match(criteria.getCriteriaValidationError(available, settings), /positive weight/)
})

test('the selected profile keeps its planetary body and region-specific profile ID', () => {
  const { catalog, profile } = liveProfileFixtures()
  const moonProfile = structuredClone(profile)
  moonProfile.profile.profile_id = 'moon-south-pole-v1'
  moonProfile.profile.body = 'moon'
  moonProfile.profile.region.name = 'Lunar south pole'
  moonProfile.profile.region.coordinate_system.body = 'moon'
  moonProfile.profile.features = [moonProfile.profile.features[0]]
  catalog.profiles.push({
    ...catalog.profiles[0],
    profile_id: 'moon-south-pole-v1',
    name: 'Lunar south pole reference',
    body: 'moon',
    region_name: 'Lunar south pole',
    feature_ids: ['slope_deg'],
  })

  const available = criteria.getAvailableProfileFeatures('live', catalog, moonProfile)
  const settings = criteria.createInitialCriteriaSettings(available)
  const request = criteria.buildSearchRequest(moonProfile.profile, 'earth-dem-v1', available, settings)
  assert.equal(request.body, 'moon')
  assert.equal(request.profile_id, 'moon-south-pole-v1')
  assert.deepEqual(request.criteria, [{ feature_id: 'slope_deg', weight: 1 }])
})

test('map visibility metadata does not change submitted scoring weights', () => {
  const { catalog, profile } = liveProfileFixtures()
  const available = criteria.getAvailableProfileFeatures('live', catalog, profile)
  const settings = criteria.createInitialCriteriaSettings(available)
  const hiddenOnMap = Object.fromEntries(Object.entries(settings).map(([id, setting]) => [id, { ...setting, visible: false }]))
  const visibleOnMap = Object.fromEntries(Object.entries(settings).map(([id, setting]) => [id, { ...setting, visible: true }]))

  assert.deepEqual(
    criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, hiddenOnMap),
    criteria.buildSearchRequest(profile.profile, 'earth-dem-v1', available, visibleOnMap),
  )
})
