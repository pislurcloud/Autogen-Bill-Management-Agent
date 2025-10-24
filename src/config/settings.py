"""
Application Settings
"""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "database" / "bill_management.db"
UPLOAD_FOLDER = PROJECT_ROOT / "uploads"
OUTPUT_FOLDER = PROJECT_ROOT / "outputs"

# Create directories
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)
(PROJECT_ROOT / "logs").mkdir(exist_ok=True)

# Database
DB_PATH = str(DATABASE_PATH)

# Supported formats
SUPPORTED_FORMATS = [".jpg", ".jpeg", ".png", ".pdf"]
MAX_FILE_SIZE_MB = 10

# Default user
DEFAULT_USER_ID = 1