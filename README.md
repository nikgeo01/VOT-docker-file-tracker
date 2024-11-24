# File Usage Tracker

The **File Usage Tracker** is an application designed to monitor file usage across different users and projects. It records user activities, such as the files they work on, the time spent on each file, and the applications used. The collected data is stored in CSV files and imported into a PostgreSQL database for report generation.

This project includes:
- A **tracking application** that logs user activities to CSV files (existing code, unchanged).
- A **report generator** that reads data from a PostgreSQL database and generates reports.
- Docker containers for the **PostgreSQL database** and the **report generator application**.
- Scripts and configurations to set up and run the application using Docker Compose.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [1. Clone the Repository](#1-clone-the-repository)
  - [2. Set Up the Database Container](#2-set-up-the-database-container)
  - [3. Import Data into the Database](#3-import-data-into-the-database)
  - [4. Run the Report Generator](#4-run-the-report-generator)
- [Application Overview](#application-overview)
  - [Tracking Application](#tracking-application)
  - [Report Generator](#report-generator)
- [Running the Application with Docker](#running-the-application-with-docker)
  - [Starting the Containers](#starting-the-containers)
  - [Stopping the Containers](#stopping-the-containers)
- [Troubleshooting](#troubleshooting)
- [Additional Notes](#additional-notes)
- [License](#license)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- **Python 3.x**
- **pip** (Python package installer)
- **Docker**
- **Docker Compose**

---

## Getting Started

### 1. Clone the Repository

Clone the repository to your local machine:

`git clone https://github.com/nikgeo01/file_usage_tracker.git`

Navigate to the project directory:

`cd file_usage_tracker`

### 2. Set Up the Database Container

Use Docker Compose to start the PostgreSQL database container:

`docker-compose up -d db`

- This command starts the database container in detached mode.
- The database service is defined in `docker-compose.yml`.

### 3. Import Data into the Database

The application data is stored in CSV files located in the `db/` directory. You need to import this data into the PostgreSQL database.

#### 3.1. Install Python Dependencies

Install the required Python packages on your host machine:

`pip install -r requirements.txt`

#### 3.2. Set the Database URL Environment Variable

Set the `DATABASE_URL` environment variable to connect to the PostgreSQL database.

- **On Linux/macOS:**

`export DATABASE_URL=postgresql://postgres:postgres@localhost:5432/file_usage_tracker`

- **On Windows (Command Prompt):**

`set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/file_usage_tracker`

#### 3.3. Run the Data Import Script

Execute the `import_csv_to_db.py` script to import data from the CSV files into the database:

`python import_csv_to_db.py`

- The script reads all CSV files in the `db/` directory and imports the data into the `user_activity` table in the database.

### 4. Run the Report Generator

With the data imported, you can now run the report generator to create reports based on the stored data.

`python report_generator.py`

- The report generator provides a GUI interface for generating two types of reports:
  - **Project Report**: Shows the total time each user spent on a specified project.
  - **User Activity Report**: Lists all files a user has worked on within a specified date range.

---

## Application Overview

### Tracking Application

- **Purpose**: Monitors and records user activities such as file usage, time spent, and applications used.
- **Data Storage**: Writes data to CSV files in the `yearly_reports/` directory (existing functionality, unchanged).
- **Note**: The tracking application is not containerized and runs independently.

### Report Generator

- **Purpose**: Generates reports based on the data collected by the tracking application.
- **Data Source**: Reads data from a PostgreSQL database.
- **Functionality**:
  - Imports data from CSV files (copies of the tracking application's CSV files) located in the `db/` directory.
  - Provides a GUI for users to generate reports.
- **Containerization**: Optionally containerized using Docker (GUI applications have limitations in containers).

---

## Running the Application with Docker

Due to limitations with running GUI applications inside Docker containers, it is recommended to run the **database** in a Docker container and the **report generator** on your host machine.

### Starting the Containers

To start the database container, run:

`docker-compose up -d db`

- The `db` service in `docker-compose.yml` sets up the PostgreSQL database with the following configurations:
  - **User**: `postgres`
  - **Password**: `postgres`
  - **Database Name**: `file_usage_tracker`
- The database is exposed on port `5432`.

### Stopping the Containers

To stop and remove the containers and networks created by Docker Compose, run:

`docker-compose down`

---

## Troubleshooting

- **Database Connection Error**:
  - Ensure the database container is running: `docker ps` should list the `db` container.
  - Verify that the `DATABASE_URL` environment variable is set correctly.
  - Check if port `5432` is open and not blocked by a firewall.

- **Import Script Issues**:
  - Ensure you have the required Python packages installed: `sqlalchemy` and `psycopg2-binary`.
  - Verify that the CSV files in the `db/` directory have the correct format and data.

- **GUI Application Doesn't Launch**:
  - Ensure you are running the `report_generator.py` script on your host machine, not inside a Docker container.
  - Check that Tkinter is installed and functioning on your system.

- **Data Not Appearing in Reports**:
  - Confirm that the data import script ran successfully and data exists in the database.
  - Check for any errors during the import process.

---

## Additional Notes

- **Database Persistence**:
  - The PostgreSQL database uses a Docker volume (`db_data`) to persist data between restarts.
  - The volume is defined in `docker-compose.yml` and stored on your local machine.

- **Running the Report Generator in Docker**:
  - Running GUI applications inside Docker containers requires additional configuration and is generally not recommended.
  - If necessary, consider using technologies like X11 forwarding or running a VNC server inside the container.

- **Data Source**:
  - The `db/` directory contains copies of the CSV files generated by the tracking application.
  - Ensure the CSV files are up-to-date before running the import script.

- **Extending the Application**:
  - Modify the tracking application to write directly to the database instead of CSV files for a more integrated solution.
  - Implement a web-based interface for the report generator to facilitate containerization and remote access.

---

## License

This project is licensed under the **MIT License**.

---
