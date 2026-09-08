import 'package:flutter/material.dart';
import '../models/farmer_forecast.dart';
import '../theme/app_theme.dart';
import '../widgets/metric_tile.dart';
import '../l10n/app_localizations.dart';

/// Detailed Weather Forecast Screen for Farmers
/// Free of technical ML jargon; focused on actionable field weather
class ForecastDetailScreen extends StatelessWidget {
  final FarmerForecast forecast;
  final VoidCallback onRefresh;
  final VoidCallback onSwitchPanchayat;

  const ForecastDetailScreen({
    super.key,
    required this.forecast,
    required this.onRefresh,
    required this.onSwitchPanchayat,
  });

  String _getCategoryLabel(String category, AppLocalizations l10n) {
    switch (category.toUpperCase()) {
      case 'LIGHT_RAIN':
        return l10n.categoryLightRain;
      case 'MODERATE_RAIN':
        return l10n.categoryModerateRain;
      case 'HEAVY_RAIN':
      case 'VERY_HEAVY_RAIN':
        return l10n.categoryHeavyRain;
      case 'NO_RAIN':
        return l10n.categoryNoRain;
      default:
        return category.replaceAll('_', ' ');
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final isHeavy = forecast.rainfallMm >= 64.5;
    final isModerate = forecast.rainfallMm >= 7.6 && forecast.rainfallMm < 64.5;

    final categoryColor = isHeavy
        ? AppColors.danger600
        : isModerate
            ? AppColors.primary700
            : AppColors.info600;

    final badgeBg = isHeavy
        ? AppColors.danger100
        : isModerate
            ? AppColors.primary100
            : AppColors.info100;

    final categoryLabel = _getCategoryLabel(forecast.rainfallCategory, l10n);

    return RefreshIndicator(
      onRefresh: () async => onRefresh(),
      color: AppColors.primary500,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Location Header Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE5EAE7)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.location_on, size: 16, color: AppColors.primary700),
                          const SizedBox(width: 4),
                          Text(
                            forecast.panchayatName,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w700,
                              color: AppColors.ink900,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 2),
                      Text(
                        '${forecast.blockName} Block, ${forecast.districtName}',
                        style: const TextStyle(
                          fontSize: 12,
                          color: AppColors.ink500,
                        ),
                      ),
                    ],
                  ),
                  GestureDetector(
                    onTap: onSwitchPanchayat,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: AppColors.primary050,
                        borderRadius: BorderRadius.circular(999),
                        border: Border.all(color: AppColors.primary100),
                      ),
                      child: Text(
                        l10n.changeVillage,
                        style: const TextStyle(
                          fontSize: 11,
                          fontWeight: FontWeight.w700,
                          color: AppColors.primary700,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Expected Rainfall Overview Card
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(20),
                border: Border.all(
                  color: isHeavy ? const Color(0xFFF5C6CB) : const Color(0xFFE5EAE7),
                  width: 1.5,
                ),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${l10n.tomorrow} • ${forecast.forecastDate}',
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.ink500,
                        ),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
                        decoration: BoxDecoration(
                          color: badgeBg,
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: Text(
                          categoryLabel,
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: categoryColor,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    crossAxisAlignment: CrossAxisAlignment.center,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.panchayatRainfall,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: AppColors.ink500,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.baseline,
                            textBaseline: TextBaseline.alphabetic,
                            children: [
                              Text(
                                forecast.rainfallMm.toStringAsFixed(1),
                                style: TextStyle(
                                  fontSize: 40,
                                  fontWeight: FontWeight.w800,
                                  color: categoryColor,
                                  height: 1.0,
                                ),
                              ),
                              const SizedBox(width: 4),
                              const Text(
                                'mm',
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: AppColors.ink700,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Container(
                        width: 56,
                        height: 56,
                        decoration: BoxDecoration(
                          color: isHeavy
                              ? AppColors.danger100
                              : isModerate
                                  ? AppColors.primary050
                                  : AppColors.info100,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Icon(
                          isHeavy
                              ? Icons.thunderstorm_outlined
                              : isModerate
                                  ? Icons.water_drop_outlined
                                  : Icons.wb_sunny_outlined,
                          color: categoryColor,
                          size: 32,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Agricultural Field Weather Conditions Grid
            Text(
              l10n.operationalGuidance,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: AppColors.ink900,
              ),
            ),
            const SizedBox(height: 10),

            Row(
              children: [
                Expanded(
                  child: MetricTile(
                    label: l10n.sprayingWindow,
                    value: forecast.rainfallMm > 2.5 ? l10n.postpone : l10n.safeWindow,
                    icon: Icons.grass,
                    iconColor: forecast.rainfallMm > 2.5
                        ? AppColors.warning600
                        : AppColors.primary600,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: MetricTile(
                    label: l10n.fieldTillage,
                    value: isHeavy ? l10n.delay : l10n.permitted,
                    icon: Icons.agriculture_outlined,
                    iconColor: isHeavy ? AppColors.danger600 : AppColors.primary600,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: MetricTile(
                    label: l10n.fieldDrainage,
                    value: forecast.rainfallMm >= 20.0 ? l10n.openTrenches : l10n.normal,
                    icon: Icons.water_damage_outlined,
                    iconColor: forecast.rainfallMm >= 20.0
                        ? AppColors.warning600
                        : AppColors.primary600,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: MetricTile(
                    label: l10n.rainRiskLevel,
                    value: forecast.severity,
                    icon: Icons.shield_outlined,
                    iconColor: isHeavy ? AppColors.danger600 : AppColors.primary600,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 20),

            // Time-of-Day Weather Breakdown
            Text(
              l10n.timeOfDayOutlook,
              style: const TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w700,
                color: AppColors.ink900,
              ),
            ),
            const SizedBox(height: 10),

            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE5EAE7)),
              ),
              child: Column(
                children: [
                  _buildTimeSlotRow(
                    'Morning (06:00 - 12:00)',
                    forecast.rainfallMm > 15 ? 'Overcast / Showers' : 'Partly Cloudy / Clear',
                    Icons.wb_twilight,
                    forecast.rainfallMm > 15 ? 'Avoid chemical sprays' : 'Favorable for weeding',
                  ),
                  const Divider(height: 20, color: Color(0xFFF0F4F1)),
                  _buildTimeSlotRow(
                    'Afternoon (12:00 - 18:00)',
                    forecast.rainfallMm > 5 ? 'Scattered Rain' : 'Moderate Sun',
                    Icons.wb_sunny_outlined,
                    forecast.rainfallMm > 5 ? 'Monitor low-lying plots' : 'Normal field work',
                  ),
                  const Divider(height: 20, color: Color(0xFFF0F4F1)),
                  _buildTimeSlotRow(
                    'Evening & Night (18:00+)',
                    forecast.rainfallMm > 0 ? 'Cool / Damp Soil' : 'Dry & Clear',
                    Icons.nights_stay_outlined,
                    'Check bunds and nursery covers',
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimeSlotRow(String time, String condition, IconData icon, String tip) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: AppColors.primary050,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Icon(icon, size: 20, color: AppColors.primary700),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                time,
                style: const TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.w700,
                  color: AppColors.ink900,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                condition,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: AppColors.primary700,
                ),
              ),
              Text(
                tip,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.ink500,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
