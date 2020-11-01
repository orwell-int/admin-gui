import { Component, OnInit } from "@angular/core";
import { Apollo, SubscriptionResult } from "apollo-angular";
import { Observable } from "rxjs";

import gql from "graphql-tag";
import { Subscription } from "apollo-angular";

import { ServerGame, ConnectionStatus } from "./types";
import { Utils } from "./utils";

@Component({
  selector: "app-server-game",
  template: `
    <div class="card" id="ServerGame">
      <div class="card-divider">
        {{ name }}
      </div>
      <div class="card-section">
        <h4>{{ status }} {{ address }}</h4>
      </div>
    </div>
  `
})
export class ServerGameComponent implements OnInit {
  serverGame: Observable<ServerGame>;
  name: string;
  status: string;
  address: string;
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
        this.status = Utils.updateStatus(result.data.serverGame.up);
        this.status == ConnectionStatus.Offline
          ? (this.address = "")
          : (this.address = result.data.serverGame.address);
      }
    });
  }

  ngOnInit() {
    console.log("Init Server-Game");
    this.apollo
      .watchQuery<ServerGame>({
        query: gql`
          {
            serverGame {
              name
              up
              address
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        this.name = result.data.serverGame.name;
        this.status = Utils.updateStatus(result.data.serverGame.up);
        this.status == ConnectionStatus.Offline
          ? (this.address = "")
          : (this.address = result.data.serverGame.address);
      });
  }
}

export class ServerGameSubscription extends Subscription<ServerGame> {
  document = gql`
    subscription serverGame {
      serverGame {
        name
        up
        address
      }
    }
  `;
}
