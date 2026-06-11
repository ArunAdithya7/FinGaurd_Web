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

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"identifier": identifier, "password": password}),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {
        "success": true,
        "message": data["message"],
        "token": data["token"],
        "user": data["user"],
      };
    } else {
      return {"success": false, "message": data["detail"] ?? "Login failed"};
    }
  }

  static Future<Map<String, dynamic>> signup({
    required String fullName,
    required String email,
    required String mobile,
    required String password,
  }) async {
    final url = Uri.parse('$baseUrl/auth/signup');

    final response = await http.post(
      url,
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({
        "full_name": fullName,
        "email": email,
        "mobile": mobile,
        "password": password,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return {"success": true, "message": data["message"]};
    } else {
      return {"success": false, "message": data["detail"] ?? "Signup failed"};
    }
  }
}
