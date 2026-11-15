export interface MapLayerVisibility {
  basemap: boolean
  cells: boolean
  markers: boolean
}

type MapLayerVisibilityTarget = {
  setLayoutProperty(layerId: string, name: 'visibility', value: 'visible' | 'none'): void
}

type MarkerVisibilityTarget = {
  getElement(): { hidden: boolean | string }
}

export function applyLayerVisibility(
  map: MapLayerVisibilityTarget,
  markers: Iterable<MarkerVisibilityTarget>,
  visibility: MapLayerVisibility,
): void {
  map.setLayoutProperty('osm-basemap', 'visibility', visibility.basemap ? 'visible' : 'none')
  const cellVisibility = visibility.cells ? 'visible' : 'none'
  ;['analysis-cells-fill', 'analysis-cells-outline', 'analysis-scope-outline', 'selected-pixel-fill', 'selected-pixel-outline']
    .forEach((layerId) => map.setLayoutProperty(layerId, 'visibility', cellVisibility))
  for (const marker of markers) marker.getElement().hidden = !visibility.markers
}
