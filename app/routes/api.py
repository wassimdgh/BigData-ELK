from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.services.database import get_elasticsearch, get_mongodb
from app.services.redis_cache import cached_route, get_cache_stats
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/logs', methods=['GET'])
@login_required
@cached_route(ttl=300)
def get_logs():
    """Récupérer la liste paginée des logs
    ---
    tags:
      - Logs
    parameters:
      - in: query
        name: page
        type: integer
        default: 1
        description: Numéro de page
      - in: query
        name: per_page
        type: integer
        default: 50
        description: Nombre d'éléments par page
      - in: query
        name: sensor_type
        type: string
        description: Type de capteur (ex. temperature)
      - in: query
        name: zone
        type: string
        description: Zone du bâtiment (ex. A, B)
      - in: query
        name: alert_level
        type: string
        description: Niveau d'alerte
    responses:
      200:
        description: Résultat paginé des logs
        schema:
          type: object
          properties:
            logs:
              type: array
              items:
                type: object
            total:
              type: integer
            page:
              type: integer
            per_page:
              type: integer
            pages:
              type: integer
      500:
        description: Erreur serveur
    """
    try:
        es = get_elasticsearch()

        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        from_index = (page - 1) * per_page

        sensor_type = request.args.get('sensor_type')
        zone = request.args.get('zone')
        alert_level = request.args.get('alert_level')

        query = {"bool": {"must": []}}
        if sensor_type:
            query["bool"]["must"].append({"term": {"sensor_type": sensor_type}})
        if zone:
            query["bool"]["must"].append({"term": {"zone": zone}})
        if alert_level:
            query["bool"]["must"].append({"term": {"alert_level": alert_level}})
        if not query["bool"]["must"]:
            query = {"match_all": {}}

        result = es.search(
            index='iot-logs-*',
            body={
                "query": query,
                "from": from_index,
                "size": per_page,
                "sort": [{"@timestamp": {"order": "desc"}}]
            }
        )

        logs = [hit['_source'] for hit in result['hits']['hits']]
        total = result['hits']['total']['value']

        return jsonify({
            'logs': logs,
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/logs/<log_id>', methods=['GET'])
@login_required
def get_log_detail(log_id):
    """Récupérer le détail d'un log spécifique
    ---
    tags:
      - Logs
    parameters:
      - in: path
        name: log_id
        type: string
        required: true
        description: Identifiant du log
    responses:
      200:
        description: Détail du log
        schema:
          type: object
      404:
        description: Log introuvable
      500:
        description: Erreur serveur
    """
    try:
        es = get_elasticsearch()

        result = es.search(
            index='iot-logs-*',
            body={
                "query": {"ids": {"values": [log_id]}}
            }
        )

        if result['hits']['total']['value'] == 0:
            return jsonify({'error': 'Log not found'}), 404

        log = result['hits']['hits'][0]['_source']
        return jsonify(log), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/stats', methods=['GET'])
@login_required
@cached_route(ttl=600)
def get_stats():
    """Récupérer les statistiques globales
    ---
    tags:
      - Stats
    responses:
      200:
        description: Statistiques globales
        schema:
          type: object
          properties:
            total_logs:
              type: integer
            total_files:
              type: integer
            sensors_count:
              type: integer
            avg_temperature:
              type: number
              format: float
            today_alerts:
              type: integer
            alerts:
              type: object
              properties:
                critical:
                  type: integer
                high:
                  type: integer
                normal:
                  type: integer
      500:
        description: Erreur serveur
    """
    try:
        es = get_elasticsearch()
        mongo = get_mongodb()

        stats = {
            'total_logs': 0,
            'total_files': 0,
            'sensors_count': 0,
            'avg_temperature': 0,
            'today_alerts': 0,
            'alerts': {
                'critical': 0,
                'high': 0,
                'normal': 0
            }
        }

        result = es.count(index='iot-logs-*')
        stats['total_logs'] = result['count']

        stats['total_files'] = mongo.uploaded_files.count_documents({})

        try:
            agg_result = es.search(
                index='iot-logs-*',
                body={
                    "aggs": {
                        "unique_sensors": {
                            "cardinality": {"field": "sensor_id"}
                        }
                    },
                    "size": 0
                }
            )
            stats['sensors_count'] = agg_result['aggregations']['unique_sensors']['value']
        except Exception:
            stats['sensors_count'] = 0

        try:
            temp_result = es.search(
                index='iot-logs-*',
                body={
                    "query": {
                        "term": {"sensor_type": "temperature"}
                    },
                    "aggs": {
                        "avg_temp": {
                            "avg": {"field": "value"}
                        }
                    },
                    "size": 0
                }
            )
            if temp_result['aggregations']['avg_temp']['value']:
                stats['avg_temperature'] = round(temp_result['aggregations']['avg_temp']['value'], 1)
        except Exception:
            stats['avg_temperature'] = 0

        try:
            today = datetime.now().strftime("%Y-%m-%d")
            today_alert_result = es.count(
                index='iot-logs-*',
                body={
                    "query": {
                        "bool": {
                            "must": [
                                {"range": {"@timestamp": {"gte": f"{today}||/d"}}},
                                {"bool": {"must_not": {"term": {"status": "normal"}}}}
                            ]
                        }
                    }
                }
            )
            stats['today_alerts'] = today_alert_result['count']
        except Exception:
            stats['today_alerts'] = 0

        try:
            alert_result = es.search(
                index='iot-logs-*',
                body={
                    "aggs": {
                        "alerts_by_status": {
                            "terms": {"field": "status"}
                        }
                    },
                    "size": 0
                }
            )

            status_mapping = {
                'normal': 'normal',
                'warning': 'high',
                'alert': 'high',
                'critical': 'critical'
            }

            for bucket in alert_result['aggregations']['alerts_by_status']['buckets']:
                status = bucket['key']
                count = bucket['doc_count']
                alert_category = status_mapping.get(status, 'normal')
                stats['alerts'][alert_category] += count
        except Exception:
            pass

        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/files', methods=['GET'])
@login_required
@cached_route(ttl=300)
def get_files():
    """Récupérer la liste des fichiers uploadés
    ---
    tags:
      - Files
    responses:
      200:
        description: Liste des fichiers
        schema:
          type: object
          properties:
            files:
              type: array
              items:
                type: object
      500:
        description: Erreur serveur
    """
    try:
        mongo = get_mongodb()
        files = list(
            mongo.uploaded_files.find({}, {'_id': 0}).sort('upload_date', -1).limit(50)
        )
        for file in files:
            if 'upload_date' in file:
                file['upload_date'] = file['upload_date'].isoformat()
        return jsonify({'files': files}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
@cached_route(ttl=600)
def get_dashboard_stats():
    """Récupérer les statistiques pour le dashboard
    ---
    tags:
      - Stats
    responses:
      200:
        description: Statistiques pour le dashboard
        schema:
          type: object
          properties:
            total_logs:
              type: integer
            avg_temperature:
              type: number
              format: float
            alerts_today:
              type: integer
            active_sensors:
              type: integer
      500:
        description: Erreur serveur
    """
    try:
        es = get_elasticsearch()
        stats = {
            'total_logs': 0,
            'avg_temperature': 0,
            'alerts_today': 0,
            'active_sensors': 0
        }
        result = es.count(index='iot-logs-*')
        stats['total_logs'] = result['count']
        temp_result = es.search(
            index='iot-logs-*',
            body={
                "query": {"term": {"sensor_type": "temperature"}},
                "aggs": {"avg_temp": {"avg": {"field": "value"}}},
                "size": 0
            }
        )
        if temp_result['aggregations']['avg_temp']['value']:
            stats['avg_temperature'] = round(temp_result['aggregations']['avg_temp']['value'], 1)
        alerts_result = es.search(
            index='iot-logs-*',
            body={
                "query": {
                    "bool": {
                        "must_not": {"term": {"status": "normal"}},
                        "filter": {"range": {"@timestamp": {"gte": "now-24h"}}}
                    }
                },
                "size": 0
            }
        )
        stats['alerts_today'] = alerts_result['hits']['total']['value']
        sensors_result = es.search(
            index='iot-logs-*',
            body={
                "aggs": {
                    "unique_sensors": {
                        "cardinality": {"field": "sensor_id.keyword"}
                    }
                },
                "size": 0
            }
        )
        stats['active_sensors'] = sensors_result['aggregations']['unique_sensors']['value']
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/dashboard/recent-alerts', methods=['GET'])
def get_recent_alerts():
    """Récupérer les alertes récentes
    ---
    tags:
      - Stats
    responses:
      200:
        description: Liste des alertes récentes
        schema:
          type: object
          properties:
            alerts:
              type: array
              items:
                type: object
      500:
        description: Erreur serveur
    """
    try:
        es = get_elasticsearch()
        result = es.search(
            index='iot-logs-*',
            body={
                "query": {
                    "bool": {
                        "must_not": {"term": {"status": "normal"}}
                    }
                },
                "sort": [{"@timestamp": {"order": "desc"}}],
                "size": 10
            }
        )
        alerts = []
        for hit in result['hits']['hits']:
            source = hit['_source']
            alerts.append({
                'date': source.get('@timestamp', source.get('timestamp', '')),
                'type': source.get('sensor_type', ''),
                'zone': source.get('zone', ''),
                'message': f"{source.get('sensor_type', '')} - {source.get('value', '')} {source.get('unit', '')}",
                'level': source.get('status', 'normal')
            })
        return jsonify({'alerts': alerts}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cache/stats', methods=['GET'])
@login_required
def get_cache_info():
    """Get Redis cache statistics
    ---
    tags:
      - Cache
    responses:
      200:
        description: Statistiques du cache Redis
        schema:
          type: object
      500:
        description: Erreur serveur
    """
    try:
        stats = get_cache_stats()
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/cache/clear', methods=['POST'])
@login_required
def clear_cache_route():
    """Clear cache (admin only)
    ---
    tags:
      - Cache
    parameters:
      - in: body
        name: payload
        required: false
        schema:
          type: object
          properties:
            pattern:
              type: string
              description: Motif des clés à supprimer (par défaut '*')
    responses:
      200:
        description: Résultat de la suppression du cache
        schema:
          type: object
          properties:
            message:
              type: string
            pattern:
              type: string
            keys_deleted:
              type: integer
      403:
        description: Accès admin requis
      500:
        description: Erreur serveur
    """
    try:
        from flask_login import current_user
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        pattern = request.get_json().get('pattern', '*') if request.is_json else '*'
        from app.services.redis_cache import clear_cache
        count = clear_cache(pattern)
        return jsonify({
            'message': 'Cleared cache',
            'pattern': pattern,
            'keys_deleted': count
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

