import {Component, OnInit, ViewEncapsulation} from '@angular/core';
import {circle, LatLng, latLng, Layer, Map, tileLayer} from 'leaflet';
import {LeafletLayersModel} from './leaflet-layers.model';
import {LeafletDrawDirective} from '@asymmetrik/ngx-leaflet-draw';
import {DisasterService} from '../disaster.service';
import {UtilsService} from '../utils.service';
import {DisasterTaxonomies, WizardSteps} from '../enums';

@Component({
  selector: 'app-map',
  templateUrl: './map.component.html',
  styleUrls: ['./map.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class MapComponent implements OnInit {
  /*** GLOBALS ********************************************************************************************************/
  map: Map;
  leafletDrawDirective: LeafletDrawDirective;
  earthquakeBaseLayer: any;
  hurricaneBaseLayers: any;

  /*** MAP PARAMETERS *************************************************************************************************/
  LAYER_OSM = {
    id: 'openstreetmap',
    name: 'Open Street Map',
    enabled: false,
    layer: tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: 'Open Street Map'
    })
  };
  model = new LeafletLayersModel([this.LAYER_OSM], this.LAYER_OSM.id, []);
  layers: Layer[];
  options = {
    zoom: 10,
    center: latLng(30.619026, -96.338900)
  };
  drawOptions = {
    position: 'topright',
    draw: {
      marker: false,
      rectangle: false,
      circlemarker: false,
      circle: false,
      polyline: false
    }
  };

  hotPatchLeafletCircleRadiusIssue() {
    // hot patch issue with leaflet-draw circle resize
    // REF: https://stackoverflow.com/a/48063394/1067005

    /* tslint:disable */
    // @ts-ignore
    declare var L: any;
    L.Edit.Circle = L.Edit.CircleMarker.extend({
      _createResizeMarker: function () {
        var center = this._shape.getLatLng(),
          resizemarkerPoint = this._getResizeMarkerPoint(center);

        this._resizeMarkers = [];
        this._resizeMarkers.push(this._createMarker(resizemarkerPoint, this.options.resizeIcon));
      },
      _getResizeMarkerPoint: function (latlng) {
        let delta = this._shape._radius * Math.cos(Math.PI / 4),
          point = this._map.project(latlng);
        return this._map.unproject([point.x + delta, point.y - delta]);
      },
      _resize: function (latlng) {
        let moveLatLng = this._moveMarker.getLatLng();
        let radius;
        if (L.GeometryUtil.isVersion07x()) {
          radius = moveLatLng.distanceTo(latlng);
        } else {
          radius = this._map.distance(moveLatLng, latlng);
        }

        // **** This fixes the cicle resizing ****
        this._shape.setRadius(radius);

        this._map.fire(L.Draw.Event.EDITRESIZE, {layer: this._shape});
      }
    });
    /* tslint:enable */
  }

  apply() {
    // Get the active base layer
    const baseLayer = this.model.baseLayers.find((l: any) => (l.id === this.model.baseLayer));

    // Get all the active overlay layers
    const newLayers = this.model.overlayLayers
      .filter((l: any) => l.enabled)
      .map((l: any) => l.layer);
    newLayers.unshift(baseLayer.layer);

    this.layers = newLayers;

    return false;
  }

  /*** COMMON METHODS *************************************************************************************************/
  stateUpdated() {
    switch (this.disasterService.state.wizardStep) {
      case WizardSteps.DisasterChoice:
        this.clearMap();
        break;
      case WizardSteps.InputParameters:
        break;
      case WizardSteps.Simulation:
        break;
      case WizardSteps.Results:
        break;
    }
  }

  enableMapEdit() {
    if (!this.leafletDrawDirective) {
      return;
    }
    // @ts-ignore
    this.leafletDrawDirective._toolbars.edit._modes.edit.handler.enable();
  }

  clearMap() {
    if (!this.leafletDrawDirective) {
      return;
    }
    // @ts-ignore
    this.leafletDrawDirective.options.edit.featureGroup.clearLayers();
  }

  baseLayerUpdated() {
    if (this.disasterService.state.chosenDisaster === DisasterTaxonomies.Earthquake) {
      this.disasterService.earthquakeParameters.center = this.earthquakeBaseLayer._latlng;
      this.disasterService.earthquakeParameters.radius = this.earthquakeBaseLayer._mRadius;
    } else if (this.disasterService.state.chosenDisaster === DisasterTaxonomies.Hurricane) {
      this.disasterService.hurricaneParameters.start.center = this.hurricaneBaseLayers.start._latlng;
      this.disasterService.hurricaneParameters.start.radius = this.hurricaneBaseLayers.start._mRadius;
      this.disasterService.hurricaneParameters.end.center = this.hurricaneBaseLayers.end._latlng;
      this.disasterService.hurricaneParameters.end.radius = this.hurricaneBaseLayers.end._mRadius;
    }
  }

  /*** EARTHQUAKE *****************************************************************************************************/
  startEarthquake(params = null) {
    this.clearMap();

    let latlng;
    latlng = params ? params.latlng : this.map.getCenter();

    this.disasterService.earthquakeParameters.center = latlng;

    this.earthquakeBaseLayer = circle(latlng, {radius: 10000});
    // @ts-ignore
    this.leafletDrawDirective.options.edit.featureGroup.addLayer(this.earthquakeBaseLayer);

    this.enableMapEdit();

    // earthquake intensity color
    this.earthquakeIntensityUpdated();
    this.disasterService.earthquakeIntensityUpdated$.subscribe(() => this.earthquakeIntensityUpdated());
  }

  earthquakeIntensityUpdated() {
      const color = this.utils.percentageToColor(this.disasterService.earthquakeParameters.intensity);
      this.earthquakeBaseLayer.setStyle({
          color: color,
          fillColor: color,
          fillOpacity: 0.3,
      });
  }

  /*** HURRICANE ******************************************************************************************************/
  startHurricane() {
    this.clearMap();

    let latlng = this.map.getCenter();

    this.hurricaneBaseLayers = {
      start: circle(latlng, {radius: 10000}),
      end: circle(new LatLng(latlng.lat + 0.4, latlng.lng + 0.4), {radius: 5000}),
    };

    // @ts-ignore
    this.leafletDrawDirective.options.edit.featureGroup.addLayer(this.hurricaneBaseLayers.start);
    // @ts-ignore
    this.leafletDrawDirective.options.edit.featureGroup.addLayer(this.hurricaneBaseLayers.end);

    this.enableMapEdit();

    // intensity colors
    this.hurricaneUpdated();
    this.disasterService.hurricaneUpdated$.subscribe(() => this.hurricaneUpdated());
  }

  hurricaneUpdated() {
      let color = this.utils.percentageToColor(this.disasterService.hurricaneParameters.start.intensity);
      this.hurricaneBaseLayers.start.setStyle({
          color: color,
          fillColor: color,
          fillOpacity: 0.3,
      });
      color = this.utils.percentageToColor(this.disasterService.hurricaneParameters.end.intensity);
      this.hurricaneBaseLayers.end.setStyle({
          color: color,
          fillColor: color,
          fillOpacity: 0.3,
      });
  }

  /*** CLASS METHODS **************************************************************************************************/
  constructor(private disasterService: DisasterService, private utils: UtilsService) {
    this.apply();
    this.disasterService.stateUpdated$.subscribe(() => this.stateUpdated());
    this.disasterService.earthquakeStarted$.subscribe((params) => this.startEarthquake(params));
    this.disasterService.hurricaneStarted$.subscribe(() => this.startHurricane());
  }

  ngOnInit() {
    this.hotPatchLeafletCircleRadiusIssue();
  }

  onMapReady(map: Map) {
    this.map = map;
  }

  onLeafletDrawReady(leafletDrawDirective: LeafletDrawDirective) {
    this.leafletDrawDirective = leafletDrawDirective;
  }
}
