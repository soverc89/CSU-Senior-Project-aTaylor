# Hunting Stand Weather Project

This project is a web application built with Python and flask, and designed to help hunters increase their success by selecting the best stand location for current weather conditions. The application takes user defined stand location data and compares it against real time weather data fetched from weather APIs. Its main function is computing the optimal stand choice by calculating the difference between stand and wind direction. The results are rendered in a "dashboard", allowing the users to easily visualize the most optimal stand in a location to hunt at.

## Compile/Deploy

Run the local application with `py run.py` (initialize a new database with `py init_db.py` first).

On first startup, the app generates a random session-signing key in `instance/secret_key`. The `instance/` directory is excluded from Git. Keep that file between restarts so login sessions remain valid. Changing or deleting the key signs existing users out; it does not delete their saved data.

For a hosted environment, set the `SECRET_KEY` environment variable to a long, randomly generated value of at least 32 characters. It takes precedence over the local key. Keep it private and stable between restarts. A `.env` file is not loaded automatically.

## Usage

## Options

## Testing

