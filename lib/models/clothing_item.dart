class ClothingItem {
  final int id;
  final int userId;
  final String imagePath;
  final String clothingType;
  final String layerType;
  final String? primaryColorHex;
  final String? secondaryColorHex;
  final List<String> attributes;
  final double? confidenceScore;
  final int timesWorn;
  final DateTime? lastWornDate;
  final DateTime createdAt;

  ClothingItem({
    required this.id,
    required this.userId,
    required this.imagePath,
    required this.clothingType,
    required this.layerType,
    this.primaryColorHex,
    this.secondaryColorHex,
    this.attributes = const [],
    this.confidenceScore,
    this.timesWorn = 0,
    this.lastWornDate,
    required this.createdAt,
  });

  factory ClothingItem.fromJson(Map<String, dynamic> json) {
    List<String> parseAttributes(dynamic attr) {
      if (attr == null) return [];
      if (attr is List) return attr.map((e) => e.toString()).toList();
      if (attr is String) {
        try {
          // Try to parse JSON string
          if (attr.startsWith('[')) {
            return List<String>.from(
              (attr
                      .replaceAll('[', '')
                      .replaceAll(']', '')
                      .replaceAll('"', '')
                      .split(','))
                  .map((e) => e.trim())
                  .where((e) => e.isNotEmpty),
            );
          }
        } catch (_) {}
      }
      return [];
    }

    return ClothingItem(
      id: json['id'],
      userId: json['user_id'],
      imagePath: json['image_path'],
      clothingType: json['clothing_type'] ?? 'unknown',
      layerType: json['layer_type'] ?? 'top',
      primaryColorHex: json['primary_color_hex'],
      secondaryColorHex: json['secondary_color_hex'],
      attributes: parseAttributes(json['attributes']),
      confidenceScore: json['confidence_score']?.toDouble(),
      timesWorn: json['times_worn'] ?? 0,
      lastWornDate: json['last_worn_date'] != null
          ? DateTime.parse(json['last_worn_date'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  String get fullImageUrl {
    // Handle backslashes in Windows paths
    final cleanPath = imagePath.replaceAll('\\', '/');
    return cleanPath;
  }
}
