import { NgModule } from "@angular/core";
import { BrowserModule } from "@angular/platform-browser";

import { AppComponent } from "./app.component";
import { ServerGameComponent } from "./server-game.component";

// Apollo
import { GraphQLModule } from "./graphql.module";
import { ProxyRobotsComponent } from "./proxy-robots.component";

@NgModule({
  imports: [
    BrowserModule,
    // Apollo
    GraphQLModule
  ],
  declarations: [AppComponent, ServerGameComponent, ProxyRobotsComponent],
  bootstrap: [AppComponent]
})
export class AppModule {}
