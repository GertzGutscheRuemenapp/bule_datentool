import { Injectable, EventEmitter } from '@angular/core';
import { AreaLevel, ExtLayer, ExtLayerGroup, Symbol } from '../rest-interfaces';
import { OlMap } from './map'
import { BehaviorSubject, forkJoin, Observable } from "rxjs";
import { HttpClient } from "@angular/common/http";
import { RestAPI } from "../rest-api";
import { sortBy } from "../helpers/utils";
import { WKT } from "ol/format";
import { SettingsService } from "../settings.service";
import { environment } from "../../environments/environment";
import { v4 as uuid } from 'uuid';
import { SelectionModel } from "@angular/cdk/collections";
import { Feature } from 'ol';
import { Layer as OlLayer } from 'ol/layer'
import { Geometry, Polygon, Point } from "ol/geom";
import { getCenter } from 'ol/extent';
import { Icon, Style } from "ol/style";
import { RestCacheService } from "../rest-cache.service";
import { MapLayerGroup, MapLayer, VectorTileLayer, WMSLayer, TileLayer, VectorLayer } from "./layers";

interface BackgroundLayerDef {
  name: string,
  url: string,
  description: string,
  attribution?: string,
  layerName?: string,
  type: 'tiles' | 'wms'
}

const backgroundLayers: BackgroundLayerDef[] = [
  {
    name: 'OSM',
    url: 'https://{a-c}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    description: 'Offizielle Weltkarte von OpenStreetMap',
    attribution: '©<a target="_blank" href="https://www.openstreetmap.org/copyright">OpenStreetMap-Mitwirkende<a>',
    type: 'tiles',
  },
  {
    name: 'TopPlusOpen',
    url: 'https://sgx.geodatenzentrum.de/wms_topplus_open',
    description: 'Weltweite einheitliche Webkarte vom BKG. Normalausgabe',
    type: 'wms',
    layerName: 'web'
  },
  {
    name: 'TopPlusOpen grau',
    url: 'https://sgx.geodatenzentrum.de/wms_topplus_open',
    description: 'Weltweite einheitliche Webkarte vom BKG. Graustufendarstellung',
    type: 'wms',
    layerName: 'web_grau'
  }
]



@Injectable({
  providedIn: 'root'
})
export class MapService {
  private controls: Record<string, MapControl> = {};
  backgroundLayers: any[] = backgroundLayers;
  // layerGroups$?: BehaviorSubject<Array<ExtLayerGroup>>;

  constructor(private http: HttpClient, private restService: RestCacheService, private settings: SettingsService) { }

  get(target: string): MapControl {
    let control = this.controls[target];
    if(!control){
      control = new MapControl(target, this, this.settings);
      control.destroyed.subscribe(target => delete this.controls[target]);
      control.init();
      this.controls[target] = control;
    }
    return control;
  }

  getLayers( options?: { internal?: boolean, external?: boolean, reset?: boolean } ): Observable<MapLayerGroup[]>{
    const observable = new Observable<MapLayerGroup[]>(subscriber => {
      const observables: Observable<MapLayerGroup[]>[] = [];
      if (options?.internal)
        observables.push(this.fetchInternalLayers(options?.reset));
      if (options?.external)
        observables.push(this.fetchExternalLayers({ reset: options?.reset, active: true }));
      forkJoin(...observables).subscribe((merged: MapLayerGroup[]) => {
        // @ts-ignore
        const flatGroups: MapLayerGroup[] = [].concat.apply([], merged);
        subscriber.next(flatGroups);
        subscriber.complete();
      })
    });
    return observable;
  }

