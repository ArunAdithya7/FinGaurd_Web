import 'dart:convert';
import 'api_config.dart';

class ForecastApi {
  static Future<Map<String, dynamic>> fetchForecast(String token) async {
    try {
      final response = await ApiConfig.get('/forecast/summary', token);
      final data = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return Map<String, dynamic>.from(data);
      } else {
        throw Exception(data['detail'] ?? 'Failed to load forecast');
      }
    } catch (_) {
      return {
        "success": true,
        "current_risk_score": 0.0,
        "current_risk_level": "Neutral",
        "chart_scores": [0.0, 0.0, 0.0, 0.0],
        "projections": [
          {
            "days": 30,
            "risk_score": 0.0,
            "risk_level": "Neutral",
            "projected_savings": 0.0,
            "projected_surplus": 0.0,
            "message": "Add transactions to calculate 30-day forecast.",
          },
          {
            "days": 60,
            "risk_score": 0.0,
            "risk_level": "Neutral",
            "projected_savings": 0.0,
            "projected_surplus": 0.0,
            "message": "Add transactions to calculate 60-day forecast.",
          },
          {
            "days": 90,
            "risk_score": 0.0,
            "risk_level": "Neutral",
            "projected_savings": 0.0,
            "projected_surplus": 0.0,
            "message": "Add transactions to calculate 90-day forecast.",
          },
        ],
        "recommendations": [
          "Start logging your monthly income and expenses to track future forecasts.",
        ],
      };
    }
  }
}
