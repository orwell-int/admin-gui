import { Component, OnInit } from "@angular/core";
import { Apollo, SubscriptionResult } from "apollo-angular";
import { Observable } from "rxjs";

import gql from "graphql-tag";
import { Subscription } from "apollo-angular";

import { ServerGame } from "./types";

@Component({
  selector: "app-server-game",
  template: `
    <div class="card" style="width: 300px;">
      <div class="card-divider">
        Server-Game
      </div>
      <div class="card-section">
        <h4>{{ name }} is</h4>
        <p>{{ up }}</p>
      </div>
    </div>
  `
})
export class ServerGameComponent implements OnInit {
  serverGame: Observable<ServerGame>;
  name: string;
  up: boolean;
  serverGameSubscription: Observable<SubscriptionResult<ServerGame>>;

  constructor(private apollo: Apollo) {
    var serverSubscription = new ServerGameSubscription(apollo);
    this.serverGameSubscription = serverSubscription.subscribe();
    this.serverGameSubscription.subscribe(result => {
      if (result.data) {
        console.log(
          "data received ; name = " +
            result.data.serverGame.name +
            ", up = " +
            result.data.serverGame.up.toString()
        );
        this.name = result.data.serverGame.name;
        this.up = result.data.serverGame.up;
      }
    });
  }

  ngOnInit() {
    console.log("Init");
    this.apollo
      .watchQuery<ServerGame>({
        query: gql`
          {
            serverGame {
              name
              up
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        this.name = result.data.serverGame.name;
        this.up = result.data.serverGame.up;
      });
  }
}

export class ServerGameSubscription extends Subscription<ServerGame> {
  document = gql`
    subscription serverGame {
      serverGame {
        name
        up
      }
    }
  `;
}
