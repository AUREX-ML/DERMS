# DERMS API Reference

Base URL: `http://localhost:8000` (development) | `https://api.your-domain.com` (production)

All endpoints (except `/health`) require an `Authorization: Bearer <token>` header.

---

## Health

### `GET /health`

Returns the health status of the DERMS application and its dependencies.

**Authentication:** None required.

**Response `200 OK`**
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-05-14T09:00:00Z",
  "dependencies": {
    "database": "ok",
    "redis": "ok",
    "mqtt": "ok"
  }
}
```

---

## Resources

### `GET /resources`

List all registered Distributed Energy Resources (DERs).

**Query Parameters**

| Name       | Type    | Default | Description                                      |
| ---------- | ------- | ------- | ------------------------------------------------ |
| `type`     | string  | —       | Filter by type: `battery`, `solar`, `ev`, `load` |
| `site_id`  | string  | —       | Filter by site identifier                        |
| `limit`    | integer | 50      | Maximum number of results                        |
| `offset`   | integer | 0       | Pagination offset                                |

**Response `200 OK`**
```json
{
  "total": 3,
  "resources": [
    {
      "id": "res-001",
      "name": "Site A Battery Bank",
      "type": "battery",
      "site_id": "site-a",
      "capacity_kwh": 500.0,
      "status": "online",
      "last_seen": "2026-05-14T08:55:00Z"
    }
  ]
}
```

---

### `POST /resources`

Register a new Distributed Energy Resource.

**Request Body**
```json
{
  "name": "Site B Solar Array",
  "type": "solar",
  "site_id": "site-b",
  "capacity_kw": 250.0,
  "panel_count": 500,
  "inverter_efficiency": 0.97,
  "tilt_angle": 30.0,
  "azimuth": 180.0
}
```

**Response `201 Created`**
```json
{
  "id": "res-002",
  "name": "Site B Solar Array",
  "type": "solar",
  "site_id": "site-b",
  "created_at": "2026-05-14T09:01:00Z"
}
```

**Error Responses**

| Status | Description                                  |
| ------ | -------------------------------------------- |
| 400    | Invalid request body / validation error      |
| 409    | Resource with the same name already exists   |

---

### `GET /resources/{id}/status`

Retrieve the real-time status of a specific DER.

**Path Parameters**

| Name | Type   | Description     |
| ---- | ------ | --------------- |
| `id` | string | Resource ID     |

**Response `200 OK`**
```json
{
  "id": "res-001",
  "type": "battery",
  "state_of_charge": 0.78,
  "power_kw": -50.0,
  "voltage_v": 800.0,
  "temperature_c": 28.5,
  "status": "discharging",
  "alarms": [],
  "timestamp": "2026-05-14T08:59:30Z"
}
```

**Error Responses**

| Status | Description             |
| ------ | ----------------------- |
| 404    | Resource not found      |

---

## Optimization

### `POST /optimize`

Trigger an optimization run across all registered DERs for a given horizon.

**Request Body**
```json
{
  "horizon_hours": 24,
  "objective": "maximize_revenue",
  "constraints": {
    "min_soc": 0.10,
    "max_soc": 0.95,
    "grid_export_limit_kw": 1000.0
  }
}
```

**Response `202 Accepted`**
```json
{
  "job_id": "opt-job-8a3f1",
  "status": "queued",
  "estimated_completion": "2026-05-14T09:00:45Z"
}
```

**Notes:**
- Optimization runs asynchronously. Poll `GET /optimize/{job_id}` for results.
- Results include a per-asset dispatch schedule and projected revenue.

---

## Forecasting

### `GET /forecast`

Retrieve the current 24-hour ahead load forecast.

**Query Parameters**

| Name        | Type    | Default | Description                          |
| ----------- | ------- | ------- | ------------------------------------ |
| `site_id`   | string  | —       | Forecast for a specific site         |
| `horizon_h` | integer | 24      | Forecast horizon in hours (max: 168) |
| `interval`  | string  | `15min` | Resolution: `15min`, `1h`            |

**Response `200 OK`**
```json
{
  "site_id": "site-a",
  "generated_at": "2026-05-14T08:00:00Z",
  "horizon_hours": 24,
  "interval": "15min",
  "forecast": [
    {
      "timestamp": "2026-05-14T09:00:00Z",
      "load_kw": 320.5,
      "p10_kw": 295.0,
      "p90_kw": 345.0
    },
    {
      "timestamp": "2026-05-14T09:15:00Z",
      "load_kw": 315.0,
      "p10_kw": 290.0,
      "p90_kw": 340.5
    }
  ]
}
```

---

## Error Format

All error responses follow a consistent structure:

```json
{
  "detail": "Human-readable error message",
  "code": "MACHINE_READABLE_CODE",
  "timestamp": "2026-05-14T09:00:00Z"
}
```

---

## Rate Limits

| Endpoint group     | Limit              |
| ------------------ | ------------------ |
| `/health`          | No limit           |
| `GET /resources`   | 100 req/min        |
| `POST /resources`  | 20 req/min         |
| `POST /optimize`   | 5 req/min          |
| `GET /forecast`    | 60 req/min         |
