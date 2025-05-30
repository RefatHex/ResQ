# ResQ API Documentation

## Overview

ResQ is an emergency response coordination platform designed to connect citizens with emergency services during crisis situations. This document provides comprehensive API documentation for developers.

## Base URL

```
https://api.resq-app.com/api/
```

For local development:

```
http://localhost:8000/api/
```

## Authentication

### Authentication Methods

ResQ supports multiple authentication methods:

1. **JWT Authentication**: Primary authentication method using JSON Web Tokens
2. **Firebase Authentication**: Alternative method for mobile clients

#### JWT Authentication

Most endpoints require an access token in the Authorization header:

```
Authorization: Bearer {your_access_token}
```

To obtain tokens, use the login endpoint.

#### Firebase Authentication

Mobile clients can authenticate using Firebase:

```
Authorization: Firebase {firebase_id_token}
```

### Authentication Endpoints

#### Register a New User

**Endpoint**: `POST /users/register/`

**Description**: Create a new user account

**Request Body**:

```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+905551234567",
  "role": "CITIZEN",
  "location": {
    "latitude": 38.4192,
    "longitude": 27.1287
  }
}
```

**Response (201 Created)**:

```json
{
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+905551234567",
    "role": "CITIZEN",
    "is_active": true,
    "date_joined": "2025-04-15T09:12:33Z"
  },
  "refresh": "eyJ0eXA...",
  "access": "eyJ0eXA..."
}
```

#### User Login

**Endpoint**: `POST /users/login/`

**Description**: Authenticate and receive JWT tokens

**Request Body**:

```json
{
  "username": "john_doe",
  "password": "secure_password"
}
```

**Response (200 OK)**:

```json
{
  "refresh": "eyJ0eXA...",
  "access": "eyJ0eXA...",
  "user": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+905551234567",
    "role": "CITIZEN",
    "is_active": true,
    "date_joined": "2025-04-15T09:12:33Z"
  }
}
```

#### Refresh Token

**Endpoint**: `POST /users/token/refresh/`

**Description**: Get a new access token using refresh token

**Request Body**:

```json
{
  "refresh": "eyJ0eXA..."
}
```

**Response (200 OK)**:

```json
{
  "access": "eyJ0eXA..."
}
```

## User Management

### Get Current User Profile

**Endpoint**: `GET /users/me/`

**Description**: Retrieve the authenticated user's profile

**Authentication**: Required

**Response (200 OK)**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+905551234567",
  "role": "CITIZEN",
  "is_active": true,
  "date_joined": "2025-04-15T09:12:33Z"
}
```

### Update User Profile

**Endpoint**: `PATCH /users/me/`

**Description**: Update current user's profile

**Authentication**: Required

**Request Body**:

```json
{
  "first_name": "Johnny",
  "last_name": "Doe",
  "phone_number": "+905559876543"
}
```

**Response (200 OK)**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "username": "john_doe",
  "email": "john@example.com",
  "first_name": "Johnny",
  "last_name": "Doe",
  "phone_number": "+905559876543",
  "role": "CITIZEN",
  "is_active": true,
  "date_joined": "2025-04-15T09:12:33Z"
}
```

### List Emergency Service Users

**Endpoint**: `GET /users/list/?role=FIRE_STATION`

**Description**: Get a list of users filtered by role

**Authentication**: Required

**Query Parameters**:

- `role`: Filter by user role (CITIZEN, FIRE_STATION, POLICE, RED_CRESCENT)

**Response (200 OK)**:

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
    "username": "central_fire_station",
    "email": "fire@example.com",
    "first_name": "Central",
    "last_name": "Fire Station",
    "phone_number": "+905551112233",
    "role": "FIRE_STATION",
    "is_active": true,
    "date_joined": "2025-04-10T09:12:33Z"
  }
]
```

## Location Management

### Update User Location

**Endpoint**: `POST /locations/`

**Description**: Update the user's current location

**Authentication**: Required

**Request Body**:

```json
{
  "latitude": 38.4192,
  "longitude": 27.1287,
  "address": "123 Main St, Izmir, Turkey",
  "is_current": true
}
```

**Response (201 Created)**:

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
  "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "latitude": 38.4192,
  "longitude": 27.1287,
  "address": "123 Main St, Izmir, Turkey",
  "is_current": true,
  "is_emergency": false,
  "timestamp": "2025-04-15T10:15:33Z"
}
```