  private fetchInternalLayers(reset: boolean = false): Observable<MapLayerGroup[]> {
    const observable = new Observable<MapLayerGroup[]>(subscriber => {
      this.restService.getAreaLevels({ active: true, reset: reset }).subscribe(levels => {
        levels = sortBy(levels, 'order');//.reverse();
        let groups = [];
        const group = new MapLayerGroup('Gebiete', { order: 2, external: false });
        let layers: MapLayer[] = [];
        sortBy(levels, 'order').forEach(level => {
          // skip levels with no symbol (aka should not be displayed)
          if (!level.symbol) return;
          // areas have no fill
          level.symbol.fillColor = '';
          let tileUrl = level.tileUrl!;
          // "force" https in production, backend returns http (running in container)
          if (environment.production) {
            tileUrl = tileUrl.replace('http:', 'https:');
          }
          const mLayer = new VectorTileLayer(level.name, tileUrl, {
            description: `Gebiete der Gebietseinheit ${level.name}`,
            style: level.symbol,
            labelField: level.labelField
          })
          layers.push(mLayer);
        });
        if (layers) {
          layers.forEach(mlayer => group.addLayer(mlayer));
          groups.push(group);
        }
        subscriber.next(groups);
        subscriber.complete();
      })
    })
    return observable;
  }

  fetchExternalLayers(options?: { reset?: boolean, active?: boolean }): Observable<MapLayerGroup[]> {
    const observable = new Observable<MapLayerGroup[]>(subscriber => {
      this.restService.getLayerGroups({ reset: options?.reset }).subscribe(groups => {
        groups = sortBy(groups, 'order');
        const mGroups: MapLayerGroup[] = groups.map(group =>
          new MapLayerGroup(group.name, { id: group.id, external: group.external, order: group.order }));
        let layerOptions: any = { reset: options?.reset };
        if (options?.active !== undefined)
          layerOptions.active = options?.active;
        this.restService.getLayers(layerOptions).subscribe(layers => {
          layers = sortBy(layers, 'order');
          layers.forEach(layer => {
            const mGroup = mGroups.find(mGroup => { return mGroup.id === layer.group });
            if (mGroup) {
              const mLayer = new WMSLayer(layer.name, layer.url!,{
                layerName: layer.layerName,
                description: layer.description,
                order: layer.order,
                active: layer.active
              })
              mGroup.addLayer(mLayer);
            }
          })
          subscriber.next(mGroups);
          subscriber.complete();
        })
      })
    })
    return observable;
  }
}

export class MapControl {
  srid = 3857;
  target = '';
  destroyed = new EventEmitter<string>();
  map?: OlMap;
  mapDescription = '';
  layerGroups: BehaviorSubject<Array<MapLayerGroup>> = new BehaviorSubject<Array<MapLayerGroup>>([]);
  private _layerGroups: MapLayerGroup[] = [];
  private markerLayer?: MapLayer;
  mapExtents: any = {};
  editMode: boolean = true;
  background?: TileLayer;
  backgroundLayers: TileLayer[] = [];
  markerImg = `${environment.backend}/static/img/map-marker-red.svg`;

  constructor(target: string, private mapService: MapService, private settings: SettingsService) {
    this.target = target;
    // call destroy on page reload
    window.onbeforeunload = () => this.destroy();
    this.settings.user?.get('extents').subscribe(extents => {
      this.mapExtents = extents || {};
    })
  }

