# Flutter App Development Prompt with GetX & Clean Architecture

## Context

This prompt is designed to be used with the `API_ARCHITECTURE_GUIDE.md` file. Pass both files to an AI code generator, Copilot, or development agent to generate a production-ready Flutter application.

---

## Project Requirements

### Overview

Create a **production-ready Flutter mobile application** that integrates with the FastAPI backend described in the attached `API_ARCHITECTURE_GUIDE.md`. The app must implement user authentication, item management (CRUD operations), and pagination.

Authentication note:
- User sign-in/sign-up should be implemented via **Supabase Auth** in the Flutter app.
- For protected backend endpoints, send the Supabase access token as `Authorization: Bearer <token>`.
- Do **not** call backend `/auth/register`, `/auth/login`, or `/auth/refresh` (they are retired and return 410).

**Target:** iOS & Android (mobile-first)  
**State Management:** GetX (GetX Controller + Obx + bindings)  
**Architecture:** Feature-Based Clean Architecture with Modular Design  
**Code Quality:** SOLID principles, DRY, clean code standards

Required auth dependency:
- Use `supabase_flutter` for authentication and session refresh.

---

## Architecture & Project Structure

### Overall Architecture Pattern

```
flutter_app/
├── lib/
│   ├── main.dart                           # App entry point
│   ├── app/
│   │   ├── bindings/                       # Global bindings
│   │   │   └── app_binding.dart
│   │   ├── middleware/                     # Route middleware
│   │   │   └── auth_middleware.dart
│   │   ├── routes/                         # Route management
│   │   │   ├── app_pages.dart
│   │   │   └── app_routes.dart
│   │   └── theme/                          # Global theming
│   │       ├── app_colors.dart
│   │       ├── app_text_styles.dart
│   │       └── app_theme.dart
│   │
│   ├── core/
│   │   ├── constants/                      # App-wide constants
│   │   │   ├── api_constants.dart
│   │   │   └── app_constants.dart
│   │   ├── extensions/                     # Dart extensions
│   │   │   ├── context_extensions.dart
│   │   │   ├── date_extensions.dart
│   │   │   ├── string_extensions.dart
│   │   │   └── num_extensions.dart
│   │   ├── network/                        # HTTP client & interceptors
│   │   │   ├── api_client.dart
│   │   │   ├── api_endpoint.dart
│   │   │   ├── interceptors/
│   │   │   │   ├── auth_interceptor.dart
│   │   │   │   └── logging_interceptor.dart
│   │   │   └── models/
│   │   │       ├── api_response_model.dart
│   │   │       └── pagination_model.dart
│   │   ├── storage/                        # Local storage (Hive/GetStorage)
│   │   │   ├── local_storage_service.dart
│   │   │   └── token_storage_service.dart
│   │   ├── utils/                          # Utility functions
│   │   │   ├── dialogs/
│   │   │   │   ├── app_dialogs.dart
│   │   │   │   └── app_snackbars.dart
│   │   │   ├── logger/
│   │   │   │   └── app_logger.dart
│   │   │   ├── validators/
│   │   │   │   └── input_validators.dart
│   │   │   └── formatters/
│   │   │       └── date_formatters.dart
│   │   ├── exceptions/                     # Custom exceptions
│   │   │   └── app_exceptions.dart
│   │   └── usecases/                       # Domain-level use cases
│   │       ├── auth_usecases.dart
│   │       └── item_usecases.dart
│   │
│   ├── features/
│   │   ├── auth/                           # Authentication feature
│   │   │   ├── bindings/
│   │   │   │   └── auth_binding.dart
│   │   │   ├── controllers/
│   │   │   │   ├── auth_controller.dart
│   │   │   │   └── login_controller.dart
│   │   │   ├── data/
│   │   │   │   ├── datasources/
│   │   │   │   │   └── auth_remote_datasource.dart
│   │   │   │   ├── models/
│   │   │   │   │   ├── user_model.dart
│   │   │   │   │   ├── login_request_model.dart
│   │   │   │   │   ├── register_request_model.dart
│   │   │   │   │   └── token_model.dart
│   │   │   │   └── repositories/
│   │   │   │       └── auth_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── user_entity.dart
│   │   │   │   │   └── token_entity.dart
│   │   │   │   └── repositories/
│   │   │   │       └── auth_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── login_page.dart
│   │   │   │   │   ├── register_page.dart
│   │   │   │   │   └── splash_screen.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── auth_text_fields.dart
│   │   │   │   │   ├── auth_button.dart
│   │   │   │   │   └── loading_overlay.dart
│   │   │   │   └── screens/ (optional sub-screens)
│   │   │   └── routes/
│   │   │       └── auth_routes.dart
│   │   │
│   │   ├── items/                          # Items/Products feature
│   │   │   ├── bindings/
│   │   │   │   └── items_binding.dart
│   │   │   ├── controllers/
│   │   │   │   ├── items_controller.dart
│   │   │   │   ├── item_detail_controller.dart
│   │   │   │   └── create_item_controller.dart
│   │   │   ├── data/
│   │   │   │   ├── datasources/
│   │   │   │   │   └── items_remote_datasource.dart
│   │   │   │   ├── models/
│   │   │   │   │   ├── item_model.dart
│   │   │   │   │   ├── item_create_model.dart
│   │   │   │   │   └── item_update_model.dart
│   │   │   │   └── repositories/
│   │   │   │       └── items_repository_impl.dart
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   │   ├── item_entity.dart
│   │   │   │   │   └── pagination_entity.dart
│   │   │   │   └── repositories/
│   │   │   │       └── items_repository.dart
│   │   │   ├── presentation/
│   │   │   │   ├── pages/
│   │   │   │   │   ├── items_list_page.dart
│   │   │   │   │   ├── item_detail_page.dart
│   │   │   │   │   ├── create_item_page.dart
│   │   │   │   │   └── edit_item_page.dart
│   │   │   │   ├── widgets/
│   │   │   │   │   ├── item_card.dart
│   │   │   │   │   ├── item_list_tile.dart
│   │   │   │   │   ├── price_display.dart
│   │   │   │   │   ├── item_input_form.dart
│   │   │   │   │   └── pagination_controls.dart
│   │   │   │   └── screens/ (optional sub-screens)
│   │   │   └── routes/
│   │   │       └── items_routes.dart
│   │   │
│   │   └── profile/                        # User profile feature
│   │       ├── bindings/
│   │       │   └── profile_binding.dart
│   │       ├── controllers/
│   │       │   └── profile_controller.dart
│   │       ├── presentation/
│   │       │   ├── pages/
│   │       │   │   └── profile_page.dart
│   │       │   └── widgets/
│   │       │       ├── profile_header.dart
│   │       │       └── user_info_tile.dart
│   │       └── routes/
│   │           └── profile_routes.dart
│   │
│   └── generated/                          # Auto-generated files (if needed)
│       └── (build artifacts from code generation)
│
├── pubspec.yaml                            # Dependencies & config
└── analysis_options.yaml                   # Linter rules
```

