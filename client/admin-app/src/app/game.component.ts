import { Component, OnInit } from "@angular/core";
import { Apollo, SubscriptionResult } from "apollo-angular";
import { Observable } from "rxjs";

import gql from "graphql-tag";
import { Subscription } from "apollo-angular";

import { SimpleTeams, Teams } from "./types";

@Component({
  selector: "app-game",
  template: `
    <div class="card" style="width: 700px;">
      <div class="card-divider">
        Game
      </div>
      <div class="card-section">
        <h4>Time Left</h4>
        <div class="card" style="width: 300px;" *ngFor="let team of teams">
          <div class="card-divider">
            {{ team.name }}
          </div>
          <div class="card-section">
            <p>Score: {{ team.score }}</p>
            <p>Player: {{ teamMember }}</p>
          </div>
        </div>
      </div>
    </div>
  `
})
export class GameComponent implements OnInit {
  teams: SimpleTeams;
  teamsSubscription: Observable<SubscriptionResult<Teams>>;

  constructor(private apollo: Apollo) {
    console.log("Constructor Game onInit");
    var teamsSubscription = new TeamsSubscription(apollo);
    this.teamsSubscription = teamsSubscription.subscribe();
    this.teamsSubscription.subscribe(result => {
      if (result.data) {
        if (result.data.teams.length > 0) {
          this.teams = result.data.teams;
        }
      } else {
        console.log("Team data is null (like the devs)");
      }
    });
  }

  ngOnInit() {
    console.log("Init Game");
    this.apollo
      .watchQuery<Teams>({
        query: gql`
          {
            teams {
              name
              score
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        if (result.data) {
          if (result.data.teams.length > 0) {
            this.teams = result.data.teams;
          }
        }
      });
  }
}

export class TeamsSubscription extends Subscription<Teams> {
  document = gql`
    subscription teams {
      teams {
        name
        score
      }
    }
  `;
}
