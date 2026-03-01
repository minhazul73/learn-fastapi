# FastAPI Backend Architecture Guide for Mobile App Development

## Project Overview

This is a **production-ready FastAPI backend** designed specifically for mobile applications (Flutter, React Native, native iOS/Android). It provides a complete authentication & CRUD system with enterprise-grade patterns.

**Key Characteristics:**
- Framework: FastAPI with async/await (SQLAlchemy 2.0 + asyncpg)
- Database: PostgreSQL with Alembic migrations
- Authentication: JWT with access/refresh token pattern
- API Versioning: `/api/v1/` URL prefix for backward compatibility
- Response Format: Standardized JSON responses across all endpoints
- Deployment: Docker containerized, Render.com ready (free tier compatible)
- Development: Hot-reload development server with auto-documentation

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│           MOBILE APP (Flutter / React Native)       │
│  ┌──────────────────────────────────────────────┐   │
│  │  HTTP Client (Dio/Http/Retrofit equivalent)  │   │
│  │  - Interceptors (auth token injection)       │   │
│  │  - Response parsing & error handling         │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
                         ↕ HTTPS
┌─────────────────────────────────────────────────────┐
│     FastAPI Application (Python 3.10+)              │
├─────────────────────────────────────────────────────┤
│  ROUTING LAYER                                      │
│  ├── /api/v1/health ..................... Health   │
│  ├── /api/v1/auth ................. Authentication  │
│  ├── /api/v1/items ................... CRUD Items  │
│                                                     │
│  DEPENDENCY INJECTION & SECURITY                   │
│  ├── get_db() ........................ DB Session  │
│  ├── get_current_user() ................... JWT    │
│                                                     │
│  BUSINESS LOGIC LAYER (Services)                   │
│  ├── AuthService ................. User Auth & JWT │
│  ├── ItemService ................... Item CRUD    │
│                                                     │
│  DATA MODELS (SQLAlchemy ORM)                      │
│  ├── User ........................ Email, Password  │
│  ├── Item .................. Name, Price, Metadata │
│                                                     │
│  RESPONSE STANDARDIZATION                          │
│  ├── success_response() ........... Successful ops │
│  ├── list_response() .......... List with pagination
│  ├── error_response() ............. Standard errors│
│                                                     │
│  SECURITY & EXCEPTIONS                             │
│  ├── JWT Encoding/Decoding ......... python-jose  │
│  ├── Password Hashing ............. bcrypt        │
│  ├── Custom Exception Handlers ... Unified errors │
└─────────────────────────────────────────────────────┘
                         ↕
┌─────────────────────────────────────────────────────┐
│      PostgreSQL Database + Connection Pool         │
│  (Async with asyncpg driver)                       │
└─────────────────────────────────────────────────────┘
```

---

## API Endpoints Complete Reference

### 1. HEALTH CHECK ENDPOINT

**Purpose:** Monitor service availability and database connectivity. Used by load balancers and container orchestration.

```
GET /api/v1/health
```

**Response (200 if healthy):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "Health check completed",
  "table_name": "",
  "data": {
    "status": "healthy",
    "environment": "prod",
    "version": "0.1.0",
    "database": "ok"
  }
}
```

**Response (503 if degraded):**
```json
{
  "success": true,
  "response_code": 503,
  "message": "Health check completed",
  "table_name": "",
  "data": {
    "status": "degraded",
    "environment": "prod",
    "version": "0.1.0",
    "database": "unreachable"
  }
}
```

**Use Cases:**
- Kubernetes/container health probes
- Load balancer checks
- Monitoring dashboards (Datadog, New Relic, etc.)
- Mobile app features requiring connectivity check

---

### 2. AUTHENTICATION ENDPOINTS

#### 2.1 Register New User

```
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "response_code": 201,
  "message": "User registered successfully",
  "table_name": "",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Error Responses:**
- `409 Conflict`: Email already registered
- `422 Unprocessable Entity`: Invalid email format or missing fields

**Mobile Implementation Notes:**
- Validate email format client-side before sending
- Store both tokens securely (encrypted SharedPreferences in Flutter)
- Use refresh_token for long-term authentication
- Typical flow: Show confirmation screen → Navigate to login

---

#### 2.2 User Login

```
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "Login successful",
  "table_name": "",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid email or password