---

## Key Implementation Requirements

### 1. State Management with GetX

#### 1.1 Controller Design Pattern

```
✓ GetX Controllers for business logic
✓ Reactive variables using Rx (RxString, RxBool, RxList, RxMap, etc.)
✓ Observable objects using Obx() for UI reactivity
✓ Workers for side effects (ever, once, debounce, throttle)
✓ Proper resource cleanup in onClose()
✓ Separation: Business logic in controller, UI in widget
```

**Example Pattern:**
```dart
class ItemsController extends GetxController {
  // Reactive variables
  final RxList<ItemEntity> items = <ItemEntity>[].obs;
  final RxBool isLoading = false.obs;
  final RxString errorMessage = ''.obs;
  final RxInt currentPage = 1.obs;
  final RxInt totalPages = 0.obs;

  // Non-reactive but managed properties
  late ItemsRepository itemsRepository;
  late PaginationEntity pagination;

  @override
  void onInit() {
    super.onInit();
    // Initialize dependencies
    itemsRepository = Get.find<ItemsRepository>();
    
    // Setup workers for side effects
    ever(isLoading, (_) => _handleLoadingState());
    debounce(errorMessage, (_) => _showErrorDialog(),
        time: const Duration(milliseconds: 300));
  }

  Future<void> fetchItems({int page = 1}) async {
    try {
      isLoading.value = true;
      errorMessage.value = '';
      
      final result = await itemsRepository.getItems(page: page);
      items.value = result.items;
      pagination = result.pagination;
      currentPage.value = page;
      totalPages.value = result.pagination.lastPage;
    } catch (e) {
      errorMessage.value = _handleException(e);
      items.clear();
    } finally {
      isLoading.value = false;
    }
  }

  @override
  void onClose() {
    // Clean up resources
    super.onClose();
  }

  // Private helper methods
  String _handleException(dynamic e) {
    if (e is AppException) return e.message;
    return 'An unexpected error occurred';
  }

  void _handleLoadingState() {
    // Handle loading state changes
  }

  void _showErrorDialog() {
    // Show error to user
  }
}
```

#### 1.2 Bindings Architecture

```dart
// app/bindings/app_binding.dart
class AppBinding extends Bindings {
  @override
  void dependencies() {
    // Core services - Singleton pattern
    Get.put<LocalStorageService>(LocalStorageService(), permanent: true);
    Get.put<TokenStorageService>(TokenStorageService(), permanent: true);
    Get.put<ApiClient>(ApiClient(), permanent: true);
    
    // Global controllers
    Get.put<AppController>(AppController(), permanent: true);
  }
}

// features/auth/bindings/auth_binding.dart
class AuthBinding extends Bindings {
  @override
  void dependencies() {
    // Auth repository & datasource
    Get.put<AuthRemoteDatasource>(AuthRemoteDatasourceImpl());
    Get.put<AuthRepository>(AuthRepositoryImpl(
      remoteDatasource: Get.find(),
      tokenService: Get.find(),
    ));
    
    // Auth controller
    Get.put<AuthController>(AuthController(
      authRepository: Get.find(),
    ));
  }
}

// features/items/bindings/items_binding.dart
class ItemsBinding extends Bindings {
  @override
  void dependencies() {
    // Items repository & datasource
    Get.put<ItemsRemoteDatasource>(ItemsRemoteDatasourceImpl());
    Get.put<ItemsRepository>(ItemsRepositoryImpl(
      remoteDatasource: Get.find(),
    ));
    
    // Items controller
    Get.put<ItemsController>(ItemsController(
      itemsRepository: Get.find(),
    ));
  }
}
```

