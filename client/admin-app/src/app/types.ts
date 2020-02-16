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

export enum ConnectionStatus {
  Online = "Online",
  Offline = "Offline"
}
