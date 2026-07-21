import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const List<String> candidateUrls = [
    "http://10.0.2.2:8000",
    "http://172.23.49.230:8000",
    "http://localhost:8000",
  ];

  static Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
  }) async {
    String? lastError;

    for (final baseUrl in candidateUrls) {
      try {
        final url = Uri.parse('$baseUrl/auth/login');
        final response = await http
            .post(
              url,
              headers: {"Content-Type": "application/json"},
              body: jsonEncode({"identifier": identifier, "password": password}),
            )
            .timeout(const Duration(seconds: 4));

        final data = jsonDecode(response.body);

        if (response.statusCode == 200) {
          return {
            "success": true,
            "message": data["message"] ?? "Login successful",
            "token": data["token"],
            "user": data["user"],
          };
        } else {
          return {
            "success": false,
            "message": data["detail"] ?? "Invalid credentials",
          };
        }
      } catch (e) {
        lastError = e.toString();
      }
    }

    return {
      "success": false,
      "message": "Cannot connect to server at 10.0.2.2 or 172.23.49.230 ($lastError)",
    };
  }

  static Future<Map<String, dynamic>> signup({
    required String fullName,
    required String email,
    required String mobile,
    required String password,
  }) async {
    String? lastError;

    for (final baseUrl in candidateUrls) {
      try {
        final url = Uri.parse('$baseUrl/auth/signup');
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
            .timeout(const Duration(seconds: 4));

        final data = jsonDecode(response.body);

        if (response.statusCode == 200) {
          return {
            "success": true,
            "message": data["message"] ?? "Account created successfully",
          };
        } else {
          return {
            "success": false,
            "message": data["detail"] ?? "Signup failed",
          };
        }
      } catch (e) {
        lastError = e.toString();
      }
    }

    return {
      "success": false,
      "message": "Cannot connect to backend server ($lastError)",
    };
  }
}
