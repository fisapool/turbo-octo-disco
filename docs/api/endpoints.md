# API Documentation

## Authentication
`POST /api/auth/login`
```json
{
  "username": "string",
  "password": "string"
}
```

## Activity Endpoints
`GET /api/activities`
- Returns paginated activity logs
- Filters: date_range, user_id, activity_type

`POST /api/activities`
```json
{
  "user_id": "string",
  "activity_type": "string",
  "duration": "number",
  "screenshot_id": "string"
}
```

## Analytics Endpoints
`GET /api/analytics/trends`
- Returns productivity trends
- Parameters: time_window, department

`GET /api/analytics/predictions`
- Returns activity predictions
- Parameters: user_id, lookahead_days

## System Endpoints
`GET /api/system/health`
- Returns service status

`POST /api/system/backup`
- Triggers manual backup
- Requires admin privileges

## Error Responses
```json
{
  "error": "string",
  "code": "number",
  "details": "string"
}
