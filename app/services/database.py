from elasticsearch import Elasticsearch
from pymongo import MongoClient
import redis
import os
from datetime import datetime

# Connexions globales
es_client = None
mongo_client = None
redis_client = None
mongo_db = None

def init_databases(app):
    """Initialiser les connexions aux bases de données"""
    global es_client, mongo_client, redis_client, mongo_db
    
    # Elasticsearch
    es_host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
    es_port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
    es_url = f'http://{es_host}:{es_port}'
    
    app.logger.info(f"🔍 Tentative de connexion Elasticsearch: {es_url}")
    
    try:
        es_client = Elasticsearch(
            [es_url],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True,
            # Ajouter des options de compatibilité
            verify_certs=False,
            ssl_show_warn=False
        )
        # Tester la connexion avec info() au lieu de ping()
        try:
            info = es_client.info()
            app.logger.info(f"✅ Connexion Elasticsearch établie ({es_url})")
            app.logger.info(f"📊 Elasticsearch version: {info['version']['number']}")
        except Exception as test_err:
            app.logger.error(f"❌ Elasticsearch test failed ({es_url}): {test_err}")
            # Fallback sur localhost si host docker n'est pas joignable
            if es_host != 'localhost':
                try:
                    app.logger.info("🔁 Tentative de fallback sur localhost:9200...")
                    es_client = Elasticsearch(
                        ['http://localhost:9200'],
                        request_timeout=30,
                        max_retries=3,
                        retry_on_timeout=True,
                        verify_certs=False,
                        ssl_show_warn=False
                    )
                    info = es_client.info()
                    app.logger.info(f"✅ Fallback: Elasticsearch connecté sur localhost:9200")
                    app.logger.info(f"📊 Elasticsearch version: {info['version']['number']}")
                except Exception as e2:
                    app.logger.error(f"❌ Erreur Fallback Elasticsearch: {e2}")
                    es_client = None
            else:
                es_client = None
    except Exception as e:
        app.logger.error(f"❌ Erreur Elasticsearch init: {e}")
        es_client = None
    
    # MongoDB
    mongo_host = os.getenv('MONGODB_HOST', 'localhost')
    mongo_port = int(os.getenv('MONGODB_PORT', 27017))
    mongo_user = os.getenv('MONGODB_USERNAME', 'admin')
    mongo_pass = os.getenv('MONGODB_PASSWORD', 'admin123')
    
    try:
        mongo_client = MongoClient(
            f'mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}/'
        )
        mongo_db = mongo_client[os.getenv('MONGODB_DATABASE', 'iot_db')]
        app.logger.info("✅ Connexion MongoDB établie")
    except Exception as e:
        app.logger.error(f"❌ Erreur MongoDB: {e}")
    
    # Redis
    redis_host = os.getenv('REDIS_HOST', 'localhost')
    redis_port = int(os.getenv('REDIS_PORT', 6379))
    
    try:
        redis_client = redis.Redis(
            host=redis_host,
            port=redis_port,
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        redis_client.ping()
        app.logger.info("✅ Connexion Redis établie")
    except Exception as e:
        app.logger.error(f"❌ Erreur Redis: {e}")
        # Fallback sur localhost si host docker n'est pas joignable
        if redis_host != 'localhost':
            try:
                redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=int(os.getenv('REDIS_DB', 0)),
                    decode_responses=True
                )
                redis_client.ping()
                app.logger.info("🔁 Fallback: Redis connecté sur localhost:6379")
            except Exception as e2:
                app.logger.error(f"❌ Erreur Fallback Redis: {e2}")

def get_elasticsearch():
    """Obtenir le client Elasticsearch"""
    return es_client

def get_mongodb():
    """Obtenir la base de données MongoDB"""
    return mongo_db

def get_redis():
    """Obtenir le client Redis"""
    return redis_client
