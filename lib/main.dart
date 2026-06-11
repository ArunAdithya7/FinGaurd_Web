import 'package:flutter/material.dart';
import 'splash_screen.dart';
// import 'dashboard_screen.dart';

void main() {
  runApp(const FinGuardApp());
}

class FinGuardApp extends StatelessWidget {
  const FinGuardApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'FinGuard',
      theme: ThemeData(useMaterial3: true),
      home: const SplashScreen(),
    );
  }
}
