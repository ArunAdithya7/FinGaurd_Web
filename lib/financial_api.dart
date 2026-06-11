import 'dart:convert';
import 'package:http/http.dart' as http;

class FinancialApi {
  static const String baseUrl = 'https://m8bkbk54-8000.inc1.devtunnels.ms';

  static Future<Map<String, dynamic>> addIncome({
    required String token,
    required String category,
    required double amount,
    String? notes,
    String? txDate, // format: yyyy-mm-dd
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/financial/income'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'category': category,
        'amount': amount,
        'notes': notes,
        'tx_date': txDate,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 200) {
      return {'success': true, 'message': data['message'] ?? 'Income added'};
    }
    return {
      'success': false,
      'message': data['detail'] ?? 'Failed to add income',
    };
  }

  static Future<Map<String, dynamic>> addExpense({
    required String token,
    required String category,
    required double amount,
    String? notes,
    String? txDate,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/financial/expense'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'category': category,
        'amount': amount,
        'notes': notes,
        'tx_date': txDate,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 200) {
      return {'success': true, 'message': data['message'] ?? 'Expense added'};
    }
    return {
      'success': false,
      'message': data['detail'] ?? 'Failed to add expense',
    };
  }

  static Future<Map<String, dynamic>> addDebt({
    required String token,
    required String liabilityName,
    required double outstandingAmount,
    required double monthlyPayment,
    double interestRate = 0.0,
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/financial/liability'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'liability_name': liabilityName,
        'outstanding_amount': outstandingAmount,
        'monthly_payment': monthlyPayment,
        'interest_rate': interestRate,
      }),
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 200) {
      return {'success': true, 'message': data['message'] ?? 'Debt added'};
    }
    return {
      'success': false,
      'message': data['detail'] ?? 'Failed to add debt',
    };
  }
}
