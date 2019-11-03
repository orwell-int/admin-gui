import { Component, OnInit } from '@angular/core';
import { Apollo, SubscriptionResult } from 'apollo-angular';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import gql from 'graphql-tag';
import {Subscription} from 'apollo-angular';

import { ServerGame } from './types';

@Component({
  selector: 'app-server-game',
  template: `
    <h1>Server-Game {{name}} is {{up}}</h1>
  `
})
export class ServerGameComponent implements OnInit {
  serverGame: Observable<ServerGame>;
  name: string;
  up: boolean;
  serverGameSubscription: Observable<SubscriptionResult<ServerGame>>;

  constructor(private apollo: Apollo) {
    var serverSubscription = new ServerSubscription(apollo);
    this.serverGameSubscription = serverSubscription.subscribe();
    this.serverGameSubscription.subscribe(
      (result => {
        if (result.data)
        {
          console.log("data received ; name = " + result.data.server.name + ", up = " + result.data.server.up.toString());
          this.name = result.data.server.name;
          this.up = result.data.server.up;
        }
      })
    );
  }

  ngOnInit() {
    console.log("Init");
    this.apollo.watchQuery<ServerGame>({
      query: gql`
      {
          server {
            name,
            up
      }
    }
      `,
    })
      .valueChanges
      .subscribe(
        (result => {
            this.name = result.data.server.name;
            this.up = result.data.server.up;})
      );
  }
}

export class ServerSubscription extends Subscription<ServerGame> {
  document = gql`
    subscription server
    {
      server
      {
        name,
        up
      }
    }
  `;
}