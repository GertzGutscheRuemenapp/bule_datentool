import { Component, ElementRef, AfterViewInit, Renderer2, OnDestroy } from '@angular/core';
import { MapService } from "../../map/map.service";
import Projection from "ol/proj/Projection";
import { FormControl } from "@angular/forms";


interface Project {
  user?: string;
  shared?: boolean;
  editable?: boolean;
  name: string;
  id: number
}

const mockMyProjects: Project[] = [
  { name: 'Beispielprojekt 1', id: 1 },
  { name: 'Beispielprojekt 2', id: 2, shared: true },
  { name: 'Beispielprojekt 3', id: 3 }
]

const mockSharedProjects: Project[] = [
  { name: 'Beispielprojekt 4', user: 'Sascha Schmidt', id: 4, editable: true, shared: true },
  { name: 'Beispielprojekt 5', user: 'Magdalena Martin', id: 5, editable: false, shared: true }
]

@Component({
  selector: 'app-planning',
  templateUrl: './planning.component.html',
  styleUrls: ['./planning.component.scss']
})
export class PlanningComponent implements AfterViewInit, OnDestroy {

  myProjects: Project[] = mockMyProjects;
  sharedProjects: Project[] = mockSharedProjects;
  activeProject?: Project;
  processForm = new FormControl();
  showScenarioMenu: boolean = false;

  constructor(private renderer: Renderer2, private elRef: ElementRef, private mapService: MapService) {  }

  ngAfterViewInit(): void {
    // there is no parent css selector yet but we only want to hide the overflow in the planning pages
    let wrapper = this.elRef.nativeElement.closest('mat-sidenav-content');
    this.renderer.setStyle(wrapper, 'overflow', 'hidden');
    this.mapService.create('planning-map');
  }

  ngOnDestroy(): void {
    this.mapService.remove('planning-map');
  }

  onProcessChange(id: number): void {
    let project = this.getProject(id);
    this.activeProject = project;
  }

  getProject(id: number): Project {
    return this.myProjects.concat(this.sharedProjects).filter(project => project.id === id)[0];
  }

  toggleScenarioMenu(): void{
    this.showScenarioMenu = !this.showScenarioMenu;
  }
}
