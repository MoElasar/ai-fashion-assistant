import 'package:flutter/material.dart';
import '../config/constants.dart';
import '../models/weather.dart';
import '../services/api_service.dart';

class WeatherProvider with ChangeNotifier {
  final ApiService _api = ApiService();

  Weather? _currentWeather;
  List<DayForecast> _forecast = [];
  bool _isLoading = false;
  String? _error;

  double _latitude = AppConstants.defaultLatitude;
  double _longitude = AppConstants.defaultLongitude;

  Weather? get currentWeather => _currentWeather;
  List<DayForecast> get forecast => _forecast;
  bool get isLoading => _isLoading;
  String? get error => _error;
  double get latitude => _latitude;
  double get longitude => _longitude;

  // Set location
  void setLocation(double lat, double lon) {
    _latitude = lat;
    _longitude = lon;
    notifyListeners();
  }

  // Fetch current weather
  Future<void> fetchCurrentWeather() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.get(
        '${AppConstants.weatherEndpoint}/current',
        queryParams: {
          'latitude': _latitude.toString(),
          'longitude': _longitude.toString(),
        },
      );

      _currentWeather = Weather.fromJson(response);
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Fetch forecast
  Future<void> fetchForecast() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.get(
        '${AppConstants.weatherEndpoint}/forecast',
        queryParams: {
          'latitude': _latitude.toString(),
          'longitude': _longitude.toString(),
          'days': '7',
        },
      );

      final List<dynamic> forecastJson = response['forecast'] ?? [];
      _forecast =
          forecastJson.map((json) => DayForecast.fromJson(json)).toList();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Fetch all weather data
  Future<void> fetchAllWeatherData() async {
    await Future.wait([
      fetchCurrentWeather(),
      fetchForecast(),
    ]);
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
