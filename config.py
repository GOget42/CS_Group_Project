import os

# Define the project root based on this file's location
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))

# Define common paths relative to the project root
TRACKER_PATH = os.path.join(PROJECT_ROOT, "data", "api", "request_tracker.json")
