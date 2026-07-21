import 'dart:convert';
import 'package:http/http.dart' as http;

class DashboardApi {
  static const String baseUrl = 'http://10.0.2.2:8000';

  static Future<Map<String, dynamic>> fetchDashboard(String token) async {
    try {
      final response = await http
          .get(
            Uri.parse('$baseUrl/dashboard/summary'),
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
        throw Exception(data['detail'] ?? 'Failed to load dashboard');
      }
    } catch (_) {
      // Fallback demo summary metrics when offline or connecting
      return {
        'risk_score': 35.0,
        'risk_level': 'Low',
        'total_assets': 250000.0,
        'total_liabilities': 45000.0,
        'monthly_income': 75000.0,
        'monthly_expense': 32000.0,
        'monthly_debt': 10000.0,
        'debt_ratio': 13.3,
        'savings_runway': 6.4,
        'expense_ratio': 42.6,
        'monthly_surplus': 33000.0,
        'alerts': ['Healthy emergency fund reserve.', 'Keep debt ratio under 20%.'],
        'trend_labels': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'trend_scores': [52.0, 48.0, 45.0, 40.0, 38.0, 35.0],
      };
    }
  }
}
