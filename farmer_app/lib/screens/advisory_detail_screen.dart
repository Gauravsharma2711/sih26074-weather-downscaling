import 'package:flutter/material.dart';
import '../models/farmer_forecast.dart';
import '../theme/app_theme.dart';
import '../l10n/app_localizations.dart';

/// Detailed Advisory Screen for Farmers
/// Displays the full approved agricultural advisory with voice support and emergency helpline
class AdvisoryDetailScreen extends StatefulWidget {
  final FarmerForecast forecast;
  final VoidCallback onRefresh;
  final String currentLang;
  final Function(String) onLanguageChanged;

  const AdvisoryDetailScreen({
    super.key,
    required this.forecast,
    required this.onRefresh,
    required this.currentLang,
    required this.onLanguageChanged,
  });

  @override
  State<AdvisoryDetailScreen> createState() => _AdvisoryDetailScreenState();
}

class _AdvisoryDetailScreenState extends State<AdvisoryDetailScreen> {
  bool _isPlayingAudio = false;

  void _handleAudioPlay() {
    if (!widget.forecast.isApproved) return;
    setState(() => _isPlayingAudio = true);
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'Playing verified voice advisory in ${widget.currentLang == 'mr' ? 'Marathi' : widget.currentLang == 'hi' ? 'Hindi' : 'English'}...',
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        backgroundColor: AppColors.primary700,
        duration: const Duration(seconds: 3),
        behavior: SnackBarBehavior.floating,
      ),
    );
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) setState(() => _isPlayingAudio = false);
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final isApproved = widget.forecast.isApproved;

    return RefreshIndicator(
      onRefresh: () async => widget.onRefresh(),
      color: AppColors.primary500,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Top Language Switcher Bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE5EAE7)),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.translate, size: 16, color: AppColors.primary700),
                      const SizedBox(width: 6),
                      Text(
                        l10n.preferredLanguage,
                        style: const TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: AppColors.ink700,
                        ),
                      ),
                    ],
                  ),
                  Row(
                    children: [
                      _buildLangChip('en', 'EN'),
                      const SizedBox(width: 6),
                      _buildLangChip('mr', 'मराठी'),
                      const SizedBox(width: 6),
                      _buildLangChip('hi', 'हिंदी'),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // Top Status Banner
            if (isApproved) ...[
              // Verified Officer Banner
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.primary050,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.primary100),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 44,
                      height: 44,
                      decoration: BoxDecoration(
                        color: AppColors.primary100,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(
                        Icons.verified,
                        color: AppColors.primary700,
                        size: 24,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            l10n.officerVerifiedAdvisory,
                            style: const TextStyle(
                              fontSize: 14,
                              fontWeight: FontWeight.w700,
                              color: AppColors.primary700,
                            ),
                          ),
                          Text(
                            '${widget.forecast.panchayatName} • ${widget.forecast.forecastDate}',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.ink700,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Audio Read-Aloud Voice Card
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
                        Text(
                          l10n.audioAdvisory,
                          style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: AppColors.ink900,
                          ),
                        ),
                        Text(
                          l10n.tapToListen,
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.ink500,
                          ),
                        ),
                      ],
                    ),
                    ElevatedButton.icon(
                      onPressed: _handleAudioPlay,
                      icon: Icon(
                        _isPlayingAudio ? Icons.volume_up : Icons.volume_mute_outlined,
                        size: 16,
                      ),
                      label: Text(_isPlayingAudio ? l10n.listeningAudio : l10n.listenAudio),
                      style: ElevatedButton.styleFrom(
                        minimumSize: const Size(110, 40),
                        backgroundColor: AppColors.primary500,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Full Advisory Content Box
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE5EAE7)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (widget.forecast.advisoryTitle != null) ...[
                      Text(
                        widget.forecast.advisoryTitle!,
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.ink900,
                          height: 1.3,
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Divider(color: Color(0xFFF0F4F1), height: 1),
                      const SizedBox(height: 16),
                    ],

                    Text(
                      l10n.actionableGuidance,
                      style: const TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.w700,
                        color: AppColors.primary700,
                      ),
                    ),
                    const SizedBox(height: 12),

                    ...widget.forecast.advisoryPoints.map(
                      (point) => Padding(
                        padding: const EdgeInsets.only(bottom: 12),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              margin: const EdgeInsets.only(top: 6, right: 10),
                              width: 8,
                              height: 8,
                              decoration: const BoxDecoration(
                                color: AppColors.primary500,
                                shape: BoxShape.circle,
                              ),
                            ),
                            Expanded(
                              child: Text(
                                point,
                                style: const TextStyle(
                                  fontSize: 13.5,
                                  color: AppColors.ink900,
                                  height: 1.5,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),

                    const SizedBox(height: 12),
                    const Divider(color: Color(0xFFF0F4F1), height: 1),
                    const SizedBox(height: 12),

                    Row(
                      children: [
                        const Icon(Icons.verified_user, size: 14, color: AppColors.primary700),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            l10n.verifiedByOfficer,
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppColors.ink500,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ] else ...[
              // Unapproved / Pending Review State (Never display DRAFT or REJECTED content)
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFFE5EAE7)),
                ),
                child: Column(
                  children: [
                    Container(
                      width: 56,
                      height: 56,
                      decoration: const BoxDecoration(
                        color: AppColors.warning100,
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Icons.hourglass_empty,
                        color: AppColors.warning600,
                        size: 28,
                      ),
                    ),
                    const SizedBox(height: 16),
                    Text(
                      l10n.advisoryUnderReview,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w700,
                        color: AppColors.ink900,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      l10n.advisoryUnderReviewDesc,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        fontSize: 13,
                        color: AppColors.ink500,
                        height: 1.5,
                      ),
                    ),
                    const SizedBox(height: 20),
                    OutlinedButton.icon(
                      onPressed: widget.onRefresh,
                      icon: const Icon(Icons.refresh, size: 16),
                      label: Text(l10n.tryAgain),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: AppColors.primary500),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 20),

            // Kisan Toll-Free Contact Banner
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: const Color(0xFFE5EAE7)),
              ),
              child: Row(
                children: [
                  Container(
                    width: 44,
                    height: 44,
                    decoration: BoxDecoration(
                      color: AppColors.primary050,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.call,
                      color: AppColors.primary700,
                      size: 22,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          l10n.kisanCallCentre,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: AppColors.ink900,
                          ),
                        ),
                        Text(
                          l10n.kisanCallCentreSub,
                          style: const TextStyle(
                            fontSize: 11,
                            color: AppColors.primary700,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildLangChip(String langCode, String label) {
    final isSelected = widget.currentLang == langCode;
    return GestureDetector(
      onTap: () => widget.onLanguageChanged(langCode),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: isSelected ? AppColors.primary500 : AppColors.surfaceSubtle,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(
            color: isSelected ? AppColors.primary500 : AppColors.ink300,
          ),
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
    );
  }
}
