# IoT Smart Building Monitoring Platform - Technical Documentation

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Architecture Overview](#architecture-overview)
3. [System Design](#system-design)
4. [Component Details](#component-details)
5. [Data Flow](#data-flow)
6. [API Documentation](#api-documentation)
7. [Database Schema](#database-schema)
8. [Deployment Guide](#deployment-guide)
9. [Testing Strategy](#testing-strategy)
10. [Monitoring & Logging](#monitoring--logging)
11. [Security Considerations](#security-considerations)
12. [Performance Optimization](#performance-optimization)
13. [Troubleshooting](#troubleshooting)

---

## 1. Executive Summary

### Project Overview
The **IoT Smart Building Monitoring Platform** is a comprehensive real-time monitoring solution for intelligent building management. It ingests, processes, stores, and visualizes IoT sensor data from multiple buildings, zones, and device types.

### Scenario
A facilities management company operates multiple buildings equipped with various IoT sensors (temperature, humidity, energy consumption, occupancy, etc.). The platform aggregates this data, detects anomalies, generates alerts, and provides visual dashboards for decision-making.

### Key Objectives
- ✅ Real-time ingestion of sensor data from multiple sources
- ✅ Centralized storage and indexing with Elasticsearch
- ✅ Interactive visualization with Kibana
- ✅ User authentication and role-based access control
- ✅ Advanced search and filtering capabilities
- ✅ Alerting and anomaly detection
- ✅ Responsive web interface
- ✅ RESTful API for third-party integrations

### Business Value
- **Cost Reduction**: Identify energy inefficiencies and waste
- **Safety**: Real-time alerts for critical conditions (temperature extremes, occupancy)
- **Compliance**: Audit trail of all monitoring activities
- **Insights**: Historical data analysis for trend identification
- **Automation**: API-driven integrations with building management systems

---

## 2. Architecture Overview

### 2.1 High-Level Architecture (C4 Model - System Context)

```
┌─────────────────────────────────────────────────────────┐
│                  IoT Sensors                             │
│          (Temperature, Humidity, Energy,                 │
│           Occupancy, Luminosity, CO2)                    │
└────────────────────┬────────────────────────────────────┘
                     │ (CSV/JSON files + TCP stream)
                     ▼
┌─────────────────────────────────────────────────────────┐
│        IoT Smart Building Monitoring Platform            │
│                                                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │   Upload     │  │   Search     │  │   Dashboard  │   │
│  │   Module     │  │   Module     │  │   Module     │   │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘   │
│         │                 │                  │            │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Flask Web Application                    │   │
│  │  (Routes, Authentication, Business Logic)        │   │
│  └──────┬──────────────────┬──────────────┬─────────┘   │
│         │                  │              │              │
│         ▼                  ▼              ▼              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ Elasticsearch│  │  MongoDB     │  │   Redis      │   │
│  │ (Indexing & │  │  (Metadata & │  │  (Caching)   │   │
│  │  Search)    │  │   Uploads)   │  │              │   │
│  └─────────────┘  └──────────────┘  └──────────────┘   │
│         │                                                │
│         ▼                                                │
│  ┌─────────────┐                                        │
│  │  Logstash   │                                        │
│  │  (Pipeline) │                                        │
│  └─────────────┘                                        │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              Kibana Dashboards                           │
│    (Visualizations, Analytics, Real-time Monitoring)    │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Container Deployment (Docker Compose)

```
Service          Image                Port    Purpose
─────────────────────────────────────────────────────────
elasticsearch    docker.elastic.co/   9200    Full-text search, indexing
                 elasticsearch:8.11.0

kibana           docker.elastic.co/   5601    Data visualization
                 kibana:8.11.0

logstash         docker.elastic.co/   5000    Data pipeline, transformation
                 logstash:8.11.0

mongodb          mongo:7.0            27017   Metadata storage
                                      
redis            redis:7-alpine       6379    Caching layer

webapp           custom (Flask)       8000    Web application
                 python:3.11                   
```

---

## 3. System Design

### 3.1 Data Flow Architecture

#### Flow 1: CSV/JSON File Upload
```
User Upload
    ↓
Flask /upload endpoint
    ↓
File validation & storage in /data/uploads/
    ↓
MongoDB: Record metadata
    ↓
Logstash: Poll /data/uploads/ (file input)
    ↓
Logstash: Parse CSV/JSON
    ↓
Logstash: Transform fields (date, numeric conversion)
    ↓
Logstash: Elasticsearch output (index: iot-logs-YYYY.MM.DD)
    ↓
Elasticsearch: Store indexed documents
    ↓
Kibana: Query & visualize
```

#### Flow 2: Real-time TCP Stream
```
IoT Sensor Device (TCP port 5000)
    ↓
JSON-formatted sensor data
    ↓
Logstash: TCP input plugin (json_lines codec)
    ↓
Logstash: Transform & enrich
    ↓
Elasticsearch: Index immediately
    ↓
Dashboard: Real-time update (auto-refresh)
```

#### Flow 3: Search & Query
```
User searches query in UI
    ↓
JavaScript AJAX → Flask /search endpoint
    ↓
Flask: Query Elasticsearch (Query DSL)
    ↓
Flask: Apply filters, pagination, sorting
    ↓
Elasticsearch: Return results
    ↓
Flask: JSON response + MongoDB metadata enrichment
    ↓
UI: Display results with formatting
```

### 3.2 Technology Stack Justification

| Component | Technology | Version | Justification |
|-----------|-----------|---------|--------------|
| **Web Framework** | Flask | 2.3+ | Lightweight, Python-native, easy to extend |
| **Authentication** | Flask-Login | Latest | Built-in session management, role support |
| **Database (Logs)** | Elasticsearch | 8.11.0 | Full-text search, aggregations, time-series |
| **Database (Metadata)** | MongoDB | 7.0 | Flexible schema, document storage |
| **Caching** | Redis | 7-alpine | Sub-millisecond caching, session store |
| **Pipeline** | Logstash | 8.11.0 | Mature, extensible, multiple input types |
| **Visualization** | Kibana | 8.11.0 | Native ES integration, no learning curve |
| **Frontend** | Bootstrap 5 | Latest | Responsive, accessible, professional |
| **Charts** | Chart.js | 4.x | Lightweight, interactive, easy integration |
| **Testing** | pytest | Latest | Comprehensive, fixtures, parametrize |
| **Linting** | flake8, pylint | Latest | Code quality, style consistency |
| **CI/CD** | GitHub Actions | Native | Free, integrated with GitHub |

---

## 4. Component Details

### 4.1 Flask Application Structure

```
app/
├── __init__.py                 # App factory, extension initialization
├── models/
│   ├── __init__.py
│   └── user.py                # User model for authentication
├── routes/
│   ├── __init__.py
│   ├── main.py                # Dashboard, home page (GET /)
│   ├── auth.py                # Login, logout, register
│   ├── upload.py              # File upload (POST /upload)
│   ├── search.py              # Search functionality (GET /search)
│   ├── api.py                 # RESTful API endpoints
│   └── admin.py               # Admin dashboard
├── services/
│   ├── __init__.py
│   ├── database.py            # Elasticsearch, MongoDB, Redis connections
│   ├── auth_decorators.py     # @login_required, @admin_required
│   └── kibana_init.py         # Kibana setup & index patterns
├── templates/
│   ├── base.html              # Base template with navbar
│   ├── index.html             # Home page
│   ├── dashboard.html         # Dashboard with charts
│   ├── upload.html            # File upload form
│   ├── search.html            # Search interface
│   ├── kibana.html            # Kibana embed
│   └── auth/
│       ├── login.html
│       ├── register.html
│       └── profile.html
├── static/
│   └── css/
│       └── style.css          # Custom styling
└── config/
    └── logstash.conf          # Logstash pipeline definition
```

### 4.2 Logstash Pipeline Configuration

```
INPUT STAGE:
├── File input (CSV): /data/uploads/*.csv
├── File input (JSON): /data/uploads/*.json
└── TCP input: port 5000 (streaming data)

FILTER STAGE:
├── CSV parsing
│   ├── Column mapping: timestamp, sensor_id, sensor_type, value, etc.
│   └── Header skip
├── JSON parsing & validation
├── Field transformations
│   ├── Date field standardization (@timestamp)
│   ├── Numeric conversion (value → float)
│   ├── String trimming (sensor_id, sensor_type, zone)
│   └── Alert level calculation (if temp > 30: alert_level = "high")
└── Field enrichment
    ├── Add building metadata
    └── Add processing timestamp

OUTPUT STAGE:
└── Elasticsearch
    ├── Index pattern: iot-logs-YYYY.MM.DD
    ├── Document type: _doc
    └── Automatic mapping detection
```

### 4.3 Elasticsearch Mapping

```json
{
  "mappings": {
    "properties": {
      "@timestamp": {
        "type": "date",
        "format": "epoch_millis||strict_date_optional_time"
      },
      "sensor_id": {
        "type": "keyword"
      },
      "sensor_type": {
        "type": "keyword",
        "index": true
      },
      "building_id": {
        "type": "keyword"
      },
      "zone": {
        "type": "keyword"
      },
      "value": {
        "type": "float"
      },
      "unit": {
        "type": "keyword"
      },
      "status": {
        "type": "keyword",
        "index": true
      },
      "alert_level": {
        "type": "keyword"
      },
      "metadata": {
        "type": "object",
        "properties": {
          "battery_level": {
            "type": "integer"
          },
          "firmware_version": {
            "type": "keyword"
          }
        }
      }
    }
  }
}
```

### 4.4 MongoDB Collections

#### Collection: `users`
```json
{
  "_id": ObjectId,
  "username": String,
  "email": String,
  "password_hash": String,
  "role": "admin|user|viewer",
  "created_at": Date,
  "last_login": Date,
  "is_active": Boolean
}
```

#### Collection: `uploaded_files`
```json
{
  "_id": ObjectId,
  "filename": String,
  "original_filename": String,
  "upload_date": Date,
  "size": Integer,
  "status": "pending|processed|error",
  "filepath": String,
  "records_count": Integer,
  "uploaded_by": String,
  "error_message": String
}
```

#### Collection: `search_history`
```json
{
  "_id": ObjectId,
  "user_id": ObjectId,
  "query": String,
  "filters": Object,
  "results_count": Integer,
  "execution_time_ms": Integer,
  "timestamp": Date
}
```

---

## 5. Data Flow

### 5.1 Complete Request-Response Cycle

#### Example: Upload IoT CSV File
```
1. User selects file (iot_sensors.csv) in UI
2. JavaScript: POST /upload/file with multipart/form-data
3. Flask upload_file():
   - Validate file extension (.csv)
   - Check file size < 100MB
   - Secure filename
   - Save to /data/uploads/20260103_HHMMSS_iot_sensors.csv
   - Extract metadata (size, timestamp)
4. MongoDB: Insert record
   {
     filename: "20260103_HHMMSS_iot_sensors.csv",
     status: "uploaded",
     records_count: 0
   }
5. Return JSON:
   {
     "message": "File uploaded successfully",
     "file": {...}
   }
6. Logstash (background):
   - Polls /data/uploads/ every 1 second
   - Detects new file
   - Reads CSV line by line
   - Parses columns
   - Transforms timestamp format
   - Sends to Elasticsearch
7. Elasticsearch:
   - Creates index if not exists
   - Stores documents with mapping
8. Kibana:
   - Auto-detects new index pattern
   - Offers to visualize
9. Dashboard:
   - Auto-refresh triggers
   - Aggregations update (avg_temperature, total_logs, etc.)
```

---

## 6. API Documentation

### 6.1 Authentication Endpoints

#### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}
```

**Response (201):**
```json
{
  "message": "User registered successfully",
  "user": {
    "username": "john_doe",
    "email": "john@example.com",
    "role": "user"
  }
}
```

#### POST /auth/login
Login with username and password.

**Request:**
```json
{
  "username": "john_doe",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Login successful",
  "user": {
    "username": "john_doe",
    "role": "user"
  }
}
```

#### POST /auth/logout
Logout current user.

**Response (200):**
```json
{
  "message": "Logged out successfully"
}
```

---

### 6.2 Data Upload Endpoints

#### POST /upload/file
Upload IoT data file (CSV or JSON).

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Auth: Required (@login_required)

**Response (201):**
```json
{
  "message": "File uploaded successfully",
  "file": {
    "_id": "507f1f77bcf86cd799439011",
    "filename": "20260103_132949_sensors.csv",
    "original_filename": "sensors.csv",
    "upload_date": "2026-01-03T13:29:49.123Z",
    "size": 1024000,
    "status": "uploaded"
  }
}
```

---

### 6.3 Search Endpoints

#### GET /search
Search logs with filters.

**Query Parameters:**
- `q` (string): Search query
- `sensor_type` (string): Filter by sensor type (temperature, energy, etc.)
- `building_id` (string): Filter by building
- `zone` (string): Filter by zone
- `date_from` (ISO8601): Start date
- `date_to` (ISO8601): End date
- `page` (integer): Page number (default: 1)
- `limit` (integer): Results per page (default: 50)

**Response (200):**
```json
{
  "total": 1234,
  "page": 1,
  "limit": 50,
  "results": [
    {
      "@timestamp": "2025-12-30T11:57:12.966Z",
      "sensor_id": "TEMP_zone_a_001",
      "sensor_type": "temperature",
      "building_id": "Building_A",
      "zone": "zone_a",
      "value": 22.5,
      "unit": "°C",
      "status": "normal"
    }
  ],
  "aggregations": {
    "by_sensor_type": {...},
    "by_building": {...}
  }
}
```

---

### 6.4 Dashboard API Endpoints

#### GET /api/v1/stats
Get dashboard statistics.

**Response (200):**
```json
{
  "total_logs": 309238,
  "avg_temperature": 22.5,
  "energy_consumption": 45678.90,
  "alerts_today": 0,
  "total_files": 8,
  "active_sensors": 48,
  "last_update": "2026-01-03T14:30:00.000Z"
}
```

#### GET /api/v1/logs
List all logs with pagination.

**Query Parameters:**
- `page` (integer, default: 1)
- `limit` (integer, default: 100)
- `sort` (string, default: "@timestamp:desc")

**Response (200):**
```json
{
  "total": 309238,
  "page": 1,
  "results": [...]
}
```

#### GET /api/v1/files
List uploaded files.

**Response (200):**
```json
{
  "files": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "filename": "sensors.csv",
      "upload_date": "2026-01-03T13:29:49.123Z",
      "size": 1024000,
      "status": "processed",
      "records_count": 5000
    }
  ]
}
```

---

## 7. Database Schema

### 7.1 Elasticsearch Index Template

```json
{
  "index_patterns": ["iot-logs-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "refresh_interval": "1s"
  },
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "sensor_id": {"type": "keyword"},
      "sensor_type": {"type": "keyword"},
      "building_id": {"type": "keyword"},
      "zone": {"type": "keyword"},
      "value": {"type": "float"},
      "unit": {"type": "keyword"},
      "status": {"type": "keyword"},
      "alert_level": {"type": "keyword"},
      "metadata": {"type": "object"}
    }
  }
}
```

### 7.2 MongoDB Indexes

```javascript
// Users collection
db.users.createIndex({ "username": 1 }, { unique: true })
db.users.createIndex({ "email": 1 }, { unique: true })

// Uploaded files collection
db.uploaded_files.createIndex({ "upload_date": -1 })
db.uploaded_files.createIndex({ "uploaded_by": 1 })

// Search history collection
db.search_history.createIndex({ "user_id": 1, "timestamp": -1 })
```

---

## 8. Deployment Guide

### 8.1 Prerequisites

- Docker & Docker Compose (version 2.0+)
- Python 3.11+
- Git
- 4GB+ RAM
- 20GB+ free disk space

### 8.2 Local Development Setup

```bash
# Clone repository
git clone https://github.com/wassimdgh/BigData-ELK.git
cd BigData-ELK

# Copy environment file
cp .env.example .env

# Install dependencies (optional, for local development)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start all services
docker-compose up -d

# Wait for services to be ready (30-60 seconds)
sleep 60

# Initialize database
python scripts/init_db.py
python scripts/setup_kibana_viz.py

# Access applications
# Web: http://localhost:8000
# Kibana: http://localhost:5601
# Elasticsearch: http://localhost:9200
```

### 8.3 Production Deployment

```bash
# Build custom images
docker-compose -f docker-compose.yml build

# Use environment variables
export ELASTICSEARCH_USER=admin
export ELASTICSEARCH_PASSWORD=secure_password
export FLASK_ENV=production

# Start with production config
docker-compose up -d

# Run migrations/initialization
docker-compose exec webapp python scripts/init_db.py

# Verify services
docker-compose ps
docker-compose logs webapp
```

---

## 9. Testing Strategy

### 9.1 Test Coverage

**Unit Tests (35%)**
- Authentication functions
- Data validation
- Utility functions
- Database queries

**Integration Tests (40%)**
- Upload → Elasticsearch flow
- Search API with filters
- API endpoint responses
- Logstash pipeline

**End-to-End Tests (15%)**
- Complete user workflows
- UI interactions
- Real-time updates

**Performance Tests (10%)**
- Load testing with Locust
- Response time benchmarks

---

## 10. Monitoring & Logging

### 10.1 Application Logging

All logs are structured JSON format:

```json
{
  "timestamp": "2026-01-03T14:30:00.000Z",
  "level": "ERROR",
  "logger": "app.routes.upload",
  "message": "Failed to parse CSV file",
  "context": {
    "filename": "sensors.csv",
    "error": "Missing required columns",
    "user_id": "user_123"
  },
  "trace_id": "abc123def456"
}
```

### 10.2 Docker Health Checks

Each service includes health checks:
- Elasticsearch: HTTP GET /
- Kibana: HTTP GET /api/status
- MongoDB: `mongosh --eval "db.adminCommand('ping')"`
- Redis: `redis-cli ping`
- Flask: HTTP GET /health

---

## 11. Security Considerations

### 11.1 Authentication & Authorization

- Flask-Login session-based authentication
- Passwords hashed with Werkzeug security
- Role-based access control:
  - **admin**: Full access
  - **user**: Can upload, search, view dashboards
  - **viewer**: Read-only access

### 11.2 Data Protection

- Elasticsearch authentication enabled (elastic/changeme)
- MongoDB no default authentication (configure in production)
- Redis password protection (configure in production)
- All file uploads validated

### 11.3 API Security

- All endpoints require authentication except public pages
- Rate limiting (implement Flask-Limiter)
- CORS headers properly configured
- Input validation on all endpoints

---

## 12. Performance Optimization

### 12.1 Caching Strategy

- Redis cache for:
  - User sessions
  - Frequently accessed stats
  - Search results (5 minute TTL)
  - Index patterns

### 12.2 Query Optimization

- Elasticsearch:
  - Use filtered queries (cheaper than full-text)
  - Aggregate data server-side
  - Pagination to limit result set
  - Refresh interval: 1 second

- MongoDB:
  - Index on frequently filtered fields
  - Use projection to limit returned fields
  - Batch operations

### 12.3 Database Performance

```
Elasticsearch:
- Shard count: 1 (single node)
- Replica count: 0
- Refresh interval: 1s
- Use keyword fields for exact matches
- Use text fields only for free-text search

MongoDB:
- Connection pooling: 50 connections
- Write concern: acknowledged
- Read preference: primary
```

---

## 13. Troubleshooting

### 13.1 Common Issues

**Issue: Elasticsearch not responding**
```bash
# Check status
curl http://localhost:9200/

# View logs
docker logs elasticsearch

# Restart
docker restart elasticsearch
```

**Issue: Logstash not processing files**
```bash
# Check Logstash logs for parsing errors
docker logs logstash

# Verify file permissions
docker exec logstash ls -la /data/uploads/

# Manually test pipeline config
docker exec logstash /usr/share/logstash/bin/logstash -f /pipeline/logstash.conf -t
```

**Issue: High memory usage**
```bash
# Check container stats
docker stats

# Reduce Elasticsearch heap
export ES_JAVA_OPTS="-Xms512m -Xmx512m"
docker restart elasticsearch
```

### 13.2 Performance Monitoring

```bash
# Monitor Docker resource usage
docker stats

# Check Elasticsearch cluster health
curl http://localhost:9200/_cluster/health

# Check index sizes
curl http://localhost:9200/_cat/indices?v

# Monitor Logstash pipeline
curl http://localhost:9600/_node/stats/pipelines
```

---

## Appendices

### A. Technology Versions
- Elasticsearch: 8.11.0
- Kibana: 8.11.0
- Logstash: 8.11.0
- MongoDB: 7.0
- Redis: 7-alpine
- Python: 3.11.14
- Flask: 2.3.0
- Bootstrap: 5.x
- Chart.js: 4.x

### B. References
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Kibana User Guide](https://www.elastic.co/guide/en/kibana/current/index.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)

---

**Document Version**: 1.0  
**Last Updated**: January 3, 2026  
**Author**: Development Team