#### 1.3 Routes with GetX Navigation

```dart
// app/routes/app_pages.dart
abstract class AppPages {
  static const INITIAL = AppRoutes.splash;

  static final routes = [
    // Splash & Auth routes
    GetPage(
      name: AppRoutes.splash,
      page: () => const SplashScreen(),
      binding: AppBinding(),
    ),
    GetPage(
      name: AppRoutes.login,
      page: () => const LoginPage(),
      binding: AuthBinding(),
      middlewares: [AuthMiddleware()],
    ),
    GetPage(
      name: AppRoutes.register,
      page: () => const RegisterPage(),
      binding: AuthBinding(),
    ),
    
    // Items routes
    GetPage(
      name: AppRoutes.itemsList,
      page: () => const ItemsListPage(),
      binding: ItemsBinding(),
    ),
    GetPage(
      name: AppRoutes.itemDetail,
      page: () => const ItemDetailPage(),
      binding: ItemsBinding(),
      middlewares: [AuthMiddleware()],
      parameters: {'id': ''},
    ),
    GetPage(
      name: AppRoutes.createItem,
      page: () => const CreateItemPage(),
      binding: ItemsBinding(),
      middlewares: [AuthMiddleware()],
    ),
  ];
}

// app/routes/app_routes.dart
abstract class AppRoutes {
  static const splash = '/splash';
  static const login = '/login';
  static const register = '/register';
  static const itemsList = '/items';
  static const itemDetail = '/items/:id';
  static const createItem = '/items/create';
  static const profile = '/profile';
}
```

### 2. Clean Architecture Layers

#### 2.1 Domain Layer (Business Logic)

**Entities:** Pure Dart classes representing core business objects
```dart
// features/items/domain/entities/item_entity.dart
class ItemEntity {
  final int id;
  final String name;
  final String? description;
  final double price;
  final double? tax;
  final DateTime createdAt;
  final DateTime updatedAt;

  ItemEntity({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    this.tax,
    required this.createdAt,
    required this.updatedAt,
  });

  // Value equality
  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ItemEntity &&
          runtimeType == other.runtimeType &&
          id == other.id &&
          name == other.name &&
          price == other.price;

  @override
  int get hashCode =>
      id.hashCode ^ name.hashCode ^ price.hashCode;
}
```

**Repositories (Abstract):** Define contracts for data access
```dart
// features/items/domain/repositories/items_repository.dart
abstract class ItemsRepository {
  Future<PaginatedResponse<ItemEntity>> getItems({
    required int page,
    required int perPage,
  });

  Future<ItemEntity> getItemById(int id);

  Future<ItemEntity> createItem(ItemCreateEntity itemCreate);

  Future<List<ItemEntity>> bulkCreateItems(List<ItemCreateEntity> items);

  Future<ItemEntity> updateItem(int id, ItemUpdateEntity itemUpdate);

  Future<void> deleteItem(int id);
}
```

#### 2.2 Data Layer (Implementation & Models)

**Remote Datasources:** Handle API calls
```dart
// features/items/data/datasources/items_remote_datasource.dart
abstract class ItemsRemoteDatasource {
  Future<PaginatedResponse<ItemModel>> getItems({
    required int page,
    required int perPage,
  });

  Future<ItemModel> getItemById(int id);

  Future<ItemModel> createItem(ItemCreateModel itemCreate);

  Future<List<ItemModel>> bulkCreateItems(List<ItemCreateModel> items);

  Future<ItemModel> updateItem(int id, ItemUpdateModel itemUpdate);

  Future<void> deleteItem(int id);
}

class ItemsRemoteDatasourceImpl implements ItemsRemoteDatasource {
  final ApiClient apiClient;

  ItemsRemoteDatasourceImpl({required this.apiClient});

  @override
  Future<PaginatedResponse<ItemModel>> getItems({
    required int page,
    required int perPage,
  }) async {
    try {
      final response = await apiClient.get(
        ApiEndpoints.items,
        queryParameters: {
          'page_no': page,
          'per_page': perPage,
        },
      );

      final data = response.data['data'] as List;
      final paginationData = response.data['pagination'] as Map;

      return PaginatedResponse(
        items: data
            .map((item) => ItemModel.fromJson(item as Map<String, dynamic>))
            .toList(),
        pagination: PaginationModel.fromJson(paginationData as Map<String, dynamic>),
      );
    } catch (e) {
      throw _handleError(e);
    }
  }

  // Implement other methods...

  AppException _handleError(dynamic error) {
    if (error is AppException) return error;
    if (error is SocketException) {
      return NetworkException('No internet connection');
    }
    return AppException('An unexpected error occurred');
  }
}
```

