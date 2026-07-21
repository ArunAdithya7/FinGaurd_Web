import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  // Android emulator -> use 10.0.2.2 instead of localhost
  // Real phone -> use your PC IP address
  static const String baseUrl = "http://10.0.2.2:8000";

  static Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
  }) async {
    final url = Uri.parse('$baseUrl/auth/login');

    try {
      final response = await http
          .post(
            url,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({"identifier": identifier, "password": password}),
          )
          .timeout(const Duration(seconds: 3));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {
          "success": true,
          "message": data["message"] ?? "Login successful",
          "token": data["token"] ?? "demo_token",
          "user":
              data["user"] ?? {"full_name": identifier, "email": identifier},
        };
      } else {
        return {"success": false, "message": data["detail"] ?? "Login failed"};
      }
    } catch (_) {
      // Seamless demo login fallback if local backend is offline
      return {
        "success": true,
        "message": "Welcome! (Running in Demo Mode)",
        "token": "demo_token_123",
        "user": {"full_name": identifier, "email": identifier},
      };
    }
  }

  static Future<Map<String, dynamic>> signup({
    required String fullName,
    required String email,
    required String mobile,
    required String password,
  }) async {
    final url = Uri.parse('$baseUrl/auth/signup');

    try {
      final response = await http
          .post(
            url,
            headers: {"Content-Type": "application/json"},
            body: jsonEncode({
              "full_name": fullName,
              "email": email,
              "mobile": mobile,
              "password": password,
            }),
          )
          .timeout(const Duration(seconds: 3));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {"success": true, "message": data["message"] ?? "Account created"};
      } else {
        return {"success": false, "message": data["detail"] ?? "Signup failed"};
      }
    } catch (_) {
      return {"success": true, "message": "Account created! (Demo Mode)"};
    }
  }
}
