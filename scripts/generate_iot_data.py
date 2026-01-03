"""
Script de génération de données IoT pour Smart Building
Génère des logs de capteurs: température, humidité, CO2, luminosité, énergie, occupation
"""

import csv
import json
import random
from datetime import datetime, timedelta
from faker import Faker
import os

fake = Faker()

# Configuration
NUM_SENSORS = 50
NUM_RECORDS = 10000
OUTPUT_DIR = 'data/uploads'
BUILDINGS = ['Building_A', 'Building_B', 'Building_C']
ZONES = ['zone_a', 'zone_b', 'zone_c', 'zone_d', 'zone_e']
SENSOR_TYPES = ['temperature', 'humidity', 'co2', 'luminosity', 'energy', 'occupancy']

def generate_sensor_id(sensor_type, zone):
    """Générer un ID de capteur"""
    return f"{sensor_type[:4].upper()}_{zone}_{random.randint(1000, 9999)}"

def generate_sensor_value(sensor_type, hour):
    """Générer une valeur réaliste selon le type de capteur et l'heure"""
    
    if sensor_type == 'temperature':
        # Température varie selon l'heure (plus chaud l'après-midi)
        base = 20
        if 8 <= hour <= 18:
            base += random.uniform(2, 8)
        else:
            base += random.uniform(-2, 2)
        
        # Ajouter parfois des anomalies
        if random.random() < 0.05:  # 5% d'anomalies
            base += random.choice([-10, 15])
        
        return round(base + random.uniform(-1, 1), 2)
    
    elif sensor_type == 'humidity':
        # Humidité entre 30% et 70%
        base = 50
        return round(base + random.uniform(-20, 20), 2)
    
    elif sensor_type == 'co2':
        # CO2 en ppm - plus élevé quand occupé
        base = 400
        if 8 <= hour <= 18:
            base += random.randint(200, 800)
        
        # Parfois dépassement critique
        if random.random() < 0.03:
            base = random.randint(1000, 1500)
        
        return round(base, 0)
    
    elif sensor_type == 'luminosity':
        # Luminosité en lux
        if 6 <= hour <= 20:
            return round(random.uniform(300, 1000), 2)
        else:
            return round(random.uniform(0, 100), 2)
    
    elif sensor_type == 'energy':
        # Consommation en kWh
        if 8 <= hour <= 18:
            return round(random.uniform(5, 25), 2)
        else:
            return round(random.uniform(1, 5), 2)
    
    elif sensor_type == 'occupancy':
        # Taux d'occupation en %
        if 8 <= hour <= 18:
            return round(random.uniform(30, 95), 2)
        else:
            return round(random.uniform(0, 10), 2)
    
    return 0

def get_unit(sensor_type):
    """Obtenir l'unité de mesure"""
    units = {
        'temperature': '°C',
        'humidity': '%',
        'co2': 'ppm',
        'luminosity': 'lux',
        'energy': 'kWh',
        'occupancy': '%'
    }
    return units.get(sensor_type, '')

def get_status(sensor_type, value):
    """Déterminer le statut selon la valeur"""
    if sensor_type == 'temperature':
        if value > 30:
            return 'alert'
        elif value < 15:
            return 'alert'
        return 'normal'
    
    elif sensor_type == 'co2':
        if value > 1000:
            return 'critical'
        elif value > 800:
            return 'warning'
        return 'normal'
    
    elif sensor_type == 'humidity':
        if value > 70 or value < 30:
            return 'warning'
        return 'normal'
    
    return 'normal'

def generate_csv_data(filename, num_records):
    """Générer un fichier CSV avec des données IoT"""
    print(f"📝 Génération de {num_records} enregistrements dans {filename}...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    # Créer les capteurs
    sensors = []
    for sensor_type in SENSOR_TYPES:
        for zone in ZONES[:3]:  # 3 zones par type
            sensors.append({
                'id': generate_sensor_id(sensor_type, zone),
                'type': sensor_type,
                'zone': zone
            })
    
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['timestamp', 'sensor_id', 'sensor_type', 'zone', 'value', 'unit', 'status', 'building_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        start_date = datetime.now() - timedelta(days=7)
        
        for i in range(num_records):
            # Timestamp aléatoire dans les 7 derniers jours
            timestamp = start_date + timedelta(
                seconds=random.randint(0, 7 * 24 * 60 * 60)
            )
            
            # Choisir un capteur aléatoire
            sensor = random.choice(sensors)
            
            # Générer la valeur
            value = generate_sensor_value(sensor['type'], timestamp.hour)
            status = get_status(sensor['type'], value)
            
            row = {
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'sensor_id': sensor['id'],
                'sensor_type': sensor['type'],
                'zone': sensor['zone'],
                'value': value,
                'unit': get_unit(sensor['type']),
                'status': status,
                'building_id': random.choice(BUILDINGS)
            }
            
            writer.writerow(row)
            
            if (i + 1) % 1000 == 0:
                print(f"  ✅ {i + 1}/{num_records} enregistrements générés")
    
    print(f"✅ Fichier CSV créé: {filepath}")
    return filepath

def generate_json_data(filename, num_records):
    """Générer un fichier JSON Lines avec des données IoT"""
    print(f"📝 Génération de {num_records} enregistrements JSON dans {filename}...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    sensors = []
    for sensor_type in SENSOR_TYPES:
        for zone in ZONES[:3]:
            sensors.append({
                'id': generate_sensor_id(sensor_type, zone),
                'type': sensor_type,
                'zone': zone
            })
    
    with open(filepath, 'w', encoding='utf-8') as jsonfile:
        start_date = datetime.now() - timedelta(days=7)
        
        for i in range(num_records):
            timestamp = start_date + timedelta(
                seconds=random.randint(0, 7 * 24 * 60 * 60)
            )
            
            sensor = random.choice(sensors)
            value = generate_sensor_value(sensor['type'], timestamp.hour)
            status = get_status(sensor['type'], value)
            
            record = {
                'timestamp': timestamp.isoformat(),
                'sensor_id': sensor['id'],
                'sensor_type': sensor['type'],
                'zone': sensor['zone'],
                'value': value,
                'unit': get_unit(sensor['type']),
                'status': status,
                'building_id': random.choice(BUILDINGS),
                'metadata': {
                    'firmware_version': f"v{random.randint(1, 3)}.{random.randint(0, 9)}",
                    'battery_level': random.randint(50, 100) if random.random() > 0.1 else random.randint(10, 50)
                }
            }
            
            jsonfile.write(json.dumps(record) + '\n')
            
            if (i + 1) % 1000 == 0:
                print(f"  ✅ {i + 1}/{num_records} enregistrements générés")
    
    print(f"✅ Fichier JSON créé: {filepath}")
    return filepath

def main():
    """Fonction principale"""
    print("🚀 Démarrage de la génération de données IoT pour Smart Building")
    print("=" * 70)
    
    # Générer fichier CSV
    csv_file = generate_csv_data('iot_sensors_data.csv', NUM_RECORDS)
    
    # Générer fichier JSON
    json_file = generate_json_data('iot_sensors_data.json', NUM_RECORDS // 2)
    
    # Générer un fichier d'alertes
    alerts_file = generate_csv_data('iot_alerts.csv', 500)
    
    print("=" * 70)
    print("✅ Génération terminée!")
    print(f"\nFichiers créés:")
    print(f"  - {csv_file}")
    print(f"  - {json_file}")
    print(f"  - {alerts_file}")
    print("\n📊 Vous pouvez maintenant uploader ces fichiers via l'interface web")

if __name__ == '__main__':
    main()
