import 'package:flutter/material.dart';
import '../config/constants.dart';
import '../services/api_service.dart';

class ChatMessage {
  final String role;
  final String content;
  final DateTime timestamp;

  ChatMessage({
    required this.role,
    required this.content,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  Map<String, dynamic> toJson() => {
        'role': role,
        'content': content,
      };
}

class ChatProvider with ChangeNotifier {
  final ApiService _api = ApiService();

  List<ChatMessage> _messages = [];
  bool _isLoading = false;
  String? _error;

  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;
  String? get error => _error;

  // Send message
  Future<void> sendMessage({
    required String message,
    double? latitude,
    double? longitude,
  }) async {
    // Add user message
    _messages.add(ChatMessage(role: 'user', content: message));
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final body = <String, dynamic>{
        'message': message,
      };

      if (latitude != null && longitude != null) {
        body['latitude'] = latitude;
        body['longitude'] = longitude;
      }

      // Include last 6 messages for context
      if (_messages.length > 1) {
        body['conversation_history'] = _messages
            .take(_messages.length - 1)
            .take(6)
            .map((m) => m.toJson())
            .toList();
      }

      final response = await _api.post(
        '${AppConstants.chatEndpoint}/message',
        body: body,
      );

      if (response['success'] == true) {
        _messages.add(ChatMessage(
          role: 'assistant',
          content: response['response'],
        ));
      } else {
        _error = response['error'] ?? 'Failed to get response';
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Quick suggestion
  Future<void> getQuickSuggestion({
    required String type,
    double? latitude,
    double? longitude,
  }) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final body = <String, dynamic>{
        'suggestion_type': type,
      };

      if (latitude != null && longitude != null) {
        body['latitude'] = latitude;
        body['longitude'] = longitude;
      }

      final response = await _api.post(
        '${AppConstants.chatEndpoint}/quick-suggestion',
        body: body,
      );

      if (response['success'] == true) {
        _messages.add(ChatMessage(
          role: 'assistant',
          content: response['response'],
        ));
      } else {
        _error = response['error'] ?? 'Failed to get suggestion';
      }

      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
    }
  }

  // Clear messages
  void clearMessages() {
    _messages = [];
    notifyListeners();
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
