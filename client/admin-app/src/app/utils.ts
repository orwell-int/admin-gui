export class Utils {
  static updateStatus(isUp: boolean) {
    if (isUp == true) {
      return "Online";
    } else {
      return "Offline";
    }
  }
}
