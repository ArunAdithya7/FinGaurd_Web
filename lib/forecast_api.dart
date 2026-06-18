import 'dart:convert';
import 'package:http/http.dart' as http;

class ForecastApi {
  static const String baseUrl = 'http://10.0.2.2:8000';

  static Future<Map<String, dynamic>> fetchForecast(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/forecast/summary'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(data);
    } else {
      throw Exception(data['detail'] ?? 'Failed to load forecast');
    }
  }
}