### Get User's Location History

**Endpoint**: `GET /locations/`

**Description**: Retrieve the user's location history

**Authentication**: Required

**Response (200 OK)**:

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa8",
    "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "latitude": 38.4192,
    "longitude": 27.1287,
    "address": "123 Main St, Izmir, Turkey",
    "is_current": true,
    "is_emergency": false,
    "timestamp": "2025-04-15T10:15:33Z"
  },
  {
    "id": "4fa85f64-5717-4562-b3fc-2c963f66afa9",
    "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "latitude": 38.418,
    "longitude": 27.129,
    "address": "456 Park Ave, Izmir, Turkey",
    "is_current": false,
    "is_emergency": false,
    "timestamp": "2025-04-14T15:20:33Z"
  }
]
```

### Emergency Location Update

**Endpoint**: `POST /locations/emergency/`

**Description**: Update user's location during an emergency

**Authentication**: Required

**Request Body**:

```json
{
  "latitude": 38.4192,
  "longitude": 27.1287,
  "address": "123 Main St, Izmir, Turkey"
}
```

**Response (201 Created)**:

```json
{
  "id": "5fa85f64-5717-4562-b3fc-2c963f66afaa",
  "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "latitude": 38.4192,
  "longitude": 27.1287,
  "address": "123 Main St, Izmir, Turkey",
  "is_current": true,
  "is_emergency": true,
  "timestamp": "2025-04-15T10:25:33Z"
}
```

### Emergency Locations List

**Endpoint**: `GET /locations/emergency-locations/`

**Description**: Get all current emergency locations (for emergency services only)

**Authentication**: Required (Emergency services only)

**Response (200 OK)**:

```json
[
  {
    "id": "5fa85f64-5717-4562-b3fc-2c963f66afaa",
    "user": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "username": "john_doe",
      "phone_number": "+905551234567"
    },
    "latitude": 38.4192,
    "longitude": 27.1287,
    "address": "123 Main St, Izmir, Turkey",
    "is_emergency": true,
    "timestamp": "2025-04-15T10:25:33Z"
  }
]
```

## Emergency Management

### List Emergency Tags

**Endpoint**: `GET /emergency/tags/`

**Description**: Get a list of all emergency tags for categorization

**Authentication**: Required

**Response (200 OK)**:

```json
[
  {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afab",
    "name": "Building Collapse",
    "emergency_type": "EARTHQUAKE",
    "description": "Structural damage or building collapse"
  },
  {
    "id": "4fa85f64-5717-4562-b3fc-2c963f66afac",
    "name": "Fire",
    "emergency_type": "FIRE",
    "description": "Active fire emergency"
  },
  {
    "id": "5fa85f64-5717-4562-b3fc-2c963f66afad",
    "name": "Trapped Individuals",
    "emergency_type": "DISASTER",
    "description": "People trapped or in need of rescue"
  }
]
```

### Report Emergency

**Endpoint**: `POST /emergency/reports/report_emergency/`

**Description**: Report a new emergency with location

**Authentication**: Required

**Request Body**:

```json
{
  "reporter_type": "VICTIM",
  "description": "Building collapsed, need urgent help",
  "location": {
    "latitude": 38.4192,
    "longitude": 27.1287,
    "address": "123 Main St, Izmir, Turkey"
  },
  "tags": [
    "3fa85f64-5717-4562-b3fc-2c963f66afab",
    "5fa85f64-5717-4562-b3fc-2c963f66afad"
  ]
}
```

**Response (201 Created)**:

```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afae",
  "reporter": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "reporter_type": "VICTIM",
  "description": "Building collapsed, need urgent help",
  "location": "5fa85f64-5717-4562-b3fc-2c963f66afaa",
  "latitude": 38.4192,
  "longitude": 27.1287,
  "status": "PENDING",
  "is_emergency": true,
  "tags": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afab",
      "name": "Building Collapse",
      "emergency_type": "EARTHQUAKE"
    },
    {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afad",
      "name": "Trapped Individuals",
      "emergency_type": "DISASTER"
    }
  ],
  "timestamp": "2025-04-15T10:30:33Z"
}
```

### List Emergencies

**Endpoint**: `GET /emergency/reports/`

**Description**: Get a list of emergency reports

**Authentication**: Required

**Query Parameters**:

- `status`: Filter by status (PENDING, RESPONDING, ON_SCENE, RESOLVED)
- `is_emergency`: Filter by emergency flag (true/false)
- `reporter_type`: Filter by reporter type (VICTIM, SPECTATOR)

**Response (200 OK)**:

```json
[
  {
    "id": "6fa85f64-5717-4562-b3fc-2c963f66afae",
    "reporter": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "reporter_type": "VICTIM",
    "description": "Building collapsed, need urgent help",
    "latitude": 38.4192,
    "longitude": 27.1287,
    "status": "PENDING",
    "is_emergency": true,
    "tags": [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afab",
        "name": "Building Collapse",
        "emergency_type": "EARTHQUAKE"
      },
      {
        "id": "5fa85f64-5717-4562-b3fc-2c963f66afad",
        "name": "Trapped Individuals",
        "emergency_type": "DISASTER"
      }
    ],
    "timestamp": "2025-04-15T10:30:33Z"
  }
]
```

### Get Emergency Details

**Endpoint**: `GET /emergency/reports/{id}/`

**Description**: Get details of a specific emergency

**Authentication**: Required

**Response (200 OK)**:

```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afae",
  "reporter": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "username": "john_doe",
    "phone_number": "+905551234567"
  },
  "reporter_type": "VICTIM",
  "description": "Building collapsed, need urgent help",
  "latitude": 38.4192,
  "longitude": 27.1287,
  "status": "PENDING",
  "is_emergency": true,
  "tags": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afab",
      "name": "Building Collapse",
      "emergency_type": "EARTHQUAKE"
    },
    {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afad",
      "name": "Trapped Individuals",
      "emergency_type": "DISASTER"
    }
  ],
  "timestamp": "2025-04-15T10:30:33Z"
}
```

### Update Emergency Status

**Endpoint**: `POST /emergency/reports/{id}/update_status/`

**Description**: Update the status of an emergency (for emergency services)

**Authentication**: Required (Emergency services only)

**Request Body**:

```json
{
  "status": "RESPONDING"
}
```

**Status Options**:

- `PENDING`: Not yet addressed
- `RESPONDING`: Emergency services on the way
- `ON_SCENE`: Emergency services at the location
- `RESOLVED`: Emergency has been resolved

**Response (200 OK)**:

```json
{
  "id": "6fa85f64-5717-4562-b3fc-2c963f66afae",
  "reporter": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "reporter_type": "VICTIM",
  "description": "Building collapsed, need urgent help",
  "latitude": 38.4192,
  "longitude": 27.1287,
  "status": "RESPONDING",
  "is_emergency": true,
  "tags": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afab",
      "name": "Building Collapse",
      "emergency_type": "EARTHQUAKE"
    },
    {
      "id": "5fa85f64-5717-4562-b3fc-2c963f66afad",
      "name": "Trapped Individuals",
      "emergency_type": "DISASTER"
    }
  ],
  "timestamp": "2025-04-15T10:30:33Z"
}
```

### Find Nearby Emergencies

**Endpoint**: `GET /emergency/nearby/?lat=38.4192&lng=27.1287&radius=5`

**Description**: Find emergencies within a specific radius

**Authentication**: Required

**Query Parameters**:

- `lat`: Latitude (required)
- `lng`: Longitude (required)
- `radius`: Search radius in kilometers (default: 5)

**Response (200 OK)**:

```json
[
  {
    "id": "6fa85f64-5717-4562-b3fc-2c963f66afae",
    "reporter": {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "username": "john_doe"
    },
    "description": "Building collapsed, need urgent help",
    "latitude": 38.4192,
    "longitude": 27.1287,
    "status": "RESPONDING",
    "is_emergency": true,
    "tags": [
      {
        "name": "Building Collapse",
        "emergency_type": "EARTHQUAKE"
      },
      {
        "name": "Trapped Individuals",
        "emergency_type": "DISASTER"
      }
    ],
    "timestamp": "2025-04-15T10:30:33Z",
    "distance": 0.35
  }
]
```

## Notifications

### List User Notifications

**Endpoint**: `GET /notifications/`

**Description**: Get a list of notifications for the current user

**Authentication**: Required

**Query Parameters**:

- `page`: Page number for pagination
- `page_size`: Number of items per page (default: 20, max: 50)

**Response (200 OK)**:

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "7fa85f64-5717-4562-b3fc-2c963f66afaf",
      "title": "Emergency Nearby",
      "message": "Emergency reported 0.5km from your location",
      "notification_type": "EMERGENCY",
      "is_read": false,
      "timestamp": "2025-04-15T10:35:33Z"
    },
    {
      "id": "8fa85f64-5717-4562-b3fc-2c963f66afb0",
      "title": "Status Update",
      "message": "Emergency services are responding to your report",
      "notification_type": "UPDATE",
      "is_read": true,
      "timestamp": "2025-04-15T10:40:33Z"
    }
  ]
}
```

