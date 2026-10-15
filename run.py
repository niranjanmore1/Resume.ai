import sys
import os

backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_path)

from app import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "=" * 50)
    print("  🎯 AutoResume AI — Server Starting")
    print(f"  Frontend: http://localhost:{port}")
    print(f"  API:      http://localhost:{port}/api")
    print("=" * 50 + "\n")
    app.run(debug=True, port=port, host='0.0.0.0')