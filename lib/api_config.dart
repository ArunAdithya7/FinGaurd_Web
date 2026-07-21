import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiConfig {
  static const List<String> candidateUrls = [
    "http://127.0.0.1:8000",
    "https://rich-coins-slide.loca.lt",
    "http://10.0.2.2:8000",
    "http://localhost:8000",
  ];

  static Future<http.Response> get(String endpoint, String token) async {
    Object? lastException;
    for (final base in candidateUrls) {
      try {
        final url = Uri.parse('$base$endpoint');
        final response = await http.get(
          url,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
            'bypass-tunnel-reminder': 'true',
          },
        ).timeout(const Duration(seconds: 4));
        return response;
      } catch (e) {
        lastException = e;
      }
    }
    throw Exception('Failed to connect to backend server ($lastException)');
  }

  static Future<http.Response> post(
    String endpoint,
    Map<String, dynamic> body, {
    String? token,
  }) async {
    Object? lastException;
    for (final base in candidateUrls) {
      try {
        final url = Uri.parse('$base$endpoint');
        final headers = <String, String>{
          'Content-Type': 'application/json',
          'bypass-tunnel-reminder': 'true',
        };
        if (token != null && token.isNotEmpty) {
          headers['Authorization'] = 'Bearer $token';
        }
        final response = await http
            .post(
              url,
              headers: headers,
              body: jsonEncode(body),
            )
            .timeout(const Duration(seconds: 4));
        return response;
      } catch (e) {
        lastException = e;
      }
    }
    throw Exception('Failed to connect to backend server ($lastException)');
  }

  static Future<http.Response> put(
    String endpoint,
    Map<String, dynamic> body, {
    String? token,
  }) async {
    Object? lastException;
    for (final base in candidateUrls) {
      try {
        final url = Uri.parse('$base$endpoint');
        final headers = <String, String>{
          'Content-Type': 'application/json',
          'bypass-tunnel-reminder': 'true',
        };
        if (token != null && token.isNotEmpty) {
          headers['Authorization'] = 'Bearer $token';
        }
        final response = await http
            .put(
              url,
              headers: headers,
              body: jsonEncode(body),
            )
            .timeout(const Duration(seconds: 4));
        return response;
      } catch (e) {
        lastException = e;
      }
    }
    throw Exception('Failed to connect to backend server ($lastException)');
  }
}
