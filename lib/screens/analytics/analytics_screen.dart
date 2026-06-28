import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../services/api_service.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  final ApiService _api = ApiService();
  Map<String, dynamic>? _overview;
  List<Map<String, dynamic>> _colorDistribution = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    setState(() => _isLoading = true);

    try {
      final response =
          await _api.get('${AppConstants.analyticsEndpoint}/overview');

      setState(() {
        _overview = response['overview'] as Map<String, dynamic>?;
        _colorDistribution = List<Map<String, dynamic>>.from(
          response['color_distribution'] ?? [],
        );
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Failed to load analytics');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryWhite,
      appBar: AppBar(
        title: const Text('ANALYTICS'),
        actions: [
          IconButton(
            icon: const Icon(Iconsax.refresh),
            onPressed: _loadAnalytics,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(
              child: CircularProgressIndicator(
                color: AppTheme.primaryBlack,
                strokeWidth: 2,
              ),
            )
          : RefreshIndicator(
              onRefresh: _loadAnalytics,
              color: AppTheme.primaryBlack,
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Overview Stats
                    _buildOverviewStats(),

                    const SizedBox(height: 24),

                    // Items by Layer
                    _buildItemsByLayer(),

                    const SizedBox(height: 24),

                    // Color Distribution
                    _buildColorDistribution(),

                    const SizedBox(height: 24),

                    // Most/Least Worn
                    _buildWornStats(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOverviewStats() {
    final totalItems = _overview?['total_items'] ?? 0;
    final totalOutfits = _overview?['total_outfits'] ?? 0;
    final totalTimesWorn = _overview?['total_times_worn'] ?? 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'OVERVIEW',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                letterSpacing: 2,
                color: AppTheme.mediumGray,
              ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildStatCard(
                icon: Iconsax.bag_2,
                value: totalItems.toString(),
                label: 'Items',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                icon: Iconsax.layer,
                value: totalOutfits.toString(),
                label: 'Outfits',
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildStatCard(
                icon: Iconsax.repeat,
                value: totalTimesWorn.toString(),
                label: 'Times Worn',
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.backgroundGray,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, size: 24, color: AppTheme.charcoal),
          const SizedBox(height: 8),
          Text(
            value,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.mediumGray,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildItemsByLayer() {
    final itemsByLayer =
        _overview?['items_by_layer'] as Map<String, dynamic>? ?? {};

    if (itemsByLayer.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ITEMS BY CATEGORY',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                letterSpacing: 2,
                color: AppTheme.mediumGray,
              ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(color: AppTheme.lightGray),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: itemsByLayer.entries.map((entry) {
              final total = _overview?['total_items'] ?? 1;
              final percentage = total > 0 ? (entry.value / total) : 0.0;

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          entry.key.toUpperCase(),
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    letterSpacing: 1,
                                    fontWeight: FontWeight.w500,
                                  ),
                        ),
                        Text(
                          '${entry.value}',
                          style:
                              Theme.of(context).textTheme.bodyMedium?.copyWith(
                                    fontWeight: FontWeight.w600,
                                  ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    LinearProgressIndicator(
                      value: percentage,
                      backgroundColor: AppTheme.lightGray,
                      valueColor: const AlwaysStoppedAnimation<Color>(
                          AppTheme.charcoal),
                      minHeight: 6,
                      borderRadius: BorderRadius.circular(3),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildColorDistribution() {
    if (_colorDistribution.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'COLOR PALETTE',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                letterSpacing: 2,
                color: AppTheme.mediumGray,
              ),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(color: AppTheme.lightGray),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              // Color circles
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: _colorDistribution.take(8).map((color) {
                  return Tooltip(
                    message: '${color['color_name']}: ${color['count']} items',
                    child: Container(
                      width: 36,
                      height: 36,
                      decoration: BoxDecoration(
                        color: _hexToColor(color['color_hex'] ?? '#CCCCCC'),
                        shape: BoxShape.circle,
                        border: Border.all(color: AppTheme.lightGray),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 4,
                            offset: const Offset(0, 2),
                          ),
                        ],
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 16),
              const Divider(),
              const SizedBox(height: 12),

              // Color list
              ...(_colorDistribution.take(5).map((color) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    children: [
                      Container(
                        width: 16,
                        height: 16,
                        decoration: BoxDecoration(
                          color: _hexToColor(color['color_hex'] ?? '#CCCCCC'),
                          shape: BoxShape.circle,
                          border: Border.all(color: AppTheme.lightGray),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          color['color_name']?.toString().toUpperCase() ??
                              'UNKNOWN',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    letterSpacing: 1,
                                  ),
                        ),
                      ),
                      Text(
                        '${color['percentage']?.toStringAsFixed(0) ?? 0}%',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ],
                  ),
                );
              })),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildWornStats() {
    final mostWorn = _overview?['most_worn_item'] as Map<String, dynamic>?;
    final leastWorn = _overview?['least_worn_item'] as Map<String, dynamic>?;

    if (mostWorn == null && leastWorn == null) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'WEAR STATISTICS',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                letterSpacing: 2,
                color: AppTheme.mediumGray,
              ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            if (mostWorn != null)
              Expanded(
                child: _buildWornItemCard(
                  title: 'MOST WORN',
                  item: mostWorn,
                  icon: Iconsax.heart,
                  iconColor: AppTheme.success,
                ),
              ),
            if (mostWorn != null && leastWorn != null)
              const SizedBox(width: 12),
            if (leastWorn != null)
              Expanded(
                child: _buildWornItemCard(
                  title: 'LEAST WORN',
                  item: leastWorn,
                  icon: Iconsax.emoji_sad,
                  iconColor: AppTheme.error,
                ),
              ),
          ],
        ),
      ],
    );
  }

  Widget _buildWornItemCard({
    required String title,
    required Map<String, dynamic> item,
    required IconData icon,
    required Color iconColor,
  }) {
    final imagePath =
        item['image_path']?.toString().replaceAll('\\', '/') ?? '';
    final imageUrl = '${AppConstants.baseUrl}/$imagePath';
    final timesWorn = item['times_worn'] ?? 0;
    final clothingType = item['clothing_type'] ?? 'Unknown';

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: AppTheme.lightGray),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, size: 16, color: iconColor),
              const SizedBox(width: 6),
              Text(
                title,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      letterSpacing: 1,
                      color: AppTheme.mediumGray,
                    ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              height: 100,
              width: double.infinity,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                color: AppTheme.backgroundGray,
                height: 100,
              ),
              errorWidget: (context, url, error) => Container(
                color: AppTheme.backgroundGray,
                height: 100,
                child: const Icon(Iconsax.image),
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            clothingType.toString().toUpperCase(),
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 4),
          Text(
            'Worn $timesWorn times',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.mediumGray,
                ),
          ),
        ],
      ),
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceAll('#', '');
    if (hex.length == 6) {
      hex = 'FF$hex';
    }
    return Color(int.parse(hex, radix: 16));
  }
}
