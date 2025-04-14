# Movie Theater API Project

Welcome to the **Movie Theater API** project! This project is designed to demonstrate my skills in creating robust web applications using FastAPI, SQLAlchemy, and Docker. Here's what the project offers:

## Table of Contents

- [Movie Theater API Project](#movie-theater-api-project)
  - [Features](#features)
    - [Database setup](#database-setup)
    - [Data population](#data-population)
    - [Docker integration](#docker-integration)
    - [Project structure](#project-structure)
  - [Primary Services (docker-compose.yml)](#primary-services-docker-composeyml)
    - [1. Database Service (`db`)](#1-database-service-db)
    - [2. Backend Service (`web`)](#3-backend-service-web)
    - [3. Database Migrator (`migrator`)](#4-database-migrator-migrator)
  - [How to Run the Project](#how-to-run-the-project)
    - [1. Clone the Repository](#1-clone-the-repository)
    - [2. Create and Activate a Virtual Environment](#2-create-and-activate-a-virtual-environment)
    - [3. Install Dependencies with Poetry](#3-install-dependencies-with-poetry)
    - [4. Create a `.env` File](#4-create-a-env-file)
    - [5. Run the Project with Docker Compose](#5-run-the-project-with-docker-compose)
    - [6. Access the Services](#6-access-the-services)


## Features

### **Database setup**
- **PostgreSQL for development**: The application uses PostgreSQL as the main database for the development environment, configured via Docker Compose.

### **Data population**
- The database can be automatically populated with movie data from a provided dataset. This includes associated entities such as genres, actors, languages, and countries, ensuring a rich and interconnected data structure.

### **Docker integration**
- The project is fully Dockerized, allowing seamless setup and execution of the application and its dependencies.
- Docker Compose simplifies the orchestration of services like the FastAPI application, PostgreSQL database, and other required components.
- **Separate Docker Compose files**:
  - `docker-compose.yml`: The main configuration for development, including FastAPI, PostgreSQL, Alembic Migrator

### **Project structure**
A well-organized and modular project structure is provided, including:
- **Database models** and schemas for movies and related entities.
- **Routing logic** for managing API endpoints.
- **Utility scripts** for tasks like data seeding and database migrations.

This setup ensures a scalable, maintainable, and testable API that adheres to best practices in web development.

---

## **Primary Services (docker-compose.yml)**

### **1. Database Service (`db`)**
- **Image**: `postgres:latest`
- **Purpose**: Acts as the primary PostgreSQL database for the application.
- **Configuration**:
  - Loads an initial schema from `init.sql`.
  - Uses a persistent Docker volume `postgres_theater_data` to store data.
  - Exposes PostgreSQL on port **5432**.
- **Health Check**: Uses `pg_isready` to ensure the database is ready before dependent services start.
- **Network**: Attached to `theater_network`.

---

### **2. Backend Service (`web`)**
- **Build Context**: Uses the local directory (`.`) as the build source.
- **Purpose**: Runs the **FastAPI application**, serving API endpoints.
- **Configuration**:
  - Runs the development server via `/commands/run_web_server_dev.sh`.
  - Uses `PYTHONPATH` to reference the `src` directory.
  - Enables live file watching (`WATCHFILES_FORCE_POLLING=true`).
  - Exposes the API on port **8000**.
- **Dependencies**:
  - Waits for `db` and `minio` services to be healthy before starting.
- **Network**: Attached to `theater_network`.

---

### **3. Database Migrator (`migrator`)**
- **Build Context**: Shares the same build context as `web`.
- **Purpose**: Runs **Alembic migrations** to keep the database schema up-to-date.
- **Configuration**:
  - Uses the `run_migration.sh` script to apply migrations.
  - Mounts the `src` directory to access migration scripts.
- **Dependency**: Starts only after `db` is healthy.
- **Network**: Attached to `theater_network`.

---

### **How to Run the Project**

Follow these steps to set up and run the **Movie Theater API** project on your local machine.

---

## **1. Clone the Repository**

Start by cloning the project repository from GitHub:

```bash
git clone <repository-url>
cd <repository-folder>
```

---
## **2. Create and Activate a Virtual Environment**

It is recommended to use a virtual environment to isolate project dependencies:

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

---

## **3. Install Dependencies with Poetry**

This project uses **Poetry** for dependency management. Install dependencies as follows:

```bash
# Install Poetry if not already installed
pip install poetry

# Install project dependencies
poetry install
```

---

## **4. Create a `.env` File**

Create a `.env` file in the project root directory from env.sample file

---
## **5. Run the Project with Docker Compose**

The project is **Dockerized** for easy setup. To start all the required services (**PostgreSQL, pgAdmin, FastAPI app, MailHog, MinIO, and Alembic migrator**), run:

```bash
docker-compose up --build
```

**Notes**:
- The first run **may take some time** as the database will be populated with initial data.
- Logs for services can be viewed using:

  ```bash
  docker-compose logs -f
  ```

---
## **6. Access the Services**

| Service        | URL |
|---------------|--------------------------|
| **API**       | `http://localhost:8000` |

---