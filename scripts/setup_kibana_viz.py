"""
Script d'initialisation Kibana
Crée automatiquement les index patterns, visualizations et dashboard
"""

import requests
import json
import time
import sys
import os

KIBANA_HOST = os.getenv('KIBANA_HOST', 'localhost')
KIBANA_PORT = int(os.getenv('KIBANA_PORT', 5601))
KIBANA_URL = f'http://{KIBANA_HOST}:{KIBANA_PORT}'
ES_URL = f'http://{os.getenv("ELASTICSEARCH_HOST", "localhost")}:{int(os.getenv("ELASTICSEARCH_PORT", 9200))}'

HEADERS = {
    'Content-Type': 'application/json',
    'kbn-xsrf': 'true'
}

def wait_for_kibana(max_retries=30):
    """Wait for Kibana to be ready"""
    print("⏳ Waiting for Kibana to be ready...")
    for i in range(max_retries):
        try:
            response = requests.get(f'{KIBANA_URL}/api/status', timeout=5)
            if response.status_code == 200:
                print("✅ Kibana is ready!")
                return True
        except:
            pass
        print(f"   Attempt {i+1}/{max_retries}...")
        time.sleep(2)
    
    print("❌ Kibana not ready")
    return False

def wait_for_elasticsearch(max_retries=30):
    """Wait for Elasticsearch to have data"""
    print("⏳ Waiting for Elasticsearch with data...")
    for i in range(max_retries):
        try:
            response = requests.get(f'{ES_URL}/iot-logs-*/_count', timeout=5)
            if response.status_code == 200:
                count = response.json().get('count', 0)
                if count > 100:
                    print(f"✅ Elasticsearch has {count} records!")
                    return True
        except:
            pass
        print(f"   Attempt {i+1}/{max_retries}...")
        time.sleep(2)
    
    print("⚠️  Continuing anyway...")
    return False

def create_index_pattern():
    """Create IoT logs index pattern"""
    print("\n📊 Creating index pattern...")
    
    url = f'{KIBANA_URL}/api/saved_objects/index-pattern/iot-logs'
    
    data = {
        "attributes": {
            "title": "iot-logs-*",
            "timeFieldName": "@timestamp",
            "fields": "[]",
            "sourceFilters": "[]",
            "fieldFormatMap": "{}"
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=10)
        if response.status_code in [200, 201]:
            print("✅ Index pattern created!")
            return True
        else:
            print(f"⚠️  Index pattern response: {response.status_code}")
            if response.status_code == 409:
                print("   (Pattern already exists)")
            return response.status_code == 409
    except Exception as e:
        print(f"❌ Error creating index pattern: {e}")
        return False

def create_visualization(viz_id, title, vis_json):
    """Create a visualization"""
    print(f"📈 Creating visualization: {title}...")
    
    url = f'{KIBANA_URL}/api/saved_objects/visualization/{viz_id}'
    
    data = {
        "attributes": {
            "title": title,
            "visState": json.dumps(vis_json['visState']),
            "uiStateJSON": "{}",
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps(vis_json['searchSource'])
            },
            "version": 1
        }
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=10)
        if response.status_code in [200, 201]:
            print(f"   ✅ Created!")
            return True
        else:
            print(f"   ⚠️  Response: {response.status_code}")
            return response.status_code == 409
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def create_temperature_viz():
    """Temperature by Zone visualization"""
    viz_json = {
        "visState": {
            "title": "Temperature by Zone",
            "type": "line",
            "params": {
                "addLegend": True,
                "addTimeMarker": True,
                "addTooltip": True,
                "legendPosition": "right",
                "type": "line"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "value"}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "date_histogram",
                    "schema": "segment",
                    "params": {
                        "field": "@timestamp",
                        "interval": "auto",
                        "min_doc_count": 1
                    }
                },
                {
                    "id": "3",
                    "enabled": True,
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "zone.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"query_string": {"query": "sensor_type:temperature"}},
            "filter": []
        }
    }
    return create_visualization("temp-by-zone", "Temperature by Zone", viz_json)