**Repositories (Implementation):** Implement domain repositories, handle caching
```dart
// features/items/data/repositories/items_repository_impl.dart
class ItemsRepositoryImpl implements ItemsRepository {
  final ItemsRemoteDatasource remoteDatasource;
  final LocalStorageService? localStorageService;

  ItemsRepositoryImpl({
    required this.remoteDatasource,
    this.localStorageService,
  });

  @override
  Future<PaginatedResponse<ItemEntity>> getItems({
    required int page,
    required int perPage,
  }) async {
    try {
      // Try to get from remote
      final result = await remoteDatasource.getItems(
        page: page,
        perPage: perPage,
      );

      // Cache result if available
      if (localStorageService != null && page == 1) {
        await localStorageService!.saveItems(result.items);
      }

      return PaginatedResponse(
        items: result.items
            .map((model) => model.toEntity())
            .toList(),
        pagination: PaginationEntity(
          currentPage: result.pagination.currentPage,
          perPage: result.pagination.perPage,
          lastPage: result.pagination.lastPage,
          total: result.pagination.total,
        ),
      );
    } catch (e) {
      // Try to get from cache on error
      if (page == 1 && localStorageService != null) {
        final cached = await localStorageService!.getItems();
        if (cached.isNotEmpty) {
          return PaginatedResponse(
            items: cached,
            pagination: PaginationEntity(
              currentPage: 1,
              perPage: cached.length,
              lastPage: 1,
              total: cached.length,
            ),
          );
        }
      }
      rethrow;
    }
  }

  // Implement other methods...
}
```

**Models:** Map API responses to entities
```dart
// features/items/data/models/item_model.dart
class ItemModel {
  final int id;
  final String name;
  final String? description;
  final double price;
  final double? tax;
  final DateTime createdAt;
  final DateTime updatedAt;

  ItemModel({
    required this.id,
    required this.name,
    this.description,
    required this.price,
    this.tax,
    required this.createdAt,
    required this.updatedAt,
  });

  factory ItemModel.fromJson(Map<String, dynamic> json) {
    return ItemModel(
      id: json['id'] as int,
      name: json['name'] as String,
      description: json['description'] as String?,
      price: (json['price'] as num).toDouble(),
      tax: json['tax'] != null ? (json['tax'] as num).toDouble() : null,
      createdAt: DateTime.parse(json['created_at'] as String),
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'description': description,
      'price': price,
      'tax': tax,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  ItemEntity toEntity() {
    return ItemEntity(
      id: id,
      name: name,
      description: description,
      price: price,
      tax: tax,
      createdAt: createdAt,
      updatedAt: updatedAt,
    );
  }
}
```

#### 2.3 Presentation Layer (UI)

**Pages:** Full-screen widgets
```dart
// features/items/presentation/pages/items_list_page.dart
class ItemsListPage extends GetView<ItemsController> {
  const ItemsListPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Items'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => Get.toNamed(AppRoutes.createItem),
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value && controller.items.isEmpty) {
          return const Center(child: CircularProgressIndicator());
        }

        if (controller.errorMessage.isNotEmpty && controller.items.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 48, color: Colors.red),
                const SizedBox(height: 16),
                Text(controller.errorMessage.value),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () => controller.fetchItems(),
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        }

        if (controller.items.isEmpty) {
          return const Center(
            child: Text('No items found'),
          );
        }

        return RefreshIndicator(
          onRefresh: () => controller.fetchItems(),
          child: ListView.builder(
            padding: const EdgeInsets.all(8),
            itemCount: controller.items.length + 1,
            itemBuilder: (context, index) {
              if (index == controller.items.length) {
                return _buildPaginationControls();
              }

              final item = controller.items[index];
              return ItemCard(
                item: item,
                onTap: () => Get.toNamed(
                  AppRoutes.itemDetail,
                  parameters: {'id': item.id.toString()},
                ),
              );
            },
          ),
        );
      }),
    );
  }

  Widget _buildPaginationControls() {
    return Obx(() {
      if (controller.totalPages <= 1) return const SizedBox.shrink();

      return Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            ElevatedButton(
              onPressed: controller.currentPage.value > 1
                  ? () => controller.fetchItems(
                      page: controller.currentPage.value - 1)
                  : null,
              child: const Text('Previous'),
            ),
            Text(
              'Page ${controller.currentPage.value} of ${controller.totalPages.value}',
            ),
            ElevatedButton(
              onPressed: controller.currentPage.value < controller.totalPages.value
                  ? () => controller.fetchItems(
                      page: controller.currentPage.value + 1)
                  : null,
              child: const Text('Next'),
            ),
          ],
        ),
      );
    });
  }
}
```

