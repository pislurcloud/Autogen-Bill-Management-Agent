"""
Setup Check Script
Verifies Bill Management Agent installation
"""

import os
import sys
from pathlib import Path


def check_dependencies():
    """Check required packages"""
    print("🔍 Checking dependencies...")
    
    required = [
        ('openai', 'openai'),
        ('streamlit', 'streamlit'),
        ('plotly', 'plotly'),
        ('pandas', 'pandas'),
        ('PIL', 'Pillow'),
        ('dotenv', 'python-dotenv'),
    ]
    
    missing = []
    for module, package in required:
        try:
            __import__(module)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Install missing: pip install {' '.join(missing)}")
        return False
    
    print("\n✅ All dependencies installed!")
    return True


def check_env():
    """Check .env configuration"""
    print("\n🔍 Checking environment...")
    
    env_path = Path('.env')
    
    if not env_path.exists():
        print("  ❌ .env file not found")
        print("  Run: cp .env.example .env")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    openrouter = os.getenv('OPENROUTER_API_KEY')
    groq = os.getenv('GROQ_API_KEY')
    
    keys_set = True
    
    if not openrouter or 'your_' in openrouter:
        print("  ⚠️  OPENROUTER_API_KEY not set")
        keys_set = False
    else:
        print("  ✅ OPENROUTER_API_KEY set")
    
    if not groq or 'your_' in groq:
        print("  ⚠️  GROQ_API_KEY not set")
        keys_set = False
    else:
        print("  ✅ GROQ_API_KEY set")
    
    if not keys_set:
        print("\n  Get FREE API keys:")
        print("  - OpenRouter: https://openrouter.ai/keys")
        print("  - Groq: https://console.groq.com/keys")
        return False
    
    return True


def check_database():
    """Check database"""
    print("\n🔍 Checking database...")
    
    try:
        sys.path.insert(0, str(Path.cwd()))
        from src.database.db_manager import DatabaseManager
        db = DatabaseManager()
        stats = db.get_statistics()
        print("  ✅ Database initialized")
        print(f"  📊 {stats['total_bills']} bills processed")
        return True
    except Exception as e:
        print("Path=", str(Path.cwd()))
        print(f"  ❌ Database error: {e}")
        return False


def check_directories():
    """Create directories"""
    print("\n🔍 Checking directories...")
    
    dirs = ['uploads', 'outputs', 'logs', 'database']
    
    for dir_name in dirs:
        dir_path = Path(dir_name)
        dir_path.mkdir(exist_ok=True)
        print(f"  ✅ {dir_name}/")
    
    return True


def main():
    """Run all checks"""
    print("="*60)
    print("💰 Bill Management Agent - Setup Check")
    print("="*60)
    
    checks = [
        check_dependencies,
        check_env,
        check_directories,
        check_database,
    ]
    
    all_passed = all(check() for check in checks)
    
    print("\n" + "="*60)
    if all_passed:
        print("✅ Setup complete!")
        print("\nRun: streamlit run gui/streamlit_app.py")
    else:
        print("⚠️  Fix issues above")
    print("="*60)


if __name__ == "__main__":
    main()