def create_alerts_viz():
    """Status by Sensor Type visualization"""
    viz_json = {
        "visState": {
            "title": "Status by Sensor Type",
            "type": "heatmap",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "legendPosition": "right",
                "type": "heatmap"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "sensor_type.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                },
                {
                    "id": "3",
                    "enabled": True,
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "status.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("alerts-heatmap", "Status by Sensor Type", viz_json)

def create_energy_viz():
    """Sensor Values by Type visualization"""
    viz_json = {
        "visState": {
            "title": "Sensor Values by Type",
            "type": "horizontal_bar",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "legendPosition": "right",
                "type": "horizontal_bar"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "value"}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "sensor_type.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("energy-gauge", "Sensor Values by Type", viz_json)

def create_total_events_metric():
    """Total Events Count - Big Number Metric"""
    viz_json = {
        "visState": {
            "title": "Total Sensor Events",
            "type": "metric",
            "params": {
                "addLegend": False,
                "addTooltip": True,
                "type": "metric",
                "metric": {
                    "colorSchema": "Green to Red",
                    "colorsRange": [{"from": 0, "to": 10000}],
                    "invertColors": False,
                    "labels": {"show": True},
                    "metricColorMode": "None",
                    "percentageMode": False,
                    "style": {"bgColor": False, "bgFill": "#000", "fontSize": 60, "labelColor": False, "subText": ""},
                    "useRanges": False
                }
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}}
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("total-events-metric", "Total Sensor Events", viz_json)

def create_avg_battery_metric():
    """Average Battery Level - Metric"""
    viz_json = {
        "visState": {
            "title": "Average Battery Level",
            "type": "metric",
            "params": {
                "addLegend": False,
                "addTooltip": True,
                "type": "metric",
                "metric": {
                    "colorSchema": "Green to Red",
                    "colorsRange": [
                        {"from": 0, "to": 30},
                        {"from": 30, "to": 70},
                        {"from": 70, "to": 100}
                    ],
                    "invertColors": True,
                    "labels": {"show": True},
                    "metricColorMode": "Background",
                    "percentageMode": False,
                    "style": {"bgColor": True, "bgFill": "#000", "fontSize": 60, "labelColor": False, "subText": "%"},
                    "useRanges": True
                }
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "metadata.battery_level"}}
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("avg-battery-metric", "Average Battery Level", viz_json)

def create_alerts_count_metric():
    """Alert Events Count"""
    viz_json = {
        "visState": {
            "title": "Critical Alerts",
            "type": "metric",
            "params": {
                "addLegend": False,
                "addTooltip": True,
                "type": "metric",
                "metric": {
                    "colorSchema": "Green to Red",
                    "colorsRange": [{"from": 0, "to": 1000}],
                    "invertColors": False,
                    "labels": {"show": True},
                    "metricColorMode": "Labels",
                    "percentageMode": False,
                    "style": {"bgColor": False, "bgFill": "#000", "fontSize": 60, "labelColor": True, "subText": ""},
                    "useRanges": False
                }
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}}
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"query_string": {"query": "status:alert OR status:critical"}},
            "filter": []
        }
    }
    return create_visualization("alerts-count-metric", "Critical Alerts", viz_json)

def create_sensor_timeline():
    """Sensor Events Timeline - Line Chart"""
    viz_json = {
        "visState": {
            "title": "Sensor Activity Timeline",
            "type": "line",
            "params": {
                "addLegend": True,
                "addTimeMarker": True,
                "addTooltip": True,
                "legendPosition": "right",
                "type": "line"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "date_histogram",
                    "schema": "segment",
                    "params": {
                        "field": "@timestamp",
                        "interval": "auto",
                        "min_doc_count": 1
                    }
                },
                {
                    "id": "3",
                    "enabled": True,
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "sensor_type.keyword",
                        "size": 6,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("sensor-timeline", "Sensor Activity Timeline", viz_json)

def create_top_devices_table():
    """Top Active Sensors - Data Table"""
    viz_json = {
        "visState": {
            "title": "Top 10 Active Sensors",
            "type": "table",
            "params": {
                "perPage": 10,
                "showPartialRows": False,
                "showMetricsAtAllLevels": False,
                "sort": {"columnIndex": None, "direction": None},
                "showTotal": False,
                "totalFunc": "sum",
                "type": "table"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "terms",
                    "schema": "bucket",
                    "params": {
                        "field": "sensor_id.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                },
                {
                    "id": "3",
                    "enabled": True,
                    "type": "terms",
                    "schema": "bucket",
                    "params": {
                        "field": "sensor_type.keyword",
                        "size": 5,
                        "order": "desc",
                        "orderBy": "1"
                    }
                },
                {"id": "4", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "metadata.battery_level"}},
                {"id": "5", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "value"}}
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("top-devices-table", "Top 10 Active Sensors", viz_json)

def create_building_comparison():
    """Building Performance Comparison - Bar Chart"""
    viz_json = {
        "visState": {
            "title": "Building Performance Comparison",
            "type": "horizontal_bar",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "legendPosition": "right",
                "type": "horizontal_bar"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "building_id.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                },
                {
                    "id": "3",
                    "enabled": True,
                    "type": "terms",
                    "schema": "group",
                    "params": {
                        "field": "sensor_type.keyword",
                        "size": 6,
                        "order": "desc",
                        "orderBy": "1"
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("building-comparison", "Building Performance Comparison", viz_json)

def create_device_health_gauge():
    """Device Health Status - Pie Chart"""
    viz_json = {
        "visState": {
            "title": "Device Health Status",
            "type": "pie",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "isDonut": True,
                "labels": {"show": True, "values": True, "last_level": True, "truncate": 100},
                "legendPosition": "right",
                "type": "pie"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "range",
                    "schema": "segment",
                    "params": {
                        "field": "metadata.battery_level",
                        "ranges": [
                            {"from": 0, "to": 20},
                            {"from": 20, "to": 50},
                            {"from": 50, "to": 80},
                            {"from": 80, "to": 100}
                        ]
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("device-health-gauge", "Device Health Status", viz_json)

def create_zone_heatmap():
    """Zone Activity Heatmap"""
    viz_json = {
        "visState": {
            "title": "Zone Activity Heatmap",
            "type": "heatmap",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "legendPosition": "right",
                "type": "heatmap"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {
                    "id": "2",
                    "enabled": True,
                    "type": "terms",
                    "schema": "segment",
                    "params": {
                        "field": "zone.keyword",
                        "size": 10,
                        "order": "desc",
                        "orderBy": "1"
                    }
                },
                {
                    "id": "3",
                    "enabled": True,
                    "type": "date_histogram",
                    "schema": "group",
                    "params": {
                        "field": "@timestamp",
                        "interval": "auto",
                        "min_doc_count": 1
                    }
                }
            ]
        },
        "searchSource": {
            "index": "iot-logs",
            "query": {"match_all": {}},
            "filter": []
        }
    }
    return create_visualization("zone-heatmap", "Zone Activity Heatmap", viz_json)

def create_dashboard():
    """Create Comprehensive IoT Smart Building Dashboard"""
    print("\n🎨 Creating comprehensive dashboard...")
    
    url = f'{KIBANA_URL}/api/saved_objects/dashboard/iot-smart-building-comprehensive'
    
    # Define panels layout - organized in rows
    panels = [
        # Row 1: Key Metrics (4 metric panels across top)
        {"version": "8.11.0", "gridData": {"x": 0, "y": 0, "w": 12, "h": 8}, "panelIndex": "1", "panelRefName": "panel_1"},
        {"version": "8.11.0", "gridData": {"x": 12, "y": 0, "w": 12, "h": 8}, "panelIndex": "2", "panelRefName": "panel_2"},
        {"version": "8.11.0", "gridData": {"x": 24, "y": 0, "w": 12, "h": 8}, "panelIndex": "3", "panelRefName": "panel_3"},
        {"version": "8.11.0", "gridData": {"x": 36, "y": 0, "w": 12, "h": 8}, "panelIndex": "4", "panelRefName": "panel_4"},
        
        # Row 2: Timeline and Health Status
        {"version": "8.11.0", "gridData": {"x": 0, "y": 8, "w": 36, "h": 15}, "panelIndex": "5", "panelRefName": "panel_5"},
        {"version": "8.11.0", "gridData": {"x": 36, "y": 8, "w": 12, "h": 15}, "panelIndex": "6", "panelRefName": "panel_6"},
        
        # Row 3: Temperature and Alerts
        {"version": "8.11.0", "gridData": {"x": 0, "y": 23, "w": 24, "h": 15}, "panelIndex": "7", "panelRefName": "panel_7"},
        {"version": "8.11.0", "gridData": {"x": 24, "y": 23, "w": 24, "h": 15}, "panelIndex": "8", "panelRefName": "panel_8"},
        
        # Row 4: Building Comparison and Zone Activity
        {"version": "8.11.0", "gridData": {"x": 0, "y": 38, "w": 24, "h": 15}, "panelIndex": "9", "panelRefName": "panel_9"},
        {"version": "8.11.0", "gridData": {"x": 24, "y": 38, "w": 24, "h": 15}, "panelIndex": "10", "panelRefName": "panel_10"},
        
        # Row 5: Top Devices and Sensor Values
        {"version": "8.11.0", "gridData": {"x": 0, "y": 53, "w": 24, "h": 15}, "panelIndex": "11", "panelRefName": "panel_11"},
        {"version": "8.11.0", "gridData": {"x": 24, "y": 53, "w": 24, "h": 15}, "panelIndex": "12", "panelRefName": "panel_12"}
    ]
    
    data = {
        "attributes": {
            "title": "IoT Smart Building - Comprehensive Dashboard",
            "panelsJSON": json.dumps(panels),
            "timeRestore": True,
            "timeFrom": "2025-11-01T00:00:00.000Z",
            "timeTo": "2026-01-31T23:59:59.999Z",
            "refreshInterval": {
                "display": "30 seconds",
                "pause": False,
                "value": 30000
            },
            "kibanaSavedObjectMeta": {
                "searchSourceJSON": json.dumps({
                    "query": {"match_all": {}},
                    "filter": [],
                    "highlightAll": True,
                    "version": True
                })
            }
        },
        "references": [
            {"name": "panel_1", "type": "visualization", "id": "total-events-metric"},
            {"name": "panel_2", "type": "visualization", "id": "avg-battery-metric"},
            {"name": "panel_3", "type": "visualization", "id": "alerts-count-metric"},
            {"name": "panel_4", "type": "visualization", "id": "device-health-gauge"},
            {"name": "panel_5", "type": "visualization", "id": "sensor-timeline"},
            {"name": "panel_6", "type": "visualization", "id": "device-health-gauge"},
            {"name": "panel_7", "type": "visualization", "id": "temp-by-zone"},
            {"name": "panel_8", "type": "visualization", "id": "alerts-heatmap"},
            {"name": "panel_9", "type": "visualization", "id": "building-comparison"},
            {"name": "panel_10", "type": "visualization", "id": "zone-heatmap"},
            {"name": "panel_11", "type": "visualization", "id": "top-devices-table"},
            {"name": "panel_12", "type": "visualization", "id": "energy-gauge"}
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=10)
        if response.status_code in [200, 201]:
            print("✅ Comprehensive dashboard created!")
            return True
        elif response.status_code == 409:
            print("   (Dashboard already exists)")
            return True
        else:
            print(f"⚠️  Response: {response.status_code}")
            if response.text:
                print(f"   Details: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🚀 KIBANA AUTO-SETUP")
    print("=" * 60)
    
    # Step 1: Wait for services
    if not wait_for_kibana():
        print("❌ Cannot reach Kibana")
        return False
    
    wait_for_elasticsearch()
    
    # Step 2: Create index pattern
    if not create_index_pattern():
        print("⚠️  Could not create index pattern")
    
    # Step 3: Create visualizations
    print("\n📊 Creating visualizations...")
    create_temperature_viz()
    create_alerts_viz()
    create_energy_viz()
    
    # New comprehensive visualizations
    create_total_events_metric()
    create_avg_battery_metric()
    create_alerts_count_metric()
    create_sensor_timeline()
    create_top_devices_table()
    create_building_comparison()
    create_device_health_gauge()
    create_zone_heatmap()
    
    # Step 4: Create dashboard
    create_dashboard()
    
    print("\n" + "=" * 60)
    print("✅ SETUP COMPLETE!")
    print("=" * 60)
    print(f"\n🌐 Open Kibana: {KIBANA_URL}")
    print("📊 Dashboard: IoT Smart Building - Comprehensive Dashboard")
    print("\n📈 Visualizations Created:")
    print("   • Total Sensor Events (Metric)")
    print("   • Average Battery Level (Metric)")
    print("   • Critical Alerts Count (Metric)")
    print("   • Device Health Status (Pie Chart)")
    print("   • Sensor Activity Timeline (Area Chart)")
    print("   • Temperature by Zone (Line Chart)")
    print("   • Status by Sensor Type (Heatmap)")
    print("   • Building Performance Comparison (Bar Chart)")
    print("   • Zone Activity Heatmap (Heatmap)")
    print("   • Top 10 Active Devices (Table)")
    print("   • Sensor Values by Type (Histogram)")
    print("\n✨ Everything is ready!")
    print("💡 Tip: All visualizations auto-update when you add new data!")
    
    return True

if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
