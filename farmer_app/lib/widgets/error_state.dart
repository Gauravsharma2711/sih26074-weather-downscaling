import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Clean Error State with Retry Button for Farmer Mobile App
class FarmerErrorState extends StatelessWidget {
  final String title;
  final String message;
  final VoidCallback onRetry;

  const FarmerErrorState({
    super.key,
    this.title = 'Unable to Load Forecast',
    this.message = 'Please check your mobile connection or try refreshing the forecast.',
    required this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(28.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: AppColors.danger100,
                shape: BoxShape.circle,
                border: Border.all(color: const Color(0xFFF5C6CB)),
              ),
              child: const Icon(
                Icons.wifi_off_rounded,
                color: AppColors.danger600,
                size: 32,
              ),
            ),
            const SizedBox(height: 16),
            Text(
              title,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w700,
                color: AppColors.ink900,
              ),
            ),
            const SizedBox(height: 6),
            Text(
              message,
              textAlign: TextAlign.center,
              style: const TextStyle(
                fontSize: 13,
                color: AppColors.ink500,
                height: 1.4,
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh, size: 16),
              label: const Text('Try Again / पुन्हा प्रयत्न करा'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(220, 46),
                backgroundColor: AppColors.primary500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