**Widgets:** Reusable UI components
```dart
// features/items/presentation/widgets/item_card.dart
class ItemCard extends StatelessWidget {
  final ItemEntity item;
  final VoidCallback onTap;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;

  const ItemCard({
    Key? key,
    required this.item,
    required this.onTap,
    this.onEdit,
    this.onDelete,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      item.name,
                      style: Theme.of(context).textTheme.titleMedium,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  if (onEdit != null || onDelete != null)
                    PopupMenuButton(
                      itemBuilder: (context) => [
                        if (onEdit != null)
                          PopupMenuItem(
                            onTap: onEdit,
                            child: const Text('Edit'),
                          ),
                        if (onDelete != null)
                          PopupMenuItem(
                            onTap: onDelete,
                            child: const Text('Delete'),
                          ),
                      ],
                    ),
                ],
              ),
              if (item.description != null && item.description!.isNotEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    item.description!,
                    style: Theme.of(context).textTheme.bodySmall,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      '\$${item.price.toStringAsFixed(2)}',
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            color: Colors.green,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    if (item.tax != null && item.tax! > 0)
                      Text(
                        'Tax: \$${item.tax!.toStringAsFixed(2)}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
```

### 3. Network Layer Implementation

#### 3.1 API Client with Interceptors

```dart
// core/network/api_client.dart
class ApiClient {
  late Dio _dio;
  final TokenStorageService _tokenService = Get.find();
  final LocalStorageService _storageService = Get.find();

  ApiClient() {
    _initializeDio();
  }

  void _initializeDio() {
    _dio = Dio(
      BaseOptions(
        baseUrl: ApiConstants.baseUrl,
        connectTimeout: const Duration(seconds: 15),
        receiveTimeout: const Duration(seconds: 15),
        sendTimeout: const Duration(seconds: 15),
        contentType: Headers.jsonContentType,
        responseType: ResponseType.json,
        validateStatus: (status) => status! < 500,
      ),
    );

    // Add interceptors
    _dio.interceptors.addAll([
      LoggingInterceptor(),
      AuthInterceptor(
        tokenService: _tokenService,
        apiClient: this,
      ),
    ]);
  }

  Future<Response> get(
    String endpoint, {
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.get(
        endpoint,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    catch (e) {
      rethrow;
    }
  }

  Future<Response> post(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.post(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } catch (e) {
      rethrow;
    }
  }

  Future<Response> put(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.put(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } catch (e) {
      rethrow;
    }
  }

  Future<Response> delete(
    String endpoint, {
    dynamic data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
  }) async {
    try {
      final response = await _dio.delete(
        endpoint,
        data: data,
        queryParameters: queryParameters,
        options: options,
        cancelToken: cancelToken,
      );
      return _handleResponse(response);
    } catch (e) {
      rethrow;
    }
  }

  Response _handleResponse(Response response) {
    final statusCode = response.statusCode;

    if (statusCode == null || statusCode >= 500) {
      throw ServerException('Server error: $statusCode');
    }

    if (statusCode >= 400) {
      final errorMessage = response.data?['message'] ?? 'An error occurred';
      switch (statusCode) {
        case 401:
          throw UnauthorizedException(errorMessage);
        case 403:
          throw ForbiddenException(errorMessage);
        case 404:
          throw NotFoundException(errorMessage);
        case 409:
          throw ConflictException(errorMessage);
        case 422:
          throw ValidationException(errorMessage);
        default:
          throw BadRequestException(errorMessage);
      }
    }

    return response;
  }
}
```

#### 3.2 Auth Interceptor

```dart
// core/network/interceptors/auth_interceptor.dart
class AuthInterceptor extends Interceptor {
  final TokenStorageService tokenService;
  final ApiClient apiClient;
  bool _isRefreshing = false;
  final _requestQueue = <Future<dynamic> Function()>[];

  AuthInterceptor({
    required this.tokenService,
    required this.apiClient,
  });

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    try {
      final accessToken = await tokenService.getAccessToken();
      if (accessToken != null) {
        options.headers['Authorization'] = 'Bearer $accessToken';
      }
    } catch (e) {
      AppLogger.error('Error adding token to request', error: e);
    }
    return handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      return _handle401Error(err, handler);
    }
    return handler.next(err);
  }

  Future<void> _handle401Error(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (!_isRefreshing) {
      _isRefreshing = true;

      try {
        // Refresh Supabase session (no backend refresh endpoint)
        final refreshed = await tokenService.refreshSupabaseSession();
        if (!refreshed) {
          _isRefreshing = false;
          _requestQueue.clear();
          return _logoutUser(handler);
        }

        final newAccessToken = await tokenService.getAccessToken();
        if (newAccessToken == null) {
          _isRefreshing = false;
          _requestQueue.clear();
          return _logoutUser(handler);
        }

        _isRefreshing = false;

        // Retry original request
        err.requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';
        return handler.resolve(await apiClient._dio.fetch(err.requestOptions));
      } catch (e) {
        AppLogger.error('Token refresh failed', error: e);
        _isRefreshing = false;
        _requestQueue.clear();
        return _logoutUser(handler);
      }
    } else {
      // Queue request while token is being refreshed
      _requestQueue.add(() => Future.delayed(const Duration(milliseconds: 500)));
      return handler.next(err);
    }
  }

  void _logoutUser(ErrorInterceptorHandler handler) {
    Get.offAllNamed(AppRoutes.login);
    AppDialogs.showError('Session expired. Please login again.');
    return handler.reject(
      DioException(
        type: DioExceptionType.unknown,
        error: UnauthorizedException('Session expired'),
        requestOptions: RequestOptions(path: ''),
      ),
    );
  }
}
```

