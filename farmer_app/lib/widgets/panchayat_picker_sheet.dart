import 'dart:async';
import 'package:flutter/material.dart';
import '../models/panchayat_item.dart';
import '../repositories/farmer_repository.dart';
import '../theme/app_theme.dart';
import '../l10n/app_localizations.dart';

/// Development & Demo Panchayat Selector for Farmer Mobile App.
/// 
/// Allows demo users to pick from all real Gram Panchayats in the live database.
/// - Read-only inspection; does not modify any database records.
/// - Clearly separated from production farmer onboarding and authentication.
class PanchayatPickerSheet extends StatefulWidget {
  final List<PanchayatItem> panchayats;
  final int selectedPanchayatId;
  final Function(PanchayatItem) onSelect;
  final FarmerRepository? repository;

  const PanchayatPickerSheet({
    super.key,
    required this.panchayats,
    required this.selectedPanchayatId,
    required this.onSelect,
    this.repository,
  });

  @override
  State<PanchayatPickerSheet> createState() => _PanchayatPickerSheetState();
}

class _PanchayatPickerSheetState extends State<PanchayatPickerSheet> {
  late List<PanchayatItem> _displayedPanchayats;
  final FarmerRepository _repo = FarmerRepository();
  Timer? _debounceTimer;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _displayedPanchayats = widget.panchayats;
  }

  @override
  void dispose() {
    _debounceTimer?.cancel();
    super.dispose();
  }

  void _onSearchChanged(String query) {
    _debounceTimer?.cancel();
    _debounceTimer = Timer(const Duration(milliseconds: 250), () async {
      if (!mounted) return;
      if (query.trim().isEmpty) {
        setState(() {
          _displayedPanchayats = widget.panchayats;
          _isLoading = false;
        });
        return;
      }

      setState(() => _isLoading = true);
      try {
        final results = await (widget.repository ?? _repo).getPanchayats(search: query.trim());
        if (mounted) {
          setState(() {
            _displayedPanchayats = results;
            _isLoading = false;
          });
        }
      } catch (_) {
        if (mounted) {
          setState(() => _isLoading = false);
        }
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);

    return Container(
      decoration: const BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppColors.ink300,
                borderRadius: BorderRadius.circular(999),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Header Row with Dev Demo Badge
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                l10n.selectVillage,
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: AppColors.ink900,
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppColors.primary050,
                  borderRadius: BorderRadius.circular(999),
                  border: Border.all(color: AppColors.primary100),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.auto_awesome, size: 12, color: AppColors.primary700),
                    SizedBox(width: 4),
                    Text(
                      'DEV DEMO',
                      style: TextStyle(
                        fontSize: 10,
                        fontWeight: FontWeight.w800,
                        color: AppColors.primary700,
                        letterSpacing: 0.4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          const Text(
            'Live read-only selector loading real IMD downscaled forecasts from database.',
            style: TextStyle(
              fontSize: 12,
              color: AppColors.ink500,
            ),
          ),
          const SizedBox(height: 14),

          // Search Field
          TextField(
            onChanged: _onSearchChanged,
            decoration: InputDecoration(
              hintText: l10n.searchVillage,
              prefixIcon: const Icon(Icons.search, color: AppColors.ink500, size: 20),
              suffixIcon: _isLoading
                  ? const Padding(
                      padding: EdgeInsets.all(12.0),
                      child: SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary500),
                      ),
                    )
                  : null,
              filled: true,
              fillColor: AppColors.surfaceSubtle,
              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFE5EAE7)),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: Color(0xFFE5EAE7)),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppColors.primary500),
              ),
            ),
          ),
          const SizedBox(height: 14),

          // List of Real Panchayats
          ConstrainedBox(
            constraints: BoxConstraints(
              maxHeight: MediaQuery.of(context).size.height * 0.45,
            ),
            child: _displayedPanchayats.isEmpty && !_isLoading
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(24.0),
                      child: Text(
                        'No matching Panchayats found in database.',
                        style: TextStyle(fontSize: 13, color: AppColors.ink500),
                      ),
                    ),
                  )
                : ListView.separated(
                    shrinkWrap: true,
                    itemCount: _displayedPanchayats.length,
                    separatorBuilder: (_, __) => const Divider(color: Color(0xFFF0F4F1), height: 1),
                    itemBuilder: (ctx, idx) {
                      final p = _displayedPanchayats[idx];
                      final isSelected = p.panchayatId == widget.selectedPanchayatId;
                      return ListTile(
                        contentPadding: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
                        leading: Container(
                          width: 38,
                          height: 38,
                          decoration: BoxDecoration(
                            color: isSelected ? AppColors.primary100 : AppColors.surfaceSubtle,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Icon(
                            Icons.location_on_outlined,
                            color: isSelected ? AppColors.primary700 : AppColors.ink500,
                            size: 20,
                          ),
                        ),
                        title: Row(
                          children: [
                            Text(
                              p.panchayatName,
                              style: TextStyle(
                                fontSize: 14,
                                fontWeight: isSelected ? FontWeight.w700 : FontWeight.w600,
                                color: isSelected ? AppColors.primary700 : AppColors.ink900,
                              ),
                            ),
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 5, vertical: 1),
                              decoration: BoxDecoration(
                                color: AppColors.ink100,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                'LGD ${p.lgdCode}',
                                style: const TextStyle(fontSize: 10, color: AppColors.ink700, fontWeight: FontWeight.w600),
                              ),
                            ),
                          ],
                        ),
                        subtitle: Text(
                          '${p.blockName} Block • ${p.districtName} • ${p.elevationM.round()}m',
                          style: const TextStyle(fontSize: 12, color: AppColors.ink500),
                        ),
                        trailing: isSelected
                            ? const Icon(Icons.check_circle, color: AppColors.primary600, size: 20)
                            : const Icon(Icons.chevron_right, color: AppColors.ink300, size: 18),
                        onTap: () {
                          widget.onSelect(p);
                          Navigator.pop(context);
                        },
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
