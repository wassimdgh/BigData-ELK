from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from app.services.database import get_elasticsearch, get_mongodb
from app.services.redis_cache import cached_route
from datetime import datetime

search_bp = Blueprint('search', __name__)

@search_bp.route('/', methods=['GET'])
@login_required
def search_page():
    """Page de recherche"""
    return render_template('search.html')

@search_bp.route('/query', methods=['GET', 'POST'])
@login_required
@cached_route(ttl=300)  # Cache search results for 5 minutes
def search_logs():

    """Recherche dans les logs"""
    try:
        es = get_elasticsearch()
        mongo = get_mongodb()
        
        # Récupérer les paramètres de recherche
        if request.method == 'POST':
            data = request.get_json()
        else:
            data = request.args
        
        query_text = data.get('q', '')
        sensor_type = data.get('sensor_type')
        zone = data.get('zone')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        alert_level = data.get('alert_level')
        page = int(data.get('page', 1))
        per_page = int(data.get('per_page', 50))
        
        # Construire la requête Elasticsearch
        must_conditions = []
        
        # Recherche textuelle
        if query_text:
            must_conditions.append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["sensor_id", "zone", "sensor_type", "alert_message"]
                }
            })
        
        # Filtres
        if sensor_type:
            must_conditions.append({"term": {"sensor_type": sensor_type}})
        
        if zone:
            must_conditions.append({"term": {"zone": zone}})
        
        if alert_level:
            must_conditions.append({"term": {"status": alert_level}})
        
        # Filtre de date
        if date_from or date_to:
            date_range = {}
            if date_from:
                date_range["gte"] = date_from
            if date_to:
                date_range["lte"] = date_to
            
            must_conditions.append({
                "range": {"@timestamp": date_range}
            })
        
        # Requête finale
        query = {
            "bool": {
                "must": must_conditions if must_conditions else [{"match_all": {}}]
            }
        }
        
        # Calculer l'offset
        from_index = (page - 1) * per_page
        
        # Exécuter la recherche
        result = es.search(
            index='iot-logs-*',
            body={
                "query": query,
                "from": from_index,
                "size": per_page,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
        )
        
        # Extraire les résultats
        logs = []
        for hit in result['hits']['hits']:
            log = hit['_source']
            log['_id'] = hit['_id']
            log['_score'] = hit['_score']
            logs.append(log)
        
        total = result['hits']['total']['value']
        
        # Enregistrer l'historique de recherche dans MongoDB
        search_history = {
            'query': query_text,
            'filters': {
                'sensor_type': sensor_type,
                'zone': zone,
                'alert_level': alert_level,
                'date_from': date_from,
                'date_to': date_to
            },
            'results_count': total,
            'search_date': datetime.now(),
            'user_id': request.args.get('user_id', 'anonymous')
        }
        mongo.search_history.insert_one(search_history)
        
        return jsonify({
            'logs': logs,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page,
            'took_ms': result['took']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@search_bp.route('/filters', methods=['GET'])
def get_search_filters():
    """Obtenir les valeurs possibles pour les filtres"""
    try:
        es = get_elasticsearch()
        
        # Récupérer les valeurs uniques pour les filtres
        filters = {
            'sensor_types': [],
            'zones': [],
            'alert_levels': []
        }
        
        # Sensor types
        result = es.search(
            index='iot-logs-*',
            body={
                "aggs": {
                    "sensor_types": {
                        "terms": {"field": "sensor_type.keyword", "size": 100}
                    }
                },
                "size": 0
            }
        )
        filters['sensor_types'] = [
            bucket['key'] for bucket in result['aggregations']['sensor_types']['buckets']
        ]
        
        # Zones
        result = es.search(
            index='iot-logs-*',
            body={
                "aggs": {
                    "zones": {
                        "terms": {"field": "zone.keyword", "size": 100}
                    }
                },
                "size": 0
            }
        )
        filters['zones'] = [
            bucket['key'] for bucket in result['aggregations']['zones']['buckets']
        ]
        
        # Alert levels
        result = es.search(
            index='iot-logs-*',
            body={
                "aggs": {
                    "alert_levels": {
                        "terms": {"field": "alert_level.keyword", "size": 100}
                    }
                },
                "size": 0
            }
        )
        filters['alert_levels'] = [
            bucket['key'] for bucket in result['aggregations']['alert_levels']['buckets']
        ]
        
        return jsonify(filters), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
