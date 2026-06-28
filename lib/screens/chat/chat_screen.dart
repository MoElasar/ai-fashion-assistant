import 'package:flutter/material.dart';
import 'package:flutter_markdown/flutter_markdown.dart';
import 'package:provider/provider.dart';
import 'package:iconsax/iconsax.dart';
import '../../config/theme.dart';
import '../../providers/chat_provider.dart';
import '../../providers/weather_provider.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  Future<void> _sendMessage() async {
    final message = _messageController.text.trim();
    if (message.isEmpty) return;

    _messageController.clear();

    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    final weatherProvider =
        Provider.of<WeatherProvider>(context, listen: false);

    await chatProvider.sendMessage(
      message: message,
      latitude: weatherProvider.latitude,
      longitude: weatherProvider.longitude,
    );

    _scrollToBottom();
  }

  Future<void> _sendQuickSuggestion(String type) async {
    final chatProvider = Provider.of<ChatProvider>(context, listen: false);
    final weatherProvider =
        Provider.of<WeatherProvider>(context, listen: false);

    await chatProvider.getQuickSuggestion(
      type: type,
      latitude: weatherProvider.latitude,
      longitude: weatherProvider.longitude,
    );

    _scrollToBottom();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryWhite,
      appBar: AppBar(
        title: const Text('STYLE ASSISTANT'),
        actions: [
          IconButton(
            icon: const Icon(Iconsax.trash),
            onPressed: () {
              Provider.of<ChatProvider>(context, listen: false).clearMessages();
            },
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, chatProvider, _) {
                if (chatProvider.messages.isEmpty) {
                  return _buildWelcomeState();
                }

                return ListView.builder(
                  controller: _scrollController,
                  padding: const EdgeInsets.all(16),
                  itemCount: chatProvider.messages.length +
                      (chatProvider.isLoading ? 1 : 0),
                  itemBuilder: (context, index) {
                    if (index == chatProvider.messages.length &&
                        chatProvider.isLoading) {
                      return _buildTypingIndicator();
                    }
                    return _buildMessageBubble(chatProvider.messages[index]);
                  },
                );
              },
            ),
          ),
          _buildInputField(),
        ],
      ),
    );
  }

  Widget _buildWelcomeState() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const SizedBox(height: 40),
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppTheme.charcoal, AppTheme.charcoal.withOpacity(0.7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: AppTheme.charcoal.withOpacity(0.3),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: const Icon(
              Iconsax.magic_star,
              size: 48,
              color: AppTheme.primaryWhite,
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'Hey there! 👋',
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
          ),
          const SizedBox(height: 8),
          Text(
            "I'm Style, your personal fashion assistant!\nAsk me anything about outfits, colors,\nor what to wear.",
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.mediumGray,
                  height: 1.5,
                ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),

          // Quick action buttons
          Text(
            'QUICK SUGGESTIONS',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  letterSpacing: 2,
                  color: AppTheme.mediumGray,
                ),
          ),
          const SizedBox(height: 16),

          _buildQuickActionRow([
            _QuickAction(
                icon: Iconsax.sun_1, label: "Today's Look", type: 'today'),
            _QuickAction(icon: Iconsax.coffee, label: 'Casual', type: 'casual'),
          ]),
          const SizedBox(height: 8),
          _buildQuickActionRow([
            _QuickAction(
                icon: Iconsax.briefcase, label: 'Formal', type: 'formal'),
            _QuickAction(
                icon: Iconsax.heart, label: 'Date Night', type: 'date'),
          ]),
          const SizedBox(height: 8),
          _buildQuickActionRow([
            _QuickAction(icon: Iconsax.weight, label: 'Workout', type: 'sport'),
            _QuickAction(icon: Iconsax.music, label: 'Party', type: 'party'),
          ]),

          const SizedBox(height: 32),

          Text(
            'OR ASK ME ANYTHING',
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  letterSpacing: 2,
                  color: AppTheme.mediumGray,
                ),
          ),
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            alignment: WrapAlignment.center,
            children: [
              _buildSuggestionChip('What colors go with navy blue?'),
              _buildSuggestionChip('Help me style my jeans'),
              _buildSuggestionChip('What should I add to my wardrobe?'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionRow(List<_QuickAction> actions) {
    return Row(
      children: actions.map((action) {
        return Expanded(
          child: Padding(
            padding: EdgeInsets.only(
              left: actions.indexOf(action) == 0 ? 0 : 4,
              right: actions.indexOf(action) == actions.length - 1 ? 0 : 4,
            ),
            child: _buildQuickActionButton(action),
          ),
        );
      }).toList(),
    );
  }

  Widget _buildQuickActionButton(_QuickAction action) {
    return GestureDetector(
      onTap: () => _sendQuickSuggestion(action.type),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 16),
        decoration: BoxDecoration(
          color: AppTheme.backgroundGray,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Icon(action.icon, color: AppTheme.charcoal, size: 24),
            const SizedBox(height: 8),
            Text(
              action.label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    fontWeight: FontWeight.w500,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionChip(String text) {
    return GestureDetector(
      onTap: () {
        _messageController.text = text;
        _sendMessage();
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          border: Border.all(color: AppTheme.lightGray),
          borderRadius: BorderRadius.circular(20),
        ),
        child: Text(
          text,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ),
    );
  }

  Widget _buildMessageBubble(ChatMessage message) {
    final isUser = message.role == 'user';

    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser) ...[
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    AppTheme.charcoal,
                    AppTheme.charcoal.withOpacity(0.7)
                  ],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Iconsax.magic_star,
                size: 18,
                color: AppTheme.primaryWhite,
              ),
            ),
            const SizedBox(width: 10),
          ],
          Flexible(
            child: Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isUser ? AppTheme.charcoal : AppTheme.backgroundGray,
                borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(20),
                  topRight: const Radius.circular(20),
                  bottomLeft: Radius.circular(isUser ? 20 : 4),
                  bottomRight: Radius.circular(isUser ? 4 : 20),
                ),
              ),
              child: isUser
                  ? Text(
                      message.content,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.primaryWhite,
                            height: 1.4,
                          ),
                    )
                  : MarkdownBody(
                      data: message.content,
                      styleSheet: MarkdownStyleSheet(
                        p: TextStyle(fontSize: 14, color: AppTheme.charcoal),
                        strong: const TextStyle(fontWeight: FontWeight.bold),
                        listBullet: TextStyle(color: AppTheme.charcoal),
                      ),
                    ),
            ),
          ),
          if (isUser) ...[
            const SizedBox(width: 10),
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: AppTheme.backgroundGray,
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Iconsax.user,
                size: 18,
                color: AppTheme.charcoal,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildFormattedResponse(String content) {
    // Parse and format the AI response for better readability
    final lines = content.split('\n');
    final List<Widget> widgets = [];

    for (int i = 0; i < lines.length; i++) {
      final line = lines[i].trim();

      if (line.isEmpty) {
        widgets.add(const SizedBox(height: 8));
        continue;
      }

      // Check for bullet points
      if (line.startsWith('•') ||
          line.startsWith('-') ||
          line.startsWith('*')) {
        widgets.add(_buildBulletPoint(line.substring(1).trim()));
      }
      // Check for headers (lines ending with :)
      else if (line.endsWith(':') && line.length < 50) {
        if (widgets.isNotEmpty) {
          widgets.add(const SizedBox(height: 12));
        }
        widgets.add(_buildSectionHeader(line));
      }
      // Check for outfit items (Top:, Bottom:, etc.)
      else if (_isOutfitLine(line)) {
        widgets.add(_buildOutfitItem(line));
      }
      // Regular text
      else {
        widgets.add(_buildParagraph(line));
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: widgets,
    );
  }

  bool _isOutfitLine(String line) {
    final lowerLine = line.toLowerCase();
    return lowerLine.startsWith('top:') ||
        lowerLine.startsWith('bottom:') ||
        lowerLine.startsWith('bottoms:') ||
        lowerLine.startsWith('footwear:') ||
        lowerLine.startsWith('shoes:') ||
        lowerLine.startsWith('outerwear:') ||
        lowerLine.startsWith('jacket:') ||
        lowerLine.startsWith('accessory:') ||
        lowerLine.startsWith('accessories:') ||
        lowerLine.startsWith('socks:');
  }

  Widget _buildBulletPoint(String text) {
    return Padding(
      padding: const EdgeInsets.only(left: 8, top: 6, bottom: 2),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.only(top: 8),
            width: 6,
            height: 6,
            decoration: BoxDecoration(
              color: AppTheme.charcoal,
              shape: BoxShape.circle,
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              text,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    height: 1.5,
                    color: AppTheme.charcoal,
                  ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w600,
              color: AppTheme.charcoal,
            ),
      ),
    );
  }

  Widget _buildOutfitItem(String line) {
    // Parse "Top: Blue T-Shirt - goes well with jeans"
    final colonIndex = line.indexOf(':');
    if (colonIndex == -1) return _buildParagraph(line);

    final category = line.substring(0, colonIndex).trim();
    final description = line.substring(colonIndex + 1).trim();

    // Check for color mentions and extract them
    final colorWidget = _extractColorIndicator(description);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppTheme.primaryWhite,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppTheme.lightGray.withOpacity(0.5)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.charcoal,
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              category.toUpperCase(),
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.primaryWhite,
                    fontWeight: FontWeight.w600,
                    fontSize: 10,
                    letterSpacing: 0.5,
                  ),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Text(
              description,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    height: 1.4,
                  ),
            ),
          ),
          if (colorWidget != null) colorWidget,
        ],
      ),
    );
  }

  Widget? _extractColorIndicator(String text) {
    // Map of color names to actual colors
    final colorMap = {
      'red': Colors.red,
      'blue': Colors.blue,
      'navy': const Color(0xFF000080),
      'navy blue': const Color(0xFF000080),
      'green': Colors.green,
      'yellow': Colors.yellow,
      'orange': Colors.orange,
      'purple': Colors.purple,
      'pink': Colors.pink,
      'black': Colors.black,
      'white': Colors.white,
      'gray': Colors.grey,
      'grey': Colors.grey,
      'brown': Colors.brown,
      'beige': const Color(0xFFF5F5DC),
      'tan': const Color(0xFFD2B48C),
      'cream': const Color(0xFFFFFDD0),
      'maroon': const Color(0xFF800000),
      'burgundy': const Color(0xFF800020),
      'teal': Colors.teal,
      'coral': const Color(0xFFFF7F50),
      'olive': const Color(0xFF808000),
      'khaki': const Color(0xFFC3B091),
      'indigo': Colors.indigo,
      'violet': const Color(0xFF8B00FF),
      'magenta': Colors.pinkAccent,
      'cyan': Colors.cyan,
      'lavender': const Color(0xFFE6E6FA),
      'mint': const Color(0xFF98FF98),
    };

    final lowerText = text.toLowerCase();

    for (final entry in colorMap.entries) {
      if (lowerText.contains(entry.key)) {
        return Container(
          width: 20,
          height: 20,
          margin: const EdgeInsets.only(left: 8),
          decoration: BoxDecoration(
            color: entry.value,
            shape: BoxShape.circle,
            border: Border.all(color: AppTheme.lightGray),
          ),
        );
      }
    }

    return null;
  }

  Widget _buildParagraph(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Text(
        text,
        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              height: 1.5,
              color: AppTheme.charcoal,
            ),
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 36,
            height: 36,
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [AppTheme.charcoal, AppTheme.charcoal.withOpacity(0.7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Iconsax.magic_star,
              size: 18,
              color: AppTheme.primaryWhite,
            ),
          ),
          const SizedBox(width: 10),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
            decoration: BoxDecoration(
              color: AppTheme.backgroundGray,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _buildAnimatedDot(0),
                const SizedBox(width: 4),
                _buildAnimatedDot(1),
                const SizedBox(width: 4),
                _buildAnimatedDot(2),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAnimatedDot(int index) {
    return TweenAnimationBuilder<double>(
      tween: Tween(begin: 0.3, end: 1.0),
      duration: Duration(milliseconds: 400 + (index * 200)),
      curve: Curves.easeInOut,
      builder: (context, value, child) {
        return Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: AppTheme.charcoal.withOpacity(value),
            shape: BoxShape.circle,
          ),
        );
      },
    );
  }

  Widget _buildInputField() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.primaryWhite,
        border: Border(
          top: BorderSide(color: AppTheme.lightGray),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            // Quick Actions Button
            GestureDetector(
              onTap: _showQuickActions,
              child: Container(
                width: 46,
                height: 46,
                decoration: BoxDecoration(
                  color: AppTheme.backgroundGray,
                  borderRadius: BorderRadius.circular(23),
                ),
                child: const Icon(
                  Iconsax.flash_1,
                  color: AppTheme.charcoal,
                  size: 22,
                ),
              ),
            ),

            const SizedBox(width: 12),

            // Text Input
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: AppTheme.backgroundGray,
                  borderRadius: BorderRadius.circular(24),
                ),
                child: TextField(
                  controller: _messageController,
                  decoration: InputDecoration(
                    hintText: 'Ask about fashion...',
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 20,
                      vertical: 14,
                    ),
                    hintStyle: TextStyle(color: AppTheme.mediumGray),
                  ),
                  textInputAction: TextInputAction.send,
                  onSubmitted: (_) => _sendMessage(),
                  maxLines: null,
                ),
              ),
            ),

            const SizedBox(width: 12),

            // Send Button
            Consumer<ChatProvider>(
              builder: (context, chatProvider, _) {
                return GestureDetector(
                  onTap: chatProvider.isLoading ? null : _sendMessage,
                  child: Container(
                    width: 46,
                    height: 46,
                    decoration: BoxDecoration(
                      gradient: chatProvider.isLoading
                          ? null
                          : LinearGradient(
                              colors: [
                                AppTheme.charcoal,
                                AppTheme.charcoal.withOpacity(0.8)
                              ],
                              begin: Alignment.topLeft,
                              end: Alignment.bottomRight,
                            ),
                      color:
                          chatProvider.isLoading ? AppTheme.mediumGray : null,
                      borderRadius: BorderRadius.circular(23),
                    ),
                    child: const Icon(
                      Iconsax.send_1,
                      color: AppTheme.primaryWhite,
                      size: 22,
                    ),
                  ),
                );
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showQuickActions() {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.primaryWhite,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                  color: AppTheme.lightGray,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 20),
              Text(
                'QUICK SUGGESTIONS',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      letterSpacing: 2,
                    ),
              ),
              const SizedBox(height: 20),
              _buildQuickActionTile(
                icon: Iconsax.sun_1,
                title: "Today's Outfit",
                subtitle: 'Based on current weather',
                type: 'today',
              ),
              _buildQuickActionTile(
                icon: Iconsax.coffee,
                title: 'Casual Look',
                subtitle: 'Relaxed everyday style',
                type: 'casual',
              ),
              _buildQuickActionTile(
                icon: Iconsax.briefcase,
                title: 'Formal Outfit',
                subtitle: 'Professional attire',
                type: 'formal',
              ),
              _buildQuickActionTile(
                icon: Iconsax.heart,
                title: 'Date Night',
                subtitle: 'Romantic occasion',
                type: 'date',
              ),
              _buildQuickActionTile(
                icon: Iconsax.music,
                title: 'Party Look',
                subtitle: 'Night out style',
                type: 'party',
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionTile({
    required IconData icon,
    required String title,
    required String subtitle,
    required String type,
  }) {
    return ListTile(
      leading: Container(
        width: 46,
        height: 46,
        decoration: BoxDecoration(
          color: AppTheme.backgroundGray,
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(icon, color: AppTheme.charcoal),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      subtitle: Text(
        subtitle,
        style: TextStyle(color: AppTheme.mediumGray, fontSize: 13),
      ),
      trailing: const Icon(Iconsax.arrow_right_3,
          size: 20, color: AppTheme.mediumGray),
      onTap: () {
        Navigator.pop(context);
        _sendQuickSuggestion(type);
      },
    );
  }
}

class _QuickAction {
  final IconData icon;
  final String label;
  final String type;

  _QuickAction({required this.icon, required this.label, required this.type});
}
