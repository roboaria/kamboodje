import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  runApp(const MaterialApp(
    debugShowCheckedModeBanner: false,
    home: TarazHomeScreen(),
  ));
}

class TarazHomeScreen extends StatefulWidget {
  const TarazHomeScreen({super.key});

  @override
  State<TarazHomeScreen> createState() => _TarazHomeScreenState();
}

class _TarazHomeScreenState extends State<TarazHomeScreen> {
  late final WebViewController controller;
  bool isLoading = true;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFF6F3EE))
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageFinished: (String url) {
            setState(() => isLoading = false);
          },
        ),
      )
      ..loadFlutterAsset('assets/index.html');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Stack(
          children: [
            WebViewWidget(controller: controller),
            if (isLoading)
              const Center(
                child: CircularProgressIndicator(color: Color(0xFF0B2D4A)),
              ),
          ],
        ),
      ),
    );
  }
}
