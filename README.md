# Set up environment
activate the environment by running source .venv/bin/activate

# Install required packages
Anyone (or any build server) that receives a copy of the project needs only to run the pip install -r requirements.txt command to reinstall the packages in the original environment.

# Save required packages
pip freeze > requirements.txt

# Run app
In the Integrated Terminal, run the app by entering python -m flask run, which runs the Flask development server.