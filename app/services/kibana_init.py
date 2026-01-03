"""
Module d'initialisation Kibana
Crée automatiquement les visualizations et dashboard au démarrage
"""

import requests
import json
import logging
import threading
import time
import os

logger = logging.getLogger(__name__)

KIBANA_URL = os.getenv('KIBANA_URL', 'http://localhost:5601')
ES_URL = os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200')

HEADERS = {
    'Content-Type': 'application/json',
    'kbn-xsrf': 'true'
}

def init_kibana_async():
    """Initialize Kibana in background thread"""
    def setup():
        try:
            logger.info("🔄 Starting Kibana setup in background...")
            time.sleep(5)  # Wait for services to be fully ready
            
            if create_index_pattern():
                create_temperature_viz()
                create_alerts_viz()
                create_energy_viz()
                create_dashboard()
                logger.info("✅ Kibana setup complete!")
            else:
                logger.warning("⚠️  Could not create index pattern")
        except Exception as e:
            logger.error(f"❌ Error in Kibana setup: {e}")
    
    thread = threading.Thread(target=setup, daemon=True)
    thread.start()

def wait_for_service(url, max_retries=15):
    """Wait for a service to be available"""
    for i in range(max_retries):
        try:
            response = requests.get(url, timeout=2)
            if response.status_code < 500:
                return True
        except:
            pass
        time.sleep(1)
    return False

def create_index_pattern():
    """Create IoT logs index pattern"""
    logger.info("📊 Creating index pattern...")
    
    if not wait_for_service(f'{KIBANA_URL}/api/status'):
        logger.error("Kibana not available")
        return False
    
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
            logger.info("✅ Index pattern created")
            return True
        elif response.status_code == 409:
            logger.info("   (Index pattern already exists)")
            return True
        else:
            logger.warning(f"⚠️  Response: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error creating index pattern: {e}")
        return False

def create_visualization(viz_id, title, vis_json):
    """Create a visualization"""
    logger.info(f"   📈 Creating {title}...")
    
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
            logger.info(f"      ✅ {title} created")
            return True
        elif response.status_code == 409:
            logger.info(f"      (Already exists)")
            return True
        else:
            logger.warning(f"      ⚠️  Response: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error creating {title}: {e}")
        return False

def create_temperature_viz():
    """Temperature by Zone visualization"""
    viz_json = {
        "visState": {
            "title": "Temperature by Zone",
            "type": "line",
            "params": {
                "grid": {"categoryLines": False, "valueAxis": "ValueAxis-1"},
                "categoryAxes": [
                    {
                        "id": "CategoryAxis-1",
                        "type": "category",
                        "position": "bottom",
                        "show": True,
                        "scale": {"type": "linear"},
                        "labels": {"show": True, "truncate": 100},
                        "title": {}
                    }
                ],
                "valueAxes": [
                    {
                        "id": "ValueAxis-1",
                        "name": "LeftAxis-1",
                        "type": "value",
                        "position": "left",
                        "show": True,
                        "scale": {"type": "linear", "mode": "normal"},
                        "labels": {"show": True, "truncate": 100},
                        "title": {"text": "Temperature (°C)"}
                    }
                ],
                "seriesParams": [{"show": True, "type": "line", "interpolate": "linear", "valueAxis": "ValueAxis-1"}],
                "legend": {"show": True, "position": "right"},
                "isVislibVis": True,
                "addLegend": True
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "avg", "schema": "metric", "params": {"field": "temperature"}},
                {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {"field": "zone", "size": 10}},
                {"id": "3", "enabled": True, "type": "date_histogram", "schema": "group", "params": {"field": "@timestamp", "interval": "auto"}}
            ]
        },
        "searchSource": {"index": "iot-logs", "query": {"match_all": {}}, "filter": []}
    }
    return create_visualization("temp-by-zone", "Temperature by Zone", viz_json)