- `422 Unprocessable Entity`: Invalid request format

**Token Structure (JWT HS256):**
```
Header: { "alg": "HS256", "typ": "JWT" }
Payload: {
  "sub": "123",        // user_id as string
  "type": "access",    // token type
  "exp": 1645000000    // expiration (30 minutes)
}
Signature: HMAC-SHA256(SECRET_KEY)
```

**Mobile Implementation Notes:**
- Implement network request timeout (15-30 seconds)
- Show loading state during login
- Cache user ID from token for local profile display
- Implement biometric login using refresh token (optional)

---

#### 2.3 Refresh Access Token

```
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "Token refreshed successfully",
  "table_name": "",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired refresh token

**Token Expiration:**
- Access Token: 30 minutes (configurable)
- Refresh Token: 7 days (configurable)

**Mobile Implementation Notes:**
- Call this endpoint when access_token expires (before or on 401)
- Implement automatic token refresh in HTTP interceptor
- Store refresh_token in encrypted storage, access_token in memory
- Implement logout when refresh token expires

---

#### 2.4 Get Current User Profile

```
GET /api/v1/auth/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response (200 OK):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "User data retrieved successfully",
  "table_name": "",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid token
- `404 Not Found`: User not found (user deleted while logged in)

**Mobile Implementation Notes:**
- Call on app startup to verify existing session
- Display in user profile/settings screen
- Use for server-side email confirmation check

---

### 3. ITEMS CRUD ENDPOINTS

#### 3.1 List All Items (Paginated)

```
GET /api/v1/items?page_no=1&per_page=10
```

**Query Parameters:**
- `page_no` (integer, ≥1, default=1): Page number (1-indexed)
- `per_page` (integer, 1-200, default=10): Items per page

**Response (200 OK):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "Items fetched successfully",
  "table_name": "items",
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "last_page": 5,
    "total": 47
  },
  "data": [
    {
      "id": 1,
      "name": "Laptop",
      "description": "High-performance computing device",
      "price": 999.99,
      "tax": 99.99,
      "created_at": "2025-01-15T10:30:00Z",
      "updated_at": "2025-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Mouse",
      "description": "Wireless mouse",
      "price": 29.99,
      "tax": 2.99,
      "created_at": "2025-01-16T14:22:00Z",
      "updated_at": "2025-01-16T14:22:00Z"
    }
  ]
}
```

**Mobile Implementation Notes:**
- No authentication required for public items
- Implement pagination with next/previous buttons or infinite scroll
- Show total count in UI: "Showing 10 of 47 items"
- Cache items locally with last_update timestamp
- Implement pull-to-refresh for data sync

---

#### 3.2 Get Single Item by ID

```
GET /api/v1/items/{item_id}
```

**Path Parameters:**
- `item_id` (integer): Item database ID

**Response (200 OK):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "Item fetched successfully",
  "table_name": "items",
  "data": {
    "id": 1,
    "name": "Laptop",
    "description": "High-performance computing device",
    "price": 999.99,
    "tax": 99.99,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
  }
}
```

**Error Responses:**
- `404 Not Found`: Item with this ID doesn't exist

**Mobile Implementation Notes:**
- Show loading skeleton while fetching
- Display creation and last modified timestamps
- Implement local caching for frequently viewed items
- Handle network errors gracefully

---

#### 3.3 Create New Item (Authenticated)

```
POST /api/v1/items
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Keyboard",
  "description": "Mechanical keyboard",
  "price": 150.00,
  "tax": 15.00
}
```

