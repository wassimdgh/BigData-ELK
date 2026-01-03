"""
Point d'entrée de l'application Flask
"""
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8000))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    print("=" * 70)
    print("🏢 IoT Smart Building Monitoring Platform")
    print("=" * 70)
    print(f"🌐 Application démarrée sur http://{host}:{port}")
    print(f"📊 Kibana: http://localhost:5601")
    print(f"🔍 Elasticsearch: http://localhost:9200")
    print("=" * 70)
    
    app.run(host=host, port=port, debug=debug)
