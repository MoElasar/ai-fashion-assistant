import 'package:flutter/material.dart';
import 'package:iconsax/iconsax.dart';
import '../../config/theme.dart';
import 'home_tab.dart';
import '../wardrobe/wardrobe_screen.dart';
import '../schedule/schedule_screen.dart';
import '../analytics/analytics_screen.dart';
import '../chat/chat_screen.dart';

class MainScreen extends StatefulWidget {
  const MainScreen({super.key});

  @override
  State<MainScreen> createState() => MainScreenState();
}

class MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  // Method to switch tabs from child widgets
  void switchToTab(int index) {
    setState(() {
      _currentIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    final List<Widget> screens = [
      HomeTab(onNavigateToWardrobe: () => switchToTab(1)),
      const WardrobeScreen(),
      const ScheduleScreen(),
      const AnalyticsScreen(),
      const ChatScreen(),
    ];

    return Scaffold(
      body: IndexedStack(
        index: _currentIndex,
        children: screens,
      ),
      bottomNavigationBar: Container(
        decoration: const BoxDecoration(
          border: Border(
            top: BorderSide(color: AppTheme.lightGray, width: 1),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) {
            setState(() {
              _currentIndex = index;
            });
          },
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Iconsax.home),
              activeIcon: Icon(Iconsax.home_15),
              label: 'Home',
            ),
            BottomNavigationBarItem(
              icon: Icon(Iconsax.bag_2),
              activeIcon: Icon(Iconsax.bag_21),
              label: 'Wardrobe',
            ),
            BottomNavigationBarItem(
              icon: Icon(Iconsax.calendar),
              activeIcon: Icon(Iconsax.calendar_15),
              label: 'Schedule',
            ),
            BottomNavigationBarItem(
              icon: Icon(Iconsax.chart),
              activeIcon: Icon(Iconsax.chart_15),
              label: 'Analytics',
            ),
            BottomNavigationBarItem(
              icon: Icon(Iconsax.message),
              activeIcon: Icon(Iconsax.message5),
              label: 'Chat',
            ),
          ],
        ),
      ),
    );
  }
}
