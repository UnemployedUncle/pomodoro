import os


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, "app")
SAMPLE_DIR = os.path.join(BASE_DIR, "sample")
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///{}".format(os.path.join(DATA_DIR, "pure_focus.db")))
SECRET_KEY = os.getenv("SECRET_KEY", "pure-focus-dev-secret")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
DEMO_EMAIL = os.getenv("DEMO_EMAIL", "demo@purefocus.local")
DEMO_NAME = os.getenv("DEMO_NAME", "Demo User")
