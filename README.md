# Sentinel Inventory Pro API

## Overview
Sentinel Inventory Pro is a high-integrity inventory management system designed for businesses that require strict oversight and predictive restocking.
This API allows you to manage inventory items, categories, stock movements, and restock alerts with full audit logging and role-based access control.

Base URL
https://sentinelinventorypro-api.onrender.com/api/

## Authentication
The API uses JWT (JSON Web Tokens) for authentication.
To access protected endpoints, you must include an Authorization header with a valid access token:

Authorization: Bearer <your_access_token>

### Obtain Token
POST /auth/login/
Authenticates a user and returns access and refresh tokens.

Request body
{
  "username": "your_username",
  "password": "your_password"
}

Response
{
  "refresh": "eyJ0eXAiOiJKV1Qi...",
  "access": "eyJ0eXAiOiJKV1Qi..."
}

### Refresh Token
POST /auth/refresh/
Obtain a new access token using a valid refresh token.

Request body
{
  "refresh": "eyJ0eXAiOiJKV1Qi..."
}

Response
{
  "access": "eyJ0eXAiOiJKV1Qi..."
}

### Register a New User
POST /auth/register/
Creates a new user account. This endpoint is publicly accessible.

Request body
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}

Response
{
  "id": 5,
  "username": "newuser",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe"
}

## Roles & Permissions
The API defines three built-in roles. Permissions are enforced per endpoint.

Role         Description
Viewer       Read-only access to all resources (items, categories, movements, alerts).
Stocker      Viewer permissions + can create/update items, categories, and stock movements.
Admin        Full access, including deletion and audit logs.

If a user does not have the required role, the API returns a 403 Forbidden error.

## Endpoints

### Categories
Method  Endpoint                 Description                Required Role
GET     /categories/             List all categories        Viewer
POST    /categories/             Create a new category      Stocker
GET     /categories/{id}/        Retrieve a category        Viewer
PUT     /categories/{id}/        Update a category          Stocker
PATCH   /categories/{id}/        Partially update a category Stocker
DELETE  /categories/{id}/        Delete a category          Admin

Example – List categories
GET /categories/
Response
[
  {
    "id": 1,
    "name": "Electronics",
    "description": "Gadgets and devices"
  }
]

Example – Create category
POST /categories/
Request
{
  "name": "Books",
  "description": "Reading materials"
}
Response
{
  "id": 2,
  "name": "Books",
  "description": "Reading materials"
}

### Items
Method  Endpoint                     Description                          Required Role
GET     /items/                      List items (filterable, searchable)  Viewer
POST    /items/                      Create a new item                    Stocker
GET     /items/{id}/                 Retrieve an item                     Viewer
PUT     /items/{id}/                 Update an item                       Stocker
PATCH   /items/{id}/                 Partially update an item             Stocker
DELETE  /items/{id}/                 Delete an item                       Admin
GET     /items/low_stock/            List items with quantity <= threshold Viewer
GET     /items/{id}/movements/       List stock movements for an item     Viewer
GET     /items/predictions/          List restock predictions for all items Viewer
GET     /items/{id}/prediction/      Get prediction for a specific item   Viewer

Item fields
{
  "sku": "LAP-001",
  "name": "Gaming Laptop",
  "description": "High performance",
  "category": 1,
  "category_detail": { ... },   // Nested category object (read-only)
  "price": 1299.99,
  "quantity": 10,
  "reorder_threshold": 3,
  "reorder_quantity": 5,
  "unit_of_measure": "units",
  "is_active": true,
  "created_at": "2025-01-01T00:00:00Z",
  "updated_at": "2025-01-02T00:00:00Z",
  "created_by": "admin",
  "updated_by": "admin"
}

Filtering & Search (on /items/)
- ?category=<id> – Filter by category ID.
- ?is_active=true – Show only active items.
- ?low_stock=true – Show items where quantity <= reorder threshold.
- ?search=<query> – Search by name or SKU.
- ?ordering=<field> – Sort by field (use -field for descending). Example: ?ordering=-price.

### Stock Movements
Method  Endpoint                     Description                  Required Role
GET     /stock-movements/            List all stock movements     Viewer
POST    /stock-movements/            Record a new movement        Stocker
GET     /stock-movements/{id}/       Retrieve a movement          Viewer

Movement types
- IN – stock received
- OUT – stock removed
- ADJUST – inventory adjustment

Example – Record stock out
POST /stock-movements/
Request
{
  "item": 1,
  "movement_type": "OUT",
  "quantity_change": -2,
  "reason": "Sale",
  "notes": "Customer order #123"
}
Response
{
  "id": 10,
  "item": 1,
  "item_detail": { ... },
  "user": "stocker",
  "movement_type": "OUT",
  "quantity_change": -2,
  "quantity_after": 8,
  "reason": "Sale",
  "notes": "Customer order #123",
  "created_at": "2025-01-03T10:30:00Z"
}

### Restock Alerts
Method  Endpoint                     Description                  Required Role
GET     /restock-alerts/             List all alerts              Viewer
GET     /restock-alerts/{id}/        Retrieve an alert            Viewer
PATCH   /restock-alerts/{id}/        Mark alert as resolved       Stocker

Example – Resolve alert
PATCH /restock-alerts/5/
Request
{
  "is_resolved": true
}
Response
{
  "id": 5,
  "item": 1,
  "item_detail": { ... },
  "predicted_days_until_zero": 3.2,
  "current_quantity": 2,
  "avg_daily_consumption": 0.6,
  "is_resolved": true,
  "created_at": "2025-01-02T00:00:00Z",
  "resolved_at": "2025-01-03T12:00:00Z"
}

### Audit Logs (Admin only)
Method  Endpoint                     Description                  Required Role
GET     /audit-logs/                 List all audit entries       Admin
GET     /audit-logs/{id}/            Retrieve an audit entry      Admin

Audit logs are read-only; they are automatically created when items, categories, or stock movements are created/updated/deleted.

## Error Handling
The API uses standard HTTP status codes.

Code  Description
200   OK – successful request.
201   Created – resource successfully created.
204   No Content – successful deletion.
400   Bad Request – invalid input (validation errors returned in response body).
401   Unauthorized – missing or invalid token.
403   Forbidden – authenticated but insufficient permissions.
404   Not Found – resource does not exist.
409   Conflict – duplicate entry (e.g., unique SKU).
500   Internal Server Error – something went wrong on the server.

Validation errors are returned as a JSON object with field names and error messages:
{
  "sku": ["This SKU is already in use."],
  "price": ["Price must be greater than 0."]
}

## Pagination
List endpoints support pagination via page and page_size query parameters (default page size is 20).
Example: GET /items/?page=2&page_size=10

The response includes pagination metadata:
{
  "count": 100,
  "next": "https://.../items/?page=3&page_size=10",
  "previous": "https://.../items/?page=1&page_size=10",
  "results": [ ... ]
}

## Rate Limiting
Currently, no rate limiting is applied. Use responsibly.

## Contact & Support
For issues or questions, please contact the project maintainer or open an issue on the GitHub repository.

This documentation reflects version 1.0 of the Sentinel Inventory Pro API.
