import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'risk_api.dart';

class RiskAnalysisScreen extends StatefulWidget {
  const RiskAnalysisScreen({super.key});

  @override
  State<RiskAnalysisScreen> createState() => _RiskAnalysisScreenState();
}

class _RiskAnalysisScreenState extends State<RiskAnalysisScreen> {
  bool isLoading = true;
  String errorMessage = '';

  Map<String, dynamic> riskData = {
    'risk_score': 0,
    'risk_level': 'Loading',
    'expense_ratio': 0.0,
    'debt_ratio': 0.0,
    'savings_runway': 0.0,
    'monthly_surplus': 0.0,
    'factors': <Map<String, dynamic>>[],
    'suggestions': <String>[],
  };

  @override
  void initState() {
    super.initState();
    loadRiskAnalysis();
  }

  Future<void> loadRiskAnalysis() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final token = prefs.getString('auth_token') ?? prefs.getString('token');

      if (token == null || token.isEmpty) {
        setState(() {
          isLoading = false;
          errorMessage = 'Login token not found';
        });
        return;
      }

      final data = await RiskApi.fetchRiskAnalysis(token);

      setState(() {
        riskData = data;
        isLoading = false;
        errorMessage = '';
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = e.toString();
      });
    }
  }

  Color riskColor(String level) {
    switch (level.toLowerCase()) {
      case 'low':
        return const Color(0xFF16A34A);
      case 'moderate':
        return const Color(0xFFF59E0B);
      case 'high':
        return const Color(0xFFF97316);
      case 'critical':
        return const Color(0xFFEF4444);
      default:
        return const Color(0xFF64748B);
    }
  }

  String riskDescription(String level) {
    switch (level.toLowerCase()) {
      case 'low':
        return 'Your financial health is stable.';
      case 'moderate':
        return 'There are warning signs to watch carefully.';
      case 'high':
        return 'You should take action soon to reduce financial stress.';
      case 'critical':
        return 'Immediate action is needed to avoid serious distress.';
      default:
        return 'Loading analysis...';
    }
  }

  String formatDecimal(dynamic value, {int digits = 1}) {
    final num v = (value is num) ? value : num.tryParse('$value') ?? 0;
    return v.toStringAsFixed(digits);
  }

  @override
  Widget build(BuildContext context) {
    final double riskScore = (riskData['risk_score'] ?? 0).toDouble();
    final String riskLevel = riskData['risk_level'] ?? 'Loading';
    final double progress = (riskScore / 100).clamp(0.0, 1.0);

    final List<Map<String, dynamic>> factors = List<Map<String, dynamic>>.from(
      riskData['factors'] ?? [],
    );

    final List<String> suggestions = List<String>.from(
      riskData['suggestions'] ?? [],
    );

    final double expenseRatio = (riskData['expense_ratio'] ?? 0).toDouble();
    final double debtRatio = (riskData['debt_ratio'] ?? 0).toDouble();
    final double savingsRunway = (riskData['savings_runway'] ?? 0).toDouble();
    final double monthlySurplus = (riskData['monthly_surplus'] ?? 0).toDouble();

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Risk Analysis',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontWeight: FontWeight.w800,
          ),
        ),
      ),
      body: isLoading
          ? const Center(child: CircularProgressIndicator())
          : errorMessage.isNotEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Text(
                  errorMessage,
                  style: const TextStyle(
                    color: Colors.red,
                    fontWeight: FontWeight.w600,
                  ),
                  textAlign: TextAlign.center,
                ),
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(18),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: const Color(0xFFE5EAF2)),
                    ),
                    child: Row(
                      children: [
                        Stack(
                          alignment: Alignment.center,
                          children: [
                            SizedBox(
                              width: 100,
                              height: 100,
                              child: CircularProgressIndicator(
                                value: progress,
                                strokeWidth: 10,
                                backgroundColor: const Color(0xFFE9EDF5),
                                valueColor: AlwaysStoppedAnimation(
                                  riskColor(riskLevel),
                                ),
                              ),
                            ),
                            Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  riskScore.toInt().toString(),
                                  style: const TextStyle(
                                    fontSize: 26,
                                    fontWeight: FontWeight.w800,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                                const Text(
                                  '/100',
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Color(0xFF64748B),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(width: 18),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Financial Distress Risk',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                riskLevel,
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: riskColor(riskLevel),
                                ),
                              ),
                              const SizedBox(height: 8),
                              Text(
                                riskDescription(riskLevel),
                                style: const TextStyle(
                                  height: 1.35,
                                  color: Color(0xFF475569),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),

                  const Text(
                    'Risk Drivers',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  Row(
                    children: [
                      Expanded(
                        child: _MetricCard(
                          title: 'Expense Ratio',
                          value: '${formatDecimal(expenseRatio)}%',
                          color: riskColor(riskLevel),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _MetricCard(
                          title: 'Debt Ratio',
                          value: '${formatDecimal(debtRatio)}%',
                          color: riskColor(riskLevel),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: _MetricCard(
                          title: 'Savings Runway',
                          value: '${formatDecimal(savingsRunway)} mo',
                          color: riskColor(riskLevel),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: _MetricCard(
                          title: 'Monthly Surplus',
                          value: '₹${monthlySurplus.toStringAsFixed(0)}',
                          color: const Color(0xFF16A34A),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  const Text(
                    'Why this score?',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (factors.isEmpty)
                    const _FactorCard(
                      title: 'No factor details available',
                      subtitle:
                          'Add more financial data to get deeper analysis.',
                      score: 0,
                      color: Color(0xFF64748B),
                    )
                  else
                    ...factors.map(
                      (factor) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _FactorCard(
                          title: factor['title'] ?? 'Factor',
                          subtitle: factor['description'] ?? '',
                          score: (factor['impact'] ?? 0).toDouble(),
                          color: _factorColor(
                            (factor['impact'] ?? 0).toDouble(),
                          ),
                        ),
                      ),
                    ),

                  const SizedBox(height: 8),

                  const Text(
                    'Suggested Actions',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (suggestions.isEmpty)
                    const _SuggestionTile(text: 'No suggestions available')
                  else
                    ...suggestions.map(
                      (s) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: _SuggestionTile(text: s),
                      ),
                    ),

                  const SizedBox(height: 20),
                ],
              ),
            ),
    );
  }

  Color _factorColor(double impact) {
    if (impact < 25) return const Color(0xFF16A34A);
    if (impact < 50) return const Color(0xFFF59E0B);
    if (impact < 75) return const Color(0xFFF97316);
    return const Color(0xFFEF4444);
  }
}

class _MetricCard extends StatelessWidget {
  final String title;
  final String value;
  final Color color;

  const _MetricCard({
    required this.title,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: const Color(0xFFE5EAF2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(
              fontSize: 13,
              color: Color(0xFF64748B),
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            width: 42,
            height: 4,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(999),
            ),
          ),
        ],
      ),
    );
  }
}

class _FactorCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final double score;
  final Color color;

  const _FactorCard({
    required this.title,
    required this.subtitle,
    required this.score,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5EAF2)),
      ),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(Icons.insights_outlined, color: color),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(color: Color(0xFF475569)),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Text(
            score.toInt().toString(),
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _SuggestionTile extends StatelessWidget {
  final String text;

  const _SuggestionTile({required this.text});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFFE5EAF2)),
      ),
      child: Row(
        children: [
          const Icon(Icons.check_circle_outline, color: Color(0xFF16A34A)),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              text,
              style: const TextStyle(
                color: Color(0xFF0F172A),
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
