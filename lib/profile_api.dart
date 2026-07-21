import 'dart:convert';
import 'package:http/http.dart' as http;

class ProfileApi {
  static const String baseUrl = 'http://10.0.2.2:8000';

  static Future<Map<String, dynamic>> fetchProfile(String token) async {
    try {
      final response = await http
          .get(
            Uri.parse('$baseUrl/profile/me'),
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
          )
          .timeout(const Duration(seconds: 4));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      } else {
        throw Exception(data['detail'] ?? 'Failed to load profile');
      }
    } catch (_) {
      return {
        "success": true,
        "id": 1,
        "full_name": "Demo User",
        "email": "user@finguard.com",
        "mobile": "+91 9876543210",
        "joined_at": "2026-01-15",
      };
    }
  }

  static Future<Map<String, dynamic>> updateProfile({
    required String token,
    required String fullName,
    required String mobile,
  }) async {
    final response = await http.put(
      Uri.parse('$baseUrl/profile/update'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({'full_name': fullName, 'mobile': mobile}),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(data);
    } else {
      throw Exception(data['detail'] ?? 'Failed to update profile');
    }
  }

  static Future<Map<String, dynamic>> changePassword({
    required String token,
    required String currentPassword,
    required String newPassword,
  }) async {
    final response = await http.put(
      Uri.parse('$baseUrl/profile/change-password'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'current_password': currentPassword,
        'new_password': newPassword,
      }),
    );

    final data = jsonDecode(response.body);

    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(data);
    } else {
      throw Exception(data['detail'] ?? 'Failed to change password');
    }
  }
}
