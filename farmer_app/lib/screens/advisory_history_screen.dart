import 'package:flutter/material.dart';
import '../models/farmer_forecast.dart';
import '../theme/app_theme.dart';

class AdvisoryHistoryScreen extends StatelessWidget {
  final FarmerForecast currentForecast;

  const AdvisoryHistoryScreen({
    super.key,
    required this.currentForecast,
  });

  @override
  Widget build(BuildContext context) {
    final historyItems = [
      {
        'date': '2026-09-08',
        'title': 'Light Scattered Showers — Weeding & Hoeing',
        'rainfall': '4.2 mm',
        'category': 'LIGHT_RAIN',
        'officer': 'SMS-AGRI-NASHIK-04',
        'points': 'Soil moisture optimal for intercultural weeding. Maintain crop bunds.',
      },
      {
        'date': '2026-09-07',
        'title': 'Dry Weather Window — Safe Spraying Permitted',
        'rainfall': '0.0 mm',
        'category': 'NO_RAIN',
        'officer': 'SMS-AGRI-NASHIK-04',
        'points': 'Clear weather suitable for bio-fungicide sprays in onion nurseries.',
      },
      {
        'date': '2026-09-06',
        'title': 'Moderate Showers — Drainage Maintenance',
        'rainfall': '18.4 mm',
        'category': 'MODERATE_RAIN',
        'officer': 'DAO-NASHIK-HEAD',
        'points': 'Ensure excess runoff is guided towards recharge pits.',
      },
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Advisory History for ${currentForecast.panchayatName}',
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: AppColors.ink900,
            ),
          ),
          const SizedBox(height: 4),
          const Text(
            'Official past weather and verified guidance records.',
            style: TextStyle(
              fontSize: 12,
              color: AppColors.ink500,
            ),
          ),
          const SizedBox(height: 16),

          ...historyItems.map((item) => Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFE5EAE7)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Row(
                          children: [
                            const Icon(Icons.calendar_month, size: 14, color: AppColors.primary700),
                            const SizedBox(width: 6),
                            Text(
                              item['date']!,
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.w700,
                                color: AppColors.ink900,
                              ),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(
                            color: AppColors.primary050,
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: Text(
                            item['rainfall']!,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: AppColors.primary700,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      item['title']!,
                      style: const TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.w600,
                        color: AppColors.ink900,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      item['points']!,
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppColors.ink700,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        const Icon(Icons.verified, size: 12, color: AppColors.primary600),
                        const SizedBox(width: 4),
                        Text(
                          'Verified by ${item['officer']}',
                          style: const TextStyle(
                            fontSize: 10,
                            color: AppColors.ink500,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
