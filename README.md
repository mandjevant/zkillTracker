# zkillTracker

A web application to view and manage activity of corporations and members in the Sigma alliance for EVE Online, using zKillboard data.

## Features

- React frontend for browsing kill/loss data
- Python backend for fetching and processing zKillboard and ESI API data
- Database population scripts for corporations and kills

## Getting Started (Docker)

1. **Build and start the services:**

   - For local development:
     ```bash
     docker-compose -f docker-compose-local.yml up --build
     ```

2. **Access the app:**

   - The frontend and backend will be available at the ports specified in the Docker Compose files.

3. **Configuration:**
   - Backend: Set environment variables in your Docker Compose files or in a `.flaskenv` file for Flask.
   - Frontend: Adjust API endpoints and other settings in `zkilltracker/src/config.js` as needed.

## Project Structure

- `zkilltracker/` – React frontend
- `zkilltracker/api/` – Python backend and scripts

## License

MIT
