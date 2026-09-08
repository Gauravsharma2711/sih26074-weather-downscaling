import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../l10n/app_localizations.dart';

class FarmerScaffold extends StatelessWidget {
  final String title;
  final String selectedPanchayatName;
  final String currentLang;
  final Function(String) onLanguageChanged;
  final VoidCallback onSelectPanchayat;
  final Widget body;
  final int selectedNavIndex;
  final Function(int) onNavIndexChanged;

  const FarmerScaffold({
    super.key,
    required this.title,
    required this.selectedPanchayatName,
    required this.currentLang,
    required this.onLanguageChanged,
    required this.onSelectPanchayat,
    required this.body,
    this.selectedNavIndex = 0,
    required this.onNavIndexChanged,
  });

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Scaffold(
      backgroundColor: AppColors.canvas,
      appBar: AppBar(
        backgroundColor: AppColors.surface,
        elevation: 0,
        titleSpacing: 16,
        title: Row(
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: AppColors.primary050,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.primary100),
              ),
              child: const Icon(
                Icons.eco,
                color: AppColors.primary700,
                size: 20,
              ),
            ),
            const SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  l10n.appName,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.w800,
                    color: AppColors.primary700,
                    height: 1.1,
                  ),
                ),
                Semantics(
                  button: true,
                  label: '${l10n.selectVillage}: $selectedPanchayatName',
                  child: InkWell(
                    onTap: onSelectPanchayat,
                    borderRadius: BorderRadius.circular(4),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Text(
                          selectedPanchayatName,
                          style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.ink700,
                          ),
                        ),
                        const SizedBox(width: 4),
                        const Icon(
                          Icons.keyboard_arrow_down,
                          size: 16,
                          color: AppColors.primary600,
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          // Language Switcher (English / Marathi / Hindi)
          Container(
            margin: const EdgeInsets.only(right: 16),
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
            decoration: BoxDecoration(
              color: AppColors.surfaceSubtle,
              borderRadius: BorderRadius.circular(999),
              border: Border.all(color: AppColors.ink300),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildLangButton('EN', 'en'),
                _buildLangButton('मराठी', 'mr'),
                _buildLangButton('हिन्दी', 'hi'),
              ],
            ),
          ),
        ],
      ),
      body: SafeArea(child: body),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(
            top: BorderSide(color: Color(0xFFE5EAE7), width: 1),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: selectedNavIndex,
          onTap: onNavIndexChanged,
          backgroundColor: AppColors.surface,
          elevation: 0,
          selectedItemColor: AppColors.primary700,
          unselectedItemColor: AppColors.ink500,
          selectedFontSize: 11,
          unselectedFontSize: 11,
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w700),
          unselectedLabelStyle: const TextStyle(fontWeight: FontWeight.w500),
          type: BottomNavigationBarType.fixed,
          items: [
            BottomNavigationBarItem(
              icon: const Icon(Icons.home_outlined),
              activeIcon: const Icon(Icons.home),
              label: l10n.navHome,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.wb_sunny_outlined),
              activeIcon: const Icon(Icons.wb_sunny),
              label: l10n.navForecast,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.assignment_outlined),
              activeIcon: const Icon(Icons.assignment),
              label: l10n.navAdvisory,
            ),
            BottomNavigationBarItem(
              icon: const Icon(Icons.person_outline),
              activeIcon: const Icon(Icons.person),
              label: l10n.navProfile,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLangButton(String label, String langCode) {
    final isSelected = currentLang == langCode;
    return Semantics(
      button: true,
      selected: isSelected,
      label: 'Switch language to $label',
      child: InkWell(
        onTap: () => onLanguageChanged(langCode),
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: isSelected ? AppColors.primary500 : Colors.transparent,
            borderRadius: BorderRadius.circular(999),
          ),
          child: Text(
            label,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: isSelected ? AppColors.surface : AppColors.ink700,
            ),
          ),
        ),
      ),
    );
  }
}
