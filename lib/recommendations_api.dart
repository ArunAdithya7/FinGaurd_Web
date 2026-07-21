import 'dart:convert';
import 'api_config.dart';

class RecommendationsApi {
  static Future<Map<String, dynamic>> fetchRecommendations(String token) async {
    try {
      final response = await ApiConfig.get('/recommendations/summary', token);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      } else {
        throw Exception(data['detail'] ?? 'Failed to load recommendations');
      }
    } catch (_) {
      return {
        "success": true,
        "risk_score": 0.0,
        "risk_level": "Neutral",
        "recommendations": [
          {
            "title": "Start Financial Tracking",
            "description": "Log your income and expenses to generate personalized AI recommendations.",
            "impact": 0.0,
          },
        ],
        "priority_actions": [
          "Add your monthly income using the Financial Entry tab.",
        ],
      };
    }
  }
}
