# IoT Smart Building Monitoring Platform

![GitHub Actions](https://github.com/wassimdgh/BigData-ELK/workflows/CI%2FCD%20Pipeline/badge.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Docker](https://img.shields.io/badge/Docker-20.10-blue)
![Elasticsearch](https://img.shields.io/badge/Elasticsearch-8.11-green)
![MongoDB](https://img.shields.io/badge/MongoDB-7.0-green)
![Redis](https://img.shields.io/badge/Redis-7-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 📋 Project Overview

A comprehensive **real-time IoT monitoring platform** for intelligent building management. The system ingests sensor data from multiple buildings, processes it through a scalable pipeline, and provides interactive dashboards for analytics and decision-making.

### Key Features
- ✅ Real-time sensor data ingestion (CSV, JSON, TCP streams)
- ✅ Full-text search and filtering with Elasticsearch
- ✅ Interactive visualizations with Kibana
- ✅ User authentication and role-based access control
- ✅ RESTful API for third-party integrations
- ✅ Redis caching for performance optimization
- ✅ Automated CI/CD pipeline with GitHub Actions
- ✅ Comprehensive testing (unit, integration)
- ✅ Docker containerization for easy deployment

## 🏢 IoT Smart Building Scenario

### Monitored Parameters
- 🌡️ **Temperature**: Per zone, per building, real-time monitoring
- 💧 **Humidity**: Environmental control, comfort assessment
- ⚡ **Energy Consumption**: Cost tracking, efficiency optimization
- 👥 **Occupancy**: Space utilization, safety management
- 💡 **Luminosity**: Lighting optimization, energy saving
- 🌍 **CO2 Levels**: Air quality monitoring, health & safety

### Business Value
- **Cost Reduction**: Identify energy waste and optimize consumption
- **Safety**: Real-time alerts for critical conditions
- **Compliance**: Audit trail of all monitoring activities
- **Analytics**: Historical data analysis for trend identification
- **Automation**: API-driven integrations with BMS systems

## 🛠️ Technology Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Backend Framework** | Flask | 2.3+ | Web application & API |
| **Search Engine** | Elasticsearch | 8.11.0 | Full-text search, indexing |
| **Data Pipeline** | Logstash | 8.11.0 | ETL, data transformation |
| **Visualization** | Kibana | 8.11.0 | Interactive dashboards |
| **Metadata Store** | MongoDB | 7.0 | User data, file metadata |
| **Cache Layer** | Redis | 7-alpine | Session management, caching |
| **Frontend** | Bootstrap 5, Chart.js | Latest | Responsive UI |
| **Testing** | pytest | Latest | Automated testing |
| **CI/CD** | GitHub Actions | Native | Automated deployment |
| **Containerization** | Docker Compose | 2.0+ | Container orchestration |

## 🚀 Quick Start

### Prerequisites
- Docker Desktop (or Docker + Docker Compose)
- Python 3.11+ (for local development)
- Git
- 8GB RAM minimum
- 20GB free disk space

### Installation

```bash
# 1. Clone repository
git clone https://github.com/wassimdgh/BigData-ELK.git
cd BigData-ELK

# 2. Copy environment file
cp .env.example .env

# 3. Start all services with Docker Compose
docker-compose up -d

# 4. Wait for services to initialize (30-60 seconds)
sleep 60

# 5. Initialize database and Kibana
docker-compose exec webapp python scripts/init_db.py
docker-compose exec webapp python scripts/setup_kibana_viz.py

# 6. Access the applications
# Web Application: http://localhost:8000
# Kibana: http://localhost:5601
# Elasticsearch: http://localhost:9200
# API: http://localhost:8000/api/v1
```

### Verify Installation

```bash
# Check all containers are running
docker-compose ps

# Check logs
docker-compose logs -f webapp

# Test Elasticsearch
curl http://localhost:9200/

# Test API
curl http://localhost:8000/api/v1/stats
```

## 📚 Documentation

### Complete Documentation
See [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md) for comprehensive documentation including:
- Architecture overview (C4 Model)
- Detailed component design
- API documentation
- Database schemas
- Deployment guides
- Troubleshooting

### Quick References
- [API Endpoints](./TECHNICAL_DOCUMENTATION.md#6-api-documentation)
- [Database Schema](./TECHNICAL_DOCUMENTATION.md#7-database-schema)
- [Logstash Pipeline](./TECHNICAL_DOCUMENTATION.md#42-logstash-pipeline-configuration)
- [Monitoring](./TECHNICAL_DOCUMENTATION.md#10-monitoring--logging)

## 🧪 Testing

### Run Tests Locally

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test category
pytest tests/test_auth.py -v          # Authentication tests
pytest tests/test_upload.py -v        # Upload validation tests
pytest tests/test_integration.py -v   # Integration tests
```

### Test Coverage
- **Unit Tests**: Authentication, validation, data types
- **Integration Tests**: API endpoints, database operations, aggregations
- **End-to-End**: Complete user workflows

### CI/CD Pipeline
Tests are automatically run on:
- Every push to `main` or `develop` branches
- Every pull request
- GitHub Actions handles: Linting → Unit Tests → Integration Tests → Build → Deploy

See [.github/workflows/ci-cd.yml](./.github/workflows/ci-cd.yml) for pipeline details.

## 📊 Dashboard & Visualizations

### Home Dashboard (`/`)
- 4 KPI cards: Total Logs, Avg Temperature, Energy Consumption, Active Sensors
- Real-time temperature graph by zone
- Recent alerts table

### Search Page (`/search`)
- Free-text search with filters
- Sensor type, building, zone filtering
- Date range selection
- Paginated results with sorting

### Kibana Dashboard (`/kibana`)
Embedded Kibana with 11 pre-configured visualizations:
1. Temperature by Zone (24h)
2. Status by Sensor Type
3. Sensor Values Timeline
4. Total Events Metric
5. Battery Level Metric
6. Critical Alerts Metric
7. Activity Timeline
8. Top Sensors Table
9. Building Comparison
10. Device Health Distribution
11. Zone Heatmap

## 📤 File Upload

### Supported Formats
- **CSV**: Comma-separated values with header row
- **JSON**: One JSON object per line (JSON Lines format)
- **LOG**: Text log files (with proper parsing)

### Sample CSV Format
```csv
timestamp,sensor_id,sensor_type,zone,value,unit,status,building_id
2025-12-30T11:57:12.966762,TEMP_zone_a_001,temperature,zone_a,22.5,°C,normal,Building_A
2025-12-30T11:57:13.000000,HUMIDITY_zone_a_002,humidity,zone_a,45.2,%,normal,Building_A
```

### Upload Limits
- Maximum file size: 100MB
- Allowed formats: CSV, JSON, LOG
- Files are validated before processing

## 🔌 API Endpoints

### Authentication
```
POST   /auth/register          - Register new user
POST   /auth/login             - Login (session-based)
POST   /auth/logout            - Logout
```

### Dashboard
```
GET    /                       - Home page
GET    /dashboard              - Dashboard with stats
GET    /api/v1/stats           - Dashboard statistics (JSON)
```

### Data Management
```
GET    /search                 - Search interface
GET    /api/v1/logs            - List all logs (paginated)
GET    /api/v1/files           - List uploaded files
POST   /upload/file            - Upload new file
GET    /upload/status/<id>     - Check upload status
```

### Kibana
```
GET    /kibana                 - Embedded Kibana dashboard
```

### Complete API documentation in [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md#6-api-documentation)

## 🔐 Security

### Authentication
- Session-based authentication with Flask-Login
- Password hashing with Werkzeug security
- Role-based access control (Admin, User, Viewer)

### Authorization
- Admin: Full system access
- User: Can upload, search, view dashboards
- Viewer: Read-only access

### Data Protection
- Elasticsearch authentication enabled
- Input validation on all endpoints
- Rate limiting on API endpoints
- HTTPS support ready (configure in .env)

## 📈 Performance

### Optimization Features
- Redis caching for frequently accessed data
- Elasticsearch query optimization
- Connection pooling
- Pagination for large result sets
- Index refresh interval: 1 second

### Monitoring
- Docker container health checks
- Application health endpoint: `GET /health`
- Elasticsearch cluster monitoring
- Performance metrics logging

## 🚢 Deployment

### Local Development
```bash
docker-compose up -d
```

### Production Deployment
```bash
export FLASK_ENV=production
export SECRET_KEY=your-secure-secret
docker-compose -f docker-compose.yml build
docker-compose up -d
```

### Docker Hub Registry
```bash
docker tag iot-platform:latest ghcr.io/wassimdgh/bigdata-elk:latest
docker push ghcr.io/wassimdgh/bigdata-elk:latest
```

## 🔧 Configuration

### Environment Variables
Copy `.env.example` to `.env` and configure:

```bash
# Flask
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Services
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
MONGODB_HOST=mongodb
REDIS_HOST=redis

# Security
ENABLE_HTTPS=False
SESSION_TIMEOUT=3600

# Features
ENABLE_CACHING=True
ENABLE_ALERTS=True
```

Full environment configuration in [.env.example](./.env.example)

## 📝 Project Structure

```
BigData-ELK/
├── app/                          # Flask application
│   ├── models/                   # Database models
│   ├── routes/                   # API routes & views
│   ├── services/                 # Business logic
│   ├── templates/                # HTML templates
│   └── static/                   # CSS, JS, images
├── scripts/                      # Initialization scripts
├── tests/                        # Automated tests
├── config/                       # Logstash, MongoDB config
├── data/uploads/                 # Uploaded files directory
├── .github/workflows/            # CI/CD pipeline
├── docker-compose.yml            # Container orchestration
├── Dockerfile                    # Flask app image
├── requirements.txt              # Python dependencies
├── TECHNICAL_DOCUMENTATION.md    # Complete documentation
└── README.md                     # This file
```

## 🐛 Troubleshooting

### Elasticsearch not responding
```bash
# Check status
curl http://localhost:9200/
docker logs elasticsearch

# Restart
docker restart elasticsearch
```

### Logstash not processing files
```bash
# Check logs
docker logs logstash

# Verify file access
docker exec logstash ls -la /data/uploads/

# Restart
docker restart logstash
```

### High memory usage
```bash
# View container stats
docker stats

# Reduce Java heap size
docker stop elasticsearch
export ES_JAVA_OPTS="-Xms512m -Xmx512m"
docker-compose up -d elasticsearch
```

### Port conflicts
If ports 8000, 5601, 9200, 27017, or 6379 are already in use:
```bash
# Edit docker-compose.yml and change port mappings
# Example: "9201:9200" (external:internal)
docker-compose up -d
```

## 📞 Support & Issues

- 📖 **Documentation**: See [TECHNICAL_DOCUMENTATION.md](./TECHNICAL_DOCUMENTATION.md)
- 🐛 **Bug Reports**: GitHub Issues
- 💬 **Questions**: GitHub Discussions
- 📧 **Email**: Check repository for contact info

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🎯 Project Status

- ✅ Core features complete
- ✅ CI/CD pipeline implemented
- ✅ Comprehensive documentation
- ✅ Test coverage (unit & integration)
- 🚀 Production-ready

### Roadmap
- [ ] Advanced ML anomaly detection
- [ ] Real-time WebSocket streaming
- [ ] Mobile app integration
- [ ] Advanced alerting system
- [ ] Data export (CSV, PDF)
- [ ] Multi-language support

## 📝 Version History

- **v1.0.0** (Jan 2026): Initial release with core features
  - IoT data ingestion
  - Real-time monitoring
  - Interactive dashboards
  - User authentication
  - REST API
  - CI/CD pipeline

---

**Last Updated**: January 3, 2026  
**Maintainer**: Development Team  
**Repository**: https://github.com/wassimdgh/BigData-ELK
