import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <header>
      <div id="title"></div>
      <nav>ORWELL ADMIN PAGE</nav>
    </header>
    <div class="grid-x grid-margin-x">
      <app-server-game class="cell medium-auto"></app-server-game>
      <app-proxy-robots class="cell medium-auto"></app-proxy-robots>
    </div>
    <app-game></app-game>
  `
})
export class AppComponent {}
