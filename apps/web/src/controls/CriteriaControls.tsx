import type { ProfileFeature } from '../api/types'
import {
  CRITERION_WEIGHT_STEP,
  MAX_CRITERION_WEIGHT,
  MIN_CRITERION_WEIGHT,
  getActiveCriteria,
  getCriteriaValidationError,
} from './criteria'
import type { CriteriaSettings } from './criteria'

interface CriteriaControlsProps {
  features: readonly ProfileFeature[]
  settings: CriteriaSettings
  onEnabledChange: (featureId: string, enabled: boolean) => void
  onWeightChange: (featureId: string, weight: number) => void
}

function formatNumber(value: number, maximumFractionDigits = 1): string {
  return value.toLocaleString('en-US', { maximumFractionDigits })
}

function symbolForFeature(featureId: string): string {
  if (featureId === 'slope_deg') return '∠'
  if (featureId === 'roughness_m') return '≈'
  return '↕'
}

export function CriteriaControls({
  features,
  settings,
  onEnabledChange,
  onWeightChange,
}: CriteriaControlsProps) {
  const activeCriteria = getActiveCriteria(features, settings)
  const activeById = new Map(activeCriteria.map((criterion) => [criterion.feature.feature_id, criterion]))
  const validationError = features.length > 0 ? getCriteriaValidationError(features, settings) : null

  return (
    <fieldset className="criteria-controls" aria-describedby="criteria-selection-summary">
      <legend className="visually-hidden">Scoring measurements</legend>
      {features.length === 0 ? (
        <p className="inline-state">No measurements are available for this profile and dataset.</p>
      ) : (
        <ul className="criteria-list" aria-label="Available scoring measurements">
          {features.map((feature) => {
            const setting = settings[feature.feature_id] ?? { enabled: false, weight: 1 }
            const activeCriterion = activeById.get(feature.feature_id)
            const featureKey = encodeURIComponent(feature.feature_id)
            const weightInputId = `criterion-weight-${featureKey}`
            const normalizedPercent = activeCriterion?.normalizedWeight === null || !activeCriterion
              ? null
              : activeCriterion.normalizedWeight * 100

            return (
              <li className={`criterion ${setting.enabled ? '' : 'is-disabled'}`} key={feature.feature_id}>
                <div className="criterion-header">
                  <label className="criterion-select" htmlFor={`criterion-enabled-${featureKey}`}>
                    <input
                      id={`criterion-enabled-${featureKey}`}
                      type="checkbox"
                      checked={setting.enabled}
                      aria-label={`Include ${feature.name} in analysis`}
                      onChange={(event) => onEnabledChange(feature.feature_id, event.target.checked)}
                    />
                    <span className="criterion-symbol" aria-hidden="true">{symbolForFeature(feature.feature_id)}</span>
                    <span className="criterion-copy">
                      <span className="criterion-name">{feature.name}</span>
                      <span className="criterion-unit">{feature.unit} · reference {formatNumber(feature.reference_interval[0])}–{formatNumber(feature.reference_interval[1])}</span>
                    </span>
                  </label>
                  <span className="criterion-state">{feature.is_proxy ? 'PROXY' : 'PROFILE'}</span>
                </div>
                {setting.enabled && (
                  <div className="criterion-weight">
                    <label htmlFor={weightInputId}>Weight <span>{formatNumber(setting.weight)}</span></label>
                    <input
                      id={weightInputId}
                      type="range"
                      min={MIN_CRITERION_WEIGHT}
                      max={MAX_CRITERION_WEIGHT}
                      step={CRITERION_WEIGHT_STEP}
                      value={setting.weight}
                      aria-label={`${feature.name} weight`}
                      aria-valuetext={`${formatNumber(setting.weight)} raw weight${normalizedPercent === null ? '' : `; normalized to ${formatNumber(normalizedPercent)} percent`}`}
                      onChange={(event) => onWeightChange(feature.feature_id, Number(event.target.value))}
                    />
                    <output htmlFor={weightInputId} className="criterion-normalized">
                      {normalizedPercent === null ? '—' : `${formatNumber(normalizedPercent)}% share`}
                    </output>
                  </div>
                )}
              </li>
            )
          })}
        </ul>
      )}
      <p id="criteria-selection-summary" className="criteria-selection-summary" role="status">
        {activeCriteria.length} of {features.length} measurements selected. Positive weights are normalized across the active set.
      </p>
      {validationError && <p className="inline-error" role="alert">{validationError}</p>}
    </fieldset>
  )
}
