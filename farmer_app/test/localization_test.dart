import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:farmer_app/l10n/app_localizations.dart';

void main() {
  group('AppLocalizations Architecture Tests', () {
    test('English dictionary resolves all core UI keys', () {
      final l10n = AppLocalizations(const Locale('en'));
      expect(l10n.appName, 'GramSevak');
      expect(l10n.navHome, 'Home');
      expect(l10n.todaysForecast, "Today's / Next Forecast");
      expect(l10n.panchayatRainfall, 'Panchayat 24-Hour Rainfall');
      expect(l10n.agriculturalAdvisory, 'Agricultural Advisory');
      expect(l10n.sprayingWindow, 'Spraying Window');
      expect(l10n.kisanCallCentre, 'Kisan Call Centre (Toll Free)');
    });

    test('Marathi dictionary resolves localized terms', () {
      final l10n = AppLocalizations(const Locale('mr'));
      expect(l10n.navHome, 'मुख्य');
      expect(l10n.todaysForecast, 'आजचा / पुढील अंदाज');
      expect(l10n.agriculturalAdvisory, 'कृषी सल्ला');
      expect(l10n.changeVillage, 'गाव बदला');
    });

    test('Hindi dictionary resolves localized terms', () {
      final l10n = AppLocalizations(const Locale('hi'));
      expect(l10n.navHome, 'होम');
      expect(l10n.todaysForecast, 'आज का / अगला पूर्वानुमान');
      expect(l10n.agriculturalAdvisory, 'कृषि सलाह');
      expect(l10n.changeVillage, 'गांव बदलें');
    });

    test('Unsupported or missing locale safely falls back to English', () {
      final l10n = AppLocalizations(const Locale('es'));
      expect(l10n.navHome, 'Home');
      expect(l10n.todaysForecast, "Today's / Next Forecast");
    });
  });
}
