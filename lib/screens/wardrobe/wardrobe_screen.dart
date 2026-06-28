import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:iconsax/iconsax.dart';
import 'package:image_picker/image_picker.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/theme.dart';
import '../../config/constants.dart';
import '../../providers/wardrobe_provider.dart';
import '../../models/clothing_item.dart';
import '../../services/api_service.dart';

class WardrobeScreen extends StatefulWidget {
  const WardrobeScreen({super.key});

  @override
  State<WardrobeScreen> createState() => _WardrobeScreenState();
}

class _WardrobeScreenState extends State<WardrobeScreen> {
  final ImagePicker _picker = ImagePicker();
  final ApiService _api = ApiService();

  @override
  void initState() {
    super.initState();
    _loadItems();
  }

  Future<void> _loadItems() async {
    await Provider.of<WardrobeProvider>(context, listen: false).fetchItems();
  }

  Future<void> _pickImage() async {
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
                'ADD CLOTHING ITEM',
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                      letterSpacing: 2,
                    ),
              ),
              const SizedBox(height: 20),
              ListTile(
                leading: const Icon(Iconsax.camera),
                title: const Text('Take Photo'),
                onTap: () {
                  Navigator.pop(context);
                  _getImage(ImageSource.camera);
                },
              ),
              ListTile(
                leading: const Icon(Iconsax.gallery),
                title: const Text('Choose from Gallery'),
                onTap: () {
                  Navigator.pop(context);
                  _getImage(ImageSource.gallery);
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _getImage(ImageSource source) async {
    try {
      final XFile? image = await _picker.pickImage(
        source: source,
        maxWidth: 1024,
        maxHeight: 1024,
        imageQuality: 85,
      );

      if (image != null) {
        _showUploadingDialog();

        // Read image as bytes (works on both web and mobile)
        final bytes = await image.readAsBytes();
        final fileName = image.name;

        final provider = Provider.of<WardrobeProvider>(context, listen: false);
        final result = await provider.uploadItem(bytes, fileName);

        Navigator.pop(context); // Close uploading dialog

        if (result != null) {
          // Only show edit dialog if detection failed
          if (result.clothingType.toLowerCase() == 'unknown') {
            _showEditItemDialog(result);
          } else {
            _showSuccessSnackBar('Added: ${result.clothingType}');
          }
        } else {
          _showErrorSnackBar(provider.error ?? 'Failed to upload item');
        }
      }
    } catch (e) {
      _showErrorSnackBar('Error selecting image: $e');
    }
  }

  void _showUploadingDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const CircularProgressIndicator(
              color: AppTheme.primaryBlack,
              strokeWidth: 2,
            ),
            const SizedBox(height: 16),
            Text(
              'Analyzing your clothing...',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  void _showSuccessSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.success,
      ),
    );
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: AppTheme.error,
      ),
    );
  }

  // ===========================================
  // ITEM DETAIL POPUP
  // ===========================================

  void _showItemDetails(ClothingItem item) {
    final imageUrl = '${AppConstants.baseUrl}/${item.fullImageUrl}';

    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.primaryWhite,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.85,
        minChildSize: 0.5,
        maxChildSize: 0.95,
        expand: false,
        builder: (context, scrollController) => Column(
          children: [
            // Handle
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: AppTheme.lightGray,
                borderRadius: BorderRadius.circular(2),
              ),
            ),

            Expanded(
              child: SingleChildScrollView(
                controller: scrollController,
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Image
                    Center(
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(16),
                        child: CachedNetworkImage(
                          imageUrl: imageUrl,
                          height: 300,
                          fit: BoxFit.contain,
                          placeholder: (context, url) => Container(
                            height: 300,
                            color: AppTheme.backgroundGray,
                            child: const Center(
                              child: CircularProgressIndicator(strokeWidth: 2),
                            ),
                          ),
                          errorWidget: (context, url, error) => Container(
                            height: 300,
                            color: AppTheme.backgroundGray,
                            child: const Icon(Iconsax.image, size: 48),
                          ),
                        ),
                      ),
                    ),

                    const SizedBox(height: 24),

                    // Clothing Type
                    Text(
                      'CLOTHING TYPE',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            letterSpacing: 2,
                            color: AppTheme.mediumGray,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      item.clothingType.toUpperCase(),
                      style:
                          Theme.of(context).textTheme.headlineSmall?.copyWith(
                                fontWeight: FontWeight.w600,
                              ),
                    ),

                    const SizedBox(height: 20),

                    // Layer Type
                    Text(
                      'CATEGORY',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            letterSpacing: 2,
                            color: AppTheme.mediumGray,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 12, vertical: 6),
                      decoration: BoxDecoration(
                        color: AppTheme.backgroundGray,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        item.layerType.toUpperCase(),
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                    ),

                    const SizedBox(height: 20),

                    // Colors
                    Text(
                      'COLORS',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            letterSpacing: 2,
                            color: AppTheme.mediumGray,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        if (item.primaryColorHex != null) ...[
                          _buildColorCircle(item.primaryColorHex!, 'Primary'),
                          const SizedBox(width: 16),
                        ],
                        if (item.secondaryColorHex != null)
                          _buildColorCircle(
                              item.secondaryColorHex!, 'Secondary'),
                        if (item.primaryColorHex == null &&
                            item.secondaryColorHex == null)
                          Text(
                            'No colors detected',
                            style: Theme.of(context)
                                .textTheme
                                .bodyMedium
                                ?.copyWith(
                                  color: AppTheme.mediumGray,
                                ),
                          ),
                      ],
                    ),

                    const SizedBox(height: 20),

                    // Attributes
                    Text(
                      'ATTRIBUTES',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            letterSpacing: 2,
                            color: AppTheme.mediumGray,
                          ),
                    ),
                    const SizedBox(height: 8),
                    if (item.attributes.isNotEmpty)
                      Wrap(
                        spacing: 8,
                        runSpacing: 8,
                        children: item.attributes.map((attr) {
                          return Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              border: Border.all(color: AppTheme.lightGray),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: Text(
                              attr,
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                          );
                        }).toList(),
                      )
                    else
                      Text(
                        'No attributes detected',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppTheme.mediumGray,
                            ),
                      ),

                    const SizedBox(height: 20),

                    // Stats
                    Text(
                      'STATS',
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            letterSpacing: 2,
                            color: AppTheme.mediumGray,
                          ),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        _buildStatItem(
                          icon: Iconsax.repeat,
                          value: '${item.timesWorn}',
                          label: 'Times Worn',
                        ),
                        const SizedBox(width: 24),
                        if (item.lastWornDate != null)
                          _buildStatItem(
                            icon: Iconsax.calendar,
                            value: _formatDate(item.lastWornDate!),
                            label: 'Last Worn',
                          ),
                      ],
                    ),

                    const SizedBox(height: 32),

                    // Action Buttons
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              _showEditItemDialog(item);
                            },
                            icon: const Icon(Iconsax.edit, size: 18),
                            label: const Text('EDIT'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: () {
                              Navigator.pop(context);
                              _deleteItem(item);
                            },
                            icon: const Icon(Iconsax.trash, size: 18),
                            label: const Text('DELETE'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: AppTheme.error,
                              side: const BorderSide(color: AppTheme.error),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildColorCircle(String hex, String label) {
    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: _hexToColor(hex),
            shape: BoxShape.circle,
            border: Border.all(color: AppTheme.lightGray, width: 2),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 4,
                offset: const Offset(0, 2),
              ),
            ],
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: AppTheme.mediumGray,
              ),
        ),
        Text(
          hex.toUpperCase(),
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                fontWeight: FontWeight.w500,
                fontSize: 10,
              ),
        ),
      ],
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Row(
      children: [
        Icon(icon, size: 20, color: AppTheme.mediumGray),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              value,
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
            Text(
              label,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: AppTheme.mediumGray,
                  ),
            ),
          ],
        ),
      ],
    );
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date).inDays;

    if (diff == 0) return 'Today';
    if (diff == 1) return 'Yesterday';
    if (diff < 7) return '$diff days ago';
    if (diff < 30) return '${(diff / 7).floor()} weeks ago';
    return '${(diff / 30).floor()} months ago';
  }

  // ===========================================
  // EDIT ITEM DIALOG
  // ===========================================

  void _showEditItemDialog(ClothingItem item) {
    String selectedClothingType = item.clothingType;
    String selectedLayerType = item.layerType;
    final bool isUnknown = item.clothingType.toLowerCase() == 'unknown';

    final clothingTypes = [
      't-shirt',
      'shirt',
      'polo',
      'blouse',
      'tank top',
      'sweater',
      'hoodie',
      'cardigan',
      'jeans',
      'pants',
      'shorts',
      'skirt',
      'dress',
      'leggings',
      'sweatpants',
      'jacket',
      'coat',
      'blazer',
      'vest',
      'bomber jacket',
      'denim jacket',
      'leather jacket',
      'sneakers',
      'boots',
      'sandals',
      'heels',
      'loafers',
      'running shoes',
      'dress shoes',
      'socks',
      'ankle socks',
      'crew socks',
      'other'
    ];

    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.primaryWhite,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      isScrollControlled: true,
      builder: (context) => StatefulBuilder(
        builder: (context, setModalState) => Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(context).viewInsets.bottom + 20,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: AppTheme.lightGray,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // Title
              Center(
                child: Text(
                  isUnknown ? 'ITEM NOT RECOGNIZED' : 'EDIT ITEM',
                  style: Theme.of(context).textTheme.labelLarge?.copyWith(
                        letterSpacing: 2,
                      ),
                ),
              ),

              if (isUnknown) ...[
                const SizedBox(height: 8),
                Center(
                  child: Text(
                    'Please select the correct category',
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: AppTheme.mediumGray,
                        ),
                  ),
                ),
              ],

              const SizedBox(height: 24),

              // Clothing Type Dropdown
              Text(
                'CLOTHING TYPE',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      letterSpacing: 2,
                      color: AppTheme.mediumGray,
                    ),
              ),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12),
                decoration: BoxDecoration(
                  color: AppTheme.backgroundGray,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: DropdownButtonHideUnderline(
                  child: DropdownButton<String>(
                    value: clothingTypes
                            .contains(selectedClothingType.toLowerCase())
                        ? selectedClothingType.toLowerCase()
                        : 'other',
                    isExpanded: true,
                    items: clothingTypes.map((type) {
                      return DropdownMenuItem(
                        value: type,
                        child: Text(type.toUpperCase()),
                      );
                    }).toList(),
                    onChanged: (value) {
                      if (value != null) {
                        setModalState(() {
                          selectedClothingType = value;
                          // Auto-set layer type based on clothing type
                          if ([
                            't-shirt',
                            'shirt',
                            'polo',
                            'blouse',
                            'tank top',
                            'sweater',
                            'hoodie',
                            'cardigan'
                          ].contains(value)) {
                            selectedLayerType = 'top';
                          } else if ([
                            'jeans',
                            'pants',
                            'shorts',
                            'skirt',
                            'leggings',
                            'sweatpants'
                          ].contains(value)) {
                            selectedLayerType = 'bottom';
                          } else if (['dress'].contains(value)) {
                            selectedLayerType =
                                'top'; // or could be a special "full" category
                          } else if ([
                            'jacket',
                            'coat',
                            'blazer',
                            'vest',
                            'bomber jacket',
                            'denim jacket',
                            'leather jacket'
                          ].contains(value)) {
                            selectedLayerType = 'outerwear';
                          } else if ([
                            'sneakers',
                            'boots',
                            'sandals',
                            'heels',
                            'loafers',
                            'running shoes',
                            'dress shoes'
                          ].contains(value)) {
                            selectedLayerType = 'footwear';
                          } else if (['socks', 'ankle socks', 'crew socks']
                              .contains(value)) {
                            selectedLayerType = 'socks';
                          }
                        });
                      }
                    },
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // Layer Type
              Text(
                'CATEGORY',
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                      letterSpacing: 2,
                      color: AppTheme.mediumGray,
                    ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 8,
                children: AppConstants.layerTypes.map((layer) {
                  final isSelected = selectedLayerType == layer;
                  return GestureDetector(
                    onTap: () {
                      setModalState(() {
                        selectedLayerType = layer;
                      });
                    },
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 16, vertical: 10),
                      decoration: BoxDecoration(
                        color: isSelected
                            ? AppTheme.primaryBlack
                            : AppTheme.backgroundGray,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: Text(
                        layer.toUpperCase(),
                        style: TextStyle(
                          color: isSelected
                              ? AppTheme.primaryWhite
                              : AppTheme.charcoal,
                          fontWeight: FontWeight.w500,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),

              const SizedBox(height: 24),

              // Save Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () async {
                    Navigator.pop(context);
                    await _updateItem(
                        item.id, selectedClothingType, selectedLayerType);
                  },
                  child: const Text('SAVE CHANGES'),
                ),
              ),

              const SizedBox(height: 8),

              // Cancel Button
              SizedBox(
                width: double.infinity,
                child: TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('CANCEL'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _updateItem(
      int itemId, String clothingType, String layerType) async {
    try {
      await _api.put(
        '${AppConstants.wardrobeEndpoint}/items/$itemId',
        body: {
          'clothing_type': clothingType,
          'layer_type': layerType,
        },
      );
      _showSuccessSnackBar('Item updated successfully!');
      _loadItems();
    } catch (e) {
      _showErrorSnackBar('Failed to update item');
    }
  }

  Future<void> _deleteItem(ClothingItem item) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Item'),
        content: const Text('Are you sure you want to delete this item?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('CANCEL'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child:
                const Text('DELETE', style: TextStyle(color: AppTheme.error)),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final provider = Provider.of<WardrobeProvider>(context, listen: false);
      final success = await provider.deleteItem(item.id);

      if (success) {
        _showSuccessSnackBar('Item deleted');
      } else {
        _showErrorSnackBar('Failed to delete item');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.primaryWhite,
      appBar: AppBar(
        title: const Text('WARDROBE'),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _pickImage,
        backgroundColor: AppTheme.primaryBlack,
        child: const Icon(Iconsax.add, color: AppTheme.primaryWhite),
      ),
      body: Column(
        children: [
          // Layer Filter
          _buildLayerFilter(),

          // Items Grid
          Expanded(
            child: RefreshIndicator(
              onRefresh: _loadItems,
              color: AppTheme.primaryBlack,
              child: Consumer<WardrobeProvider>(
                builder: (context, provider, _) {
                  if (provider.isLoading && provider.allItems.isEmpty) {
                    return const Center(
                      child: CircularProgressIndicator(
                        color: AppTheme.primaryBlack,
                        strokeWidth: 2,
                      ),
                    );
                  }

                  final items = provider.items;

                  if (items.isEmpty) {
                    return _buildEmptyState();
                  }

                  return GridView.builder(
                    padding: const EdgeInsets.all(16),
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 0.75,
                    ),
                    itemCount: items.length,
                    itemBuilder: (context, index) {
                      return _buildItemCard(items[index]);
                    },
                  );
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLayerFilter() {
    return Consumer<WardrobeProvider>(
      builder: (context, provider, _) {
        return Container(
          height: 50,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: [
              _buildFilterChip(
                label: 'All',
                isSelected: provider.selectedLayer == null,
                onTap: () => provider.setLayerFilter(null),
              ),
              ...AppConstants.layerTypes.map((layer) {
                return _buildFilterChip(
                  label: layer.toUpperCase(),
                  isSelected: provider.selectedLayer == layer,
                  onTap: () => provider.setLayerFilter(layer),
                );
              }),
            ],
          ),
        );
      },
    );
  }

  Widget _buildFilterChip({
    required String label,
    required bool isSelected,
    required VoidCallback onTap,
  }) {
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: GestureDetector(
        onTap: onTap,
        child: Chip(
          label: Text(
            label,
            style: TextStyle(
              color: isSelected ? AppTheme.primaryWhite : AppTheme.charcoal,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
          backgroundColor:
              isSelected ? AppTheme.primaryBlack : AppTheme.backgroundGray,
          side: BorderSide.none,
          padding: const EdgeInsets.symmetric(horizontal: 8),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Iconsax.bag_2, size: 64, color: AppTheme.lightGray),
          const SizedBox(height: 16),
          Text(
            'No items yet',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            'Tap + to add your first clothing item',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                  color: AppTheme.mediumGray,
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildItemCard(ClothingItem item) {
    final imageUrl = '${AppConstants.baseUrl}/${item.fullImageUrl}';
    final isUnknown = item.clothingType.toLowerCase() == 'unknown';

    return GestureDetector(
      onTap: () => _showItemDetails(item),
      onLongPress: () => _deleteItem(item),
      child: Container(
        decoration: BoxDecoration(
          color: AppTheme.primaryWhite,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isUnknown
                ? AppTheme.error.withOpacity(0.5)
                : AppTheme.lightGray,
            width: isUnknown ? 2 : 1,
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            Expanded(
              child: Stack(
                children: [
                  ClipRRect(
                    borderRadius:
                        const BorderRadius.vertical(top: Radius.circular(11)),
                    child: CachedNetworkImage(
                      imageUrl: imageUrl,
                      width: double.infinity,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(
                        color: AppTheme.backgroundGray,
                        child: const Center(
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: AppTheme.primaryBlack,
                          ),
                        ),
                      ),
                      errorWidget: (context, url, error) => Container(
                        color: AppTheme.backgroundGray,
                        child: const Icon(Iconsax.image,
                            color: AppTheme.mediumGray),
                      ),
                    ),
                  ),
                  // Warning badge for unknown items
                  if (isUnknown)
                    Positioned(
                      top: 8,
                      right: 8,
                      child: Container(
                        padding: const EdgeInsets.all(6),
                        decoration: const BoxDecoration(
                          color: AppTheme.error,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Iconsax.warning_2,
                          size: 14,
                          color: AppTheme.primaryWhite,
                        ),
                      ),
                    ),
                ],
              ),
            ),

            // Details
            Padding(
              padding: const EdgeInsets.all(10),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          item.clothingType.toUpperCase(),
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    fontWeight: FontWeight.w500,
                                    letterSpacing: 0.5,
                                    color: isUnknown ? AppTheme.error : null,
                                  ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (item.primaryColorHex != null)
                        Container(
                          width: 16,
                          height: 16,
                          decoration: BoxDecoration(
                            color: _hexToColor(item.primaryColorHex!),
                            shape: BoxShape.circle,
                            border: Border.all(color: AppTheme.lightGray),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    isUnknown ? 'Tap to categorize' : item.layerType,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color:
                              isUnknown ? AppTheme.error : AppTheme.mediumGray,
                          fontStyle:
                              isUnknown ? FontStyle.italic : FontStyle.normal,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceAll('#', '');
    if (hex.length == 6) {
      hex = 'FF$hex';
    }
    return Color(int.parse(hex, radix: 16));
  }
}
