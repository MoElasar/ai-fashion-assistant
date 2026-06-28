import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:iconsax/iconsax.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/auth_provider.dart';
import '../../providers/weather_provider.dart';
import '../../providers/wardrobe_provider.dart';
import '../recommendations/recommendation_screen.dart';

class HomeTab extends StatefulWidget {
  final VoidCallback? onNavigateToWardrobe;

  const HomeTab({super.key, this.onNavigateToWardrobe});

  @override
  State<HomeTab> createState() => _HomeTabState();
}

class _HomeTabState extends State<HomeTab> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final weatherProvider =
        Provider.of<WeatherProvider>(context, listen: false);
    final wardrobeProvider =
        Provider.of<WardrobeProvider>(context, listen: false);

    await Future.wait([
      weatherProvider.fetchCurrentWeather(),
      wardrobeProvider.fetchItems(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryWhite,
      appBar: AppBar(
        title: const Text('AI FASHION'),
        actions: [
          IconButton(
            icon: const Icon(Iconsax.logout),
            onPressed: () {
              Provider.of<AuthProvider>(context, listen: false).logout();
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        color: AppTheme.primaryBlack,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Greeting
              Consumer<AuthProvider>(
                builder: (context, auth, _) {
                  return Text(
                    'Hello!',
                    style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                          fontWeight: FontWeight.w300,
                        ),
                  );
                },
              ),

              const SizedBox(height: 4),

              Text(
                'What will you wear today?',
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: AppTheme.mediumGray,
                    ),
              ),

              const SizedBox(height: 24),

              // Weather Card
              _buildWeatherCard(),

              const SizedBox(height: 24),

              // Quick Actions
              Text(
                'QUICK ACTIONS',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      letterSpacing: 2,
                      color: AppTheme.mediumGray,
                    ),
              ),

              const SizedBox(height: 16),

              _buildQuickActions(),

              const SizedBox(height: 24),

              // Wardrobe Summary
              Text(
                'YOUR WARDROBE',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      letterSpacing: 2,
                      color: AppTheme.mediumGray,
                    ),
              ),

              const SizedBox(height: 16),

              _buildWardrobeSummary(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWeatherCard() {
    return Consumer<WeatherProvider>(
      builder: (context, weather, _) {
        if (weather.isLoading) {
          return Container(
            height: 140,
            decoration: BoxDecoration(
              color: AppTheme.backgroundGray,
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Center(
              child: CircularProgressIndicator(
                color: AppTheme.primaryBlack,
                strokeWidth: 2,
              ),
            ),
          );
        }

        final current = weather.currentWeather;
        if (current == null) {
          return Container(
            height: 140,
            decoration: BoxDecoration(
              color: AppTheme.backgroundGray,
              borderRadius: BorderRadius.circular(16),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Iconsax.cloud_cross,
                      size: 32, color: AppTheme.mediumGray),
                  const SizedBox(height: 8),
                  Text(
                    'Unable to load weather',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          );
        }

        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                AppTheme.charcoal,
                AppTheme.charcoal.withOpacity(0.8),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        current.temperatureDisplay,
                        style:
                            Theme.of(context).textTheme.displayLarge?.copyWith(
                                  color: AppTheme.primaryWhite,
                                  fontWeight: FontWeight.w300,
                                ),
                      ),
                      Text(
                        current.conditionDisplay,
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppTheme.primaryWhite.withOpacity(0.7),
                            ),
                      ),
                    ],
                  ),
                  Icon(
                    _getWeatherIcon(current.condition),
                    size: 48,
                    color: AppTheme.primaryWhite,
                  ),
                ],
              ),
              const SizedBox(height: 16),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: AppTheme.primaryWhite.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  current.suggestions.needsOuterwear
                      ? '🧥 Bring a ${current.suggestions.outerwearType ?? "jacket"}'
                      : '☀️ Light clothing recommended',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: AppTheme.primaryWhite,
                      ),
                ),
              ),
            ],
          ),
        );
      },
    );
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

  Widget _buildQuickActions() {
    return Row(
      children: [
        Expanded(
          child: _buildActionCard(
            icon: Iconsax.magic_star,
            label: 'Get Outfit',
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => const RecommendationScreen(),
                ),
              );
            },
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildActionCard(
            icon: Iconsax.add_circle,
            label: 'Add Item',
            onTap: () {
              // Navigate to wardrobe tab
              if (widget.onNavigateToWardrobe != null) {
                widget.onNavigateToWardrobe!();
              }
            },
          ),
        ),
      ],
    );
  }

  Widget _buildActionCard({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: AppTheme.backgroundGray,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(icon, size: 28, color: AppTheme.charcoal),
            const SizedBox(height: 8),
            Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWardrobeSummary() {
    return Consumer<WardrobeProvider>(
      builder: (context, wardrobe, _) {
        if (wardrobe.isLoading) {
          return const Center(
            child: CircularProgressIndicator(
              color: AppTheme.primaryBlack,
              strokeWidth: 2,
            ),
          );
        }

        final items = wardrobe.allItems;

        // Count by layer
        final layerCounts = <String, int>{};
        for (final item in items) {
          layerCounts[item.layerType] = (layerCounts[item.layerType] ?? 0) + 1;
        }

        if (items.isEmpty) {
          return GestureDetector(
            onTap: () {
              if (widget.onNavigateToWardrobe != null) {
                widget.onNavigateToWardrobe!();
              }
            },
            child: Container(
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: AppTheme.backgroundGray,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  const Icon(Iconsax.bag_2,
                      size: 48, color: AppTheme.mediumGray),
                  const SizedBox(height: 12),
                  Text(
                    'Your wardrobe is empty',
                    style: Theme.of(context).textTheme.bodyLarge,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Tap to add items',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                  ),
                ],
              ),
            ),
          );
        }

        return Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            border: Border.all(color: AppTheme.lightGray),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    '${items.length}',
                    style: Theme.of(context).textTheme.displayMedium?.copyWith(
                          fontWeight: FontWeight.w300,
                        ),
                  ),
                  Text(
                    'Total Items',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                  ),
                ],
              ),
              const Divider(height: 24),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: AppConstants.layerTypes.map((layer) {
                  final count = layerCounts[layer] ?? 0;
                  return Column(
                    children: [
                      Text(
                        count.toString(),
                        style: Theme.of(context).textTheme.titleLarge,
                      ),
                      const SizedBox(height: 4),
                      Text(
                        layer.toUpperCase(),
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontSize: 10,
                              letterSpacing: 1,
                            ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ],
          ),
        );
      },
    );
  }
}
