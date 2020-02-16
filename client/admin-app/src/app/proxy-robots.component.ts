import { Component, OnInit } from "@angular/core";
import { Apollo, SubscriptionResult } from "apollo-angular";
import { Observable } from "rxjs";

import gql from "graphql-tag";
import { Subscription } from "apollo-angular";

import { ProxyRobots, ConnectionStatus } from "./types";
import { Utils } from "./utils";

@Component({
  selector: "app-proxy-robots",
  template: `
    <div class="card" style="width: 300px;">
      <div class="card-divider">
        {{ name }}
      </div>
      <div class="card-section">
        <h4>{{ status }}</h4>
        <p>{{ address }}</p>
      </div>
    </div>
  `
})
export class ProxyRobotsComponent implements OnInit {
  serverGame: Observable<ProxyRobots>;
  name: string;
  status: string;
  address: string;
  proxyRobotsSubscription: Observable<SubscriptionResult<ProxyRobots>>;

  constructor(private apollo: Apollo) {
    var proxyRobotsSubscription = new ProxyRobotsSubscription(apollo);
    this.proxyRobotsSubscription = proxyRobotsSubscription.subscribe();
    this.proxyRobotsSubscription.subscribe(result => {
      if (result.data) {
        console.log(
          "data received ; name = " +
            result.data.proxyRobots.name +
            ", up = " +
            result.data.proxyRobots.up.toString()
        );
        this.name = result.data.proxyRobots.name;
        this.status = Utils.updateStatus(result.data.proxyRobots.up);
        this.status == ConnectionStatus.Offline
          ? (this.address = "")
          : (this.address = result.data.proxyRobots.address);
      }
    });
  }

  ngOnInit() {
    console.log("Init");
    this.apollo
      .watchQuery<ProxyRobots>({
        query: gql`
          {
            proxyRobots {
              name
              up
              address
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        this.name = result.data.proxyRobots.name;
        this.status = Utils.updateStatus(result.data.proxyRobots.up);
        this.status == ConnectionStatus.Offline
          ? (this.address = "")
          : (this.address = result.data.proxyRobots.address);
      });
  }
}

export class ProxyRobotsSubscription extends Subscription<ProxyRobots> {
  document = gql`
    subscription proxyRobots {
      proxyRobots {
        name
        up
        address
      }
    }
  `;
}
