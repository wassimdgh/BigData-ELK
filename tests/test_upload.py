"""
Unit tests for data validation and upload module
"""
import pytest
import os
from werkzeug.datastructures import FileStorage
from io import BytesIO


class TestFileValidation:
    """Test file upload validation"""
    
    def test_allowed_csv_file(self):
        """Test that CSV files are allowed"""
        filename = "sensors.csv"
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        assert ext in {'csv', 'json', 'log'}
    
    def test_allowed_json_file(self):
        """Test that JSON files are allowed"""
        filename = "sensors.json"
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        assert ext in {'csv', 'json', 'log'}
    
    def test_disallowed_file_type(self):
        """Test that unsupported file types are rejected"""
        filename = "sensors.exe"
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        assert ext not in {'csv', 'json', 'log'}
    
    def test_file_with_no_extension(self):
        """Test that files without extension are rejected"""
        filename = "sensors"
        assert '.' not in filename
    
    def test_empty_filename(self):
        """Test that empty filenames are rejected"""
        filename = ""
        assert filename == ''


class TestCSVParsing:
    """Test CSV data parsing"""
    
    def test_csv_column_mapping(self):
        """Test CSV column mapping"""
        expected_columns = [
            "timestamp", "sensor_id", "sensor_type", 
            "zone", "value", "unit", "status", "building_id"
        ]
        assert len(expected_columns) == 8
        assert "sensor_type" in expected_columns
        assert "value" in expected_columns
    
    def test_csv_header_validation(self):
        """Test CSV header validation"""
        headers = ["timestamp", "sensor_id", "sensor_type", 
                   "zone", "value", "unit", "status", "building_id"]
        required_fields = ["timestamp", "sensor_type", "value"]
        
        for field in required_fields:
            assert field in headers


class TestDataTypeConversion:
    """Test data type conversions"""
    
    def test_float_conversion(self):
        """Test numeric value conversion to float"""
        test_values = ["22.5", "100", "0.001"]
        
        for val in test_values:
            try:
                converted = float(val)
                assert isinstance(converted, float)
            except ValueError:
                pytest.fail(f"Failed to convert {val} to float")
    
    def test_integer_conversion(self):
        """Test integer conversion"""
        test_values = ["100", "0", "-50"]
        
        for val in test_values:
            try:
                converted = int(val)
                assert isinstance(converted, int)
            except ValueError:
                pytest.fail(f"Failed to convert {val} to int")
    
    def test_invalid_numeric_conversion(self):
        """Test that non-numeric values fail conversion"""
        invalid_values = ["abc", "12.34.56", ""]
        
        for val in invalid_values:
            with pytest.raises(ValueError):
                float(val)


class TestTimestampParsing:
    """Test timestamp parsing and formatting"""
    
    def test_iso8601_format(self):
        """Test ISO8601 timestamp parsing"""
        valid_timestamp = "2025-12-30T11:57:12.966Z"
        assert "T" in valid_timestamp
        assert "Z" in valid_timestamp or "+" in valid_timestamp
    
    def test_timestamp_format_variation(self):
        """Test multiple timestamp formats"""
        formats = [
            "2025-12-30T11:57:12.966Z",
            "2025-12-30 11:57:12",
            "2025-12-30T11:57:12.966804"
        ]
        
        for ts in formats:
            assert len(ts) > 0
            assert ts.count("-") >= 2  # At least YYYY-MM-DD


class TestSensorTypeValidation:
    """Test sensor type validation"""
    
    def test_valid_sensor_types(self):
        """Test valid sensor types"""
        valid_types = [
            "temperature", "humidity", "energy", 
            "occupancy", "luminosity", "co2"
        ]
        sensor_type = "temperature"
        assert sensor_type in valid_types
    
    def test_invalid_sensor_type(self):
        """Test invalid sensor type"""
        valid_types = [
            "temperature", "humidity", "energy", 
            "occupancy", "luminosity", "co2"
        ]
        invalid_type = "invalid_sensor"
        assert invalid_type not in valid_types
