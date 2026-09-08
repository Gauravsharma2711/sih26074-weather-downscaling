import 'package:flutter/material.dart';

/// Universal Farmer Product Design System — Color Tokens & Theme
/// Source of Truth: brain.md
class AppColors {
  // Primary Palette
  static const Color primary700 = Color(0xFF056B43);
  static const Color primary600 = Color(0xFF087A4B);
  static const Color primary500 = Color(0xFF0A8A57);
  static const Color primary100 = Color(0xFFDDF3E8);
  static const Color primary050 = Color(0xFFEFFAF4);

  // Background Surfaces
  static const Color canvas = Color(0xFFF3F4F2);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceSubtle = Color(0xFFF8F9F7);

  // Typography & Neutrals (Ink)
  static const Color ink900 = Color(0xFF1E2823);
  static const Color ink700 = Color(0xFF425149);
  static const Color ink500 = Color(0xFF77847C);
  static const Color ink300 = Color(0xFFC9D1CC);
  static const Color ink100 = Color(0xFFEAEFEA);

  // Semantic Alerts
  static const Color warning600 = Color(0xFFC78318);
  static const Color warning100 = Color(0xFFFFF1CF);

  static const Color danger600 = Color(0xFFC94B43);
  static const Color danger100 = Color(0xFFFDE8E6);

  static const Color info600 = Color(0xFF3D78A6);
  static const Color info100 = Color(0xFFE3F2FD);

  static const Color sun500 = Color(0xFFF6C744);
  static const Color sun100 = Color(0xFFFEF9E7);
}

class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: AppColors.canvas,
      colorScheme: const ColorScheme.light(
        primary: AppColors.primary500,
        onPrimary: AppColors.surface,
        surface: AppColors.surface,
        onSurface: AppColors.ink900,
        surfaceContainerLow: AppColors.surfaceSubtle,
        outline: AppColors.ink300,
        error: AppColors.danger600,
      ),
      fontFamily: 'Inter',
      appBarTheme: const AppBarTheme(
        backgroundColor: AppColors.surface,
        elevation: 0,
        scrolledUnderElevation: 1,
        centerTitle: false,
        iconTheme: IconThemeData(color: AppColors.ink900),
        titleTextStyle: TextStyle(
          color: AppColors.ink900,
          fontSize: 18,
          fontWeight: FontWeight.w700,
          letterSpacing: -0.2,
        ),
      ),
      cardTheme: CardThemeData(
        color: AppColors.surface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: Color(0xFFE5EAE7), width: 1),
        ),
        margin: EdgeInsets.zero,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary500,
          foregroundColor: AppColors.surface,
          elevation: 0,
          minimumSize: const Size(double.infinity, 48),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
            letterSpacing: 0.1,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: AppColors.ink900,
          elevation: 0,
          minimumSize: const Size(double.infinity, 48),
          side: const BorderSide(color: AppColors.ink300, width: 1),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(999),
          ),
          textStyle: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
    );
  }
}
