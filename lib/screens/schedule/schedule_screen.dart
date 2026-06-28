import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:iconsax/iconsax.dart';
import 'package:intl/intl.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/weather_provider.dart';
import '../../services/api_service.dart';

class ScheduleScreen extends StatefulWidget {
  const ScheduleScreen({super.key});

  @override
  State<ScheduleScreen> createState() => _ScheduleScreenState();
}

class _ScheduleScreenState extends State<ScheduleScreen> {
  final ApiService _api = ApiService();
  List<Map<String, dynamic>> _weekSchedule = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadSchedule();
  }

  Future<void> _loadSchedule() async {
    setState(() => _isLoading = true);

    try {
      final weatherProvider =
          Provider.of<WeatherProvider>(context, listen: false);

      final response = await _api.get(
        '${AppConstants.scheduleEndpoint}/week',
        queryParams: {
          'latitude': weatherProvider.latitude.toString(),
          'longitude': weatherProvider.longitude.toString(),
        },
      );

      setState(() {
        _weekSchedule = List<Map<String, dynamic>>.from(response['week'] ?? []);
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      _showErrorSnackBar('Failed to load schedule');
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.error),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: AppTheme.success),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryWhite,
      appBar: AppBar(
        title: const Text('SCHEDULE'),
        actions: [
          IconButton(
            icon: const Icon(Iconsax.refresh),
            onPressed: _loadSchedule,
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
              onRefresh: _loadSchedule,
              color: AppTheme.primaryBlack,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _weekSchedule.length,
                itemBuilder: (context, index) {
                  return _buildDayCard(_weekSchedule[index]);
                },
              ),
            ),
    );
  }

  Widget _buildDayCard(Map<String, dynamic> day) {
    final date = DateTime.parse(day['date']);
    final dayName = day['day_name'] ?? DateFormat('EEEE').format(date);
    final isToday = day['is_today'] ?? false;
    final weather = day['weather_forecast'] as Map<String, dynamic>?;
    final scheduledOutfit = day['scheduled_outfit'] as Map<String, dynamic>?;

    return GestureDetector(
      onTap: () {
        if (scheduledOutfit != null) {
          _showOutfitDetails(day, scheduledOutfit);
        } else {
          _generateOutfitForDay(day);
        }
      },
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        decoration: BoxDecoration(
          color: isToday ? AppTheme.charcoal : AppTheme.primaryWhite,
          borderRadius: BorderRadius.circular(16),
          border: isToday ? null : Border.all(color: AppTheme.lightGray),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Text(
                            dayName.toUpperCase(),
                            style: Theme.of(context)
                                .textTheme
                                .labelLarge
                                ?.copyWith(
                                  color: isToday
                                      ? AppTheme.primaryWhite
                                      : AppTheme.primaryBlack,
                                  letterSpacing: 1.5,
                                ),
                          ),
                          if (isToday) ...[
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 2),
                              decoration: BoxDecoration(
                                color: AppTheme.primaryWhite.withOpacity(0.2),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                'TODAY',
                                style: Theme.of(context)
                                    .textTheme
                                    .bodySmall
                                    ?.copyWith(
                                      color: AppTheme.primaryWhite,
                                      fontSize: 10,
                                      fontWeight: FontWeight.w600,
                                    ),
                              ),
                            ),
                          ],
                        ],
                      ),
                      const SizedBox(height: 4),
                      Text(
                        DateFormat('MMM d').format(date),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: isToday
                                  ? AppTheme.primaryWhite.withOpacity(0.7)
                                  : AppTheme.mediumGray,
                            ),
                      ),
                    ],
                  ),

                  // Weather
                  if (weather != null)
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 8),
                      decoration: BoxDecoration(
                        color: isToday
                            ? AppTheme.primaryWhite.withOpacity(0.1)
                            : AppTheme.backgroundGray,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Row(
                        children: [
                          Icon(
                            _getWeatherIcon(weather['condition'] ?? 'unknown'),
                            size: 18,
                            color: isToday
                                ? AppTheme.primaryWhite
                                : AppTheme.charcoal,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '${weather['temp_min']?.round() ?? '-'}° / ${weather['temp_max']?.round() ?? '-'}°',
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: isToday
                                          ? AppTheme.primaryWhite
                                          : AppTheme.charcoal,
                                      fontWeight: FontWeight.w500,
                                    ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),

            // Scheduled Outfit or Empty State
            if (scheduledOutfit != null)
              _buildScheduledOutfit(scheduledOutfit, isToday)
            else
              _buildEmptySchedule(isToday),
          ],
        ),
      ),
    );
  }

  Widget _buildScheduledOutfit(Map<String, dynamic> outfit, bool isToday) {
    final outfitItems = outfit['outfit_items'] as List<dynamic>? ?? [];
    final isWorn = outfit['is_worn'] ?? false;

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Outfit Items Preview
          SizedBox(
            height: 60,
            child: ListView.builder(
              scrollDirection: Axis.horizontal,
              itemCount: outfitItems.length,
              itemBuilder: (context, index) {
                final item = outfitItems[index] as Map<String, dynamic>;
                final imagePath =
                    item['image_path']?.toString().replaceAll('\\', '/') ?? '';
                final imageUrl = '${AppConstants.baseUrl}/$imagePath';

                return Container(
                  width: 60,
                  height: 60,
                  margin: const EdgeInsets.only(right: 8),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: isToday
                          ? AppTheme.primaryWhite.withOpacity(0.3)
                          : AppTheme.lightGray,
                    ),
                  ),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(7),
                    child: CachedNetworkImage(
                      imageUrl: imageUrl,
                      fit: BoxFit.cover,
                      placeholder: (context, url) =>
                          Container(color: AppTheme.backgroundGray),
                      errorWidget: (context, url, error) => Container(
                        color: AppTheme.backgroundGray,
                        child: const Icon(Iconsax.image, size: 20),
                      ),
                    ),
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 12),

          // Status indicator
          if (isWorn)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 10),
              decoration: BoxDecoration(
                color: AppTheme.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Iconsax.tick_circle,
                      size: 16, color: AppTheme.success),
                  const SizedBox(width: 6),
                  Text(
                    'WORN',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.success,
                          fontWeight: FontWeight.w600,
                          letterSpacing: 1,
                        ),
                  ),
                ],
              ),
            )
          else
            Row(
              children: [
                Icon(
                  Iconsax.eye,
                  size: 14,
                  color: isToday
                      ? AppTheme.primaryWhite.withOpacity(0.5)
                      : AppTheme.mediumGray,
                ),
                const SizedBox(width: 6),
                Text(
                  'Tap to view details',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: isToday
                            ? AppTheme.primaryWhite.withOpacity(0.5)
                            : AppTheme.mediumGray,
                      ),
                ),
              ],
            ),
        ],
      ),
    );
  }

  Widget _buildEmptySchedule(bool isToday) {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isToday
              ? AppTheme.primaryWhite.withOpacity(0.1)
              : AppTheme.backgroundGray,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Iconsax.magic_star,
              size: 20,
              color: isToday
                  ? AppTheme.primaryWhite.withOpacity(0.7)
                  : AppTheme.mediumGray,
            ),
            const SizedBox(width: 8),
            Text(
              'Tap to generate outfit',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: isToday
                        ? AppTheme.primaryWhite.withOpacity(0.7)
                        : AppTheme.mediumGray,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _generateOutfitForDay(Map<String, dynamic> day) async {
    final date = DateTime.parse(day['date']);
    final dayName = day['day_name'] ?? DateFormat('EEEE').format(date);
    final weather = day['weather_forecast'] as Map<String, dynamic>?;

    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(
                color: AppTheme.primaryBlack, strokeWidth: 2),
            const SizedBox(height: 16),
            Text(
              'Generating outfit for $dayName...',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );

    try {
      final weatherProvider =
          Provider.of<WeatherProvider>(context, listen: false);

      // Generate outfit recommendation
      final recommendation = await _api.post(
        '${AppConstants.recommendationsEndpoint}/generate',
        body: {
          'latitude': weatherProvider.latitude,
          'longitude': weatherProvider.longitude,
          'occasion': 'casual',
        },
      );

      Navigator.pop(context); // Close loading dialog

      if (recommendation['success'] == true &&
          recommendation['outfit'] != null) {
        _showGeneratedOutfit(day, recommendation);
      } else {
        _showErrorSnackBar(recommendation['message'] ??
            'Could not generate outfit. Add more items to your wardrobe.');
      }
    } catch (e) {
      Navigator.pop(context); // Close loading dialog
      _showErrorSnackBar('Failed to generate outfit: $e');
    }
  }

  void _showGeneratedOutfit(
      Map<String, dynamic> day, Map<String, dynamic> recommendation) {
    final date = DateTime.parse(day['date']);
    final dayName = day['day_name'] ?? DateFormat('EEEE').format(date);
    final weather = day['weather_forecast'] as Map<String, dynamic>?;
    final outfit = recommendation['outfit'] as Map<String, dynamic>;
    final colorHarmony =
        recommendation['color_harmony'] as Map<String, dynamic>?;

    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.primaryWhite,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.75,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppTheme.lightGray,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Title
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    'OUTFIT FOR $dayName'.toUpperCase(),
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          letterSpacing: 2,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    DateFormat('MMMM d, yyyy').format(date),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                  ),
                  if (weather != null) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppTheme.backgroundGray,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            _getWeatherIcon(weather['condition'] ?? 'unknown'),
                            size: 16,
                            color: AppTheme.charcoal,
                          ),
                          const SizedBox(width: 6),
                          Text(
                            '${weather['temp_min']?.round() ?? '-'}° / ${weather['temp_max']?.round() ?? '-'}°',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),
            ),

            // Color Harmony Badge
            if (colorHarmony != null)
              Container(
                margin: const EdgeInsets.symmetric(horizontal: 20),
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _getHarmonyColor(colorHarmony['harmony'])
                      .withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: _getHarmonyColor(colorHarmony['harmony'])
                        .withOpacity(0.3),
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: _getHarmonyColor(colorHarmony['harmony']),
                        shape: BoxShape.circle,
                      ),
                      child: const Icon(
                        Iconsax.colorfilter,
                        size: 16,
                        color: AppTheme.primaryWhite,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            colorHarmony['strategy'] ?? 'Color Matched',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  fontWeight: FontWeight.w600,
                                ),
                          ),
                          if (colorHarmony['description'] != null)
                            Text(
                              colorHarmony['description'],
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(
                                    color: AppTheme.mediumGray,
                                  ),
                            ),
                        ],
                      ),
                    ),
                    Text(
                      '${((colorHarmony['score'] ?? 0) * 100).round()}%',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(
                            color: _getHarmonyColor(colorHarmony['harmony']),
                            fontWeight: FontWeight.w600,
                          ),
                    ),
                  ],
                ),
              ),

            const SizedBox(height: 16),

            // Outfit Items
            Expanded(
              child: ListView(
                controller: scrollController,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                children: [
                  ...outfit.entries
                      .map((entry) => _buildOutfitItem(entry.key, entry.value)),
                ],
              ),
            ),

            // Action Buttons
            Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                        _generateOutfitForDay(day); // Regenerate
                      },
                      icon: const Icon(Iconsax.refresh, size: 18),
                      label: const Text('REGENERATE'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () => _saveGeneratedOutfit(date, outfit),
                      icon: const Icon(Iconsax.calendar_add, size: 18),
                      label: const Text('SAVE'),
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

  Widget _buildOutfitItem(String layer, dynamic itemData) {
    final item = itemData as Map<String, dynamic>;
    final imagePath =
        item['image_path']?.toString().replaceAll('\\', '/') ?? '';
    final imageUrl = '${AppConstants.baseUrl}/$imagePath';
    final colorHex = item['primary_color_hex'] as String?;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: AppTheme.lightGray),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          // Image
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              width: 70,
              height: 70,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                width: 70,
                height: 70,
                color: AppTheme.backgroundGray,
              ),
              errorWidget: (context, url, error) => Container(
                width: 70,
                height: 70,
                color: AppTheme.backgroundGray,
                child: const Icon(Iconsax.image),
              ),
            ),
          ),

          const SizedBox(width: 12),

          // Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  layer.toUpperCase(),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.mediumGray,
                        letterSpacing: 1,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  item['clothing_type']?.toString() ?? 'Unknown',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                ),
                if (item['attributes'] != null &&
                    (item['attributes'] as List).isNotEmpty)
                  Padding(
                    padding: const EdgeInsets.only(top: 4),
                    child: Text(
                      (item['attributes'] as List).take(2).join(', '),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: AppTheme.mediumGray,
                          ),
                    ),
                  ),
              ],
            ),
          ),

          // Color indicator
          if (colorHex != null)
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: _hexToColor(colorHex),
                shape: BoxShape.circle,
                border: Border.all(color: AppTheme.lightGray),
              ),
            ),
        ],
      ),
    );
  }

  void _showOutfitDetails(
      Map<String, dynamic> day, Map<String, dynamic> scheduledOutfit) {
    final date = DateTime.parse(day['date']);
    final dayName = day['day_name'] ?? DateFormat('EEEE').format(date);
    final outfitItems = scheduledOutfit['outfit_items'] as List<dynamic>? ?? [];
    final isWorn = scheduledOutfit['is_worn'] ?? false;

    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.primaryWhite,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.4,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppTheme.lightGray,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            // Title
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Text(
                    '$dayName\'S OUTFIT'.toUpperCase(),
                    style: Theme.of(context).textTheme.labelLarge?.copyWith(
                          letterSpacing: 2,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    DateFormat('MMMM d, yyyy').format(date),
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                  ),
                ],
              ),
            ),

            // Outfit Items
            Expanded(
              child: ListView.builder(
                controller: scrollController,
                padding: const EdgeInsets.symmetric(horizontal: 20),
                itemCount: outfitItems.length,
                itemBuilder: (context, index) {
                  final item = outfitItems[index] as Map<String, dynamic>;
                  return _buildScheduledOutfitItem(item);
                },
              ),
            ),

            // Action Buttons
            Padding(
              padding: const EdgeInsets.all(20),
              child: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {
                        Navigator.pop(context);
                        _removeSchedule(scheduledOutfit['id']);
                      },
                      icon: const Icon(Iconsax.trash, size: 18),
                      label: const Text('REMOVE'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.error,
                        side: const BorderSide(color: AppTheme.error),
                      ),
                    ),
                  ),
                  if (!isWorn) ...[
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: () {
                          Navigator.pop(context);
                          _confirmWorn(scheduledOutfit['id']);
                        },
                        icon: const Icon(Iconsax.tick_circle, size: 18),
                        label: const Text('MARK WORN'),
                      ),
                    ),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScheduledOutfitItem(Map<String, dynamic> item) {
    final imagePath =
        item['image_path']?.toString().replaceAll('\\', '/') ?? '';
    final imageUrl = '${AppConstants.baseUrl}/$imagePath';
    final colorHex = item['primary_color_hex'] as String?;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: AppTheme.lightGray),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              width: 70,
              height: 70,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                width: 70,
                height: 70,
                color: AppTheme.backgroundGray,
              ),
              errorWidget: (context, url, error) => Container(
                width: 70,
                height: 70,
                color: AppTheme.backgroundGray,
                child: const Icon(Iconsax.image),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  (item['layer_type'] ?? 'item').toString().toUpperCase(),
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.mediumGray,
                        letterSpacing: 1,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  item['clothing_type']?.toString() ?? 'Unknown',
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                ),
              ],
            ),
          ),
          if (colorHex != null)
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: _hexToColor(colorHex),
                shape: BoxShape.circle,
                border: Border.all(color: AppTheme.lightGray),
              ),
            ),
        ],
      ),
    );
  }

  Future<void> _saveGeneratedOutfit(
      DateTime date, Map<String, dynamic> outfit) async {
    Navigator.pop(context); // Close bottom sheet

    try {
      // Extract item IDs
      final itemIds = <int>[];
      outfit.forEach((layer, item) {
        if (item is Map && item['id'] != null) {
          itemIds.add(item['id']);
        }
      });

      if (itemIds.isEmpty) {
        _showErrorSnackBar('No items to save');
        return;
      }

      // Create outfit
      final outfitResponse = await _api.post(
        '${AppConstants.outfitsEndpoint}/',
        body: {
          'name': 'Outfit for ${DateFormat('MMM d').format(date)}',
          'occasion': 'casual',
          'item_ids': itemIds,
        },
      );

      final outfitId = outfitResponse['id'];

      // Schedule it
      await _api.post(
        '${AppConstants.scheduleEndpoint}/',
        body: {
          'outfit_id': outfitId,
          'scheduled_date': DateFormat('yyyy-MM-dd').format(date),
        },
      );

      _showSuccessSnackBar(
          'Outfit scheduled for ${DateFormat('EEEE').format(date)}!');
      _loadSchedule();
    } catch (e) {
      _showErrorSnackBar('Failed to save outfit: $e');
    }
  }

  Future<void> _confirmWorn(int scheduleId) async {
    try {
      await _api
          .post('${AppConstants.scheduleEndpoint}/$scheduleId/confirm-worn');
      _showSuccessSnackBar('Outfit marked as worn!');
      _loadSchedule();
    } catch (e) {
      _showErrorSnackBar('Failed to update');
    }
  }

  Future<void> _removeSchedule(int scheduleId) async {
    try {
      await _api.delete('${AppConstants.scheduleEndpoint}/$scheduleId');
      _showSuccessSnackBar('Schedule removed');
      _loadSchedule();
    } catch (e) {
      _showErrorSnackBar('Failed to remove schedule');
    }
  }

  Color _getHarmonyColor(String? harmony) {
    switch (harmony) {
      case 'excellent':
        return AppTheme.success;
      case 'good':
        return Colors.green.shade400;
      case 'acceptable':
        return Colors.orange;
      default:
        return AppTheme.mediumGray;
    }
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceAll('#', '');
    if (hex.length == 6) {
      hex = 'FF$hex';
    }
    return Color(int.parse(hex, radix: 16));
  }

  IconData _getWeatherIcon(String condition) {
    switch (condition) {
      case 'clear':
        return Iconsax.sun_1;
      case 'partly_cloudy':
      case 'mainly_clear':
        return Iconsax.cloud_sunny;
      case 'overcast':
        return Iconsax.cloud;
      case 'foggy':
        return Iconsax.cloud_fog;
      case 'light_rain':
      case 'moderate_rain':
      case 'heavy_rain':
      case 'rain_showers':
        return Iconsax.cloud_drizzle;
      case 'light_snow':
      case 'moderate_snow':
      case 'heavy_snow':
        return Iconsax.cloud_snow;
      case 'thunderstorm':
        return Iconsax.cloud_lightning;
      default:
        return Iconsax.cloud;
    }
  }
}
