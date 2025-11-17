import os

from app import create_app
from config.config import Config
from config.prod_config import ProdConfig

if os.environ.get("PYTHONANYWHERE_DOMAIN"):
    environment = "pythonanywhere"
    config = ProdConfig
else:
    environment = "local"
    config = Config

app = create_app(config)

if __name__ == '__main__':
    app.run(debug=(environment == 'local'))