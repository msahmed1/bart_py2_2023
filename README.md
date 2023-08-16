# Prerequisiete
This code uses python2 and the robot used is a Nao robot.

# Start up virtual environment
activate the environment by running source .venv/bin/activate

# Install required packages
Anyone (or any build server) that receives a copy of the project needs only to run the pip install -r requirements.txt command to reinstall the packages in the original environment.

# Save required packages
pip freeze > requirements.txt

# Run app
In the Terminal, go to the location where this application is located.

Set flask enviroment vairable to
$ export FLASK_APP=webapp.py
This is so that flask knows which application to run.

To run the app enter
$ python -m flask run
this will run the Flask app in the development server.