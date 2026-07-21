import 'dart:convert';
import 'api_config.dart';

class RiskApi {
  static Future<Map<String, dynamic>> fetchRiskAnalysis(String token) async {
    try {
      final response = await ApiConfig.get('/risk/analysis', token);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      } else {
        throw Exception(data['detail'] ?? 'Failed to load risk analysis');
      }
    } catch (_) {
      return {
        "success": true,
        "risk_score": 0.0,
        "risk_level": "Neutral",
        "expense_ratio": 0.0,
        "debt_ratio": 0.0,
        "savings_runway": 0.0,
        "monthly_surplus": 0.0,
        "factors": [
          {
            "title": "Expense Ratio",
            "description": "How much of your income is spent every month.",
            "impact": 0.0,
          },
          {
            "title": "Debt Ratio",
            "description": "How much of your income goes to debt payments.",
            "impact": 0.0,
          },
        ],
        "suggestions": [
          "Add your income and expenses to view detailed risk analysis.",
        ],
      };
    }
  }
}
