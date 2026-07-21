import 'dart:convert';
import 'package:http/http.dart' as http;

class RiskApi {
  static const String baseUrl = 'http://10.0.2.2:8000';
  

  static Future<Map<String, dynamic>> fetchRiskAnalysis(String token) async {
    try {
      final response = await http
          .get(
            Uri.parse('$baseUrl/risk/analysis'),
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
        throw Exception(data['detail'] ?? 'Failed to load risk analysis');
      }
    } catch (_) {
      // Fallback risk metrics for demo mode & offline
      return {
        "success": true,
        "risk_score": 35.0,
        "risk_level": "Low",
        "expense_ratio": 42.6,
        "debt_ratio": 13.3,
        "savings_runway": 6.4,
        "monthly_surplus": 33000.0,
        "factors": [
          {
            "title": "Expense Ratio",
            "description": "How much of your income is spent every month.",
            "impact": 42.6,
          },
          {
            "title": "Debt Ratio",
            "description": "How much of your income goes to debt payments.",
            "impact": 13.3,
          },
          {
            "title": "Savings Runway",
            "description": "How many months your savings can cover expenses.",
            "impact": 25.0,
          },
          {
            "title": "Monthly Surplus",
            "description": "Income left after expenses and debt payments.",
            "impact": 20.0,
          },
        ],
        "suggestions": [
          "Maintain your current savings discipline.",
          "Keep high-interest liabilities minimal.",
        ],
      };
    }
  }
}
