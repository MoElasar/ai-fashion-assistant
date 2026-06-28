import 'package:flutter/material.dart';
import '../config/constants.dart';
import '../services/api_service.dart';

class RecommendationProvider with ChangeNotifier {
  final ApiService _api = ApiService();

  Map<String, dynamic>? _currentRecommendation;
  List<Map<String, dynamic>> _occasions = [];
  bool _isLoading = false;
  String? _error;
  String _selectedOccasion = 'casual';

  Map<String, dynamic>? get currentRecommendation => _currentRecommendation;
  List<Map<String, dynamic>> get occasions => _occasions;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String get selectedOccasion => _selectedOccasion;

  // Set occasion
  void setOccasion(String occasion) {
    _selectedOccasion = occasion;
    notifyListeners();
  }

  // Fetch occasions
  Future<void> fetchOccasions() async {
    try {
      final response =
          await _api.get('${AppConstants.recommendationsEndpoint}/occasions');
      final List<dynamic> occasionsJson = response['occasions'] ?? [];
      _occasions =
          occasionsJson.map((o) => Map<String, dynamic>.from(o)).toList();
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
    }
  }

  // Generate recommendation
  Future<void> generateRecommendation({
    required double latitude,
    required double longitude,
    String? occasion,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.post(
        '${AppConstants.recommendationsEndpoint}/generate',
        body: {
          'latitude': latitude,
          'longitude': longitude,
          'occasion': occasion ?? _selectedOccasion,
        },
      );

      _currentRecommendation = response;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Generate for specific date
  Future<void> generateForDate({
    required double latitude,
    required double longitude,
    required String date,
    String? occasion,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.post(
        '${AppConstants.recommendationsEndpoint}/generate-for-date',
        body: {
          'latitude': latitude,
          'longitude': longitude,
          'occasion': occasion ?? _selectedOccasion,
        },
      );

      _currentRecommendation = response;
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Clear recommendation
  void clearRecommendation() {
    _currentRecommendation = null;
    notifyListeners();
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
