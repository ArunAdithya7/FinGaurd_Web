class ApiConfig {
  // Your PC's Local Wi-Fi IP address
  static const String pcIp = "172.23.49.230";

  // Base URL pointing to FastAPI server
  // On physical phone over Wi-Fi or USB reverse port forwarding:
  static const String baseUrl = "http://10.0.2.2:8000";
  
  // Backup / Wi-Fi URL for physical phone:
  static const String wifiUrl = "http://$pcIp:8000";
}
