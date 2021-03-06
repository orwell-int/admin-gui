import { Component, OnInit } from "@angular/core";
import { Apollo, SubscriptionResult } from "apollo-angular";
import { Observable } from "rxjs";

import gql from "graphql-tag";
import { Subscription } from "apollo-angular";

import { ProxyRobots } from "./types";

@Component({
  selector: "app-proxy-robots",
  template: `
    <div class="card" style="width: 300px;">
      <div class="card-divider">
        Proxy-Robots
      </div>
      <div class="card-section">
        <h4>{{ name }} is</h4>
        <p>{{ up }}</p>
      </div>
    </div>
  `
})
export class ProxyRobotsComponent implements OnInit {
  serverGame: Observable<ProxyRobots>;
  name: string;
  up: boolean;
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
        this.up = result.data.proxyRobots.up;
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
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        this.name = result.data.proxyRobots.name;
        this.up = result.data.proxyRobots.up;
      });
  }
}

export class ProxyRobotsSubscription extends Subscription<ProxyRobots> {
  document = gql`
    subscription proxyRobots {
      proxyRobots {
        name
        up
      }
    }
  `;
}
