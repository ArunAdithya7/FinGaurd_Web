import 'dart:convert';
import 'api_config.dart';

class FinancialApi {
  static Future<Map<String, dynamic>> addIncome({
    required String token,
    required String category,
    required double amount,
    String? notes,
    String? txDate,
  }) async {
    final response = await ApiConfig.post(
      '/financial/income',
      {
        'category': category,
        'amount': amount,
        'notes': notes,
        'tx_date': txDate,
      },
      token: token,
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
    final response = await ApiConfig.post(
      '/financial/expense',
      {
        'category': category,
        'amount': amount,
        'notes': notes,
        'tx_date': txDate,
      },
      token: token,
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
    final response = await ApiConfig.post(
      '/financial/liability',
      {
        'liability_name': liabilityName,
        'outstanding_amount': outstandingAmount,
        'monthly_payment': monthlyPayment,
        'interest_rate': interestRate,
      },
      token: token,
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

  static Future<Map<String, dynamic>> addAsset({
    required String token,
    required String assetName,
    required double amount,
    String assetType = 'Savings Account',
  }) async {
    final response = await ApiConfig.post(
      '/financial/asset',
      {
        'asset_name': assetName,
        'amount': amount,
        'asset_type': assetType,
      },
      token: token,
    );

    final data = jsonDecode(response.body);
    if (response.statusCode == 200) {
      return {'success': true, 'message': data['message'] ?? 'Asset added'};
    }
    return {
      'success': false,
      'message': data['detail'] ?? 'Failed to add asset',
    };
  }
}