def create_alerts_viz():
    """Alerts Heatmap visualization"""
    viz_json = {
        "visState": {
            "title": "Alerts by Zone",
            "type": "heatmap",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "cellNormalizer": 0,
                "col": "",
                "colLabelFontSize": 12,
                "colWidth": 30,
                "invertColors": False,
                "legendPosition": "right",
                "percentageMode": False,
                "rowLabelFontSize": 12,
                "tooltip": {"show": True},
                "type": "heatmap"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "count", "schema": "metric", "params": {}},
                {"id": "2", "enabled": True, "type": "terms", "schema": "segment", "params": {"field": "zone", "size": 10}},
                {"id": "3", "enabled": True, "type": "terms", "schema": "group", "params": {"field": "alert_level", "size": 5}}
            ]
        },
        "searchSource": {"index": "iot-logs", "query": {"match_all": {}}, "filter": [{"term": {"sensor_type": "alert"}}]}
    }
    return create_visualization("alerts-heatmap", "Alerts by Zone", viz_json)

def create_energy_viz():
    """Energy Consumption Gauge visualization"""
    viz_json = {
        "visState": {
            "title": "Energy Consumption",
            "type": "gauge",
            "params": {
                "addLegend": True,
                "addTooltip": True,
                "gauge": {
                    "alignment": "automatic",
                    "colorSchema": "Green-Yellow-Red",
                    "extendRange": True,
                    "gaugeColorMode": "Labels",
                    "gaugeType": "Arc",
                    "invertColors": False,
                    "labels": {"currentMetricLabel": "kWh", "show": True},
                    "orientation": "vertical",
                    "percentageMode": False,
                    "scale": {"labels": [], "show": False, "type": "linear"},
                    "thresholds": "0,10000"
                },
                "type": "gauge"
            },
            "aggs": [
                {"id": "1", "enabled": True, "type": "sum", "schema": "metric", "params": {"field": "energy"}},
                {"id": "2", "enabled": True, "type": "date_histogram", "schema": "group", "params": {"field": "@timestamp", "interval": "auto"}}
            ]
        },
        "searchSource": {"index": "iot-logs", "query": {"match_all": {}}, "filter": [{"term": {"sensor_type": "energy"}}]}
    }
    return create_visualization("energy-gauge", "Energy Consumption", viz_json)

def create_dashboard():
    """Create IoT Smart Building Dashboard"""
    logger.info("   🎨 Creating dashboard...")
    
    url = f'{KIBANA_URL}/api/saved_objects/dashboard/iot-smart-building'
    
    panels = [
        {
            "version": "8.11.0",
            "gridData": {"x": 0, "y": 0, "w": 24, "h": 15},
            "panelIndex": "1",
            "embeddableConfig": {},
            "panelRefName": "panel_1"
        },
        {
            "version": "8.11.0",
            "gridData": {"x": 24, "y": 0, "w": 24, "h": 15},
            "panelIndex": "2",
            "embeddableConfig": {},
            "panelRefName": "panel_2"
        },
        {
            "version": "8.11.0",
            "gridData": {"x": 0, "y": 15, "w": 24, "h": 15},
            "panelIndex": "3",
            "embeddableConfig": {},
            "panelRefName": "panel_3"
        }
    ]
    
    data = {
        "attributes": {
            "title": "IoT Smart Building - Monitoring",
            "panelsJSON": json.dumps(panels),
            "timeRestore": True,
            "timeFrom": "now-7d",
            "timeTo": "now",
            "refreshInterval": {"display": "30 seconds", "pause": False, "value": 30000},
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
            {"name": "panel_1", "type": "visualization", "id": "temp-by-zone"},
            {"name": "panel_2", "type": "visualization", "id": "alerts-heatmap"},
            {"name": "panel_3", "type": "visualization", "id": "energy-gauge"}
        ]
    }
    
    try:
        response = requests.post(url, json=data, headers=HEADERS, timeout=10)
        if response.status_code in [200, 201]:
            logger.info("      ✅ Dashboard created")
            return True
        elif response.status_code == 409:
            logger.info("      (Dashboard already exists)")
            return True
        else:
            logger.warning(f"      ⚠️  Response: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Error creating dashboard: {e}")
        return False
