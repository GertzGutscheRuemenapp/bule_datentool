import { AfterViewInit, ChangeDetectorRef, Component, OnDestroy } from '@angular/core';
import { MapControl, MapService } from "../../../map/map.service";
import { AreaLevel, BasedataSettings } from "../../../backendInterfaces";
import { Observable } from "rxjs";
import { sortBy } from "../../../helpers/utils";
import { HttpClient } from "@angular/common/http";
import { MatDialog } from "@angular/material/dialog";
import { RestAPI } from "../../../rest-api";
import { mockAreaLevels } from "./areas";


@Component({
  selector: 'app-areas',
  templateUrl: './areas.component.html',
  styleUrls: ['../../../map/legend/legend.component.scss','./areas.component.scss']
})
export class AreasComponent implements AfterViewInit, OnDestroy {
  mapControl?: MapControl;
  selectedAreaLevel?: AreaLevel;
  basedataSettings?: BasedataSettings;
  presetLevels!: AreaLevel[];
  areaLevels?: AreaLevel[];
  colorSelection: string = 'black';

  constructor(private mapService: MapService, private cdRef:ChangeDetectorRef, private http: HttpClient, private dialog: MatDialog,
              private rest: RestAPI) { }

  ngAfterViewInit(): void {
    this.mapControl = this.mapService.get('base-areas-map');
    this.mapControl.setBackground(this.mapControl.getBackgroundLayers()[0].id);

    this.fetchBasedataSettings().subscribe(res => {
      this.fetchLayerGroups().subscribe(res => {
        this.selectedAreaLevel = this.presetLevels[0];
        this.colorSelection = this.selectedAreaLevel.layer?.symbol?.fillColor || 'black';
        this.areaLevels = mockAreaLevels;
      })
    })
  }

  /**
   * fetch basedata-settings
   */
  fetchBasedataSettings(): Observable<BasedataSettings> {
    const query = this.http.get<BasedataSettings>(this.rest.URLS.basedataSettings);
    query.subscribe((basedataSettings) => {
      this.basedataSettings = basedataSettings;
    });
    return query;
  }

  /**
   * fetch areas
   */
  fetchLayerGroups(): Observable<AreaLevel[]> {
    const query = this.http.get<AreaLevel[]>(this.rest.URLS.arealevels);
    query.subscribe((areaLevels) => {
      this.presetLevels = sortBy(areaLevels, 'order');
    });
    return query;
  }

  ngOnDestroy(): void {
    this.mapControl?.destroy();
  }

  onSelect(areaLevel: AreaLevel): void {
    this.selectedAreaLevel = areaLevel;
    this.colorSelection = this.selectedAreaLevel.layer?.symbol?.fillColor || 'black';
  }

  onCreateArea(): void {
  }

  onDeleteArea(): void {
  }

}