### Get Notification Details

**Endpoint**: `GET /notifications/{id}/`

**Description**: Get details of a specific notification

**Authentication**: Required

**Response (200 OK)**:

```json
{
  "id": "7fa85f64-5717-4562-b3fc-2c963f66afaf",
  "title": "Emergency Nearby",
  "message": "Emergency reported 0.5km from your location",
  "notification_type": "EMERGENCY",
  "is_read": false,
  "timestamp": "2025-04-15T10:35:33Z"
}
```

### Mark Notification as Read

**Endpoint**: `PATCH /notifications/{id}/`

**Description**: Mark a notification as read

**Authentication**: Required

**Request Body**:

```json
{
  "is_read": true
}
```

**Response (200 OK)**:

```json
{
  "id": "7fa85f64-5717-4562-b3fc-2c963f66afaf",
  "title": "Emergency Nearby",
  "message": "Emergency reported 0.5km from your location",
  "notification_type": "EMERGENCY",
  "is_read": true,
  "timestamp": "2025-04-15T10:35:33Z"
}
```

### Mark All Notifications as Read

**Endpoint**: `POST /notifications/mark-all-read/`

**Description**: Mark all notifications as read

**Authentication**: Required

**Response (200 OK)**:

```json
{
  "status": "All notifications marked as read"
}
```

