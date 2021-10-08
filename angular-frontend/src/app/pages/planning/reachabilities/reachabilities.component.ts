import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-reachabilities',
  templateUrl: './reachabilities.component.html',
  styleUrls: ['./reachabilities.component.scss']
})
export class ReachabilitiesComponent implements OnInit {
  selectMode = false;
  transportMode = 1;

  constructor() { }

  ngOnInit(): void {
  }

}
