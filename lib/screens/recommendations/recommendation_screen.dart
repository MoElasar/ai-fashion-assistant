import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:iconsax/iconsax.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/weather_provider.dart';
import '../../providers/recommendation_provider.dart';

class RecommendationScreen extends StatefulWidget {
  const RecommendationScreen({super.key});

  @override
  State<RecommendationScreen> createState() => _RecommendationScreenState();
}

class _RecommendationScreenState extends State<RecommendationScreen> {
  int _selectedOutfitIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadOccasions();
  }

  Future<void> _loadOccasions() async {
    final provider =
        Provider.of<RecommendationProvider>(context, listen: false);
    await provider.fetchOccasions();
  }

  Future<void> _generateOutfit() async {
    final provider =
        Provider.of<RecommendationProvider>(context, listen: false);
    final weatherProvider =
        Provider.of<WeatherProvider>(context, listen: false);

    setState(() {
      _selectedOutfitIndex = 0;
    });

    await provider.generateRecommendation(
      latitude: weatherProvider.latitude,
      longitude: weatherProvider.longitude,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryWhite,
      appBar: AppBar(
        title: const Text('GET OUTFIT'),
        leading: IconButton(
          icon: const Icon(Iconsax.arrow_left),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Occasion Selector
            Text(
              'SELECT OCCASION',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    letterSpacing: 2,
                    color: AppTheme.mediumGray,
                  ),
            ),

            const SizedBox(height: 16),

            _buildOccasionSelector(),

            const SizedBox(height: 24),

            // Generate Button
            SizedBox(
              width: double.infinity,
              child: Consumer<RecommendationProvider>(
                builder: (context, provider, _) {
                  return ElevatedButton.icon(
                    onPressed: provider.isLoading ? null : _generateOutfit,
                    icon: provider.isLoading
                        ? const SizedBox(
                            height: 20,
                            width: 20,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : const Icon(Iconsax.magic_star, size: 20),
                    label: Text(provider.isLoading
                        ? 'GENERATING...'
                        : 'GENERATE OUTFITS'),
                  );
                },
              ),
            ),

            const SizedBox(height: 32),

            // Recommendation Result
            Consumer<RecommendationProvider>(
              builder: (context, provider, _) {
                if (provider.currentRecommendation == null) {
                  return _buildEmptyState();
                }

                return _buildOutfitResults(provider.currentRecommendation!);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOccasionSelector() {
    return Consumer<RecommendationProvider>(
      builder: (context, provider, _) {
        return Wrap(
          spacing: 8,
          runSpacing: 8,
          children: AppConstants.occasions.map((occasion) {
            final isSelected = provider.selectedOccasion == occasion['id'];
            return GestureDetector(
              onTap: () => provider.setOccasion(occasion['id']!),
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(
                  color: isSelected
                      ? AppTheme.primaryBlack
                      : AppTheme.backgroundGray,
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  occasion['name']!,
                  style: TextStyle(
                    color:
                        isSelected ? AppTheme.primaryWhite : AppTheme.charcoal,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
            );
          }).toList(),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Container(
      padding: const EdgeInsets.all(40),
      child: Column(
        children: [
          Icon(
            Iconsax.magic_star,
            size: 64,
            color: AppTheme.lightGray,
          ),
          const SizedBox(height: 16),
          Text(
            'Select an occasion and tap Generate',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.mediumGray,
                ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildOutfitResults(Map<String, dynamic> recommendation) {
    // Get multiple outfits
    final outfits = recommendation['outfits'] as List<dynamic>? ?? [];
    final totalOptions = recommendation['total_options'] ?? 1;

    // Fallback to single outfit format if no outfits array
    if (outfits.isEmpty) {
      final outfit = recommendation['outfit'] as Map<String, dynamic>?;
      if (outfit == null || outfit.isEmpty) {
        return _buildNoOutfitState();
      }
      return _buildSingleOutfitResult(recommendation);
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header with count
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'YOUR OUTFITS',
              style: Theme.of(context).textTheme.labelLarge?.copyWith(
                    letterSpacing: 2,
                    color: AppTheme.mediumGray,
                  ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: AppTheme.backgroundGray,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '$totalOptions OPTIONS',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      letterSpacing: 1,
                    ),
              ),
            ),
          ],
        ),

        const SizedBox(height: 16),

        // Outfit Option Tabs
        _buildOutfitTabs(outfits),

        const SizedBox(height: 20),

        // Selected Outfit Details
        if (_selectedOutfitIndex < outfits.length)
          _buildOutfitCard(
              outfits[_selectedOutfitIndex] as Map<String, dynamic>),

        const SizedBox(height: 24),

        // Regenerate Button
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: _generateOutfit,
            icon: const Icon(Iconsax.refresh, size: 20),
            label: const Text('REGENERATE ALL'),
          ),
        ),
      ],
    );
  }

  Widget _buildOutfitTabs(List<dynamic> outfits) {
    return Row(
      children: List.generate(outfits.length, (index) {
        final outfit = outfits[index] as Map<String, dynamic>;
        final isSelected = _selectedOutfitIndex == index;
        // Use composite score for overall match (not just color harmony)
        final score = outfit['composite_score'] ?? outfit['color_harmony']?['score'] ?? 0.0;
        final isRecommended = outfit['is_recommended'] ?? false;

        return Expanded(
          child: GestureDetector(
            onTap: () {
              setState(() {
                _selectedOutfitIndex = index;
              });
            },
            child: Container(
              margin:
                  EdgeInsets.only(right: index < outfits.length - 1 ? 8 : 0),
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
              decoration: BoxDecoration(
                color: isSelected
                    ? AppTheme.primaryBlack
                    : AppTheme.backgroundGray,
                borderRadius: BorderRadius.circular(12),
                border: isRecommended && !isSelected
                    ? Border.all(color: AppTheme.success, width: 2)
                    : null,
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (isRecommended)
                        Icon(
                          Iconsax.star1,
                          size: 14,
                          color: isSelected ? Colors.amber : AppTheme.success,
                        ),
                      if (isRecommended) const SizedBox(width: 4),
                      Text(
                        'Option ${index + 1}',
                        style: TextStyle(
                          color: isSelected
                              ? AppTheme.primaryWhite
                              : AppTheme.charcoal,
                          fontWeight: FontWeight.w600,
                          fontSize: 13,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${(score * 100).toInt()}% match',
                    style: TextStyle(
                      color: isSelected
                          ? AppTheme.primaryWhite.withOpacity(0.7)
                          : AppTheme.mediumGray,
                      fontSize: 11,
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      }),
    );
  }

  Widget _buildOutfitCard(Map<String, dynamic> outfitData) {
    final outfit = outfitData['outfit'] as Map<String, dynamic>?;
    final colorHarmony = outfitData['color_harmony'] as Map<String, dynamic>?;
    final explanation = outfitData['explanation'] as Map<String, dynamic>?;
    final isComplete = outfitData['complete'] ?? false;
    final missingLayers = List<String>.from(outfitData['missing_layers'] ?? []);

    if (outfit == null || outfit.isEmpty) {
      return _buildNoOutfitState();
    }

    return Container(
      decoration: BoxDecoration(
        color: AppTheme.primaryWhite,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.lightGray),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Harmony Header
          if (colorHarmony != null)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color:
                    _getHarmonyColor(colorHarmony['harmony']).withOpacity(0.1),
                borderRadius: const BorderRadius.only(
                  topLeft: Radius.circular(16),
                  topRight: Radius.circular(16),
                ),
              ),
              child: Row(
                children: [
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getHarmonyColor(colorHarmony['harmony']),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      colorHarmony['harmony']?.toString().toUpperCase() ??
                          'N/A',
                      style: const TextStyle(
                        color: AppTheme.primaryWhite,
                        fontWeight: FontWeight.w600,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      colorHarmony['strategy']
                              ?.toString()
                              .replaceAll('_', ' ')
                              .toUpperCase() ??
                          '',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontWeight: FontWeight.w600,
                            letterSpacing: 1,
                          ),
                    ),
                  ),
                  Text(
                    '${((colorHarmony['score'] ?? 0) * 100).toInt()}%',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: _getHarmonyColor(colorHarmony['harmony']),
                        ),
                  ),
                ],
              ),
            ),

          // Explanation Section
          if (explanation != null) _buildExplanationSection(explanation),

          // Score Breakdown
          _buildScoreBreakdown(outfitData),

          // Outfit Items
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'ITEMS',
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        letterSpacing: 2,
                        color: AppTheme.mediumGray,
                      ),
                ),
                const SizedBox(height: 12),
                ...outfit.entries.map((entry) {
                  final item = entry.value as Map<String, dynamic>;
                  return _buildOutfitItem(entry.key, item);
                }),
              ],
            ),
          ),

          // Missing Layers Warning
          if (!isComplete && missingLayers.isNotEmpty)
            Container(
              margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.accentBeige.withOpacity(0.3),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Iconsax.info_circle,
                      size: 20, color: AppTheme.charcoal),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Missing: ${missingLayers.join(", ")}',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            ),

          // Fashion Rules Applied
          if (colorHarmony != null &&
              colorHarmony['fashion_rules_applied'] != null)
            _buildFashionRules(
                colorHarmony['fashion_rules_applied'] as List<dynamic>),
        ],
      ),
    );
  }

  Widget _buildExplanationSection(Map<String, dynamic> explanation) {
    final summary = explanation['summary'] as String?;
    final colorStrategy =
        explanation['color_strategy'] as Map<String, dynamic>?;
    final harmonyInfo = explanation['harmony'] as Map<String, dynamic>?;
    final colorsUsed = explanation['colors_used'] as List<dynamic>?;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: AppTheme.lightGray.withOpacity(0.5)),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Summary
          if (summary != null)
            Text(
              summary,
              style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),

          // Strategy Explanation
          if (colorStrategy != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.backgroundGray,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Iconsax.lamp_on,
                          size: 16, color: AppTheme.charcoal),
                      const SizedBox(width: 8),
                      Text(
                        'Why it works',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.w600,
                            ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Text(
                    colorStrategy['explanation'] ?? '',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.charcoal,
                          height: 1.4,
                        ),
                  ),
                  if (colorStrategy['tip'] != null &&
                      colorStrategy['tip'].toString().isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Iconsax.magic_star,
                            size: 14, color: AppTheme.mediumGray),
                        const SizedBox(width: 6),
                        Expanded(
                          child: Text(
                            colorStrategy['tip'],
                            style:
                                Theme.of(context).textTheme.bodySmall?.copyWith(
                                      color: AppTheme.mediumGray,
                                      fontStyle: FontStyle.italic,
                                    ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ],

          // Colors Used
          if (colorsUsed != null && colorsUsed.isNotEmpty) ...[
            const SizedBox(height: 16),
            Text(
              'COLORS',
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                    letterSpacing: 2,
                    color: AppTheme.mediumGray,
                  ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: colorsUsed.map((color) {
                final hex = color['hex'] as String?;
                final name = color['name'] as String?;
                return Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: AppTheme.backgroundGray,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (hex != null)
                        Container(
                          width: 16,
                          height: 16,
                          decoration: BoxDecoration(
                            color: _hexToColor(hex),
                            shape: BoxShape.circle,
                            border: Border.all(color: AppTheme.lightGray),
                          ),
                        ),
                      const SizedBox(width: 6),
                      Text(
                        name?.toString().replaceAll('_', ' ') ?? 'Unknown',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ],
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFashionRules(List<dynamic> rules) {
    if (rules.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'STYLE NOTES',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  letterSpacing: 2,
                  color: AppTheme.mediumGray,
                ),
          ),
          const SizedBox(height: 8),
          ...rules.map((rule) {
            final isPositive = rule.toString().startsWith('✓');
            return Padding(
              padding: const EdgeInsets.only(bottom: 4),
              child: Row(
                children: [
                  Icon(
                    isPositive ? Iconsax.tick_circle : Iconsax.warning_2,
                    size: 14,
                    color: isPositive ? AppTheme.success : Colors.orange,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      rule
                          .toString()
                          .replaceFirst('✓ ', '')
                          .replaceFirst('⚠ ', ''),
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildNoOutfitState() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: AppTheme.backgroundGray,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          const Icon(Iconsax.warning_2, size: 48, color: AppTheme.mediumGray),
          const SizedBox(height: 12),
          Text(
            'No outfit could be generated',
            style: Theme.of(context).textTheme.bodyLarge,
          ),
          const SizedBox(height: 4),
          Text(
            'Add more items to your wardrobe',
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ],
      ),
    );
  }

  Widget _buildSingleOutfitResult(Map<String, dynamic> recommendation) {
    final outfit = recommendation['outfit'] as Map<String, dynamic>?;
    final colorHarmony =
        recommendation['color_harmony'] as Map<String, dynamic>?;
    final explanation = recommendation['explanation'] as Map<String, dynamic>?;
    final isComplete = recommendation['complete'] ?? false;
    final missingLayers =
        List<String>.from(recommendation['missing_layers'] ?? []);

    if (outfit == null || outfit.isEmpty) {
      return _buildNoOutfitState();
    }

    // Wrap single outfit in same format as multiple
    final wrappedOutfit = {
      'outfit': outfit,
      'color_harmony': colorHarmony,
      'explanation': explanation,
      'complete': isComplete,
      'missing_layers': missingLayers,
    };

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'YOUR OUTFIT',
          style: Theme.of(context).textTheme.labelLarge?.copyWith(
                letterSpacing: 2,
                color: AppTheme.mediumGray,
              ),
        ),
        const SizedBox(height: 16),
        _buildOutfitCard(wrappedOutfit),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          child: OutlinedButton.icon(
            onPressed: _generateOutfit,
            icon: const Icon(Iconsax.refresh, size: 20),
            label: const Text('REGENERATE'),
          ),
        ),
      ],
    );
  }

  Widget _buildOutfitItem(String layer, Map<String, dynamic> item) {
    final imagePath =
        item['image_path']?.toString().replaceAll('\\', '/') ?? '';
    final imageUrl = '${AppConstants.baseUrl}/$imagePath';

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        border: Border.all(color: AppTheme.lightGray.withOpacity(0.5)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          // Image
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: CachedNetworkImage(
              imageUrl: imageUrl,
              width: 56,
              height: 56,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                color: AppTheme.backgroundGray,
                child: const Center(
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
              ),
              errorWidget: (context, url, error) => Container(
                color: AppTheme.backgroundGray,
                child: const Icon(Iconsax.image, color: AppTheme.mediumGray),
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
                        fontSize: 10,
                      ),
                ),
                const SizedBox(height: 2),
                Text(
                  item['clothing_type']?.toString() ?? 'Unknown',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                ),
              ],
            ),
          ),

          // Color indicator
          if (item['primary_color_hex'] != null)
            Container(
              width: 22,
              height: 22,
              decoration: BoxDecoration(
                color: _hexToColor(item['primary_color_hex']),
                shape: BoxShape.circle,
                border: Border.all(color: AppTheme.lightGray),
              ),
            ),
        ],
      ),
    );
  }

  Color _getHarmonyColor(String? harmony) {
    switch (harmony) {
      case 'excellent':
        return AppTheme.success;
      case 'good':
        return Colors.green.shade400;
      case 'acceptable':
        return Colors.orange;
      case 'poor':
        return Colors.red.shade400;
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

  Widget _buildScoreBreakdown(Map<String, dynamic> outfitData) {
    final scoreBreakdown = outfitData['score_breakdown'] as Map<String, dynamic>?;
    final compositeScore = outfitData['composite_score'] ?? 0.0;

    if (scoreBreakdown == null) return const SizedBox.shrink();

    final colorScore = scoreBreakdown['color_harmony'] ?? 0.0;
    final weatherScore = scoreBreakdown['weather_suitability'] ?? 0.0;
    final occasionScore = scoreBreakdown['occasion_suitability'] ?? 0.0;

    return Container(
      margin: const EdgeInsets.fromLTRB(16, 0, 16, 16),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.backgroundGray,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'SCORE BREAKDOWN',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  letterSpacing: 2,
                  color: AppTheme.mediumGray,
                ),
          ),
          const SizedBox(height: 12),
          _buildScoreRow('Color Harmony', colorScore, 0.60),
          const SizedBox(height: 8),
          _buildScoreRow('Weather', weatherScore, 0.20),
          const SizedBox(height: 8),
          _buildScoreRow('Occasion', occasionScore, 0.20),
          const Divider(height: 20),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Total Score',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              Text(
                '${(compositeScore * 100).toInt()}%',
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: AppTheme.success,
                    ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildScoreRow(String label, double score, double weight) {
    final percentage = (score * 100).toInt();
    final weightPercentage = (weight * 100).toInt();

    return Row(
      children: [
        Expanded(
          flex: 2,
          child: Text(
            label,
            style: Theme.of(context).textTheme.bodySmall,
          ),
        ),
        Expanded(
          flex: 3,
          child: Stack(
            children: [
              Container(
                height: 8,
                decoration: BoxDecoration(
                  color: AppTheme.lightGray,
                  borderRadius: BorderRadius.circular(4),
                ),
              ),
              FractionallySizedBox(
                widthFactor: score,
                child: Container(
                  height: 8,
                  decoration: BoxDecoration(
                    color: _getScoreColor(score),
                    borderRadius: BorderRadius.circular(4),
                  ),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 75,
          child: Text(
            '$percentage% × $weightPercentage%',
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppTheme.mediumGray,
                  fontSize: 11,
                ),
            textAlign: TextAlign.right,
          ),
        ),
      ],
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 0.85) return AppTheme.success;
    if (score >= 0.70) return Colors.green.shade400;
    if (score >= 0.55) return Colors.orange;
    return Colors.red.shade400;
  }
}