**Request Schema:**
```python
{
  "name": str (required, max 255 chars),
  "description": str | null (optional, unlimited length),
  "price": float (required, must be ≥ 0),
  "tax": float | null (optional, default 0.0)
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "response_code": 201,
  "message": "Item created successfully",
  "table_name": "items",
  "data": {
    "id": 3,
    "name": "Keyboard",
    "description": "Mechanical keyboard",
    "price": 150.00,
    "tax": 15.00,
    "created_at": "2025-02-19T12:45:00Z",
    "updated_at": "2025-02-19T12:45:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication token
- `422 Unprocessable Entity`: Validation error (invalid price, missing name, etc.)

**Mobile Implementation Notes:**
- Require authentication (login first)
- Validate inputs client-side before sending
- Disable submit button while request is in flight
- Show optimistic UI updates for better UX
- Implement offline queue for items created without internet

---

#### 3.4 Bulk Create Items (Authenticated)

```
POST /api/v1/items/bulk/import
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

[
  {
    "name": "Monitor",
    "description": "4K Ultra HD",
    "price": 450.00,
    "tax": 45.00
  },
  {
    "name": "USB Cable",
    "description": "USB-C charging cable",
    "price": 15.00,
    "tax": 1.50
  },
  {
    "name": "Webcam",
    "description": null,
    "price": 99.99,
    "tax": 10.00
  }
]
```

**Response (201 Created):**
```json
{
  "success": true,
  "response_code": 201,
  "message": "3 items created successfully",
  "table_name": "items",
  "data": [
    {
      "id": 4,
      "name": "Monitor",
      "description": "4K Ultra HD",
      "price": 450.00,
      "tax": 45.00,
      "created_at": "2025-02-19T13:00:00Z",
      "updated_at": "2025-02-19T13:00:00Z"
    },
    {
      "id": 5,
      "name": "USB Cable",
      "description": "USB-C charging cable",
      "price": 15.00,
      "tax": 1.50,
      "created_at": "2025-02-19T13:00:00Z",
      "updated_at": "2025-02-19T13:00:00Z"
    },
    {
      "id": 6,
      "name": "Webcam",
      "description": null,
      "price": 99.99,
      "tax": 10.00,
      "created_at": "2025-02-19T13:00:00Z",
      "updated_at": "2025-02-19T13:00:00Z"
    }
  ]
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication
- `422 Unprocessable Entity`: One or more items have validation errors (entire request fails)

**Mobile Implementation Notes:**
- Use for CSV import or bulk item entry features
- Validate all items client-side first
- Show progress indication for large imports
- Implement transaction-like behavior (all-or-nothing)
- The API automatically returns created items with generated IDs

---

#### 3.5 Update Item (Authenticated)

```
PUT /api/v1/items/{item_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "name": "Gaming Laptop",
  "price": 1299.99
}
```

**Path Parameters:**
- `item_id` (integer): Item to update

**Request Schema (All fields optional):**
```python
{
  "name": str | null (optional),
  "description": str | null (optional),
  "price": float | null (optional),
  "tax": float | null (optional)
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "response_code": 200,
  "message": "Item updated successfully",
  "table_name": "items",
  "data": {
    "id": 1,
    "name": "Gaming Laptop",
    "description": "High-performance computing device",
    "price": 1299.99,
    "tax": 129.99,
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-02-19T14:15:00Z"
  }
}
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Item doesn't exist
- `422 Unprocessable Entity`: Invalid field values

**Mobile Implementation Notes:**
- Only changed fields need to be sent (true PATCH behavior)
- Update timestamps are automatically updated server-side
- Show before/after values for confirmation
- Implement optimistic UI updates with rollback on error
- Warn user if item has been modified by others since last fetch

---

#### 3.6 Delete Item (Authenticated)

```
DELETE /api/v1/items/{item_id}
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Path Parameters:**
- `item_id` (integer): Item to delete

**Response (204 No Content):**
```
(Empty body, just HTTP 204 status)
```

**Error Responses:**
- `401 Unauthorized`: Missing or invalid authentication
- `404 Not Found`: Item doesn't exist

**Mobile Implementation Notes:**
- Show confirmation dialog before deletion
- Implement undo functionality with local cache
- Remove from UI immediately (optimistic delete)
- Show error toast if deletion fails
- Disable delete button while request is in flight

---

## Data Models & Database Schema

### User Model

```python
class User:
    id: int                          # Primary key, auto-increment
    email: str                       # Unique, indexed, email validation
    hashed_password: str             # bcrypt hashed, never stored plaintext
    is_active: bool                  # Account status flag
    is_superuser: bool               # Admin flag
    created_at: datetime             # Auto-set on creation
    updated_at: datetime             # Auto-updated on modification
```

**Constraints:**
- Email must be unique across all users
- Email must be valid email format
- Password must be SHA256 hashed with bcrypt (cost factor 12)

---

### Item Model

```python
class Item:
    id: int                          # Primary key, auto-increment
    name: str                        # Required, max 255 characters
    description: str | null          # Optional, unlimited length
    price: float                     # Required, non-negative
    tax: float | null                # Optional, default 0.0
    created_at: datetime             # Auto-set on creation
    updated_at: datetime             # Auto-updated on modification
```

**Constraints:**
- Name is required and indexed for search performance
- Price must be non-negative (validated on creation/update)
- No soft deletes in this MVP (items are hard-deleted)

**Indexes for Performance:**
- `items.id` (primary key)
- `items.name` (for full-text search, future feature)

---

## Response Format Standard

All API responses follow this standardized format:

### Success Response

```json
{
  "success": true,
  "response_code": 200,
  "message": "Human-readable operation result",
  "table_name": "items",
  "pagination": null,
  "data": {
    // Response data object or array
  }
}
```

### Error Response

```json
{
  "success": false,
  "response_code": 400,
  "message": "Descriptive error message",
  "table_name": "",
  "data": null
}
```

### Paginated List Response

```json
{
  "success": true,
  "response_code": 200,
  "message": "Items fetched successfully",
  "table_name": "items",
  "pagination": {
    "current_page": 1,
    "per_page": 10,
    "last_page": 5,
    "total": 47
  },
  "data": [
    // Array of items
  ]
}
```

**Field Explanations:**
- `success` (bool): Operation success/failure
- `response_code` (int): HTTP status code
- `message` (str): Human-readable message for UI display
- `table_name` (str): Database table affected (empty for errors)
- `pagination` (object): Only present on list endpoints
  - `current_page`: Current page (1-indexed)
  - `per_page`: Items returned in this response
  - `last_page`: Total number of pages
  - `total`: Total items across all pages
- `data` (any): Actual response payload

---

## Authentication & Security

### JWT Token Flow

1. **Registration/Login** → Server returns `access_token` + `refresh_token`
2. **Subsequent Requests** → Include `access_token` in Authorization header
3. **Token Expiry** → Use `refresh_token` to get new `access_token`
4. **Logout** → Delete tokens from client storage

### Token Details

```
Authorization: Bearer <access_token>
```

**Access Token:**
- Valid for: 30 minutes
- Used for: API requests
- Storage: In-memory (app variable)
- Lost on app restart ✓ (intentional for security)

**Refresh Token:**
- Valid for: 7 days
- Used for: Getting new access tokens
- Storage: Encrypted persistent storage
- Survives app restart

**Token Payload Example:**
```python
{
  "sub": "123",              # user ID as string
  "type": "access",          # or "refresh"
  "iat": 1645000000,         # issued at timestamp
  "exp": 1645001800          # expiration timestamp
}
```

### Password Security

- Algorithm: bcrypt (cost factor 12)
- Never stored plaintext
- Verified using constant-time comparison
- On registration: hashed and stored
- On login: input hashed and compared to stored hash

### HTTP Security Headers

- CORS enabled (configurable origins)
- Trusted Host validation in production
- Secure cookies recommended (client-side implementation)

---

## Error Handling

### HTTP Status Codes Used

| Code | Scenario | Example |
|------|----------|---------|
| 200 | Successful GET, POST (refresh) | Login successful |
| 201 | Successful POST/create | Item created |
| 204 | Successful DELETE | Item deleted |
| 400 | Bad request | Invalid JSON |
| 401 | Unauthorized | Invalid token, not logged in |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not found | Item doesn't exist |
| 409 | Conflict | Email already registered |
| 422 | Validation error | Invalid email format |
| 500 | Server error | Database connection failed |
| 503 | Service unavailable | Database unreachable |

### Error Response Format

```json
{
  "success": false,
  "response_code": 401,
  "message": "Invalid or expired token",
  "table_name": "",
  "data": null
}
```

### Common Error Scenarios

**Email Already Registered:**
```
POST /api/v1/auth/register
Status: 409 Conflict
Message: "Email already registered"
```

**Invalid Credentials:**
```
POST /api/v1/auth/login
Status: 401 Unauthorized
Message: "Invalid email or password"
```

**Missing Authentication:**
```
GET /api/v1/items (with auth required)
Status: 401 Unauthorized
Message: "Not authenticated"
```

**Item Not Found:**
```
GET /api/v1/items/99999
Status: 404 Not Found
Message: "Item not found"
```

**Validation Error:**
```
POST /api/v1/items
Status: 422 Unprocessable Entity
Message: "Validation details..." (auto-generated by Pydantic)
```

---

## Building a Flutter App with These APIs

### Architecture Pattern

```
Flutter App
├── Presentation Layer (Screens, Widgets)
├── State Management (Provider, Riverpod, BLoC)
├── Repository Layer (Data abstraction)
├── Service Layer
│   ├── AuthService
│   │   └── Uses token management
│   ├── ItemService
│   │   └── CRUD operations
│   └── ApiService (HTTP client)
│       ├── Interceptors (add auth tokens)
│       ├── Error handling
│       └── Response parsing
└── Local Storage (Hive, SharedPreferences)
    ├── Tokens
    ├── User data
    └── Cache

Database Connection
PostgreSQL
```

### Required HTTP Client Package

```yaml
dependencies:
  dio: ^5.0.0              # HTTP client with interceptors
  secure_storage: ^9.0.0   # Encrypted token storage
  freezed_annotation: ^2.0.0  # DTO generation
```

### Token Management Implementation

```dart
class ApiService extends DioMixin with HttpClientMixin implements Dio {
  ApiService({required this.baseUrl, required this.tokenService}) {
    interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          /// Add access token to every request
          final token = await tokenService.getAccessToken();
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          return handler.next(options);
        },
        onError: (error, handler) async {
          /// Handle 401: refresh token
          if (error.response?.statusCode == 401) {
            final refreshed = await tokenService.refreshToken();
            if (refreshed) {
              // Retry original request
              final newToken = await tokenService.getAccessToken();
              error.requestOptions.headers['Authorization'] = 'Bearer $newToken';
              return handler.resolve(await fetch(error.requestOptions));
            }
          }
          return handler.next(error);
        },
      ),
    );
  }
}
```

### Authentication Flow Example

```dart
class AuthService {
  Future<void> register(String email, String password) async {
    final response = await apiService.post('/auth/register', data: {
      'email': email,
      'password': password,
    });
    
    final tokens = response.data['data'];
    await tokenService.saveTokens(tokens);
    await userService.setCurrentUser(userId: extractUserId(tokens));
  }

  Future<void> login(String email, String password) async {
    final response = await apiService.post('/auth/login', data: {
      'email': email,
      'password': password,
    });
    
    final tokens = response.data['data'];
    await tokenService.saveTokens(tokens);
    await userService.setCurrentUser(userId: extractUserId(tokens));
  }

  Future<void> logout() async {
    await tokenService.clearTokens();
    await userService.clearCurrentUser();
  }
}
```

### Items CRUD Example

```dart
class ItemService {
  // List with pagination
  Future<PaginatedResponse<Item>> getItems({
    int page = 1,
    int perPage = 10,
  }) async {
    final response = await apiService.get('/items', queryParameters: {
      'page_no': page,
      'per_page': perPage,
    });
    
    final data = response.data['data'];
    final pagination = response.data['pagination'];
    
    return PaginatedResponse(
      items: List<Item>.from(data.map((x) => Item.fromJson(x))),
      pagination: Pagination.fromJson(pagination),
    );
  }

  // Get single item
  Future<Item> getItem(int id) async {
    final response = await apiService.get('/items/$id');
    return Item.fromJson(response.data['data']);
  }

  // Create item
  Future<Item> createItem(ItemCreate data) async {
    final response = await apiService.post('/items', data: data.toJson());
    return Item.fromJson(response.data['data']);
  }

  // Update item
  Future<Item> updateItem(int id, ItemUpdate data) async {
    final response = await apiService.put('/items/$id', data: data.toJson());
    return Item.fromJson(response.data['data']);
  }

  // Delete item
  Future<void> deleteItem(int id) async {
    await apiService.delete('/items/$id');
  }

  // Bulk create
  Future<List<Item>> bulkCreateItems(List<ItemCreate> items) async {
    final response = await apiService.post('/items/bulk/import', 
      data: items.map((x) => x.toJson()).toList(),
    );
    return List<Item>.from(
      response.data['data'].map((x) => Item.fromJson(x))
    );
  }
}
```

### Model Generation (Freezed)

```dart
import 'package:freezed_annotation/freezed_annotation.dart';

part 'item.freezed.dart';
part 'item.g.dart';

@freezed
class Item with _$Item {
  const factory Item({
    required int id,
    required String name,
    String? description,
    required double price,
    double? tax,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _Item;

  factory Item.fromJson(Map<String, dynamic> json) => _$ItemFromJson(json);
}

@freezed
class ItemCreate with _$ItemCreate {
  const factory ItemCreate({
    required String name,
    String? description,
    required double price,
    double? tax,
  }) = _ItemCreate;

  factory ItemCreate.fromJson(Map<String, dynamic> json) => 
    _$ItemCreateFromJson(json);
}
```

### Error Handling Pattern

```dart
class ApiResponseHandler {
  static Future<T> handle<T>(Future<Response> request) async {
    try {
      final response = await request;
      final data = response.data as Map<String, dynamic>;
      
      if (data['success'] == true) {
        return data['data'] as T;
      } else {
        throw ApiException(
          message: data['message'],
          statusCode: data['response_code'],
        );
      }
    } on DioException catch (e) {
      throw ApiException(
        message: e.message ?? 'Network error',
        statusCode: e.response?.statusCode,
      );
    }
  }
}

class ApiException implements Exception {
  final String message;
  final int? statusCode;

  ApiException({required this.message, this.statusCode});

  bool get isUnauthorized => statusCode == 401;
  bool get isNotFound => statusCode == 404;
  bool get isValidationError => statusCode == 422;

  @override
  String toString() => 'ApiException($statusCode): $message';
}
```

---

## Configuration & Environment Variables

### Development Environment (.env.dev)

```env
APP_NAME=MyApp API
APP_VERSION=0.1.0
ENVIRONMENT=dev
DEBUG=True

HOST=0.0.0.0
PORT=8000
WORKERS=1

DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/myapp_dev
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=0

SECRET_KEY=dev-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["http://localhost:3000", "http://localhost:8081"]
```

### Production Environment (.env.prod)

```env
APP_NAME=MyApp API
APP_VERSION=0.1.0
ENVIRONMENT=prod
DEBUG=False

HOST=0.0.0.0
PORT=8000
WORKERS=4

DATABASE_URL=postgresql+asyncpg://[user]:[password]@[host]:[port]/[db]
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=3

SECRET_KEY=[generate-with-openssl-rand-hex-32]
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

CORS_ORIGINS=["https://app.example.com"]
```

**Generate Secure Secret Key:**
```bash
openssl rand -hex 32
# Output: a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

---

## Deployment & DevOps

### Docker Build & Run

```bash
# Build image
docker build -t myapp-api:latest .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/myapp \
  -e SECRET_KEY=your-secret-key \
  myapp-api:latest

# With docker-compose
docker-compose up --build
```

### Database Migrations (Alembic)

```bash
# Create migration
alembic revision --autogenerate -m "Add new column"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

### Production Deployment Checklist

- [ ] Generate new SECRET_KEY (not default "CHANGE-ME")
- [ ] Set ENVIRONMENT=prod
- [ ] Set CORS_ORIGINS to actual domain(s)
- [ ] Disable DEBUG mode
- [ ] Configure PostgreSQL with backups
- [ ] Set up monitoring (Datadog, New Relic)
- [ ] Configure log aggregation
- [ ] Set up health check endpoint with load balancer
- [ ] Enable HTTPS/SSL certificate
- [ ] Configure rate limiting (use nginx reverse proxy)
- [ ] Set up automated database backups
- [ ] Create admin user for monitoring

---

## Performance & Scaling

### Load Handling

| Metric | Default | Optimized |
|--------|---------|-----------|
| Workers | 1 | 2-4 (Render) |
| DB Pool | 5 | 10 (Render) |
| Memory | ~300MB | ~150MB per worker |
| Requests/sec | ~50 | ~200+ |

### Optimization Tips

1. **Database Indexing**: Add indexes on frequently queried fields (email, item.name)
2. **Caching**: Implement Redis for session storage and rate limiting
3. **Pagination**: Always paginate large result sets (max 200 items/page)
4. **Compression**: Enable gzip compression in nginx
5. **Connection Pooling**: asyncpg handles this automatically
6. **Query Optimization**: Use select() with specific columns, not full ORM objects

### Monitoring Queries

```bash
# Check active connections
SELECT count(*) FROM pg_stat_activity WHERE datname = 'myapp';

# Check slow queries
SELECT query, mean_time FROM pg_stat_statements 
  WHERE mean_time > 100 
  ORDER BY mean_time DESC;

# Database size
SELECT pg_size_pretty(pg_database_size('myapp'));
```

---

## Development Workflow

### Local Setup

```bash
# Clone repository
git clone <repo>
cd learn-fastapi

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment
cp .env.example .env

# Start database
docker-compose up -d db

# Apply migrations
alembic upgrade head

# Run development server
uvicorn app.main:app --reload
```

### Running Tests (Note: No tests in MVP)

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### API Documentation

- **Swagger UI**: http://localhost:8000/docs (dev only)
- **ReDoc**: http://localhost:8000/redoc (dev only)
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Future Enhancements

### Immediate (Next Sprint)

- [ ] Add email verification on registration
- [ ] Implement password reset flow
- [ ] Add user profile update endpoint (PATCH /auth/me)
- [ ] Add item search/filtering
- [ ] Add soft deletes for items

### Medium Term

- [ ] Two-factor authentication (TOTP)
- [ ] OAuth2 integration (Google, Apple Sign-In)
- [ ] WebSocket for real-time item updates
- [ ] File upload (images for items)
- [ ] Full-text search on items
- [ ] Audit logging (who created/modified items)

### Long Term

- [ ] Multi-tenant support
- [ ] GraphQL API alongside REST
- [ ] Machine learning recommendations
- [ ] Mobile push notifications
- [ ] Advanced analytics dashboard

---

## Quick Reference: cURL Examples

### Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

### Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Create Item

```bash
curl -X POST http://localhost:8000/api/v1/items \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "tax": 99.99
  }'
```

### List Items

```bash
curl http://localhost:8000/api/v1/items?page_no=1&per_page=10
```

### Get Single Item

```bash
curl http://localhost:8000/api/v1/items/1
```

### Update Item

```bash
curl -X PUT http://localhost:8000/api/v1/items/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Gaming Laptop",
    "price": 1299.99
  }'
```

### Delete Item

```bash
curl -X DELETE http://localhost:8000/api/v1/items/1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

---

## Questions & Support

**For Architecture Decisions:**
- See README.md for high-level design rationale
- Review RESPONSE_FORMAT.md for standardized response documentation

**For Deployment:**
- See RENDER_DEPLOYMENT.md for step-by-step production deployment

**For Database Migrations:**
- Check alembic/versions/ for migration history
- Use `alembic current` to check applied version

---

**Document Version:** 1.0  
**Last Updated:** February 19, 2026  
**Created For:** AI Agent Development (Flutter App Architecture)
