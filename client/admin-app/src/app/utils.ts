import { ConnectionStatus } from "./types";

export class Utils {
  static updateStatus(isUp: boolean) {
    if (isUp) {
      return ConnectionStatus.Online;
    } else {
      return ConnectionStatus.Offline;
    }
  }
}
