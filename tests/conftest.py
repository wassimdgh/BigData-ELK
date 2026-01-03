"""
pytest configuration and fixtures
"""
import pytest
import os
import sys


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        "elasticsearch_url": "http://localhost:9200",
        "mongodb_url": "mongodb://localhost:27017",
        "redis_url": "redis://localhost:6379",
        "app_url": "http://localhost:8000"
    }


@pytest.fixture(scope="session")
def sample_csv_data():
    """Provide sample CSV data for testing"""
    return """timestamp,sensor_id,sensor_type,zone,value,unit,status,building_id
2025-12-30T11:57:12.966762,TEMP_zone_a_001,temperature,zone_a,22.5,°C,normal,Building_A
2025-12-30T11:57:13.000000,HUMIDITY_zone_a_002,humidity,zone_a,45.2,%,normal,Building_A
2025-12-30T11:57:14.000000,ENERGY_building_a_001,energy,zone_a,125.5,kWh,normal,Building_A
"""


@pytest.fixture(scope="session")
def sample_json_data():
    """Provide sample JSON data for testing"""
    return {
        "timestamp": "2025-12-30T11:57:12.966804",
        "sensor_id": "LUMI_zone_c_6373",
        "sensor_type": "luminosity",
        "zone": "zone_c",
        "value": 856.44,
        "unit": "lux",
        "status": "normal",
        "building_id": "Building_A",
        "metadata": {
            "firmware_version": "v1.5",
            "battery_level": 82
        }
    }


@pytest.fixture
def sensor_types():
    """Provide list of valid sensor types"""
    return [
        "temperature",
        "humidity",
        "energy",
        "occupancy",
        "luminosity",
        "co2"
    ]


@pytest.fixture
def buildings():
    """Provide list of buildings"""
    return ["Building_A", "Building_B", "Building_C"]


@pytest.fixture
def zones():
    """Provide list of zones"""
    return ["zone_a", "zone_b", "zone_c", "zone_d"]