### 4. Error Handling & Exception Management

```dart
// core/exceptions/app_exceptions.dart
abstract class AppException implements Exception {
  final String message;
  
  AppException(this.message);

  @override
  String toString() => message;
}

class NetworkException extends AppException {
  NetworkException(String message) : super(message);
}

class ServerException extends AppException {
  final int? statusCode;
  
  ServerException(String message, {this.statusCode}) : super(message);
}

class UnauthorizedException extends AppException {
  UnauthorizedException(String message) : super(message);
}

class ForbiddenException extends AppException {
  ForbiddenException(String message) : super(message);
}

class NotFoundException extends AppException {
  NotFoundException(String message) : super(message);
}

class ConflictException extends AppException {
  ConflictException(String message) : super(message);
}

class ValidationException extends AppException {
  final dynamic errors;
  
  ValidationException(String message, {this.errors}) : super(message);
}

class BadRequestException extends AppException {
  BadRequestException(String message) : super(message);
}

class CacheException extends AppException {
  CacheException(String message) : super(message);
}
```

### 5. Local Storage

```dart
// core/storage/token_storage_service.dart
class TokenStorageService {
  static const _accessTokenKey = 'access_token';
  
  final GetStorage _storage = GetStorage();

  Future<void> saveAccessToken(String token) async {
    await _storage.write(_accessTokenKey, token);
  }

  Future<String?> getAccessToken() async {
    // Prefer Supabase session token (authoritative)
    final token = Supabase.instance.client.auth.currentSession?.accessToken;
    return token ?? _storage.read<String>(_accessTokenKey);
  }

  Future<bool> refreshSupabaseSession() async {
    try {
      final res = await Supabase.instance.client.auth.refreshSession();
      return res.session?.accessToken != null;
    } catch (_) {
      return false;
    }
  }

  Future<void> clearTokens() async {
    await _storage.remove(_accessTokenKey);
  }

  Future<bool> isTokenAvailable() async {
    final token = await getAccessToken();
    return token != null && token.isNotEmpty;
  }
}
```

### 6. Input Validation

```dart
// core/utils/validators/input_validators.dart
class InputValidators {
  static const _emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  static const _passwordMinLength = 6;
  static const _nameMinLength = 2;
  static const _pricePattern = r'^\d+(\.\d{1,2})?$';

  static String? validateEmail(String? value) {
    if (value == null || value.isEmpty) {
      return 'Email is required';
    }
    if (!RegExp(_emailPattern).hasMatch(value)) {
      return 'Enter a valid email';
    }
    return null;
  }

  static String? validatePassword(String? value) {
    if (value == null || value.isEmpty) {
      return 'Password is required';
    }
    if (value.length < _passwordMinLength) {
      return 'Password must be at least $_passwordMinLength characters';
    }
    return null;
  }

  static String? validateName(String? value) {
    if (value == null || value.isEmpty) {
      return 'Name is required';
    }
    if (value.length < _nameMinLength) {
      return 'Name must be at least $_nameMinLength characters';
    }
    return null;
  }

  static String? validatePrice(String? value) {
    if (value == null || value.isEmpty) {
      return 'Price is required';
    }
    if (double.tryParse(value) == null || double.parse(value) < 0) {
      return 'Enter a valid price';
    }
    return null;
  }

  static String? validateDescription(String? value) {
    // Optional field
    return null;
  }
}
```

---

## UI/UX Best Practices

### 1. Theme Management

```dart
// app/theme/app_theme.dart
class AppTheme {
  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      primaryColor: AppColors.primary,
      scaffoldBackgroundColor: AppColors.background,
      appBarTheme: AppBarTheme(
        backgroundColor: AppColors.primary,
        elevation: 0,
        centerTitle: true,
        titleTextStyle: AppTextStyles.appBarTitle,
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.border),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: AppColors.primary),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: Colors.red),
        ),
      ),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData.dark(useMaterial3: true);
  }
}
```

### 2. Responsive Design

