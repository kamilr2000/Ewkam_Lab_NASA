const criteria = [
  { label: 'Surface slope', symbol: '∠', unit: 'degrees' },
  { label: 'Local roughness', symbol: '≈', unit: 'metres' },
  { label: 'Relative relief', symbol: '↕', unit: 'metres' },
]

function App() {
  return (
    <main className="app-shell">
      <header className="topbar">
        <a className="brand" href="#main-content" aria-label="Terra Analog home">
          <span className="brand-mark" aria-hidden="true">
            <span />
            <span />
            <span />
          </span>
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
          <p className="intro-copy">
            Compare measured terrain on Earth with a selected region beyond it.
            Start with a target and the features that matter to your fieldwork.
          </p>

          <div className="form-section">
            <label className="field-label" htmlFor="body-select">Destination body</label>
            <select id="body-select" defaultValue="mars" disabled aria-describedby="service-note">
              <option value="mars">Mars</option>
              <option value="moon">Moon</option>
            </select>
            <label className="field-label second-label" htmlFor="profile-select">Reference region</label>
            <select id="profile-select" defaultValue="pending" disabled aria-describedby="service-note">
              <option value="pending">Profiles appear when data is connected</option>
            </select>
          </div>

          <div className="criteria-section">
            <div className="section-title-row">
              <div>
                <p className="eyebrow">TERRAIN CRITERIA</p>
                <h2>What should match?</h2>
              </div>
              <span className="count-badge">03</span>
            </div>
            <p className="section-hint">Available criteria depend on the selected profile.</p>
            <ul className="criteria-list" aria-label="Planned terrain criteria">
              {criteria.map((criterion) => (
                <li className="criterion" key={criterion.label}>
                  <span className="criterion-symbol" aria-hidden="true">{criterion.symbol}</span>
                  <span className="criterion-copy">
                    <span className="criterion-name">{criterion.label}</span>
                    <span className="criterion-unit">{criterion.unit}</span>
                  </span>
                  <span className="criterion-state">CORE</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="panel-bottom">
            <div className="service-note" id="service-note" role="status">
              <span className="status-dot" aria-hidden="true" />
              <span><strong>Analysis service not connected</strong><br />Search controls will be available with the data API.</span>
            </div>
            <button className="run-button" type="button" disabled>
              <span>Run terrain analysis</span><span aria-hidden="true">↗</span>
            </button>
            <p className="fine-print">Results are a terrain similarity index, not a measure of habitability.</p>
          </div>
        </aside>

        <section className="results-area" aria-label="Analysis results">
          <div className="results-toolbar">
            <div className="breadcrumb"><span>WORKSPACE</span><span aria-hidden="true">/</span><strong>NEW ANALYSIS</strong></div>
            <div className="toolbar-status"><span className="status-dot" aria-hidden="true" />Awaiting analysis</div>
          </div>

          <div className="map-frame" aria-label="Map canvas awaiting analysis data">
            <div className="map-grid" aria-hidden="true" />
            <div className="map-coordinate coordinate-nw">GLOBAL TERRAIN VIEW <span>·</span> WGS 84</div>
            <div className="map-coordinate coordinate-ne">NO ACTIVE DATASET</div>
            <div className="map-empty-state">
              <div className="orbit-mark" aria-hidden="true"><span /><span /><span /></div>
              <p className="eyebrow">YOUR NEXT FIELD SITE STARTS HERE</p>
              <h2>A world of terrain,<br />waiting to be explored.</h2>
              <p>Connect an analysis to see measured cells, source coverage and the strongest matching locations.</p>
            </div>
            <div className="map-coordinate coordinate-sw">MAP LAYERS <span>·</span> NOT YET LOADED</div>
            <div className="map-coordinate coordinate-se">CELL OUTLINES WILL REFLECT THE ANALYSIS GRID</div>
            <div className="map-scale" aria-label="Map scale unavailable"><span /><span>—</span><span>Scale unavailable</span></div>
          </div>

          <div className="results-bottom">
            <section className="result-card ranking-card" aria-labelledby="ranking-heading">
              <div className="card-heading">
                <div><p className="eyebrow">BEST MATCHES</p><h2 id="ranking-heading">Top 10 pixels</h2></div>
                <span className="empty-tag">NO RESULTS</span>
              </div>
              <div className="empty-list-state">
                <span className="empty-glyph" aria-hidden="true">↗</span>
                <p>Run an analysis to rank individual grid cells.</p>
              </div>
              <p className="card-footnote">Nearby cells can each appear in the ranking.</p>
            </section>

            <section className="result-card explanation-card" aria-labelledby="explanation-heading">
              <div className="card-heading">
                <div><p className="eyebrow">READ THE RESULT</p><h2 id="explanation-heading">A transparent comparison</h2></div>
                <span className="info-mark" aria-hidden="true">i</span>
              </div>
              <p className="explanation-copy">Each score will show the measured value, its unit, reference range and weighted contribution—alongside source scale and quality flags.</p>
              <div className="legend-row"><span className="legend-swatch" aria-hidden="true" /><span>Similarity index</span><span className="legend-range">0–100%</span></div>
              <p className="card-footnote">A similarity index describes selected terrain features; it does not establish that two environments are alike in every way.</p>
            </section>
          </div>

          <footer className="workspace-footer">
            <span>EARTH ANALOGS <span className="footer-separator">/</span> TERRAIN SCREENING</span>
            <span>NASA data sources will be cited with each released analysis.</span>
          </footer>
        </section>
      </section>
    </main>
  )
}

export default App
