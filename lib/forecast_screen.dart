import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'forecast_api.dart';

class ForecastScreen extends StatefulWidget {
  const ForecastScreen({super.key});

  @override
  State<ForecastScreen> createState() => _ForecastScreenState();
}

class _ForecastScreenState extends State<ForecastScreen> {
  bool isLoading = true;
  String errorMessage = '';

  Map<String, dynamic> forecastData = {
    'current_risk_score': 0,
    'current_risk_level': 'Loading',
    'projections': <Map<String, dynamic>>[],
    'chart_scores': <double>[0, 0, 0, 0],
    'recommendations': <String>[],
  };

  @override
  void initState() {
    super.initState();
    loadForecast();
  }

  Future<void> loadForecast() async {
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

      final data = await ForecastApi.fetchForecast(token);

      setState(() {
        forecastData = data;
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

  String formatCurrency(dynamic value) {
    final num v = (value is num) ? value : num.tryParse('$value') ?? 0;
    return '₹${v.toStringAsFixed(0)}';
  }

  @override
  Widget build(BuildContext context) {
    final currentRiskScore = (forecastData['current_risk_score'] ?? 0)
        .toDouble();
    final currentRiskLevel = forecastData['current_risk_level'] ?? 'Loading';
    final progress = (currentRiskScore / 100).clamp(0.0, 1.0);

    final List<Map<String, dynamic>> projections =
        List<Map<String, dynamic>>.from(forecastData['projections'] ?? []);

    final List<double> chartScores =
        (forecastData['chart_scores'] as List<dynamic>? ?? [0, 0, 0, 0])
            .map((e) => (e as num).toDouble())
            .toList();

    final List<String> recommendations = List<String>.from(
      forecastData['recommendations'] ?? [],
    );

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        title: const Text(
          'Predictions',
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
                                  riskColor(currentRiskLevel),
                                ),
                              ),
                            ),
                            Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Text(
                                  currentRiskScore.toInt().toString(),
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
                                'Forecasted Financial Risk',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w800,
                                  color: Color(0xFF0F172A),
                                ),
                              ),
                              const SizedBox(height: 6),
                              Text(
                                currentRiskLevel,
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.w700,
                                  color: riskColor(currentRiskLevel),
                                ),
                              ),
                              const SizedBox(height: 8),
                              const Text(
                                'These values show your expected financial path based on current trends.',
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
                    '30 / 60 / 90 Day Forecast',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (projections.isEmpty)
                    const _ForecastCard(
                      label: 'No forecast data',
                      riskScore: 0,
                      note: 'Add more financial data to generate predictions.',
                      color: Color(0xFF64748B),
                    )
                  else
                    ...projections.map(
                      (item) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: _ForecastCard(
                          label: '${item['days']} Days',
                          riskScore: (item['risk_score'] ?? 0).toDouble(),
                          note: item['message'] ?? 'Forecast available',
                          projectedSavings: item['projected_savings'] != null
                              ? formatCurrency(item['projected_savings'])
                              : null,
                          projectedSurplus: item['projected_surplus'] != null
                              ? formatCurrency(item['projected_surplus'])
                              : null,
                          color: riskColor(item['risk_level'] ?? 'moderate'),
                        ),
                      ),
                    ),

                  const SizedBox(height: 8),

                  const Text(
                    'Risk Trend Preview',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  Container(
                    width: double.infinity,
                    height: 220,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(18),
                      border: Border.all(color: const Color(0xFFE5EAF2)),
                    ),
                    child: CustomPaint(
                      painter: ForecastTrendPainter(
                        values: chartScores,
                        lineColor: riskColor(currentRiskLevel),
                      ),
                      child: const SizedBox.expand(),
                    ),
                  ),

                  const SizedBox(height: 16),

                  const Text(
                    'Recommended Actions',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.w800,
                      color: Color(0xFF0F172A),
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (recommendations.isEmpty)
                    const _RecommendationTile(
                      text: 'No recommendations available',
                    )
                  else
                    ...recommendations.map(
                      (r) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: _RecommendationTile(text: r),
                      ),
                    ),

