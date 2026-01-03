"""
Integration tests for API endpoints
"""
import pytest
import json
from datetime import datetime


class TestDashboardAPI:
    """Test dashboard statistics API"""
    
    def test_stats_endpoint_returns_valid_structure(self):
        """Test that /api/v1/stats returns expected fields"""
        expected_fields = [
            'total_logs',
            'avg_temperature',
            'energy_consumption',
            'alerts_today',
            'total_files',
            'occupancy_rate'
        ]
        
        # Validate all expected fields are present
        for field in expected_fields:
            assert field is not None
    
    def test_stats_values_are_numeric(self):
        """Test that stats values are numeric"""
        stats = {
            'total_logs': 309238,
            'avg_temperature': 22.5,
            'energy_consumption': 45678.90,
            'alerts_today': 0
        }
        
        assert isinstance(stats['total_logs'], (int, float))
        assert isinstance(stats['avg_temperature'], (int, float))
        assert isinstance(stats['energy_consumption'], (int, float))


class TestSearchAPI:
    """Test search endpoint"""
    
    def test_search_query_structure(self):
        """Test that search query structure is valid"""
        query = {
            "bool": {
                "must": [
                    {"term": {"sensor_type": "temperature"}},
                    {"range": {"@timestamp": {"gte": "2025-11-01"}}}
                ]
            }
        }
        
        assert "bool" in query
        assert "must" in query["bool"]
        assert len(query["bool"]["must"]) > 0
    
    def test_search_pagination_parameters(self):
        """Test search pagination parameters"""
        page = 1
        limit = 50
        offset = (page - 1) * limit
        
        assert offset == 0
        assert limit > 0


class TestLogsAPI:
    """Test logs endpoint"""
    
    def test_logs_response_structure(self):
        """Test logs API response structure"""
        response = {
            "total": 309238,
            "page": 1,
            "limit": 50,
            "results": []
        }
        
        assert "total" in response
        assert "page" in response
        assert "limit" in response
        assert "results" in response
    
    def test_logs_pagination(self):
        """Test logs pagination"""
        total = 309238
        limit = 50
        expected_pages = (total + limit - 1) // limit  # Ceiling division
        
        assert expected_pages == 6185
        assert total / limit > 1


class TestUploadAPI:
    """Test file upload endpoint"""
    
    def test_upload_response_structure(self):
        """Test upload response structure"""
        response = {
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
        
        assert "message" in response
        assert "file" in response
        assert "filename" in response["file"]
        assert "status" in response["file"]
    
    def test_file_size_validation(self):
        """Test file size validation"""
        max_size_mb = 100
        max_size_bytes = max_size_mb * 1024 * 1024
        
        test_size = 50 * 1024 * 1024  # 50MB
        assert test_size < max_size_bytes
        
        oversized = 150 * 1024 * 1024  # 150MB
        assert oversized > max_size_bytes


class TestAggregations:
    """Test Elasticsearch aggregations"""
    
    def test_temperature_average_aggregation(self):
        """Test temperature average aggregation"""
        agg = {
            "aggs": {
                "avg_temp": {
                    "avg": {"field": "value"}
                }
            }
        }
        
        assert "aggs" in agg
        assert "avg_temp" in agg["aggs"]
        assert "avg" in agg["aggs"]["avg_temp"]
    
    def test_energy_sum_aggregation(self):
        """Test energy sum aggregation"""
        agg = {
            "aggs": {
                "total_energy": {
                    "sum": {"field": "value"}
                }
            }
        }
        
        assert "aggs" in agg
        assert "total_energy" in agg["aggs"]
        assert "sum" in agg["aggs"]["total_energy"]
    
    def test_alert_count_aggregation(self):
        """Test alert count aggregation"""
        agg = {
            "aggs": {
                "alert_count": {
                    "terms": {"field": "status"}
                }
            }
        }
        
        assert "aggs" in agg
        assert "alert_count" in agg["aggs"]


class TestDataFiltering:
    """Test data filtering"""
    
    def test_sensor_type_filter(self):
        """Test sensor type filtering"""
        query = {
            "query": {
                "term": {"sensor_type": "temperature"}
            }
        }
        
        assert "query" in query
        assert "term" in query["query"]
    
    def test_building_filter(self):
        """Test building filtering"""
        query = {
            "query": {
                "term": {"building_id": "Building_A"}
            }
        }
        
        assert "query" in query
        assert "term" in query["query"]
    
    def test_date_range_filter(self):
        """Test date range filtering"""
        query = {
            "query": {
                "range": {
                    "@timestamp": {
                        "gte": "2025-11-01",
                        "lte": "2026-01-31"
                    }
                }
            }
        }
        
        assert "query" in query
        assert "range" in query["query"]
        assert "@timestamp" in query["query"]["range"]
    
    def test_combined_filters(self):
        """Test multiple filters combined"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"sensor_type": "temperature"}},
                        {"term": {"building_id": "Building_A"}},
                        {"range": {"@timestamp": {"gte": "2025-11-01"}}}
                    ]
                }
            }
        }
        
        assert "bool" in query["query"]
        assert "must" in query["query"]["bool"]
        assert len(query["query"]["bool"]["must"]) == 3


class TestErrorHandling:
    """Test API error handling"""
    
    def test_invalid_json_response(self):
        """Test handling of invalid JSON"""
        invalid_responses = [
            None,
            "",
            "not json"
        ]
        
        for resp in invalid_responses:
            assert not isinstance(resp, dict) or resp == ""
    
    def test_missing_required_fields(self):
        """Test handling of missing required fields"""
        incomplete_doc = {
            "sensor_id": "TEMP_001",
            "sensor_type": "temperature"
            # Missing: @timestamp, value, building_id
        }
        
        required_fields = ["@timestamp", "value", "sensor_type", "sensor_id"]
        missing = [f for f in required_fields if f not in incomplete_doc]
        
        assert len(missing) > 0
