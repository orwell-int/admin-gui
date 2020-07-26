import { Component, OnInit } from "@angular/core";
import { Apollo, SubscriptionResult } from "apollo-angular";
import { Observable } from "rxjs";

import gql from "graphql-tag";
import { Subscription } from "apollo-angular";

import {
  SimpleTeams,
  Teams,
  RobotsQuery,
  Robot,
  GameQuery,
  Game
} from "./types";

@Component({
  selector: "app-game",
  template: `
    <div class="card" style="width: 700px;">
      <div class="card-divider">
        Game
      </div>
      <div class="card-section">
        <h4 *ngIf="game?.running; else notRunning">
          Time Left: {{ game.time }}/{{ game.duration }}
        </h4>
        <ng-template #notRunning>
          <h4>Game is not running</h4>
        </ng-template>
        <div class="card" style="width: 300px;" *ngFor="let team of teams">
          <div class="card-divider">
            {{ team.name }}
          </div>
          <div class="card-section">
            <p>Score: {{ team.score }}</p>
            <p *ngFor="let robot of team.robots">Robot: {{ robot.name }}</p>
          </div>
        </div>
      </div>
      <div class="card-section">
        <h4>Robots</h4>
        <table>
          <thead>
            <tr>
              <th>Status</th>
              <th>Robot</th>
              <th>IP</th>
              <th>Description</th>
              <th>Player</th>
              <th>Client IP</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let robot of robots">
              <td></td>
              <td>{{ robot.name }}</td>
              <td></td>
              <td></td>
              <td>{{ robot.player.name }}</td>
              <td></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `
})
export class GameComponent implements OnInit {
  teams: SimpleTeams;
  teamsSubscription: Observable<SubscriptionResult<Teams>>;
  robots: Robot[];
  game: Game;
  gameSubscription: Observable<SubscriptionResult<GameQuery>>;
  robotsSubscription: Observable<SubscriptionResult<RobotsQuery>>;

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
        console.log("Team or robot data is null (like the devs)");
      }
    });

    var gameSubscription = new GameSubscription(apollo);
    this.gameSubscription = gameSubscription.subscribe();
    this.gameSubscription.subscribe(result => {
      if (result.data) {
        console.log("Game data is NOT null");

        this.game = result.data.game;
      } else {
        console.log("Game data is null");
      }
    });

    var robotsSubscription = new RobotsSubscription(apollo);
    this.robotsSubscription = robotsSubscription.subscribe();
    this.robotsSubscription.subscribe(result => {
      if (result.data) {
        this.robots = result.data.robots;
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
              robots {
                name
              }
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

    console.log("Looking for Game info");

    this.apollo
      .watchQuery<GameQuery>({
        query: gql`
          {
            game {
              running
              duration
              time
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        if (result.data) {
          this.game = result.data.game;
          console.log("Game data is NOT null");
        } else {
          console.log("Game data is null");
        }
      });

    this.apollo
      .watchQuery<RobotsQuery>({
        query: gql`
          {
            robots {
              name
              player {
                name
              }
            }
          }
        `
      })
      .valueChanges.subscribe(result => {
        if (result.data) {
          if (result.data) {
            this.robots = result.data.robots;
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
        robots {
          name
        }
      }
    }
  `;
}

export class GameSubscription extends Subscription<GameQuery> {
  document = gql`
    subscription game {
      game {
        running
        duration
        time
      }
    }
  `;
}

export class RobotsSubscription extends Subscription<RobotsQuery> {
  document = gql`
    subscription robots {
      robots {
        name
        player {
          name
        }
      }
    }
  `;
}
