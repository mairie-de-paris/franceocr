import os


class DefaultConfig(object):
    DEBUG = False
    TESTING = False

    # Grabs the folder where the script runs.
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    UPLOAD_FOLDER = os.path.abspath(BASEDIR + "/../uploads")
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024


class ProductionConfig(DefaultConfig):
    pass


class DevelopmentConfig(DefaultConfig):
    DEBUG = True


class TestingConfig(DefaultConfig):
    TESTING = True
