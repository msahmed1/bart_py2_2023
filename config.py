import os

# Get the path to the 'instance' folder
instance_path = os.path.join(os.getcwd(), 'instance')

# Configure SQLite database
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///{}'.format(os.path.join(instance_path, 'participant.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False