import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_config.dart';

class ProfileApi {
  static Future<Map<String, dynamic>> fetchProfile(String token) async {
    try {
      final response = await ApiConfig.get('/profile/me', token);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      } else {
        throw Exception(data['detail'] ?? 'Failed to load profile');
      }
    } catch (_) {
      final prefs = await SharedPreferences.getInstance();
      final storedData = prefs.getString('user_data');
      String name = "New User";
      String email = "user@finguard.com";
      String mobile = "Not set";

      if (storedData != null) {
        try {
          final map = jsonDecode(storedData);
          name = map['full_name'] ?? map['name'] ?? name;
          email = map['email'] ?? email;
          mobile = map['mobile'] ?? mobile;
        } catch (e) {}
      }

      return {
        "success": true,
        "id": 1,
        "full_name": name,
        "email": email,
        "mobile": mobile,
        "joined_at": DateTime.now().toString().split(' ')[0],
      };
    }
  }

  static Future<Map<String, dynamic>> updateProfile({
    required String token,
    required String fullName,
    required String mobile,
  }) async {
    final response = await ApiConfig.put(
      '/profile/update',
      {'full_name': fullName, 'mobile': mobile},
      token: token,
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
    final response = await ApiConfig.put(
      '/profile/change-password',
      {'current_password': currentPassword, 'new_password': newPassword},
      token: token,
    );
    final data = jsonDecode(response.body);
    if (response.statusCode == 200) {
      return Map<String, dynamic>.from(data);
    } else {
      throw Exception(data['detail'] ?? 'Failed to change password');
    }
  }
}