```dart
// core/extensions/context_extensions.dart
extension ResponsiveExtension on BuildContext {
  bool get isMobile => MediaQuery.of(this).size.width < 600;
  
  bool get isTablet => 
      MediaQuery.of(this).size.width >= 600 &&
      MediaQuery.of(this).size.width < 1200;
  
  bool get isDesktop => MediaQuery.of(this).size.width >= 1200;

  double get screenWidth => MediaQuery.of(this).size.width;
  
  double get screenHeight => MediaQuery.of(this).size.height;

  double responsiveWidth(double width) {
    if (isMobile) return width;
    if (isTablet) return width * 0.8;
    return width * 0.6;
  }
}
```

### 3. Dialog & Snackbar Utilities

```dart
// core/utils/dialogs/app_dialogs.dart
class AppDialogs {
  static Future<void> showLoading({String message = 'Loading...'}) {
    return Get.dialog(
      WillPopScope(
        onWillPop: () async => false,
        child: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(),
              const SizedBox(height: 16),
              Text(message),
            ],
          ),
        ),
      ),
      barrierDismissible: false,
    );
  }

  static void hideLoading() {
    if (Get.isDialogOpen == true) {
      Get.back();
    }
  }

  static Future<bool?> showConfirmDialog({
    required String title,
    required String message,
    String confirmText = 'Yes',
    String cancelText = 'No',
  }) {
    return Get.dialog<bool>(
      AlertDialog(
        title: Text(title),
        content: Text(message),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: Text(cancelText),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: Text(confirmText),
          ),
        ],
      ),
    );
  }

  static void showError(String message) {
    AppSnackbars.showError(message);
  }

  static void showSuccess(String message) {
    AppSnackbars.showSuccess(message);
  }
}

class AppSnackbars {
  static const int _duration = 2;

  static void showError(String message) {
    Get.snackbar(
      'Error',
      message,
      backgroundColor: Colors.red,
      colorText: Colors.white,
      duration: const Duration(seconds: _duration),
      snackPosition: SnackPosition.BOTTOM,
    );
  }

  static void showSuccess(String message) {
    Get.snackbar(
      'Success',
      message,
      backgroundColor: Colors.green,
      colorText: Colors.white,
      duration: const Duration(seconds: _duration),
      snackPosition: SnackPosition.BOTTOM,
    );
  }

  static void showInfo(String message) {
    Get.snackbar(
      'Info',
      message,
      backgroundColor: Colors.blue,
      colorText: Colors.white,
      duration: const Duration(seconds: _duration),
      snackPosition: SnackPosition.BOTTOM,
    );
  }
}
```

---

## Dependencies (pubspec.yaml)

```yaml
name: flutter_app
description: Production-ready Flutter app with GetX and Clean Architecture

environment:
  sdk: '>=3.0.0 <4.0.0'
  flutter: '>=3.10.0'

dependencies:
  flutter:
    sdk: flutter

  # State Management & Navigation
  get: ^4.6.6

  # Network requests
  dio: ^5.4.0
  pretty_dio_logger: ^1.3.1

  # Local storage
  get_storage: ^2.1.2
  hive: ^2.2.3
  hive_flutter: ^1.1.0

  # Serialization
  json_annotation: ^4.8.1
  freezed_annotation: ^2.4.1

  # Utility packages
  intl: ^0.19.0
  uuid: ^4.1.0

  # UI/UX
  cached_network_image: ^3.3.1
  shimmer: ^3.0.0
  flutter_spinkit: ^5.2.1
  lottie: ^2.7.0

  # Date/Time handling
  timeago: ^3.6.1

  # Logging
  logger: ^2.1.0

dev_dependencies:
  flutter_test:
    sdk: flutter

  flutter_lints: ^3.0.0

  # Code generation
  build_runner: ^2.4.9
  json_serializable: ^6.7.1
  freezed: ^2.4.5

flutter:
  uses-material-design: true
  assets:
    - assets/images/
    - assets/icons/
    - assets/animations/
  fonts:
    - family: Poppins
      fonts:
        - asset: assets/fonts/Poppins-Regular.ttf
        - asset: assets/fonts/Poppins-Bold.ttf
          weight: 700
        - asset: assets/fonts/Poppins-SemiBold.ttf
          weight: 600
```

---

## Code Quality Standards

### 1. Naming Conventions

```
✓ ServiceClass / Repository / Controller naming: PascalCase
✓ Files: snake_case.dart
✓ Variables & methods: camelCase
✓ Constants: CONSTANT_CASE or camelCase for private
✓ Widget files: lowercase_with_underscores.dart
✓ Controllers: *_controller.dart
✓ Models: *_model.dart
✓ Entities: *_entity.dart
✓ Routes: app_routes.dart
```

### 2. Code Organization

```dart
// Import order
import 'dart:async';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'relative/imports.dart';

// Class structure
class ClassName {
  // 1. Constants
  static const String constant = 'value';

  // 2. Static variables
  static int staticVariable = 0;

  // 3. Instance variables
  final String instanceVariable;
  late String lateVariable;

  // 4. Getters
  String get computedValue => instanceVariable;

  // 5. Constructors
  ClassName({required this.instanceVariable});

  // 6. Lifecycle methods (GetxController)
  @override
  void onInit() {
    super.onInit();
  }

  @override
  void onClose() {
    super.onClose();
  }

  // 7. Public methods
  void publicMethod() {}

  // 8. Private methods
  String _privateMethod() => '';
}
```

