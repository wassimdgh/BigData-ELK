"""
Script d'initialisation d'Elasticsearch
Crée les index et mappings nécessaires
"""

from elasticsearch import Elasticsearch
import json
import time
import os

# Connexion à Elasticsearch
ES_HOST = os.getenv('ELASTICSEARCH_HOST', 'localhost')
ES_PORT = int(os.getenv('ELASTICSEARCH_PORT', 9200))

def wait_for_elasticsearch(max_retries=30):
    """Attendre qu'Elasticsearch soit prêt"""
    print("⏳ Attente de la disponibilité d'Elasticsearch...")
    
    es = Elasticsearch([f'http://{ES_HOST}:{ES_PORT}'])
    
    for i in range(max_retries):
        try:
            if es.ping():
                print("✅ Elasticsearch est prêt!")
                return es
        except:
            pass
        
        print(f"   Tentative {i+1}/{max_retries}...")
        time.sleep(2)
    
    raise Exception("❌ Impossible de se connecter à Elasticsearch")

def create_index_template(es):
    """Créer un template d'index pour les logs IoT"""
    
    template = {
        "index_patterns": ["iot-logs-*"],
        "template": {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "refresh_interval": "5s"
            },
            "mappings": {
                "properties": {
                    "@timestamp": {
                        "type": "date"
                    },
                    "sensor_id": {
                        "type": "keyword"
                    },
                    "sensor_type": {
                        "type": "keyword"
                    },
                    "zone": {
                        "type": "keyword"
                    },
                    "value": {
                        "type": "float"
                    },
                    "unit": {
                        "type": "keyword"
                    },
                    "status": {
                        "type": "keyword"
                    },
                    "alert_level": {
                        "type": "keyword"
                    },
                    "alert_message": {
                        "type": "text"
                    },
                    "building_id": {
                        "type": "keyword"
                    },
                    "location": {
                        "type": "geo_point"
                    },
                    "ingestion_timestamp": {
                        "type": "date"
                    }
                }
            }
        }
    }
    
    try:
        # Supprimer l'ancien template s'il existe
        if es.indices.exists_index_template(name="iot-logs-template"):
            es.indices.delete_index_template(name="iot-logs-template")
            print("🗑️  Ancien template supprimé")
        
        # Créer le nouveau template
        es.indices.put_index_template(name="iot-logs-template", body=template)
        print("✅ Template d'index 'iot-logs-template' créé avec succès")
    except Exception as e:
        print(f"❌ Erreur lors de la création du template: {e}")

def create_initial_index(es):
    """Créer un index initial pour tester"""
    from datetime import datetime
    
    index_name = f"iot-logs-{datetime.now().strftime('%Y.%m.%d')}"
    
    try:
        if not es.indices.exists(index=index_name):
            es.indices.create(index=index_name)
            print(f"✅ Index '{index_name}' créé")
        else:
            print(f"ℹ️  Index '{index_name}' existe déjà")
    except Exception as e:
        print(f"❌ Erreur lors de la création de l'index: {e}")

def insert_sample_data(es):
    """Insérer quelques données de test"""
    from datetime import datetime
    
    sample_docs = [
        {
            "@timestamp": datetime.now().isoformat(),
            "sensor_id": "TEMP_zone_a_1234",
            "sensor_type": "temperature",
            "zone": "zone_a",
            "value": 22.5,
            "unit": "°C",
            "status": "normal",
            "alert_level": "normal",
            "building_id": "Building_A"
        },
        {
            "@timestamp": datetime.now().isoformat(),
            "sensor_id": "CO2_zone_b_5678",
            "sensor_type": "co2",
            "zone": "zone_b",
            "value": 850,
            "unit": "ppm",
            "status": "warning",
            "alert_level": "warning",
            "alert_message": "Niveau CO2 élevé",
            "building_id": "Building_A"
        },
        {
            "@timestamp": datetime.now().isoformat(),
            "sensor_id": "ENER_zone_c_9012",
            "sensor_type": "energy",
            "zone": "zone_c",
            "value": 15.3,
            "unit": "kWh",
            "status": "normal",
            "alert_level": "normal",
            "building_id": "Building_B"
        }
    ]
    
    index_name = f"iot-logs-{datetime.now().strftime('%Y.%m.%d')}"
    
    try:
        for doc in sample_docs:
            es.index(index=index_name, document=doc)
        
        print(f"✅ {len(sample_docs)} documents de test insérés")
    except Exception as e:
        print(f"❌ Erreur lors de l'insertion des données: {e}")

def main():
    """Fonction principale"""
    print("=" * 70)
    print("🚀 Initialisation d'Elasticsearch pour IoT Smart Building")
    print("=" * 70)
    
    try:
        # Attendre qu'Elasticsearch soit prêt
        es = wait_for_elasticsearch()
        
        # Créer le template d'index
        create_index_template(es)
        
        # Créer l'index initial
        create_initial_index(es)
        
        # Insérer des données de test
        insert_sample_data(es)
        
        # Afficher les stats
        stats = es.count(index='iot-logs-*')
        print(f"\n📊 Total de documents dans 'iot-logs-*': {stats['count']}")
        
        print("\n" + "=" * 70)
        print("✅ Initialisation terminée avec succès!")
        print("=" * 70)
        print(f"\n🔗 Elasticsearch: http://{ES_HOST}:{ES_PORT}")
        print(f"🔗 Kibana: http://localhost:5601")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
