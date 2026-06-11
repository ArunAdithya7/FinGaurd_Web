import 'dart:convert';
import 'package:http/http.dart' as http;

class DashboardApi {
  static const String baseUrl = 'https://m8bkbk54-8000.inc1.devtunnels.ms';

  static Future<Map<String, dynamic>> fetchDashboard(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/dashboard/summary'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(data);
    } else {
      throw Exception(data['detail'] ?? 'Failed to load dashboard');
    }
  }
}
