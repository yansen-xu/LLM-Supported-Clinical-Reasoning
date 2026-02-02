import os
from datetime import datetime


class Config:
    """Base configuration class"""
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    DEBUG = False
    TESTING = False

    # Log configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    # Security configuration
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS') or ['*']

    # File path configuration
    CONVERSATIONS_DIR = os.environ.get(
        'CONVERSATIONS_DIR') or "./conversations"

    @property
    def OPENAI_API_KEY(self):
        """Dynamically read from environment"""
        return os.environ.get('OPENAI_API_KEY')

    @property
    def OPENAI_BASE_URL(self):
        """Dynamically read from environment"""
        return os.environ.get('OPENAI_BASE_URL')

    @property
    def OPENAI_MODEL(self):
        """Dynamically read from environment"""
        return os.environ.get('OPENAI_MODEL')

    @staticmethod
    def init_app(app):
        """Initialize app configuration"""
        # Ensure necessary directories exist
        conversations_dir = Config.CONVERSATIONS_DIR
        if not os.path.exists(conversations_dir):
            os.makedirs(conversations_dir, exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'


class DockerConfig(Config):
    """Docker environment configuration"""
    DEBUG = False
    LOG_LEVEL = 'INFO'

    # Docker environment paths
    CONVERSATIONS_DIR = "/app/conversations"


# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'docker': DockerConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get current environment configuration"""
    env = os.environ.get('FLASK_ENV', 'default')
    config_class = config.get(env, config['default'])
    return config_class()  # Return an instance of the config class
