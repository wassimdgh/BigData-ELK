from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.services.database import get_elasticsearch, get_mongodb, get_redis
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Page d'accueil - Dashboard principal"""
    return render_template('index.html')

@main_bp.route('/kibana')
@login_required
def kibana():
    """Embedded Kibana Dashboard"""
    dashboard_url = "http://localhost:5601/app/dashboards#/view/2441ba60-e57f-11f0-9f88-973a8ca8d7dd?embed=true&_g=(refreshInterval:(pause:!f,value:30000),time:(from:'2025-11-01T00:00:00.000Z',to:'2026-01-31T23:59:59.999Z'))"
    return render_template('kibana.html', dashboard_url=dashboard_url)

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard avec statistiques"""
    try:
        es = get_elasticsearch()
        mongo = get_mongodb()
        
        # Récupérer les statistiques
        stats = get_dashboard_stats(es, mongo)
        
        return render_template('dashboard.html', stats=stats)
    except Exception as e:
        return render_template('dashboard.html', error=str(e))

def get_dashboard_stats(es, mongo):
    """Calculer les statistiques pour le dashboard"""
    stats = {
        'total_logs': 0,
        'total_files': 0,
        'alerts_today': 0,
        'avg_temperature': 0,
        'energy_consumption': 0,
        'occupancy_rate': 0
    }
    
    try:
        # Compter le nombre total de logs dans Elasticsearch
        result = es.count(index='iot-logs-*')
        stats['total_logs'] = result['count']
        
        # Compter les fichiers uploadés dans MongoDB
        stats['total_files'] = mongo.uploaded_files.count_documents({})
        
        # Compter les alertes d'aujourd'hui (critical + warning)
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        today_end = datetime.now().replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
        alerts_query = {
            "query": {
                "bool": {
                    "must": [
                        {"terms": {"status": ["critical", "warning"]}},
                        {"range": {"@timestamp": {"gte": today_start, "lte": today_end}}}
                    ]
                }
            },
            "size": 0
        }
        alerts_result = es.count(index='iot-logs-*', body=alerts_query)
        stats['alerts_today'] = alerts_result['count']
        
        # Température moyenne (toutes les données - all time)
        temp_query = {
            "query": {
                "term": {"sensor_type": "temperature"}
            },
            "aggs": {
                "avg_temp": {"avg": {"field": "value"}}
            },
            "size": 0
        }
        
        temp_result = es.search(index='iot-logs-*', body=temp_query)
        avg_temp_value = temp_result['aggregations']['avg_temp']['value']
        if avg_temp_value is not None:
            stats['avg_temperature'] = round(avg_temp_value, 1)
        
        # Consommation énergétique totale (all time)
        energy_query = {
            "query": {
                "term": {"sensor_type": "energy"}
            },
            "aggs": {
                "total_energy": {"sum": {"field": "value"}}
            },
            "size": 0
        }
        
        energy_result = es.search(index='iot-logs-*', body=energy_query)
        total_energy_value = energy_result['aggregations']['total_energy']['value']
        if total_energy_value is not None:
            stats['energy_consumption'] = round(total_energy_value, 2)
        
    except Exception as e:
        print(f"Erreur lors du calcul des stats: {e}")
    
    return stats
