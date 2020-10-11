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
  running: boolean;
  duration: Int32Array;
  time: Int32Array;
};

export type GameQuery = {
  game: Game;
};

export type Robot = {
  name: string;
  status: RobotStatus;
  registered: boolean;
  player: {
    name: string;
    address: string;
  };
};

export enum RobotStatus {
  Ok = 1,
  Warning,
  Ko
}

export type RobotsQuery = {
  robots: Robot[];
};

export type SimpleTeams = [
  {
    name: string;
    score: string;
    robots: Robot[];
  }
];

export type Teams = {
  teams: SimpleTeams;
};

export enum ConnectionStatus {
  Online = "Online",
  Offline = "Offline"
}
