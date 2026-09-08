import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:farmer_app/models/farmer_forecast.dart';
import 'package:farmer_app/repositories/farmer_repository.dart';
import 'package:farmer_app/widgets/advisory_card.dart';
import 'package:farmer_app/l10n/app_localizations.dart';

void main() {
  group('FarmerForecast Model Tests', () {
    test('Parses approved backend response correctly', () {
      final json = {
        'panchayat_name': 'Ajmer Saundane',
        'block_name': 'Baglan',
        'district_name': 'Nashik',
        'forecast_date': '2026-09-10',
        'rainfall_mm': 22.5,
        'rainfall_category': 'Moderate rainfall',
        'severity': 'MODERATE',
        'advisory_title': 'Moderate Rainfall Advisory for Ajmer Saundane',
        'advisory_points': [
          'Temporarily suspend all irrigation operations.',
          'Inspect and clean field drainage channels.'
        ],
        'advisory_status': 'APPROVED',
        'language': 'en',
        'available_languages': ['en', 'mr', 'hi'],
        'language_status': 'VERIFIED_PRIMARY'
      };

      final forecast = FarmerForecast.fromJson(json);

      expect(forecast.panchayatName, 'Ajmer Saundane');
      expect(forecast.rainfallMm, 22.5);
      expect(forecast.isApproved, isTrue);
      expect(forecast.hasActionableAdvice, isTrue);
      expect(forecast.advisoryPoints.length, 2);
    });

    test('Clamps negative rainfall values to 0.0 without crashing', () {
      final json = {
        'panchayat_name': 'Akhatwade',
        'block_name': 'Baglan',
        'district_name': 'Nashik',
        'forecast_date': '2026-09-10',
        'rainfall_mm': -4.5,
        'rainfall_category': 'No rainfall',
        'severity': 'LOW',
        'advisory_points': [],
        'advisory_status': 'NO_APPROVED_ADVISORY',
      };

      final forecast = FarmerForecast.fromJson(json);

      expect(forecast.rainfallMm, 0.0);
      expect(forecast.isApproved, isFalse);
      expect(forecast.hasActionableAdvice, isFalse);
    });

    test('Handles missing advisory and non-approved status safely', () {
      final json = {
        'panchayat_name': 'Mulher',
        'block_name': 'Baglan',
        'district_name': 'Nashik',
        'forecast_date': '2026-09-10',
        'rainfall_mm': 12.0,
        'rainfall_category': 'Moderate rainfall',
        'severity': 'MODERATE',
        'advisory_title': null,
        'advisory_points': null,
        'advisory_status': 'NO_APPROVED_ADVISORY',
      };

      final forecast = FarmerForecast.fromJson(json);

      expect(forecast.isApproved, isFalse);
      expect(forecast.advisoryTitle, isNull);
      expect(forecast.advisoryPoints, isEmpty);
      expect(forecast.hasActionableAdvice, isFalse);
    });
  });

  group('FarmerRepository Tests', () {
    test('Fallback Panchayats contains verified pilot list', () async {
      final repo = FarmerRepository();
      final panchayats = await repo.getPanchayats();

      expect(panchayats, isNotEmpty);
      expect(panchayats.any((p) => p.panchayatName.contains('Ajmer')), isTrue);
    });
  });

  group('Advisory UI Visibility Rules', () {
    testWidgets('Approved advisory renders officer seal and points', (tester) async {
      final forecast = FarmerForecast(
        panchayatName: 'Ajmer Saundane',
        blockName: 'Baglan',
        districtName: 'Nashik',
        forecastDate: '2026-09-10',
        rainfallMm: 22.5,
        rainfallCategory: 'Moderate rainfall',
        severity: 'MODERATE',
        advisoryTitle: 'Verified Moderate Rainfall Guidance',
        advisoryPoints: const ['Clear field drainage trenches immediately.'],
        advisoryStatus: 'APPROVED',
        language: 'en',
        availableLanguages: const ['en', 'mr', 'hi'],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            DefaultMaterialLocalizations.delegate,
            DefaultWidgetsLocalizations.delegate,
          ],
          home: Scaffold(
            body: AdvisoryCard(
              forecast: forecast,
              onAudioPlay: () {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text('Verified Moderate Rainfall Guidance'), findsOneWidget);
      expect(find.text('Clear field drainage trenches immediately.'), findsOneWidget);
      expect(find.byIcon(Icons.verified_user), findsOneWidget);
    });

    testWidgets('Non-approved advisory renders under-review placeholder and hides raw text', (tester) async {
      final forecast = FarmerForecast(
        panchayatName: 'Ajmer Saundane',
        blockName: 'Baglan',
        districtName: 'Nashik',
        forecastDate: '2026-09-10',
        rainfallMm: 15.0,
        rainfallCategory: 'Moderate rainfall',
        severity: 'LOW',
        advisoryTitle: 'Draft Unapproved Text',
        advisoryPoints: const ['Unverified advice that must never show.'],
        advisoryStatus: 'NO_APPROVED_ADVISORY',
        language: 'en',
        availableLanguages: const ['en', 'mr', 'hi'],
      );

      await tester.pumpWidget(
        MaterialApp(
          localizationsDelegates: const [
            AppLocalizations.delegate,
            DefaultMaterialLocalizations.delegate,
            DefaultWidgetsLocalizations.delegate,
          ],
          home: Scaffold(
            body: AdvisoryCard(
              forecast: forecast,
              onAudioPlay: () {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Must NOT show draft guidance text
      expect(find.text('Draft Unapproved Text'), findsNothing);
      expect(find.text('Unverified advice that must never show.'), findsNothing);

      // Must show under-review indicator
      expect(find.byIcon(Icons.hourglass_empty), findsOneWidget);
      expect(find.text('Advisory Under Officer Review'), findsOneWidget);
    });
  });
}
