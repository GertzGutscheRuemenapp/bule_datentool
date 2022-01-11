import { AfterViewInit, ChangeDetectorRef, Component, Input, OnInit } from '@angular/core';
import { MapControl, MapService } from "../map.service";
import { LayerGroup, Layer } from "../../pages/basedata/external-layers/external-layers.component";
import { HttpClient } from "@angular/common/http";
import { CookieService } from "../../helpers/cookies.service";

@Component({
  selector: 'app-legend',
  templateUrl: './legend.component.html',
  styleUrls: ['./legend.component.scss']
})
export class LegendComponent implements AfterViewInit {

  @Input() target!: string;
  layers: any;
  mapControl!: MapControl;
  activeBackground?: number;
  backgroundOpacity = 1;
  backgroundLayers: Layer[] = [];
  layerGroups: LayerGroup[] = [];
  activeGroups: LayerGroup[] = [];
  editMode: boolean = true;
  Object = Object;

  constructor(private mapService: MapService, private cdRef:ChangeDetectorRef, private cookies: CookieService) {
  }

  ngAfterViewInit (): void {
    this.mapControl = this.mapService.get(this.target);
    this.initSelect();
  }

  initSelect(): void {
    this.backgroundLayers = this.mapControl.getBackgroundLayers();
    const background = parseInt(<string>this.cookies.get(`background-layer`) || this.backgroundLayers[0].id.toString());
    this.activeBackground = background;
    this.mapControl.setBackground(background);

    this.mapService.getLayers().subscribe(groups => {
      this.layerGroups = groups;
      groups.forEach(group => group.children!.forEach(layer => {
        layer.checked = <boolean>(this.cookies.get(`legend-layer-checked-${layer.id}`) || false);
        if (layer.checked) this.mapControl.toggleLayer(layer.id, true);
      }))
    })
    this.filterActiveGroups();
    this.cdRef.detectChanges();
  }

  onLayerToggle(layer: Layer): void {
    layer.checked = !layer.checked;
    this.cookies.set(`legend-layer-checked-${layer.id}`, layer.checked);
    this.mapControl.toggleLayer(layer.id, layer.checked);
    this.filterActiveGroups();
  }

  // ToDo: use template filter
  filterActiveGroups(): void {
    this.activeGroups = this.layerGroups.filter(g => g.children!.filter(l => l.checked).length > 0);
  }

  opacityChanged(id: number, value: number | null): void {
    if(value === null) return;
    this.mapControl?.setLayerAttr(id, { opacity: value });
  }

  setBackground(id: number) {
    this.cookies.set(`background-layer`, id);
    this.mapControl.setBackground(id);
  }
}
