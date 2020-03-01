export type ServerGame = {
  serverGame: {
    name: string;
    up: boolean;
    address: string;
  };
};

export type ProxyRobots = {
  proxyRobots: {
    name: string;
    up: boolean;
    address: string;
  };
};

export type Game = {
  game: {};
};

export type Robot = {
  robot: {
    name: string;
    registered: boolean;
    player: {
      name: string;
    };
  };
};

export type SimpleTeams = [
  {
    name: string;
    score: string;
  }
];

export type Teams = {
  teams: SimpleTeams;
};

export enum ConnectionStatus {
  Online = "Online",
  Offline = "Offline"
}
