import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../config/constants.dart';
import '../models/clothing_item.dart';
import '../services/api_service.dart';

class WardrobeProvider with ChangeNotifier {
  final ApiService _api = ApiService();

  List<ClothingItem> _items = [];
  bool _isLoading = false;
  String? _error;
  String? _selectedLayer;

  List<ClothingItem> get items => _selectedLayer == null
      ? _items
      : _items.where((item) => item.layerType == _selectedLayer).toList();

  List<ClothingItem> get allItems => _items;
  bool get isLoading => _isLoading;
  String? get error => _error;
  String? get selectedLayer => _selectedLayer;

  // Get items by layer
  List<ClothingItem> getItemsByLayer(String layer) {
    return _items.where((item) => item.layerType == layer).toList();
  }

  // Set layer filter
  void setLayerFilter(String? layer) {
    _selectedLayer = layer;
    notifyListeners();
  }

  // Fetch all items
  Future<void> fetchItems() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.get('${AppConstants.wardrobeEndpoint}/items');
      final List<dynamic> itemsJson = response['items'] ?? [];
      _items = itemsJson.map((json) => ClothingItem.fromJson(json)).toList();
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Upload new item (cross-platform: works on web and mobile)
  Future<ClothingItem?> uploadItem(
      Uint8List imageBytes, String fileName) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.uploadFileBytes(
        '${AppConstants.wardrobeEndpoint}/upload',
        imageBytes,
        fileName,
      );

      final newItem = ClothingItem.fromJson(response['clothing_item']);
      _items.insert(0, newItem);
      _isLoading = false;
      notifyListeners();
      return newItem;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return null;
    }
  }

  // Delete item
  Future<bool> deleteItem(int itemId) async {
    try {
      await _api.delete('${AppConstants.wardrobeEndpoint}/items/$itemId');
      _items.removeWhere((item) => item.id == itemId);
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  // Update item
  Future<bool> updateItem(int itemId, Map<String, dynamic> data) async {
    try {
      final response = await _api.put(
        '${AppConstants.wardrobeEndpoint}/items/$itemId',
        body: data,
      );

      final updatedItem = ClothingItem.fromJson(response);
      final index = _items.indexWhere((item) => item.id == itemId);
      if (index != -1) {
        _items[index] = updatedItem;
        notifyListeners();
      }
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      notifyListeners();
      return false;
    }
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