                  const SizedBox(height: 20),
                ],
              ),
            ),
    );
  }
}

class _ForecastCard extends StatelessWidget {
  final String label;
  final double riskScore;
  final String note;
  final Color color;
  final String? projectedSavings;
  final String? projectedSurplus;

  const _ForecastCard({
    required this.label,
    required this.riskScore,
    required this.note,
    required this.color,
    this.projectedSavings,
    this.projectedSurplus,
  });

  @override
  Widget build(BuildContext context) {
    final progress = (riskScore / 100).clamp(0.0, 1.0);

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
          Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: 74,
                height: 74,
                child: CircularProgressIndicator(
                  value: progress,
                  strokeWidth: 8,
                  backgroundColor: const Color(0xFFE9EDF5),
                  valueColor: AlwaysStoppedAnimation(color),
                ),
              ),
              Text(
                riskScore.toInt().toString(),
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0F172A),
                ),
              ),
            ],
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  label,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A),
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  note,
                  style: const TextStyle(color: Color(0xFF475569), height: 1.3),
                ),
                if (projectedSavings != null || projectedSurplus != null) ...[
                  const SizedBox(height: 8),
                  if (projectedSavings != null)
                    Text(
                      'Projected savings: $projectedSavings',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF334155),
                      ),
                    ),
                  if (projectedSurplus != null)
                    Text(
                      'Projected surplus: $projectedSurplus',
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF334155),
                      ),
                    ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _RecommendationTile extends StatelessWidget {
  final String text;

  const _RecommendationTile({required this.text});

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
          const Icon(Icons.lightbulb_outline, color: Color(0xFFF59E0B)),
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

class ForecastTrendPainter extends CustomPainter {
  final List<double> values;
  final Color lineColor;

  ForecastTrendPainter({required this.values, required this.lineColor});

  @override
  void paint(Canvas canvas, Size size) {
    if (values.isEmpty) return;

    const leftPad = 14.0;
    const rightPad = 10.0;
    const topPad = 10.0;
    const bottomPad = 24.0;

    final chartWidth = size.width - leftPad - rightPad;
    final chartHeight = size.height - topPad - bottomPad;

    final minValue = values.reduce((a, b) => a < b ? a : b);
    final maxValue = values.reduce((a, b) => a > b ? a : b);
    final range = (maxValue - minValue).abs() < 0.001
        ? 1.0
        : (maxValue - minValue);

    Offset pointForIndex(int i) {
      final x = leftPad + (chartWidth / (values.length - 1)) * i;
      final normalized = (values[i] - minValue) / range;
      final y = topPad + chartHeight - (normalized * chartHeight);
      return Offset(x, y);
    }

    final points = List.generate(values.length, pointForIndex);

    final gridPaint = Paint()
      ..color = const Color(0xFFEAEFF5)
      ..strokeWidth = 1;

    for (int i = 0; i <= 4; i++) {
      final y = topPad + (chartHeight / 4) * i;
      canvas.drawLine(
        Offset(leftPad, y),
        Offset(size.width - rightPad, y),
        gridPaint,
      );
    }

    final linePaint = Paint()
      ..color = lineColor
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    final path = Path()..moveTo(points.first.dx, points.first.dy);
    for (int i = 1; i < points.length; i++) {
      path.lineTo(points[i].dx, points[i].dy);
    }
    canvas.drawPath(path, linePaint);

    final dotPaint = Paint()..color = lineColor;
    for (final p in points) {
      canvas.drawCircle(p, 4.8, dotPaint);
      canvas.drawCircle(p, 2.2, Paint()..color = Colors.white);
    }
  }

  @override
  bool shouldRepaint(covariant ForecastTrendPainter oldDelegate) {
    return oldDelegate.values != values || oldDelegate.lineColor != lineColor;
  }
}
