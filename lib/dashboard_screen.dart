import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dashboard_api.dart';
import 'financial_entry_screen.dart';
import 'risk_analysis_screen.dart';
import 'forecast_screen.dart';
import 'recommendations_screen.dart';
import 'profile_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int selectedIndex = 0;
  bool isLoading = true;
  String errorMessage = '';

  Map<String, dynamic> dashboardData = {
    'risk_score': 0,
    'risk_level': 'Loading',
    'total_assets': 0,
    'total_liabilities': 0,
    'monthly_income': 0,
    'monthly_expense': 0,
    'monthly_debt': 0,
    'debt_ratio': 0.0,
    'savings_runway': 0.0,
    'expense_ratio': 0.0,
    'monthly_surplus': 0.0,
    'alerts': <String>[],
    'trend_labels': <String>['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
    'trend_scores': <double>[52, 48, 55, 44, 38, 33],
  };

  @override
  void initState() {
    super.initState();
    loadDashboard();
  }

  void onItemTapped(int index) {
    setState(() {
      selectedIndex = index;
    });

    if (index == 0) {
      // Home Dashboard
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const DashboardScreen()),
      );
    }

    if (index == 1) {
      // Risk Analysis
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const RiskAnalysisScreen()),
      );
    }

    if (index == 2) {
      // Forecast / Predictions
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (_) => const ForecastScreen()),
      );
    }

    if (index == 3) {
      // Profile Screen
      // Replace with your profile screen
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const ProfileScreen()),
      );
    }
  }

  Future<void> loadDashboard() async {
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

      final data = await DashboardApi.fetchDashboard(token);

      setState(() {
        dashboardData = data;
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

  String formatCurrency(dynamic value) {
    final num v = (value is num) ? value : num.tryParse('$value') ?? 0;

    return '₹${v.toStringAsFixed(0)}';
  }

  String formatDecimal(dynamic value, {int digits = 1}) {
    final num v = (value is num) ? value : num.tryParse('$value') ?? 0;

    return v.toStringAsFixed(digits);
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
        return 'Your financial health looks stable. Keep tracking your savings and spending.';

      case 'moderate':
        return 'Your spending pattern is getting tighter. Reduce expenses and improve savings.';

      case 'high':
        return 'Your finances need attention. Control debt and reduce monthly expenses soon.';

      case 'critical':
        return 'Immediate action is needed. Your financial stress level is very high.';

      default:
        return 'Loading your financial health data...';
    }
  }

  Widget _drawerItem(
    IconData icon,
    String text,
    bool selected, {
    VoidCallback? onTap,
  }) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      decoration: BoxDecoration(
        color: selected ? const Color(0xFF2457F5) : Colors.transparent,
        borderRadius: BorderRadius.circular(12),
      ),
      child: ListTile(
        leading: Icon(icon, color: Colors.white),
        title: Text(
          text,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.w600,
          ),
        ),
        onTap: onTap,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final double riskScore = (dashboardData['risk_score'] ?? 0).toDouble();

    final String riskLevel = dashboardData['risk_level'] ?? 'Loading';

    final double riskProgress = (riskScore / 100).clamp(0.0, 1.0);

    final String totalAssets = formatCurrency(
      dashboardData['total_assets'] ?? 0,
    );

    final String totalLiabilities = formatCurrency(
      dashboardData['total_liabilities'] ?? 0,
    );

    final String savingsRunway =
        '${formatDecimal(dashboardData['savings_runway'] ?? 0)} mo';

    final String expenseRatio =
        '${formatDecimal(dashboardData['expense_ratio'] ?? 0)}%';

    final String debtRatio =
        '${formatDecimal(dashboardData['debt_ratio'] ?? 0)}%';

    final String monthlySurplus = formatCurrency(
      dashboardData['monthly_surplus'] ?? 0,
    );

    final List<String> alerts = List<String>.from(
      dashboardData['alerts'] ?? [],
    );

    final List<String> trendLabels = List<String>.from(
      dashboardData['trend_labels'] ??
          ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
    );

    final List<double> trendScores =
        (dashboardData['trend_scores'] as List<dynamic>? ??
                [52, 48, 55, 44, 38, 33])
            .map((e) => (e as num).toDouble())
            .toList();

    return Scaffold(
      backgroundColor: const Color(0xFFF4F7FB),

      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        titleSpacing: 0,

        title: Row(
          children: [
            Image.asset(
              'assets/images/finguard_logo.png',
              width: 32,
              height: 32,
            ),

            const SizedBox(width: 10),

            const Text(
              'FinGuard',
              style: TextStyle(
                color: Color(0xFF0F172A),
                fontWeight: FontWeight.w800,
              ),
            ),
          ],
        ),

        iconTheme: const IconThemeData(color: Color(0xFF0F172A)),

        actions: [
          Stack(
            children: [
              IconButton(
                onPressed: () {},
                icon: const Icon(Icons.notifications_none_rounded),
              ),

              Positioned(
                right: 12,
                top: 12,
                child: Container(
                  width: 9,
                  height: 9,
                  decoration: const BoxDecoration(
                    color: Colors.red,
                    shape: BoxShape.circle,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(width: 8),
        ],
      ),

      drawer: Drawer(
        child: Container(
          color: const Color(0xFF08142F),

          child: SafeArea(
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),

                  child: Row(
                    children: [
                      Image.asset(
                        'assets/images/finguard_logo.png',
                        width: 36,
                        height: 36,
                      ),

                      const SizedBox(width: 10),

                      const Text(
                        'FinGuard',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 8),

                _drawerItem(Icons.dashboard_rounded, 'Dashboard', true),

                _drawerItem(
                  Icons.analytics_outlined,
                  'Risk Analysis',
                  false,
                  onTap: () {
                    Navigator.pop(context);

                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const RiskAnalysisScreen(),
                      ),
                    );
                  },
                ),

                _drawerItem(Icons.show_chart_rounded, 'Predictions', false),

                _drawerItem(
                  Icons.lightbulb_outline,
                  'Recommendations',
                  false,
                  onTap: () {
                    Navigator.push(
                      context,
                      MaterialPageRoute(
                        builder: (_) => const RecommendationsScreen(),
                      ),
                    );
                  },
                ),

                _drawerItem(
                  Icons.account_balance_wallet_outlined,
                  'Investments',
                  false,
                ),

                _drawerItem(Icons.receipt_long_outlined, 'Reports', false),

                _drawerItem(Icons.settings_outlined, 'Settings', false),

                const Spacer(),

                _drawerItem(Icons.logout_rounded, 'Logout', false),

                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),

      body: SafeArea(
        child: isLoading
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
                    const Text(
                      'Dashboard',
                      style: TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                    ),

                    const SizedBox(height: 16),

                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(18),

                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(18),

                        border: Border.all(color: const Color(0xFFE5EAF2)),

                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x10000000),
                            blurRadius: 16,
                            offset: Offset(0, 8),
                          ),
                        ],
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
                                  value: riskProgress,
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

                    Row(
                      children: [
                        Expanded(
                          child: _SummaryCard(
                            title: 'Assets',
                            value: totalAssets,
                            subtitle: 'Live from backend',
                            color: const Color(0xFF16A34A),
                          ),
                        ),

                        const SizedBox(width: 12),

                        Expanded(
                          child: _SummaryCard(
                            title: 'Liabilities',
                            value: totalLiabilities,
                            subtitle: 'Live from backend',
                            color: const Color(0xFFEF4444),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 12),

                    Row(
                      children: [
                        Expanded(
                          child: _SummaryCard(
                            title: 'Savings Runway',
                            value: savingsRunway,
                            subtitle: 'Months covered',
                            color: riskColor(riskLevel),
                          ),
                        ),

                        const SizedBox(width: 12),

                        Expanded(
                          child: _SummaryCard(
                            title: 'Expense Ratio',
                            value: expenseRatio,
                            subtitle: 'Income spent on expenses',
                            color: riskColor(riskLevel),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 12),

                    Row(
                      children: [
                        Expanded(
                          child: _SummaryCard(
                            title: 'Debt Ratio',
                            value: debtRatio,
                            subtitle: 'Debt vs income',
                            color: riskColor(riskLevel),
                          ),
                        ),

                        const SizedBox(width: 12),

                        Expanded(
                          child: _SummaryCard(
                            title: 'Monthly Surplus',
                            value: monthlySurplus,
                            subtitle: 'Income minus all outflow',
                            color: const Color(0xFF16A34A),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    const Text(
                      'Risk Score Trend',
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

                      child: Column(
                        children: [
                          Expanded(
                            child: CustomPaint(
                              painter: RiskTrendPainter(
                                values: trendScores,
                                lineColor: riskColor(riskLevel),
                              ),
                              child: const SizedBox.expand(),
                            ),
                          ),

                          const SizedBox(height: 8),

                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,

                            children: trendLabels
                                .map(
                                  (label) => Text(
                                    label,
                                    style: const TextStyle(
                                      color: Color(0xFF64748B),
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                )
                                .toList(),
                          ),
                        ],
                      ),
                    ),

                    const SizedBox(height: 16),

                    const Text(
                      'Quick Actions',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                    ),

                    const SizedBox(height: 12),

                    GridView.count(
                      crossAxisCount: 2,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 2.9,

                      children: [
                        _ActionTile(
                          icon: Icons.add_circle_outline,
                          label: 'Add Expense',
                          onTap: () {},
                        ),

                        _ActionTile(
                          icon: Icons.trending_up,
                          label: 'Add Income',
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const FinancialEntryScreen(),
                              ),
                            );
                          },
                        ),

                        _ActionTile(
                          icon: Icons.credit_card_off_outlined,
                          label: 'Add Debt',
                          onTap: () {},
                        ),

                        _ActionTile(
                          icon: Icons.insights_outlined,
                          label: 'Forecast',
                          onTap: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => const ForecastScreen(),
                              ),
                            );
                          },
                        ),
                      ],
                    ),

                    const SizedBox(height: 16),

                    const Text(
                      'Latest Alerts',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0F172A),
                      ),
                    ),

                    const SizedBox(height: 12),

                    if (alerts.isEmpty)
                      const _AlertCard(
                        title: 'No alerts found',
                        subtitle: 'Your current financial status looks stable.',
                        icon: Icons.check_circle_outline,
                        iconColor: Color(0xFF16A34A),
                      )
                    else
                      ...alerts.map(
                        (a) => Padding(
                          padding: const EdgeInsets.only(bottom: 10),

                          child: _AlertCard(
                            title: a,
                            subtitle:
                                'Generated from your latest financial data.',
                            icon: Icons.warning_amber_rounded,
                            iconColor: riskColor(riskLevel),
                          ),
                        ),
                      ),

                    const SizedBox(height: 20),
                  ],
                ),
              ),
      ),

      bottomNavigationBar: BottomNavigationBar(
        currentIndex: selectedIndex,
        onTap: onItemTapped,
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF2457F5),
        unselectedItemColor: Colors.grey,

        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_rounded),
            label: 'Home',
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.analytics_outlined),
            label: 'Risk',
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.show_chart_rounded),
            label: 'Predictions',
          ),

          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String title;
  final String value;
  final String subtitle;
  final Color color;

  const _SummaryCard({
    required this.title,
    required this.value,
    required this.subtitle,
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
              fontSize: 20,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0F172A),
            ),
          ),

          const SizedBox(height: 8),

          Text(
            subtitle,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _ActionTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  const _ActionTile({required this.icon, required this.label, this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,

      borderRadius: BorderRadius.circular(14),

      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),

        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(14),

          border: Border.all(color: const Color(0xFFE5EAF2)),
        ),

        child: Row(
          children: [
            Icon(icon, color: const Color(0xFF2457F5)),

            const SizedBox(width: 10),

            Expanded(
              child: Text(
                label,
                style: const TextStyle(
                  fontWeight: FontWeight.w600,
                  color: Color(0xFF0F172A),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _AlertCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Color iconColor;

  const _AlertCard({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.iconColor,
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
              color: iconColor.withOpacity(0.12),
              borderRadius: BorderRadius.circular(12),
            ),

            child: Icon(icon, color: iconColor),
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
        ],
      ),
    );
  }
}

class RiskTrendPainter extends CustomPainter {
  final List<double> values;
  final Color lineColor;

  RiskTrendPainter({required this.values, required this.lineColor});

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

    final linePoints = List.generate(values.length, pointForIndex);

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

    final path = Path()..moveTo(linePoints.first.dx, linePoints.first.dy);

    for (int i = 1; i < linePoints.length; i++) {
      path.lineTo(linePoints[i].dx, linePoints[i].dy);
    }

    canvas.drawPath(path, linePaint);

    final dotPaint = Paint()..color = lineColor;

    for (final p in linePoints) {
      canvas.drawCircle(p, 4.8, dotPaint);

      canvas.drawCircle(p, 2.2, Paint()..color = Colors.white);
    }

    final textPainter = TextPainter(
      textDirection: TextDirection.ltr,
      textAlign: TextAlign.center,
    );

    for (int i = 0; i < values.length; i++) {
      textPainter.text = TextSpan(
        text: values[i].toInt().toString(),
        style: const TextStyle(
          fontSize: 11,
          fontWeight: FontWeight.w700,
          color: Color(0xFF0F172A),
        ),
      );

      textPainter.layout();

      textPainter.paint(
        canvas,
        Offset(linePoints[i].dx - textPainter.width / 2, linePoints[i].dy - 22),
      );
    }
  }

  @override
  bool shouldRepaint(covariant RiskTrendPainter oldDelegate) {
    return oldDelegate.values != values || oldDelegate.lineColor != lineColor;
  }
}
