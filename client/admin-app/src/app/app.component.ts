import { Component } from "@angular/core";

@Component({
  selector: "app-root",
  template: `
    <header>
      <div class="top-bar">
        <div class="top-bar-left">
          <ul class="dropdown menu" data-dropdown-menu>
            <li class="menu-text">ORWELL ADMIN</li>
            <li><a href="#ProxyRobots">ProxyRobots</a></li>
            <li><a href="#Game">Game</a></li>
            <li><a href="#Robots">Robots</a></li>
          </ul>
        </div>
      </div>
    </header>
    <br />
    <div class="grid-container">
      <div class="grid-x grid-margin-x">
        <app-server-game class="cell medium-auto"></app-server-game>
        <app-proxy-robots class="cell medium-auto"></app-proxy-robots>
      </div>
      <app-game></app-game>
    </div>
  `
})
export class AppComponent {}
