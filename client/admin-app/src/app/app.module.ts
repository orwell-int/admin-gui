import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";

import { AppComponent } from "./app.component";
import { ServerGameComponent } from "./server-game.component";
import { ProxyRobotsComponent } from "./proxy-robots.component";
import { GameComponent } from "./game.component";

// Apollo
import { GraphQLModule } from "./graphql.module";

@NgModule({
  imports: [
    BrowserModule,
    // Apollo
    GraphQLModule
  ],
  declarations: [
    AppComponent,
    ServerGameComponent,
    ProxyRobotsComponent,
    GameComponent
  ],
  bootstrap: [AppComponent]
})
export class AppModule {}
