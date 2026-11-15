import { Component, lazy, Suspense, useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { ApiError, demoScenarios, getCatalog, getProfile, runSearch } from './api/client'
import { RequestEpoch } from './api/requestEpoch'
import { CriteriaControls } from './controls/CriteriaControls'
import {
  buildSearchRequest,
  createInitialCriteriaSettings,
  getActiveCriteria,
  getAvailableProfileFeatures,
  getAvailableSearchRegions,
  MAX_AREA_DISTANCE_KM,
  getCriteriaValidationError,
  selectDatasetForMode,
  setCriterionEnabled,
  setCriterionWeight,
} from './controls/criteria'
import type { CriteriaSettings } from './controls/criteria'
import { updateMapLayerVisibility, type MapLayerVisibility } from './map/layerVisibility'
import type {
  CatalogResponse,
  DataMode,
  DemoScenario,
  PlanetaryBody,
  ProfileResponse,
  ResultMode,
  SearchPixel,
  SearchRequest,
  SearchResponse,
} from './api/types'

const loadAnalysisMap = () => import('./map/AnalysisMap')
const AnalysisMap = lazy(loadAnalysisMap)

class MapModuleBoundary extends Component<{ children: ReactNode }, { hasError: boolean }> {
  state = { hasError: false }

  static getDerivedStateFromError() {
    return { hasError: true }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="map-frame map-frame-loading" role="alert">
          <div className="map-frame-loading-content">
            <p className="eyebrow">MAP UNAVAILABLE</p>
            <strong>The interactive map could not be loaded.</strong>
            <p>Your ranking and pixel details remain available below.</p>
            <button className="secondary-button" type="button" onClick={() => window.location.reload()}>Reload the app to try again</button>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

function isSelectableAvailability(mode: DataMode, value: string): boolean {
  return value === (mode === 'synthetic' ? 'synthetic_only' : 'available')
}

function pixelsFromResponse(response: SearchResponse): SearchPixel[] {
  if (response.query.result_mode === 'pixels' && 'ranking' in response && response.ranking) return response.ranking
  if (response.query.result_mode === 'distinct_areas' && 'area_ranking' in response && response.area_ranking) {
    return response.area_ranking.map((entry) => entry.representative_pixel)
  }
  return []
}

function formatNumber(value: number | null, maximumFractionDigits = 2): string {
  if (value === null || !Number.isFinite(value)) return 'Not available'
  return value.toLocaleString('en-US', { maximumFractionDigits })
}

function makeRequest(
  mode: DataMode,
  catalog: CatalogResponse,
  profile: ProfileResponse,
  criteriaSettings: CriteriaSettings,
  searchRegionId: string,
  resultMode: ResultMode,
  minimumDistanceKm: string,
): SearchRequest {
  if (mode === 'live' && !searchRegionId) {
    throw new ApiError('Choose an available Earth search region before running a live analysis.')
  }
  const dataset = selectDatasetForMode(mode, catalog, mode === 'live' ? searchRegionId : undefined)
  const profileFeatures = getAvailableProfileFeatures(mode, catalog, profile)
  if (profileFeatures.length === 0) {
    throw new ApiError('This profile has no features available for the selected Earth dataset.')
  }

  try {
    const options = mode === 'live'
      ? {
          scope: { type: 'regional' as const, region_id: searchRegionId },
          resultMode,
          ...(resultMode === 'distinct_areas' ? { minDistanceKm: Number(minimumDistanceKm) } : {}),
        }
      : undefined
    return buildSearchRequest(profile.profile, dataset.dataset_version, profileFeatures, criteriaSettings, options)
  } catch (error) {
    throw new ApiError(error instanceof Error ? error.message : 'The selected criteria are not valid.')
  }
}

function configurationKey(mode: DataMode, catalog: CatalogResponse, profile: ProfileResponse): string {
  return JSON.stringify([
    mode,
    catalog.catalog_version,
    profile.profile.profile_id,
    profile.profile.profile_version,
  ])
}

function App() {
  const [mode, setMode] = useState<DataMode>('synthetic')
  const [scenario, setScenario] = useState<DemoScenario>('success')
  const [catalog, setCatalog] = useState<CatalogResponse | null>(null)
  const [catalogMode, setCatalogMode] = useState<DataMode | null>(null)
  const [body, setBody] = useState<PlanetaryBody>('mars')
  const [profileId, setProfileId] = useState('')
  const [searchRegionId, setSearchRegionId] = useState('')
  const [resultMode, setResultMode] = useState<ResultMode>('pixels')
  const [minimumDistanceKm, setMinimumDistanceKm] = useState('')
  const [profile, setProfile] = useState<ProfileResponse | null>(null)
  const [criteriaConfiguration, setCriteriaConfiguration] = useState<{
    key: string
    settings: CriteriaSettings
  } | null>(null)
  const [analysis, setAnalysis] = useState<SearchResponse | null>(null)
  const [layerVisibility, setLayerVisibility] = useState<MapLayerVisibility>({ basemap: true, cells: true, markers: true })
  const [selectedPixelId, setSelectedPixelId] = useState<string | null>(null)
  const [zoomRequest, setZoomRequest] = useState(0)
  const [catalogLoading, setCatalogLoading] = useState(true)
  const [profileLoading, setProfileLoading] = useState(false)
  const [searching, setSearching] = useState(false)
  const [catalogError, setCatalogError] = useState<string | null>(null)
  const [profileError, setProfileError] = useState<string | null>(null)
  const [searchError, setSearchError] = useState<string | null>(null)

  const catalogEpoch = useRef(new RequestEpoch())
  const profileEpoch = useRef(new RequestEpoch())
  const searchEpoch = useRef(new RequestEpoch())
  const catalogController = useRef<AbortController | null>(null)
  const profileController = useRef<AbortController | null>(null)
  const searchController = useRef<AbortController | null>(null)

  const bodyProfiles = useMemo(
    () => catalogMode === mode
      ? (catalog?.profiles ?? []).filter((item) => item.body === body && isSelectableAvailability(mode, item.availability))
      : [],
    [catalog, catalogMode, body, mode],
  )
  const visibleProfiles = useMemo(
    () => catalogMode === mode
      ? (catalog?.profiles ?? []).filter((item) => isSelectableAvailability(mode, item.availability))
      : [],
    [catalog, catalogMode, mode],
  )
  const searchRegions = useMemo(
    () => catalog && catalogMode === mode ? getAvailableSearchRegions(mode, catalog) : [],
    [catalog, catalogMode, mode],
  )
  const selectedSearchRegion = searchRegions.find((item) => item.region_id === searchRegionId) ?? null
  const profileFeatures = useMemo(
    () => catalog && catalogMode === mode && profile
      ? getAvailableProfileFeatures(mode, catalog, profile)
      : [],
    [catalog, catalogMode, mode, profile],
  )
  const currentConfigurationKey = catalog && profile ? configurationKey(mode, catalog, profile) : null
  const defaultCriteriaSettings = useMemo(
    () => createInitialCriteriaSettings(profileFeatures),
    [profileFeatures],
  )
  const criteriaSettings = currentConfigurationKey && criteriaConfiguration?.key === currentConfigurationKey
    ? criteriaConfiguration.settings
    : defaultCriteriaSettings
  const activeCriteriaCount = getActiveCriteria(profileFeatures, criteriaSettings).length
  const criteriaValidationError = getCriteriaValidationError(profileFeatures, criteriaSettings)
  const searchRegionError = mode === 'live' && catalog
    ? searchRegions.length === 0
      ? 'The live catalog lists no available regional Earth search packages.'
      : selectedSearchRegion ? null : 'Choose an Earth search region from the live catalog.'
    : null
  const distanceValue = minimumDistanceKm.trim() ? Number(minimumDistanceKm) : Number.NaN
  const distanceValidationError = mode === 'live' && resultMode === 'distinct_areas' &&
    (!Number.isFinite(distanceValue) || distanceValue <= 0 || distanceValue > MAX_AREA_DISTANCE_KM)
    ? 'Enter a minimum distance greater than 0 and no more than 10,000 km.'
    : null
  const runConfigurationError = criteriaValidationError ?? searchRegionError ?? distanceValidationError
  const resultPixels = useMemo(() => (analysis ? pixelsFromResponse(analysis) : []), [analysis])
  const selectedPixel = resultPixels.find((pixel) => pixel.pixel_id === selectedPixelId) ?? null
  const activeScenario = demoScenarios.find((item) => item.id === scenario)

  useEffect(() => {
    const epoch = catalogEpoch.current.begin()
    const controller = new AbortController()
    catalogController.current?.abort()
    catalogController.current = controller
    setCatalog(null)
    setCatalogMode(null)
    setProfile(null)
    setSearchRegionId('')
    setCriteriaConfiguration(null)
    setAnalysis(null)
    setSelectedPixelId(null)
    setCatalogLoading(true)
    setProfileLoading(false)
    setCatalogError(null)
    setProfileError(null)
    setSearchError(null)
    searchController.current?.abort()
    searchEpoch.current.invalidate()

    void getCatalog(mode, controller.signal).then((result) => {
      if (!catalogEpoch.current.isCurrent(epoch)) return
      setCatalog(result)
      setCatalogMode(mode)
      const firstProfile = result.profiles.find((item) => isSelectableAvailability(mode, item.availability))
      const firstSearchRegion = mode === 'live' ? getAvailableSearchRegions(mode, result)[0] : undefined
      setSearchRegionId(firstSearchRegion?.region_id ?? '')
      if (firstProfile) {
        setBody(firstProfile.body)
        setProfileId(firstProfile.profile_id)
      } else {
        setProfileId('')
      }
    }).catch((error: unknown) => {
      if (!catalogEpoch.current.isCurrent(epoch) || (error instanceof DOMException && error.name === 'AbortError')) return
      setCatalogError(error instanceof Error ? error.message : 'Catalog could not be loaded.')
    }).finally(() => {
      if (catalogEpoch.current.isCurrent(epoch)) setCatalogLoading(false)
    })

    return () => {
      controller.abort()
      catalogEpoch.current.invalidate()
    }
  }, [mode])

  useEffect(() => {
    if (!catalog || catalogMode !== mode || !profileId) {
      setProfile(null)
      setProfileLoading(false)
      setProfileError(null)
      return
    }
    const epoch = profileEpoch.current.begin()
    const controller = new AbortController()
    profileController.current?.abort()
    profileController.current = controller
    setProfile(null)
    setProfileLoading(true)
    setProfileError(null)

    void getProfile(mode, profileId, controller.signal).then((result) => {
      if (!profileEpoch.current.isCurrent(epoch)) return
      if (result.profile.body !== body) throw new ApiError('Profile body does not match the selected destination body.')
      const availableFeatures = getAvailableProfileFeatures(mode, catalog, result)
      const key = configurationKey(mode, catalog, result)
      setCriteriaConfiguration((current) => current?.key === key
        ? current
        : { key, settings: createInitialCriteriaSettings(availableFeatures) })
      setProfile(result)
    }).catch((error: unknown) => {
      if (!profileEpoch.current.isCurrent(epoch) || (error instanceof DOMException && error.name === 'AbortError')) return
      setProfileError(error instanceof Error ? error.message : 'Profile could not be loaded.')
    }).finally(() => {
      if (profileEpoch.current.isCurrent(epoch)) setProfileLoading(false)
    })

    return () => {
      controller.abort()
      profileEpoch.current.invalidate()
    }
  }, [body, catalog, catalogMode, mode, profileId])

  useEffect(() => () => {
    catalogController.current?.abort()
    profileController.current?.abort()
    searchController.current?.abort()
    searchEpoch.current.invalidate()
  }, [])

  function chooseBody(value: PlanetaryBody): void {
    const nextProfile = (catalog?.profiles ?? []).find((item) => item.body === value && isSelectableAvailability(mode, item.availability))
    searchController.current?.abort()
    searchEpoch.current.invalidate()
    setSearching(false)
    setBody(value)
    setProfileId(nextProfile?.profile_id ?? '')
    setCriteriaConfiguration(null)
    setAnalysis(null)
    setSelectedPixelId(null)
    setSearchError(null)
  }

  function chooseProfile(value: string): void {
    const nextProfile = visibleProfiles.find((item) => item.profile_id === value)
    if (!nextProfile) return
    searchController.current?.abort()
    searchEpoch.current.invalidate()
    setSearching(false)
    setBody(nextProfile.body)
    setProfileId(nextProfile.profile_id)
    setCriteriaConfiguration(null)
    setAnalysis(null)
    setSelectedPixelId(null)
    setSearchError(null)
  }

  async function runAnalysis(): Promise<void> {
    if (!catalog || !profile) return
    const epoch = searchEpoch.current.begin()
    const controller = new AbortController()
    searchController.current?.abort()
    searchController.current = controller
    setSearching(true)
    setSearchError(null)
    setAnalysis(null)
    setSelectedPixelId(null)

    try {
      const request = makeRequest(mode, catalog, profile, criteriaSettings, searchRegionId, resultMode, minimumDistanceKm)
      const response = await runSearch(mode, request, scenario, controller.signal)
      if (!searchEpoch.current.isCurrent(epoch)) return
      setAnalysis(response)
      const firstPixel = pixelsFromResponse(response)[0]
      setSelectedPixelId(firstPixel?.pixel_id ?? null)
    } catch (error) {
      if (!searchEpoch.current.isCurrent(epoch) || (error instanceof DOMException && error.name === 'AbortError')) return
      setSearchError(error instanceof Error ? error.message : 'The analysis request failed.')
    } finally {
      if (searchEpoch.current.isCurrent(epoch)) setSearching(false)
    }
  }

  function chooseSearchRegion(value: string): void {
    if (!searchRegions.some((region) => region.region_id === value)) return
    searchController.current?.abort()
    searchEpoch.current.invalidate()
    setSearching(false)
    setSearchRegionId(value)
    clearAnalysisForCriteriaChange()
  }

  function changeResultMode(value: ResultMode): void {
    if (value === resultMode) return
    setResultMode(value)
    clearAnalysisForCriteriaChange()
  }

  function changeMinimumDistance(value: string): void {
    setMinimumDistanceKm(value)
    clearAnalysisForCriteriaChange()
  }

  function changeMode(nextMode: DataMode): void {
    if (nextMode === mode) return
    searchController.current?.abort()
    searchEpoch.current.invalidate()
    setSearching(false)
    setCriteriaConfiguration(null)
    setSearchRegionId('')
    setProfile(null)
    setProfileId('')
    setAnalysis(null)
    setSelectedPixelId(null)
    setSearchError(null)
    profileController.current?.abort()
    catalogController.current?.abort()
    setMode(nextMode)
  }

  function changeScenario(nextScenario: DemoScenario): void {
    searchController.current?.abort()
    searchEpoch.current.invalidate()
    setSearching(false)
    setAnalysis(null)
    setSelectedPixelId(null)
    setSearchError(null)
    setScenario(nextScenario)
  }

  function selectPixelAndZoom(pixelId: string): void {
    setSelectedPixelId(pixelId)
    setZoomRequest((current) => current + 1)
  }

  function clearAnalysisForCriteriaChange(): void {
    searchController.current?.abort()
    searchEpoch.current.invalidate()
    setSearching(false)
    setAnalysis(null)
    setSelectedPixelId(null)
    setSearchError(null)
  }

  function changeCriterionEnabled(featureId: string, enabled: boolean): void {
    if (!currentConfigurationKey) return
    setCriteriaConfiguration((current) => {
      const settings = current?.key === currentConfigurationKey
        ? current.settings
        : defaultCriteriaSettings
      return { key: currentConfigurationKey, settings: setCriterionEnabled(settings, featureId, enabled) }
    })
    clearAnalysisForCriteriaChange()
  }

  function changeCriterionWeight(featureId: string, weight: number): void {
    if (!currentConfigurationKey) return
    setCriteriaConfiguration((current) => {
      const settings = current?.key === currentConfigurationKey
        ? current.settings
        : defaultCriteriaSettings
      return { key: currentConfigurationKey, settings: setCriterionWeight(settings, featureId, weight) }
    })
    clearAnalysisForCriteriaChange()
  }

  const profileCatalogEntry = visibleProfiles.find((item) => item.profile_id === profileId)
  const maxMapCell = analysis?.map_cells.reduce<typeof analysis.map_cells[number] | null>((best, cell) => {
    if (cell.max_score_pct === null) return best
    if (!best || best.max_score_pct === null || cell.max_score_pct > best.max_score_pct) return cell
    return best
  }, null) ?? null

  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#main-content" aria-label="Terra Analog home">
          <span className="brand-mark" aria-hidden="true"><span /><span /><span /></span>
          <span className="brand-name">terra<span>analog</span></span>
        </a>
        <div className="topbar-center">
          <span className="eyebrow">FIELDWORK CONSOLE</span>
          <span className="topbar-divider" aria-hidden="true" />
          <span className="topbar-caption">Earth analog discovery</span>
        </div>
        <a className="about-link" href="https://github.com/kamilr2000/Ewkam_Lab_NASA" target="_blank" rel="noreferrer">
          Project notes <span aria-hidden="true">↗</span>
        </a>
      </header>

      <section className="workspace" id="main-content" aria-labelledby="page-title">
        <aside className="control-panel" aria-label="Analysis setup">
          <div className="panel-heading">
            <span className="step-index">01</span>
            <div>
              <p className="eyebrow">BUILD A SEARCH</p>
              <h1 id="page-title">Find a place<br />that feels familiar.</h1>
            </div>
          </div>
          <p className="intro-copy">Compare measured terrain on Earth with a selected region beyond it. Start with a target and the features that matter to your fieldwork.</p>

          <div className={`data-mode-banner ${mode === 'synthetic' ? 'is-synthetic' : 'is-live'}`} role="status" aria-live="polite">
            <span className="status-dot" aria-hidden="true" />
            <div>
              <strong>{mode === 'synthetic' ? 'Synthetic demo' : 'Live API mode'}</strong>
              <p>{mode === 'synthetic'
                ? 'Contract fixtures only. These are not planetary measurements.'
                : 'Requests go to the configured API. Errors never switch to fixtures.'}</p>
            </div>
          </div>

          <div className="form-section">
            <label className="field-label" htmlFor="data-mode">Data source</label>
            <select id="data-mode" value={mode} onChange={(event) => changeMode(event.target.value as DataMode)}>
              <option value="synthetic">Synthetic fixture demo</option>
              <option value="live">Live API</option>
            </select>

            {mode === 'synthetic' && (
              <>
                <label className="field-label second-label" htmlFor="demo-scenario">Fixture scenario</label>
                <select id="demo-scenario" value={scenario} onChange={(event) => changeScenario(event.target.value as DemoScenario)}>
                  {demoScenarios.map((item) => <option key={item.id} value={item.id}>{item.label}</option>)}
                </select>
                <p className="field-help">{activeScenario?.description} The response preserves the query and values stored in that fixture.</p>
              </>
            )}

            <label className="field-label second-label" htmlFor="body-select">Destination body</label>
            <select id="body-select" value={body} onChange={(event) => chooseBody(event.target.value as PlanetaryBody)} disabled={catalogLoading || visibleProfiles.length === 0}>
              <option value="mars" disabled={!visibleProfiles.some((item) => item.body === 'mars')}>Mars{!visibleProfiles.some((item) => item.body === 'mars') ? ' — no profile available' : ''}</option>
              <option value="moon" disabled={!visibleProfiles.some((item) => item.body === 'moon')}>Moon{!visibleProfiles.some((item) => item.body === 'moon') ? ' — no profile available' : ''}</option>
            </select>

            <label className="field-label second-label" htmlFor="profile-select">Reference region</label>
            <select id="profile-select" value={profileId} onChange={(event) => chooseProfile(event.target.value)} disabled={catalogLoading || bodyProfiles.length === 0}>
              {bodyProfiles.length === 0 && <option value="">No available profile for this body</option>}
              {bodyProfiles.map((item) => <option key={item.profile_id} value={item.profile_id}>{item.name} · {item.region_name}</option>)}
            </select>
            {profileCatalogEntry && <p className="field-help">Profile {profileCatalogEntry.profile_version} · {profileCatalogEntry.availability.replace('_', ' ')}</p>}
            {mode === 'live' && (
              <>
                <label className="field-label second-label" htmlFor="search-region-select">Earth search region</label>
                <select
                  id="search-region-select"
                  value={searchRegionId}
                  onChange={(event) => chooseSearchRegion(event.target.value)}
                  disabled={catalogLoading || searchRegions.length === 0}
                >
                  {searchRegions.length === 0 && <option value="">No available regional Earth search package</option>}
                  {searchRegions.map((item) => <option key={item.region_id} value={item.region_id}>{item.name} · {item.dataset_version}</option>)}
                </select>
                {selectedSearchRegion && <p className="field-help">{selectedSearchRegion.description} Dataset {selectedSearchRegion.dataset_version}.</p>}
                {searchRegionError && <p className="inline-error" role="alert">{searchRegionError}</p>}

                <label className="field-label second-label" htmlFor="result-mode-select">Ranking view</label>
                <select id="result-mode-select" value={resultMode} onChange={(event) => changeResultMode(event.target.value as ResultMode)}>
                  <option value="pixels">Top 10 pixels</option>
                  <option value="distinct_areas">Distinct areas</option>
                </select>
                {resultMode === 'distinct_areas' && (
                  <>
                    <label className="field-label second-label" htmlFor="minimum-distance-km">Minimum separation (km)</label>
                    <input
                      id="minimum-distance-km"
                      type="number"
                      min="0.001"
                      max={MAX_AREA_DISTANCE_KM}
                      step="any"
                      value={minimumDistanceKm}
                      onChange={(event) => changeMinimumDistance(event.target.value)}
                      aria-describedby="distinct-distance-help"
                      aria-invalid={distanceValidationError ? true : undefined}
                    />
                    <p className="field-help" id="distinct-distance-help">The API selects representative pixels using this minimum geodesic separation. Switch to Top 10 pixels to see nearby cells without area selection.</p>
                    {distanceValidationError && <p className="inline-error" role="alert">{distanceValidationError}</p>}
                  </>
                )}
              </>
            )}
          </div>

          <div className="criteria-section">
            <div className="section-title-row">
              <div><p className="eyebrow">PROFILE FEATURES</p><h2>{mode === 'live' ? 'Scoring measurements' : 'Available measurements'}</h2></div>
              <span className="count-badge">{mode === 'live' ? `${activeCriteriaCount}/${profileFeatures.length}` : String(profileFeatures.length).padStart(2, '0')}</span>
            </div>
            <p className="section-hint">Feature definitions, units and reference ranges come from the selected {body === 'mars' ? 'Mars' : 'Moon'} profile. {mode === 'live' ? 'Choose one or more available measurements; the API scores the submitted set.' : 'Fixture results use their recorded query and do not recalculate scores in this browser.'}</p>
            {profileLoading && <p className="inline-state">Loading profile…</p>}
            {profileError && <p className="inline-error" role="alert">{profileError}</p>}
            {catalogError && <p className="inline-error" role="alert">{catalogError}</p>}
            {!profileLoading && !profileError && mode === 'live' && (
              <CriteriaControls
                features={profileFeatures}
                settings={criteriaSettings}
                onEnabledChange={changeCriterionEnabled}
                onWeightChange={changeCriterionWeight}
              />
            )}
            {!profileLoading && !profileError && mode === 'synthetic' && profileFeatures.length > 0 && (
              <ul className="criteria-list" aria-label="Measurements in the selected fixture profile">
                {profileFeatures.map((feature) => (
                  <li className="criterion fixture-criterion" key={feature.feature_id}>
                    <span className="criterion-symbol" aria-hidden="true">{feature.feature_id === 'slope_deg' ? '∠' : feature.feature_id === 'roughness_m' ? '≈' : '↕'}</span>
                    <span className="criterion-copy">
                      <span className="criterion-name">{feature.name}</span>
                      <span className="criterion-unit">{feature.unit} · reference {formatNumber(feature.reference_interval[0])}–{formatNumber(feature.reference_interval[1])}</span>
                    </span>
                    <span className="criterion-state">{feature.is_proxy ? 'PROXY' : 'PROFILE'}</span>
                  </li>
                ))}
              </ul>
            )}
            {!profileLoading && !profileError && mode === 'synthetic' && profile && profileFeatures.length === 0 && (
              <p className="inline-state">No measurements are available for this profile and selected Earth dataset.</p>
            )}
            {profile && profileFeatures.length > 0 && profileFeatures.length < profile.profile.features.length && (
              <p className="scope-note">Some profile measurements are not selectable in the current catalog and will not be sent.</p>
            )}
            {mode === 'synthetic' && <p className="scope-note">Fixture scenarios use preset features and weights. Switch to Live API to select measurements and configure their weights.</p>}
          </div>

          <div className="panel-bottom">
            <div className="service-note" role="status">
              <span className={`status-dot ${mode === 'synthetic' ? 'is-ready' : ''}`} aria-hidden="true" />
              <span>
                <strong>{catalogLoading ? 'Loading catalog' : catalogError ? 'Catalog unavailable' : mode === 'synthetic' ? 'Fixture catalog loaded' : 'Live catalog loaded'}</strong><br />
                {mode === 'synthetic' ? 'Each example is marked synthetic in its response.' : 'Catalog and search are requested from the configured API.'}
              </span>
            </div>
            <button className="run-button" type="button" onClick={() => void runAnalysis()} disabled={catalogLoading || profileLoading || !catalog || !profile || profileFeatures.length === 0 || Boolean(runConfigurationError) || searching}>
              <span>{searching ? 'Running analysis…' : 'Run terrain analysis'}</span><span aria-hidden="true">↗</span>
            </button>
            <p className="fine-print">0–100% is a similarity index for selected features, not a probability or a measure of habitability.</p>
          </div>
        </aside>

        <section className="results-area" aria-label="Analysis results">
          <div className="results-toolbar">
            <div className="breadcrumb"><span>WORKSPACE</span><span aria-hidden="true">/</span><strong>{analysis ? analysis.query.result_mode === 'pixels' ? 'PIXEL ANALYSIS' : 'DISTINCT AREAS' : 'NEW ANALYSIS'}</strong></div>
            <div className={`toolbar-status ${analysis ? 'is-complete' : ''}`} role="status" aria-live="polite"><span className="status-dot" aria-hidden="true" />{searching ? 'Analysis in progress' : searchError ? 'Request failed' : analysis ? (analysis.is_synthetic ? 'Synthetic response' : 'API response') : 'Awaiting analysis'}</div>
          </div>

          {analysis || searching || searchError ? (
            <MapModuleBoundary>
              <Suspense fallback={<div className="map-frame map-frame-loading" role="status"><p>Loading interactive map…</p></div>}>
                <AnalysisMap
                  analysis={analysis}
                  mode={mode}
                  layerVisibility={layerVisibility}
                  onLayerVisibilityChange={(layer, visible) => setLayerVisibility((current) => updateMapLayerVisibility(current, layer, visible))}
                  pixels={resultPixels}
                  selectedPixel={selectedPixel}
                  selectedPixelId={selectedPixelId}
                  zoomRequest={zoomRequest}
                  onSelectPixel={selectPixelAndZoom}
                  searchError={searchError}
                  onRetry={() => void runAnalysis()}
                  emptyMessage={searchError
                    ? `Analysis could not be loaded. ${searchError}`
                    : catalogError || (catalogLoading ? 'Loading the selected catalog and profile.' : 'Run the synthetic fixture or connect the live API to inspect a versioned result.')}
                />
              </Suspense>
            </MapModuleBoundary>
          ) : (
            <div className="map-frame map-frame-loading" role="region" aria-label="Interactive analysis map">
              <div className="map-frame-loading-content">
                <p className="eyebrow">MAP PREVIEW</p>
                <strong>Run an analysis to load the interactive map.</strong>
                <p>The map will use the same versioned result as the ranking and pixel details.</p>
              </div>
            </div>
          )}

          {analysis && (
            <div className="analysis-summary">
              <div className="analysis-summary-heading">
                <div>
                  <p className="eyebrow">{analysis.is_synthetic ? 'SYNTHETIC CONTRACT FIXTURE' : 'LIVE API RESPONSE'}</p>
                  <h2>{analysis.scope.region_name ?? (analysis.is_synthetic ? 'Synthetic fixture test universe' : 'Regional search scope')}</h2>
                </div>
                <span className="analysis-contract-tag">{analysis.grid_version} · {analysis.model_version}</span>
              </div>
              <p className="summary-description">{analysis.scope.description}</p>
              <div className="summary-metrics">
                <div><span>Eligible cells</span><strong>{formatNumber(analysis.coverage.eligible_pixels, 0)} / {formatNumber(analysis.coverage.total_pixels, 0)}</strong></div>
                <div><span>Eligible area</span><strong>{formatNumber(analysis.coverage.eligible_area_fraction === null ? null : analysis.coverage.eligible_area_fraction * 100)}{analysis.coverage.eligible_area_fraction === null ? '' : '%'}</strong></div>
                <div><span>Map display cells</span><strong>{formatNumber(analysis.map_cells.length, 0)}</strong></div>
              </div>
              {maxMapCell ? (
                <p className="map-maximum">Highest display-cell maximum: <strong>{formatNumber(maxMapCell.max_score_pct)}%</strong> · pixel <code>{maxMapCell.max_pixel_id}</code>. Its mean ({formatNumber(maxMapCell.mean_score_pct)}%) describes the cell as context; the fill shows only the best eligible pixel.</p>
              ) : (
                <p className="map-maximum no-data-note">No eligible pixel scores are available for the map. Missing data remain null; they are not zero.</p>
              )}
            </div>
          )}

          {analysis?.warnings.length ? <ul className="warning-list" aria-label="Analysis warnings">{analysis.warnings.map((warning) => <li key={`${warning.code}-${warning.message}`}>{warning.message}</li>)}</ul> : null}
          {analysis && <p className="analysis-id-line">Analysis <code>{analysis.analysis_id}</code> · contract {analysis.contract_version} · profile {analysis.query.profile_id} ({analysis.profile_version}) · dataset {analysis.dataset_version} · grid {analysis.grid_version} · model {analysis.model_version}</p>}

          <div className="results-bottom">
            <section className="result-card ranking-card" aria-labelledby="ranking-heading">
              <div className="card-heading">
                <div><p className="eyebrow">{analysis?.query.result_mode === 'distinct_areas' ? 'DISTINCT REPRESENTATIVES' : 'BEST MATCHES'}</p><h2 id="ranking-heading">{analysis?.query.result_mode === 'distinct_areas' ? 'Distinct areas' : 'Top 10 pixels'}</h2></div>
                <span className={`empty-tag ${resultPixels.length ? 'filled-tag' : ''}`}>{analysis ? `${resultPixels.length} RESULTS` : searchError ? 'ERROR' : 'NO RESULTS'}</span>
              </div>
              {resultPixels.length ? (
                <ol className="ranking-list" aria-label={analysis?.query.result_mode === 'distinct_areas' ? 'Distinct area representatives' : 'Top ranked pixels'}>
                  {resultPixels.map((pixel, index) => {
                    const areaEntry = analysis && 'area_ranking' in analysis && analysis.area_ranking
                      ? analysis.area_ranking.find((entry) => entry.representative_pixel.pixel_id === pixel.pixel_id) ?? null
                      : null
                    const resultRank = pixel.rank ?? areaEntry?.rank ?? index + 1
                    const separation = areaEntry?.nearest_selected_distance_km
                    const resultDescription = analysis?.query.result_mode === 'distinct_areas'
                      ? 'Representative pixel · candidate ' + (areaEntry?.candidate_id ?? 'unknown') + ' · ' +
                        (separation === null ? 'first selected' : separation === undefined ? 'distance unavailable' : 'nearest selected representative ' + formatNumber(separation) + ' km')
                      : 'Individual pixel'
                    return (
                      <li key={pixel.pixel_id}>
                        <button className={`ranking-row ${selectedPixelId === pixel.pixel_id ? 'is-selected' : ''}`} type="button" onClick={() => setSelectedPixelId(pixel.pixel_id)} aria-pressed={selectedPixelId === pixel.pixel_id}>
                          <span className="rank-number">{String(resultRank).padStart(2, '0')}</span>
                          <span className="rank-copy"><strong>{pixel.pixel_id}</strong><small>{formatNumber(pixel.pixel_area_km2)} km² cell · {resultDescription}</small></span>
                          <span className="rank-score">{pixel.score_pct === null ? '—' : `${formatNumber(pixel.score_pct)}%`}</span>
                        </button>
                      </li>
                    )
                  })}
                </ol>
              ) : (
                <div className="empty-list-state">
                  <span className="empty-glyph" aria-hidden="true">↗</span>
                  <p>{analysis
                    ? analysis.coverage.total_pixels === 0 ? 'No cells intersect this scope. This is an empty search, not a zero-score result.' : 'No cells have all active measurements. Missing values remain excluded, not scored as zero.'
                    : 'Run an analysis to rank individual physical grid cells.'}</p>
                </div>
              )}
              <p className="card-footnote">{analysis?.query.result_mode === 'distinct_areas' ? 'Each row is a representative pixel selected using the requested minimum distance. Run Top 10 pixels to inspect nearby cell candidates.' : 'Nearby cells can each appear in Top 10 pixels. Distinct areas is a separate mode with an explicit minimum distance.'}</p>
            </section>

            <section className="result-card pixel-card" aria-labelledby="pixel-heading">
              <div className="card-heading">
                <div><p className="eyebrow">SELECTED CELL</p><h2 id="pixel-heading">Pixel details</h2></div>
                <span className={`empty-tag ${selectedPixel ? 'filled-tag' : ''}`}>{selectedPixel ? 'IN ANALYSIS' : 'NO SELECTION'}</span>
              </div>
              {selectedPixel && analysis ? (
                <>
                  <div className="pixel-summary"><strong>{selectedPixel.pixel_id}</strong><span>{selectedPixel.score_pct === null ? 'Score unavailable' : `${formatNumber(selectedPixel.score_pct)}% similarity index`}</span></div>
                  <dl className="pixel-metadata">
                    <div><dt>Cell area</dt><dd>{formatNumber(selectedPixel.pixel_area_km2)} km²</dd></div>
                    <div><dt>Data coverage</dt><dd>{formatNumber(selectedPixel.coverage_fraction * 100)}%</dd></div>
                    <div><dt>Center</dt><dd>{formatNumber(selectedPixel.center[0], 4)}°, {formatNumber(selectedPixel.center[1], 4)}°</dd></div>
                    <div><dt>Quality flags</dt><dd>{selectedPixel.quality_flags.length ? selectedPixel.quality_flags.join(', ') : 'None recorded'}</dd></div>
                    <div><dt>Missing reasons</dt><dd>{selectedPixel.missing_reasons?.length ? selectedPixel.missing_reasons.join(', ') : 'None recorded'}</dd></div>
                  </dl>
                  <div className="feature-results">
                    {selectedPixel.features.map((feature) => (
                      <div className="feature-result" key={feature.feature_id}>
                        <div className="feature-result-title"><strong>{profileFeatures.find((item) => item.feature_id === feature.feature_id)?.name ?? feature.feature_id}</strong><span>{feature.similarity_pct === null ? 'No similarity value' : `${formatNumber(feature.similarity_pct)}% similarity`}</span></div>
                        <p>Scale {feature.measurement_scale} · measured {feature.value === null ? 'not available' : formatNumber(feature.value) + ' ' + feature.unit}{feature.value === null && feature.missing_reason ? ' · ' + feature.missing_reason.replaceAll('_', ' ') : ''} · reference {formatNumber(feature.reference_interval[0])}–{formatNumber(feature.reference_interval[1])} {feature.unit} · outside-interval tolerance {formatNumber(feature.tolerance)} {feature.unit} · weight share {formatNumber(feature.normalized_weight * 100)}% · weighted contribution {feature.contribution_pct === null ? 'not available' : formatNumber(feature.contribution_pct) + '%'}</p>
                        <small>Sources: {feature.source_ids.join(', ') || 'not listed'}</small>
                      </div>
                    ))}
                  </div>
                </>
              ) : (
                <p className="explanation-copy">Select a ranked pixel to inspect its measurements, units, reference interval, weighted contribution, source IDs and quality flags.</p>
              )}
              <p className="card-footnote">A zoomed view does not increase measurement resolution. Details stay tied to the displayed analysis ID.</p>
            </section>

            <section className="result-card explanation-card" aria-labelledby="explanation-heading">
              <div className="card-heading">
                <div><p className="eyebrow">READ THE RESULT</p><h2 id="explanation-heading">A transparent comparison</h2></div>
                <span className="info-mark" aria-hidden="true">i</span>
              </div>
              <p className="explanation-copy">The score is the API's 0–100% similarity index for the selected features. It is not a probability and does not establish that two environments are alike in every way.</p>
              {analysis ? (
                <>
                  <div className="legend-row"><span className="legend-swatch" aria-hidden="true" /><span>Similarity index</span><span className="legend-range">0–100%</span></div>
                  <p className="card-footnote">Data: {analysis.is_synthetic ? 'synthetic fixture' : analysis.dataset_version}. Grid {analysis.grid_version}; model {analysis.model_version}. Scope: {analysis.scope.type}.</p>
                </>
              ) : (
                <p className="card-footnote">The current catalog lists profile features and their units. No score is computed until an analysis response is returned.</p>
              )}
            </section>
          </div>

          <footer className="workspace-footer">
            <span>EARTH ANALOGS <span className="footer-separator">/</span> TERRAIN SCREENING</span>
            <span>{analysis?.is_synthetic ? 'Synthetic contract fixture · not a planetary observation.' : 'Source IDs appear when provided; full citations are not linked in this prototype.'}</span>
          </footer>
        </section>
      </section>
    </main>
  )
}

export default App
