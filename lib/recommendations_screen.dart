import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'recommendations_api.dart';

class RecommendationsScreen extends StatefulWidget {
  const RecommendationsScreen({super.key});

  @override
  State<RecommendationsScreen> createState() => _RecommendationsScreenState();
}

class _RecommendationsScreenState extends State<RecommendationsScreen> {
  bool isLoading = true;
  String errorMessage = '';

  Map<String, dynamic> recData = {
    'risk_score': 0,
    'risk_level': 'Loading',
    'recommendations': <Map<String, dynamic>>[],
    'priority_actions': <String>[],
  };

  @override
  void initState() {
    super.initState();
    loadRecommendations();
  }

  Future<void> loadRecommendations() async {
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

      final data = await RecommendationsApi.fetchRecommendations(token);

      setState(() {
        recData = data;
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

  @override
  Widget build(BuildContext context) {
    final double riskScore = (recData['risk_score'] ?? 0).toDouble();
    final String riskLevel = recData['risk_level'] ?? 'Loading';
    final double progress = (riskScore / 100).clamp(0.0, 1.0);

    final List<Map<String, dynamic>> recommendations =
        List<Map<String, dynamic>>.from(recData['recommendations'] ?? []);

    final List<String> priorityActions = List<String>.from(
      recData['priority_actions'] ?? [],
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Recommendations',
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
                              width: 92,
                              height: 92,
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
                                    fontSize: 24,
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
                        const SizedBox(width: 16),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text(
                                'Recommended Actions',
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
                              const Text(
                                'These actions are based on your current financial risk and forecast.',
                                style: TextStyle(
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
                    'Priority Actions',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (priorityActions.isEmpty)
                    const _ActionTile(
                      text: 'No priority actions available',
                      icon: Icons.check_circle_outline,
                      color: Color(0xFF16A34A),
                    )
                  else
                    ...priorityActions.map(
                      (a) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: _ActionTile(
                          text: a,
                          icon: Icons.priority_high_rounded,
                          color: const Color(0xFFF59E0B),
                        ),
                      ),
                    ),

                  const SizedBox(height: 16),

                  const Text(
                    'Detailed Recommendations',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (recommendations.isEmpty)
                    const _RecommendationCard(
                      title: 'No recommendations available',
                      subtitle:
                          'Add more financial data to generate personalized suggestions.',
                      impact: '0',
                      color: Color(0xFF64748B),
                    )
                  else
                    ...recommendations.map(
                      (item) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _RecommendationCard(
                          title: item['title'] ?? 'Recommendation',
                          subtitle: item['description'] ?? '',
                          impact: '${item['impact'] ?? 0}',
                          color: _impactColor((item['impact'] ?? 0).toDouble()),
                        ),
                      ),
                    ),

                  const SizedBox(height: 20),
                ],
              ),
            ),
    );
  }

  Color _impactColor(double impact) {
    if (impact < 25) return const Color(0xFF16A34A);
    if (impact < 50) return const Color(0xFFF59E0B);
    if (impact < 75) return const Color(0xFFF97316);
    return const Color(0xFFEF4444);
  }
}

class _ActionTile extends StatelessWidget {
  final String text;
  final IconData icon;
  final Color color;

  const _ActionTile({
    required this.text,
    required this.icon,
    required this.color,
  });

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
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: color.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 14),
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

class _RecommendationCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final String impact;
  final Color color;

  const _RecommendationCard({
    required this.title,
    required this.subtitle,
    required this.impact,
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
            child: Icon(Icons.lightbulb_outline, color: color),
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
                  style: const TextStyle(color: Color(0xFF475569), height: 1.3),
                ),
              ],
            ),
          ),
          const SizedBox(width: 10),
          Text(
            impact,
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
