import { AfterViewInit, ChangeDetectorRef, Component, Input, TemplateRef, ViewChild } from '@angular/core';
import { MapControl, MapService } from "../map.service";
import { FloatingDialog } from "../../dialogs/help-dialog/help-dialog.component";
import { MatDialog, MatDialogRef } from "@angular/material/dialog";
import { MapLayer, MapLayerGroup, VectorLayer } from '../layers';

@Component({
  selector: 'app-legend',
  templateUrl: './legend.component.html',
  styleUrls: ['./legend.component.scss']
})
export class LegendComponent implements AfterViewInit {
  @Input() target!: string;
  @Input() showInternal: boolean = true;
  @Input() showExternal: boolean = true;
  @ViewChild('legendImage') legendImageTemplate?: TemplateRef<any>;
  legendImageDialogs: Record<number | string, MatDialogRef<any>> = {};
  mapControl?: MapControl;
  layerGroups: MapLayerGroup[] = [];
  protected activeGroups: MapLayerGroup[] = [];
  Object = Object;

  constructor(public dialog: MatDialog, private mapService: MapService, private cdRef: ChangeDetectorRef) {
  }

  ngAfterViewInit (): void {
    this.mapControl = this.mapService.get(this.target);
    this.cdRef.detectChanges();
    this.mapControl.zoomToProject();
    this.mapControl.layerGroups.subscribe(groups => {
      let layerGroups: MapLayerGroup[] = [];
      // ToDo filter
      groups.forEach(group => {
        if (group.children.length === 0 || (!this.showExternal && group.external) || (!this.showInternal && !group.external))
          return;
        layerGroups.push(group);
      });
      this.layerGroups = layerGroups;
      this.filterActiveGroups();
    })
  }

  /**
   * handle changed check state of layer
   *
   * @param layer
   */
  toggleLayer(layer: MapLayer): void {
    layer.setVisible(false);
    this.filterActiveGroups();
  }

  // ToDo: use template filter
  filterActiveGroups(): void {
    this.activeGroups = this.layerGroups.filter(g => g.children!.filter(l => l.visible).length > 0);
  }

  /**
   * open a dialog with the legend image of given layer
   *
   * @param layer
   */
  toggleLegendImage(layer: MapLayer): void {
    if (layer.id === undefined) return;
    let dialogRef = this.legendImageDialogs[layer.id];
    if (dialogRef && dialogRef.getState() === 0)
      dialogRef.close();
    else
      this.legendImageDialogs[layer.id] = this.dialog.open(FloatingDialog, {
        panelClass: 'help-container',
        hasBackdrop: false,
        autoFocus: false,
        data: {
          title: layer.name,
          context: { layer: layer },
          template: this.legendImageTemplate
        }
      });
  }

  toggleLabel(layer: VectorLayer): void {
    layer.setShowLabel(!layer.showLabel);
  }

  toggleLayerLegend(layer: VectorLayer): void {
    if (!layer.legend) return;
    layer.legend.elapsed = !layer.legend.elapsed;
  }

}