  init(): void {
    this.map = new OlMap(this.target, { projection: `EPSG:${this.srid}` });
    this.map.selected.subscribe(evt => {
      if (evt.selected && evt.selected.length > 0)
        this.onFeatureSelected(evt.layer, evt.selected);
      if (evt.deselected && evt.deselected.length > 0)
        this.onFeatureDeselected(evt.layer, evt.deselected);
    })
    this.settings.user?.get(this.target).subscribe(mapSettings => {
      mapSettings = mapSettings || {};
      const editMode = mapSettings['legend-edit-mode'];
      this.editMode = (editMode != undefined)? editMode : true;
      const backgroundId = parseInt(mapSettings[`background-layer`]);
      this.mapService.backgroundLayers.forEach(layerDef => {
        const opacity = parseFloat(mapSettings[`layer-opacity-${layerDef.id}`]) || 1;
        const bg = (layerDef.type === 'wms')?
          new WMSLayer(layerDef.name, layerDef.url, {visible: layerDef.id === backgroundId}):
          new TileLayer(layerDef.name, layerDef.url, {visible: layerDef.id === backgroundId});
        this.backgroundLayers.push(bg);
        bg.addToMap(this.map);
      });
      this.background = this.mapService.backgroundLayers.find(
        l => { return l.id === backgroundId }) || this.backgroundLayers[1];
/*      if (this.background)
        this.background.s = mapSettings[`layer-opacity-${this.background.id}`] || 1;*/
/*      for (let layer of this.mapService.backgroundLayers) {
          layer.opacity = parseFloat(mapSettings[`layer-opacity-${layer.id}`]) || 1;*/
/*        this._addLayerToMap(layer, {
          visible: layer === this.background
        });*/
    })
    this.getServiceLayerGroups();
    this.markerLayer = new VectorLayer('marker-layer', {});
    this.markerLayer.addToMap(this.map);
      /*
      this.map!.addVectorLayer('marker-layer',
      {stroke: {width: 5, color: 'red'}, fill: {color: 'red'}, radius: 10, visible: true, zIndex: 100});*/
  }

  private getServiceLayerGroups(reset: boolean = false): void {
    this.mapService.getLayers({ reset: reset }).subscribe(layerGroups => {
      // ToDo: remember former checked layers on reset
      layerGroups.forEach(group => {
        if (!group.children) return;
        this.addGroup(group);
/*        for (let layer of group.layers!.slice().reverse()) {
          let visible = false;
          // if (Boolean(this.mapSettings[`layer-checked-${layer.id}`])) {
          //   this.checklistSelection.select(layer);
          //   visible = true;
          // }
          // layer.opacity = parseFloat(this.mapSettings[`layer-opacity-${layer.id}`]) || 1;
          this._addLayerToMap(layer, { visible: visible });
        }*/
      })
      this.layerGroups.next(this._layerGroups.filter(g => g.global));
    })
  }

  getLayers(): MapLayer[] {
    let layers: MapLayer[] = [];
    this._layerGroups.forEach(g => layers.concat(g.children));
    // if (this.background) layers.push(this.background);
    return layers;
  }

  getLayer(id: number |string): MapLayer | undefined {
    // ToDo: background as well?
    return this.getLayers().find(l => l.id === id);
  }

  getGroup(id: number | string): MapLayerGroup | undefined {
    // ToDo: background as well?
    return this._layerGroups.find(g => g.id === id);
  }

  addLayer(layer: MapLayer, emit?: boolean): void {
    // if (layer.map) throw `Layer ${layer.name} already set to another map`;
    if (layer.map !== this.map) layer.map = this.map;
    if (!layer.group) {
      let group = this._layerGroups.find(group => group.name === 'Sonstiges');
      if (!group){
        group = new MapLayerGroup('Sonstiges', { order: 0 });
        this.addGroup(group, false);
      }
      group.addLayer(layer);
    }
    if (emit) this.layerGroups.next(this._layerGroups);
  }
/*

  private _addVectorLayerToMap(layer: MapLayer): OlLayer<any>{

  }

  private _addVectorTileLayerToMap(layer: MapLayer): OlLayer<any>{

  }

  private _addWmsLayerToMap(layer: MapLayer):
*/

  getBackgroundLayers(): ExtLayer[]{
    return this.mapService.backgroundLayers;
  }

  addMarker(geometry: Geometry): Feature<any> {
    this.removeMarker();
    if (geometry instanceof Polygon) {
      geometry = new Point(getCenter(geometry.getExtent()));
    }
    const marker = new Feature(geometry);

    const iconStyle = new Style({
      image: new Icon({
        anchor: [0.5, 0.8],
        anchorXUnits: 'fraction',
        anchorYUnits: 'fraction',
        src: this.markerImg,
        scale: 0.05
      }),
    });

    marker.setStyle(iconStyle);
    this.map?.addFeatures('marker-layer', [marker]);
    return marker;
  }

  removeMarker(): void {
    this.map?.clear('marker-layer');
  }

