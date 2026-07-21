import 'dart:convert';
import 'api_config.dart';

class DashboardApi {
  static Future<Map<String, dynamic>> fetchDashboard(String token) async {
    try {
      final response = await ApiConfig.get('/dashboard/summary', token);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      } else {
        throw Exception(data['detail'] ?? 'Failed to load dashboard');
      }
    } catch (_) {
      // 0 initial state for new users
      return {
        'risk_score': 0,
        'risk_level': 'Neutral',
        'total_assets': 0.0,
        'total_liabilities': 0.0,
        'monthly_income': 0.0,
        'monthly_expense': 0.0,
        'monthly_debt': 0.0,
        'debt_ratio': 0.0,
        'savings_runway': 0.0,
        'expense_ratio': 0.0,
        'monthly_surplus': 0.0,
        'alerts': ['Welcome! Add income or expenses to generate your risk score.'],
        'trend_labels': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
        'trend_scores': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
      };
    }
  }
}