### 3. Dart Analysis Rules

```yaml
# analysis_options.yaml
linter:
  rules:
    - camel_case_extensions
    - camel_case_types
    - constant_identifier_names
    - directives_ordering
    - empty_catches
    - file_names
    - library_names
    - library_prefixes
    - non_constant_identifier_names
    - prefer_adjacent_string_concatenation
    - prefer_const_constructors
    - prefer_final_fields
    - prefer_final_locals
    - prefer_single_quotes
    - sized_box_shrink
    - sort_pub_dependencies
    - type_init_formals
    - unnecessary_await_in_return
    - unnecessary_brace_in_string_interps
    - unnecessary_const
    - unnecessary_constructor_name
    - unnecessary_getters_setters
    - unnecessary_lambdas
    - unnecessary_new
    - unnecessary_string_escapes
    - unnecessary_string_interpolations
    - unnecessary_to_list_in_spreads
    - use_full_hex_values_for_flutter_colors
    - use_key_in_widget_constructors
    - use_raw_strings
    - use_setters_to_change_properties
    - use_string_buffers
    - use_test_throws_matchers
    - use_to_close_resource
```

### 4. Documentation Standards

```dart
/// Comprehensive documentation for public APIs
/// 
/// This is a detailed description of what this method does.
/// 
/// **Parameters:**
/// - [itemId]: The unique identifier of the item
/// - [name]: The name of the item (max 255 characters)
/// 
/// **Returns:** 
/// Returns a [Future<ItemEntity>] containing the updated item,
/// or throws [AppException] if operation fails
/// 
/// **Example:**
/// ```dart
/// final updatedItem = await itemService.updateItem(1, 'New Name');
/// ```
Future<ItemEntity> updateItem(int itemId, String name) async {
  // Implementation
}
```

---

## Development Workflow

### 1. Creating a New Feature

```
1. Create feature folder: features/feature_name/
2. Create subfolders: bindings, controllers, data, domain, presentation
3. Implement layers: domain → data → presentation
4. Create binding and register in AppBinding
5. Add routes in app_routes.dart and app_pages.dart
6. Create models, entities, repositories
7. Create controller with Rx variables and logic
8. Create pages and widgets
9. Test all flows
```

### 2. Best Practices Checklist

```
API Integration:
☐ Use abstract repositories in domain
☐ Implement repositories in data layer
☐ Use datasources for API calls
☐ Handle all exceptions properly
☐ Add token refresh mechanism
☐ Implement logging

State Management:
☐ Use Rx variables for reactive updates
☐ Implement onClose() for cleanup
☐ Use workers for side effects
☐ Avoid direct state manipulation
☐ Use Obx() for UI updates

UI/UX:
☐ Implement proper error handling
☐ Show loading states
☐ Add user feedback (snackbars/dialogs)
☐ Use responsive design
☐ Handle empty states
☐ Implement proper pagination

Code Quality:
☐ Follow naming conventions
☐ Add documentation
☐ Keep methods focused and small
☐ Use extensions for common operations
☐ Handle edge cases
☐ Test with different screen sizes
```

---

## Testing Recommendations

While unit tests are not included in this prompt, implement the following structure when ready:

```
test/
├── features/
│   ├── auth/
│   │   ├── controllers/
│   │   │   └── auth_controller_test.dart
│   │   ├── data/
│   │   │   ├── datasources/
│   │   │   │   └── auth_remote_datasource_test.dart
│   │   │   └── repositories/
│   │   │       └── auth_repository_test.dart
│   │   └── domain/
│   │       └── usecases/ (if applicable)
│   └── items/
│       └── ...
└── core/
    ├── network/
    │   └── api_client_test.dart
    └── storage/
        └── token_storage_test.dart
```

---

## Summary of Key Architecture Principles

1. **Clean Architecture**: Separation of concerns across domain, data, and presentation layers
2. **SOLID Principles**: Single responsibility, dependency injection, interface segregation
3. **Reactive Programming**: GetX Rx variables and Obx for UI reactivity
4. **Modular Design**: Feature-based structure for scalability
5. **Error Handling**: Custom exceptions and comprehensive error management
6. **Code Reusability**: Extensions, utilities, and widget composition
7. **State Management**: Controllers handle business logic, widgets handle UI
8. **Security**: Token management and secure storage
9. **Performance**: Caching, pagination, and lazy loading
10. **User Experience**: Loading states, error messages, and smooth animations

---

**Generated:** February 19, 2026  
**Framework:** Flutter + GetX  
**Architecture:** Clean Architecture with Feature-Based Modules  
**Code Style:** SOLID Principles & Clean Code Standards
