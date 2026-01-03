// Initialisation de la base de données MongoDB
db = db.getSiblingDB('iot_db');

// Créer la collection pour les fichiers uploadés
db.createCollection('uploaded_files');

// Créer la collection pour l'historique des recherches
db.createCollection('search_history');

// Créer la collection pour les alertes
db.createCollection('alerts');

// Créer la collection pour les utilisateurs (si authentification)
db.createCollection('users');

// Créer les index pour optimiser les performances
db.uploaded_files.createIndex({ "upload_date": -1 });
db.uploaded_files.createIndex({ "filename": 1 });
db.uploaded_files.createIndex({ "status": 1 });

db.search_history.createIndex({ "search_date": -1 });
db.search_history.createIndex({ "user_id": 1 });

db.alerts.createIndex({ "timestamp": -1 });
db.alerts.createIndex({ "sensor_id": 1 });
db.alerts.createIndex({ "alert_level": 1 });
db.alerts.createIndex({ "resolved": 1 });

db.users.createIndex({ "email": 1 }, { unique: true });
db.users.createIndex({ "username": 1 }, { unique: true });

// Insérer des données de test
db.uploaded_files.insertOne({
  filename: "initial_test.csv",
  upload_date: new Date(),
  size: 1024,
  status: "processed",
  records_count: 100,
  uploaded_by: "system"
});

print("MongoDB initialized successfully!");
