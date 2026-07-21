import 'dart:convert';
import 'api_config.dart';

class AuthService {
  static Future<Map<String, dynamic>> login({
    required String identifier,
    required String password,
  }) async {
    try {
      final response = await ApiConfig.post(
        '/auth/login',
        {"identifier": identifier, "password": password},
      );

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
      return {
        "success": false,
        "message": "Cannot connect to server ($e)",
      };
    }
  }

  static Future<Map<String, dynamic>> signup({
    required String fullName,
    required String email,
    required String mobile,
    required String password,
  }) async {
    try {
      final response = await ApiConfig.post(
        '/auth/signup',
        {
          "full_name": fullName,
          "email": email,
          "mobile": mobile,
          "password": password,
        },
      );

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
      return {
        "success": false,
        "message": "Cannot connect to backend server ($e)",
      };
    }
  }
}
