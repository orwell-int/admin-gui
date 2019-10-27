import { Component, OnInit } from '@angular/core';
import { Apollo } from 'apollo-angular';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import gql from 'graphql-tag';

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
  constructor(private apollo: Apollo) {}

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