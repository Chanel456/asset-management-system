import os

from app import create_app
from config.config import Config
from config.prod_config import ProdConfig

app = create_app()

is_production = os.getenv('RENDER') == 'true'

if is_production:
    config = ProdConfig
else:
    config = Config

if __name__ == '__main__':
    app.run(debug=not is_production)