import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <app-server-game></app-server-game>
    <app-proxy-robots></app-proxy-robots>
    <app-game></app-game>
  `
})
export class AppComponent {}