### Register FCM Token

**Endpoint**: `POST /notifications/register-token/`

**Description**: Register a Firebase Cloud Messaging token for push notifications

**Authentication**: Required

**Request Body**:

```json
{
  "fcm_token": "eEGH_-QORtGUz9b...LONG_FCM_TOKEN",
  "device_type": "ANDROID"
}
```

**Device Type Options**:

- `ANDROID`: Android device
- `IOS`: iOS device

**Response (200 OK)**:

```json
{
  "status": "FCM token registered"
}
```

## Map Services

### Create Route Request

**Endpoint**: `POST /map/`

**Description**: Request a route between two points

**Authentication**: Required

**Request Body**:

```json
{
  "start_location": "38.4192,27.1287",
  "end_location": "38.4500,27.1800",
  "waypoints": ["38.4300,27.1400"],
  "avoid_hazards": true
}
```

**Response (201 Created)**:

```json
{
  "id": "9fa85f64-5717-4562-b3fc-2c963f66afb1",
  "user": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "start_location": "38.4192,27.1287",
  "end_location": "38.4500,27.1800",
  "waypoints": ["38.4300,27.1400"],
  "avoid_hazards": true,
  "timestamp": "2025-04-15T11:00:33Z",
  "routes": [
    {
      "id": "10fa85f64-5717-4562-b3fc-2c963f66afb2",
      "polyline": "gpq`FccveEgB}HoA...LONG_POLYLINE_STRING",
      "distance": 5.3,
      "duration": 15.2,
      "timestamp": "2025-04-15T11:00:33Z"
    }
  ]
}
```

## Dashboards

### Citizen Dashboard

**Endpoint**: `GET /dashboards/citizen/`

**Description**: Get dashboard data for citizens

**Authentication**: Required (CITIZEN role)

**Response (200 OK)**:

```json
{
  "username": "john_doe",
  "role": "CITIZEN",
  "recent_notifications": [
    {
      "id": "7fa85f64-5717-4562-b3fc-2c963f66afaf",
      "title": "Emergency Nearby",
      "message": "Emergency reported 0.5km from your location",
      "timestamp": "2025-04-15T10:35:33Z",
      "is_read": false
    }
  ],
  "unread_notifications": 1,
  "profile_completeness": 80,
  "recent_reports": [
    {
      "id": "6fa85f64-5717-4562-b3fc-2c963f66afae",
      "description": "Building collapsed, need urgent help",
      "status": "RESPONDING",
      "timestamp": "2025-04-15T10:30:33Z",
      "reporter_type": "VICTIM"
    }
  ],
  "ongoing_emergencies": 1,
  "total_reports": 3,
  "resolved_reports": 2
}
```

### Emergency Service Dashboard

**Endpoint**: `GET /dashboards/emergency-service/`

**Description**: Get dashboard data for emergency services

**Authentication**: Required (FIRE_STATION, POLICE, or RED_CRESCENT role)

**Response (200 OK)**:

```json
{
  "username": "central_fire_station",
  "role": "FIRE_STATION",
  "recent_notifications": [],
  "unread_notifications": 0,
  "profile_completeness": 90,
  "pending_emergencies": [
    {
      "id": "11fa85f64-5717-4562-b3fc-2c963f66afb3",
      "description": "Fire in apartment building",
      "status": "PENDING",
      "timestamp": "2025-04-15T11:30:33Z",
      "latitude": 38.42,
      "longitude": 27.13,
      "is_emergency": true
    }
  ],
  "current_status": {
    "pending": 5,
    "responding": 3,
    "on_scene": 2
  },
  "service_type": "FIRE_STATION",
  "recent_activity": {
    "today": 8,
    "this_week": 32
  }
}
```

## Social Media Integration

### Post to Social Media

**Endpoint**: `POST /social/post/`

**Description**: Post emergency information to social media platforms

**Authentication**: Required (Admin or emergency services only)

**Request Body (multipart/form-data)**:

- `content`: Text content for the post
- `media_file`: Image or video file
- `platforms`: Array of platforms (FACEBOOK, TELEGRAM, DISCORD)

**Response (200 OK)**:

```json
{
  "message": "Posted to all social media platforms",
  "results": [
    {
      "platform": "FACEBOOK",
      "status": "success"
    },
    {
      "platform": "TELEGRAM",
      "status": "success"
    },
    {
      "platform": "DISCORD",
      "status": "success"
    }
  ]
}
```

## Analytics

### Global Analytics

**Endpoint**: `GET /analytics/global/?days=30`

**Description**: Get system-wide analytics data

**Authentication**: Required (Admin or emergency services only)

**Query Parameters**:

- `days`: Number of days to include in the analysis (default: 30)

**Response (200 OK)**:

```json
{
  "period": "Last 30 days",
  "active_users": 1250,
  "new_users": 380,
  "emergency_reports": 425,
  "resolved_emergencies": 398,
  "resolution_rate": 93.65,
  "emergency_types": {
    "EARTHQUAKE": {
      "count": 245,
      "avg_response_time": 15.3,
      "resolution_rate": 92.2
    },
    "FIRE": {
      "count": 120,
      "avg_response_time": 12.5,
      "resolution_rate": 96.7
    }
  }
}
```

### Regional Analytics

**Endpoint**: `GET /analytics/regional/?days=30`

**Description**: Get analytics data by region

**Authentication**: Required (Emergency services only)

**Query Parameters**:

- `days`: Number of days to include in the analysis (default: 30)

**Response (200 OK)**:

```json
{
  "period": "Last 30 days",
  "regions": {
    "Izmir-Konak": {
      "emergency_count": 85,
      "response_time_avg": 13.2
    },
    "Izmir-Bornova": {
      "emergency_count": 62,
      "response_time_avg": 14.8
    }
  }
}
```

### User Analytics

**Endpoint**: `GET /analytics/user/?days=30`

**Description**: Get analytics data for the current user

**Authentication**: Required

**Query Parameters**:

- `days`: Number of days to include in the analysis (default: 30)

**Response (200 OK)**:

```json
{
  "period": "Last 30 days",
```
