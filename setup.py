"""
setup.py — First-run setup for AutoResume AI
Run once before starting the app: python setup.py
"""
import os
import sys
import subprocess

def header(msg):
    print(f"\n{'='*50}")
    print(f"  {msg}")
    print(f"{'='*50}")

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print(f"❌ Python 3.9+ required (you have {version.major}.{version.minor})")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")

def install_requirements():
    req_path = os.path.join("backend", "requirements.txt")
    if not os.path.exists(req_path):
        print(f"❌ {req_path} not found")
        sys.exit(1)
    print("📦 Installing Python packages...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", req_path, "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"❌ pip install failed:\n{result.stderr}")
        sys.exit(1)
    print("✅ All packages installed")

def download_nltk():
    print("📚 Downloading NLTK data...")
    import nltk
    for pkg in ['punkt', 'stopwords', 'punkt_tab']:
        try:
            nltk.download(pkg, quiet=True)
            print(f"  ✅ {pkg}")
        except Exception as e:
            print(f"  ⚠️  {pkg}: {e}")

def create_directories():
    dirs = [
        os.path.join("data", "uploads"),
        os.path.join("data"),
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    print("✅ Directories created")

def create_env():
    env_path = ".env"
    if not os.path.exists(env_path):
        with open(env_path, "w") as f:
            f.write("FLASK_ENV=development\n")
            f.write("FLASK_DEBUG=True\n")
            f.write("PORT=5000\n")
        print("✅ .env file created")
    else:
        print("✅ .env already exists")

def validate_structure():
    required = [
        "backend/app.py",
        "backend/parser.py",
        "backend/scorer.py",
        "backend/recommender.py",
        "backend/database.py",
        "backend/skills_db.py",
        "frontend/index.html",
        "frontend/upload.html",
        "frontend/builder.html",
        "frontend/results.html",
        "frontend/dashboard.html",
        "frontend/history.html",
        "frontend/jd_input.html",
        "frontend/style.css",
        "frontend/main.js",
        "run.py",
    ]
    missing = [f for f in required if not os.path.exists(f)]
    if missing:
        print(f"\n❌ Missing files:")
        for f in missing: print(f"   • {f}")
        return False
    print("✅ All project files present")
    return True

def test_imports():
    print("🔍 Testing imports...")
    try:
        sys.path.insert(0, "backend")
        from skills_db import SKILLS_DB
        from database import init_db
        init_db()
        print("✅ Backend modules import successfully")
        print("✅ Database initialized")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("\n🎯 AutoResume AI — Setup")

    header("1. Checking Python version")
    check_python()

    header("2. Installing dependencies")
    install_requirements()

    header("3. Downloading NLTK data")
    download_nltk()

    header("4. Creating directories")
    create_directories()

    header("5. Creating .env file")
    create_env()

    header("6. Validating project structure")
    ok = validate_structure()

    header("7. Testing backend imports")
    imports_ok = test_imports()

    print("\n" + "="*50)
    if ok and imports_ok:
        print("  ✅ Setup complete!")
        print("  Run the app with:  python run.py")
        print("  Open in browser:   http://localhost:5000")
    else:
        print("  ⚠️  Setup completed with warnings above")
        print("  Fix the issues and run setup.py again")
    print("="*50 + "\n")
