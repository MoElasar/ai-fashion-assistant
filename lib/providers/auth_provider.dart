import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../config/constants.dart';
import '../models/user.dart';
import '../services/api_service.dart';

class AuthProvider with ChangeNotifier {
  final ApiService _api = ApiService();

  User? _user;
  bool _isLoading = false;
  bool _isAuthenticated = false;
  String? _error;

  User? get user => _user;
  bool get isLoading => _isLoading;
  bool get isAuthenticated => _isAuthenticated;
  String? get error => _error;

  // Check if user is logged in
  Future<bool> checkAuth() async {
    final token = await _api.getToken();
    if (token == null) {
      _isAuthenticated = false;
      return false;
    }

    try {
      final response = await _api.get('${AppConstants.authEndpoint}/me');
      _user = User.fromJson(response);
      _isAuthenticated = true;
      notifyListeners();
      return true;
    } catch (e) {
      _isAuthenticated = false;
      await _api.clearToken();
      return false;
    }
  }

  // Register
  Future<bool> register(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.post(
        '${AppConstants.authEndpoint}/register',
        body: {
          'email': email,
          'password': password,
        },
        withAuth: false,
      );

      // Save token
      await _api.saveToken(response['access_token']);

      // Save user
      _user = User.fromJson(response['user']);
      _isAuthenticated = true;

      // Cache user data
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.userKey, jsonEncode(response['user']));

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Login
  Future<bool> login(String email, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await _api.post(
        '${AppConstants.authEndpoint}/login',
        body: {
          'email': email,
          'password': password,
        },
        withAuth: false,
      );

      // Save token
      await _api.saveToken(response['access_token']);

      // Save user
      _user = User.fromJson(response['user']);
      _isAuthenticated = true;

      // Cache user data
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(AppConstants.userKey, jsonEncode(response['user']));

      _isLoading = false;
      notifyListeners();
      return true;
    } catch (e) {
      _error = e.toString().replaceAll('Exception: ', '');
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }

  // Logout
  Future<void> logout() async {
    await _api.clearToken();
    _user = null;
    _isAuthenticated = false;
    notifyListeners();
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }
}
