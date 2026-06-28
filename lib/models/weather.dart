class Weather {
  final double temperature;
  final double? humidity;
  final double? windSpeed;
  final String condition;
  final WeatherSuggestions suggestions;
  final String fetchedAt;

  Weather({
    required this.temperature,
    this.humidity,
    this.windSpeed,
    required this.condition,
    required this.suggestions,
    required this.fetchedAt,
  });

  factory Weather.fromJson(Map<String, dynamic> json) {
    return Weather(
      temperature: json['temperature']?.toDouble() ?? 0.0,
      humidity: json['humidity']?.toDouble(),
      windSpeed: json['wind_speed']?.toDouble(),
      condition: json['condition'] ?? 'unknown',
      suggestions: WeatherSuggestions.fromJson(json['suggestions'] ?? {}),
      fetchedAt: json['fetched_at'] ?? '',
    );
  }

  String get conditionDisplay {
    return condition.replaceAll('_', ' ').toUpperCase();
  }

  String get temperatureDisplay {
    return '${temperature.round()}°C';
  }
}

class WeatherSuggestions {
  final bool needsOuterwear;
  final bool needsWarmOuterwear;
  final bool needsRainProtection;
  final bool lightClothing;
  final bool warmClothing;
  final List<String> recommendedLayers;
  final String? outerwearType;

  WeatherSuggestions({
    required this.needsOuterwear,
    required this.needsWarmOuterwear,
    required this.needsRainProtection,
    required this.lightClothing,
    required this.warmClothing,
    required this.recommendedLayers,
    this.outerwearType,
  });

  factory WeatherSuggestions.fromJson(Map<String, dynamic> json) {
    return WeatherSuggestions(
      needsOuterwear: json['needs_outerwear'] ?? false,
      needsWarmOuterwear: json['needs_warm_outerwear'] ?? false,
      needsRainProtection: json['needs_rain_protection'] ?? false,
      lightClothing: json['light_clothing'] ?? false,
      warmClothing: json['warm_clothing'] ?? false,
      recommendedLayers: List<String>.from(json['recommended_layers'] ?? []),
      outerwearType: json['outerwear_type'],
    );
  }
}

class DayForecast {
  final String date;
  final double tempMax;
  final double tempMin;
  final double tempAvg;
  final String condition;
  final int? precipitationProbability;
  final WeatherSuggestions suggestions;

  DayForecast({
    required this.date,
    required this.tempMax,
    required this.tempMin,
    required this.tempAvg,
    required this.condition,
    this.precipitationProbability,
    required this.suggestions,
  });

  factory DayForecast.fromJson(Map<String, dynamic> json) {
    return DayForecast(
      date: json['date'],
      tempMax: json['temp_max']?.toDouble() ?? 0.0,
      tempMin: json['temp_min']?.toDouble() ?? 0.0,
      tempAvg: json['temp_avg']?.toDouble() ?? 0.0,
      condition: json['condition'] ?? 'unknown',
      precipitationProbability: json['precipitation_probability'],
      suggestions: WeatherSuggestions.fromJson(json['suggestions'] ?? {}),
    );
  }

  String get temperatureRange {
    return '${tempMin.round()}° / ${tempMax.round()}°';
  }
}
