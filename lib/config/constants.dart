import 'package:flutter/foundation.dart' show kIsWeb;
import 'dart:io' show Platform;

class AppConstants {
  // API Configuration - Auto-detect platform
  static String get baseUrl {
    if (kIsWeb) {
      // Chrome / Web
      return 'http://localhost:8000';
    }
    try {
      if (Platform.isAndroid) {
        // Android Emulator
        return 'http://10.0.2.2:8000';
      } else if (Platform.isIOS) {
        // iOS Simulator
        return 'http://localhost:8000';
      }
    } catch (e) {
      // Fallback for web (Platform not available)
    }
    return 'http://localhost:8000';
  }

  static const String apiPrefix = '/api';

  // Endpoints
  static String get authEndpoint => '$apiPrefix/auth';
  static String get wardrobeEndpoint => '$apiPrefix/wardrobe';
  static String get weatherEndpoint => '$apiPrefix/weather';
  static String get recommendationsEndpoint => '$apiPrefix/recommendations';
  static String get outfitsEndpoint => '$apiPrefix/outfits';
  static String get scheduleEndpoint => '$apiPrefix/schedule';
  static String get analyticsEndpoint => '$apiPrefix/analytics';
  static String get chatEndpoint => '$apiPrefix/chat';

  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userKey = 'user_data';

  // Default Location (Istanbul)
  static const double defaultLatitude = 41.0082;
  static const double defaultLongitude = 28.9784;

  // Occasions
  static const List<Map<String, String>> occasions = [
    {'id': 'casual', 'name': 'Casual', 'icon': 'shirt'},
    {'id': 'formal', 'name': 'Formal', 'icon': 'briefcase'},
    {'id': 'sport', 'name': 'Sport', 'icon': 'activity'},
    {'id': 'party', 'name': 'Party', 'icon': 'music'},
    {'id': 'date', 'name': 'Date', 'icon': 'heart'},
    {'id': 'home', 'name': 'Home', 'icon': 'home'},
  ];

  // Layer Types
  static const List<String> layerTypes = [
    'top',
    'bottom',
    'outerwear',
    'footwear',
    'socks',
  ];
}
