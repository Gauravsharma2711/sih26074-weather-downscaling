import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

/// Shimmer Skeleton Loading State for Farmer Mobile App
class FarmerLoadingState extends StatelessWidget {
  const FarmerLoadingState({super.key});

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      physics: const NeverScrollableScrollPhysics(),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Greeting Skeleton
          _buildShimmerBox(width: 180, height: 22),
          const SizedBox(height: 6),
          _buildShimmerBox(width: 130, height: 14),
          const SizedBox(height: 16),

          // Weather Hero Card Skeleton
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
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildShimmerBox(width: 120, height: 16),
                    _buildShimmerBox(width: 80, height: 20, radius: 999),
                  ],
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        _buildShimmerBox(width: 100, height: 14),
                        const SizedBox(height: 6),
                        _buildShimmerBox(width: 140, height: 44),
                      ],
                    ),
                    _buildShimmerBox(width: 60, height: 60, radius: 16),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Metric Tiles Skeleton
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 72,
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE5EAE7)),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Container(
                  height: 72,
                  decoration: BoxDecoration(
                    color: AppColors.surface,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(color: const Color(0xFFE5EAE7)),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Advisory Card Skeleton
          Container(
            height: 180,
            decoration: BoxDecoration(
              color: AppColors.surface,
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: const Color(0xFFE5EAE7)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildShimmerBox({
    required double width,
    required double height,
    double radius = 8,
  }) {
    return Container(
      width: width,
      height: height,
      decoration: BoxDecoration(
        color: const Color(0xFFE8ECE9),
        borderRadius: BorderRadius.circular(radius),
      ),
    );
  }
}
