# API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require JWT token in Authorization header:
```
Authorization: Bearer <jwt_token>
```

## Endpoints

### Authentication Endpoints

#### Register User
- **URL**: `/auth/register`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword",
  "full_name": "John Doe",
  "role": "developer"
}
```
- **Success Response**: 201 Created
```json
{
  "id": "user123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "role": "developer",
  "created_at": "2024-01-15T10:30:00Z"
}
```

#### Login
- **URL**: `/auth/login`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
```json
{
  "email": "user@example.com",
  "password": "securepassword"
}
```
- **Success Response**: 200 OK
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "user123",
    "email": "user@example.com",
    "role": "developer"
  }
}
```

### Task Endpoints

#### Get All Tasks
- **URL**: `/tasks`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Parameters**: `page` (default: 1), `limit` (default: 10), `status` (optional), `assignee_id` (optional)
- **Success Response**: 200 OK
```json
{
  "data": [
    {
      "id": "task123",
      "title": "Implement authentication",
      "description": "Add JWT authentication",
      "status": "in_progress",
      "priority": "high",
      "assignee_id": "user123",
      "due_date": "2024-01-20T00:00:00Z",
      "created_at": "2024-01-10T10:00:00Z",
      "updated_at": "2024-01-15T14:30:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 10
}
```

#### Create Task
- **URL**: `/tasks`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
```json
{
  "title": "New Feature",
  "description": "Add new feature",
  "priority": "medium",
  "assignee_id": "user123",
  "due_date": "2024-01-25T00:00:00Z",
  "tags": ["feature", "backend"]
}
```
- **Success Response**: 201 Created

#### Update Task
- **URL**: `/tasks/{task_id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Request Body**: Same as Create Task
- **Success Response**: 200 OK

#### Delete Task
- **URL**: `/tasks/{task_id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**: 204 No Content

### Team Endpoints

#### Get Team Members
- **URL**: `/teams/{team_id}/members`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**: 200 OK

#### Add Team Member
- **URL**: `/teams/{team_id}/members`
- **Method**: `POST`
- **Auth Required**: Yes (Admin only)
- **Request Body**:
```json
{
  "user_id": "user456",
  "role": "developer"
}
```

## WebSocket Events

### Connection
```javascript
const socket = io('http://localhost:8000', {
  auth: {
    token: jwt_token
  }
});
```

### Events

#### task:created
Emitted when a new task is created
```json
{
  "event": "task:created",
  "data": { ...task_data }
}
```

#### task:updated
Emitted when a task is updated
```json
{
  "event": "task:updated",
  "data": { ...task_data }
}
```

#### task:deleted
Emitted when a task is deleted
```json
{
  "event": "task:deleted",
  "data": { "task_id": "task123" }
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

- Limit: 1000 requests per hour
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Pagination

All list endpoints support pagination with limit and offset:
```
GET /api/v1/tasks?page=2&limit=20
```