  refresh(options?: { internal?: boolean, external?: boolean }): void {
    this.getLayers().forEach(l => l.removeFromMap());
    this.getServiceLayerGroups();
  }

  /**
   * add a layer-group to this map only
   * sets unique id if id is undefined
   *
   * @param group
   * @param emit
   */
  addGroup(group: MapLayerGroup, emit= true): void {
    if (group.id == undefined)
      group.id = uuid();
    if (!group.map) {
      group.map = this.map;
      group.children.forEach(layer => layer.addToMap(this.map));
    }
    this._layerGroups.push(group);
    if (emit) this.layerGroups.next(this._layerGroups);
  }

  /**
   * remove a layer-group and its children, can only remove groups added specifically to this map
   * (not the global ones)
   *
   * @param id
   * @param emit
   */
  removeGroup(group: MapLayerGroup, emit= true): void {
    const idx = this._layerGroups.findIndex(g => g === group);
    if (idx < 0) return;
    group.clear();
    this._layerGroups.splice(idx, 1);
    if (emit) this.layerGroups.next(this._layerGroups);
  }

  private onFeatureSelected(ollayer: OlLayer<any>, selected: Feature<any>[]): void {
    const layer = this.getLayer(ollayer.get('name'));
    if (layer && layer.featureSelected)
      selected.forEach(feature => layer.featureSelected!.emit({ feature: feature, selected: true }));
  }

  private onFeatureDeselected(ollayer: OlLayer<any>, deselected: Feature<any>[]): void {
    const layer = this.getLayers().find(l => l.mapId === ollayer.get('id'));
    if (layer)
      deselected.forEach(feature => layer.featureSelected!.emit({ feature: feature, selected: false }));
  }

  setBackground(id: number): void {
/*    this.mapSettings['background-layer'] = id;
    const layer = this.layerMap[id];*/
    this.background = this.backgroundLayers.find(l => l.id === id);
    this.backgroundLayers.forEach(l => l.setVisible(l.id === id));
  }

  zoomTo(layer: MapLayer): void {
    if (!layer.mapId) return;
    const mapLayer = this.map?.getLayer(layer.mapId),
          _this = this;
    mapLayer!.getSource().once('featuresloadend', (evt: any) => {
      this.map?.centerOnLayer(layer.mapId!);
    })
  }

  zoomToProject(): void {
    this.settings.projectSettings$.subscribe(settings => {
      if (!settings.projectArea) return;
      const format = new WKT();
      const wktSplit = settings.projectArea.split(';'),
            epsg = wktSplit[0].replace('SRID=','EPSG:'),
            wkt = wktSplit[1];

      const feature = format.readFeature(wkt);
      feature.getGeometry().transform(epsg, `EPSG:${this.srid}`);
      this.map?.map.getView().fit(feature.getGeometry().getExtent());
    })
  }

  toggleEditMode(): void {
    this.editMode = !this.editMode;
  }

  saveCurrentExtent(name: string): void {
    this.mapExtents[name] = this.map?.view.calculateExtent();
  }

  loadExtent(name: string): void {
    const extent = this.mapExtents[name];
    if (!extent) return;
    this.map?.view.fit(extent);
  }

  removeExtent(name: string): void {
    delete this.mapExtents[name];
  }

  saveSettings(): void {
    let mapSettings: any = {};
    const layers = this.getLayers();
    layers.forEach(layer => {
      if (layer.id != undefined) {
        mapSettings[`layer-opacity-${layer.id}`] = layer.opacity;
        mapSettings[`layer-visibility-${layer.id}`] = layer.visible;
      }
    })
    mapSettings['background-layer'] = this.background?.id;
    mapSettings['legend-edit-mode'] = this.editMode;
    this.settings.user?.set(this.target, mapSettings, { patch: true });
    this.settings.user?.set('extents', this.mapExtents, { patch: true });
  }

  destroy(): void {
    this.saveSettings();
    if(!this.map) return;
    this.map.unset();
    this.destroyed.emit(this.target);
  }

}
