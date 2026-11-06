# Weather Data Pipeline | Data Engineering Project

An end-to-end Data Engineering project that extracts hourly weather forecast data from the Open-Meteo API, transforms it using Python and Pandas, and loads it into a PostgreSQL database running in Docker.

The project demonstrates practical experience with API integration, ETL development, relational databases, containerization, and data validation.

## Project Overview

This project implements an ETL (Extract, Transform, Load) pipeline to collect and process hourly weather forecast data for Messina, Italy.

The goal is to develop a reusable data ingestion workflow that retrieves weather information from an external API, prepares it for analysis, and stores it in a structured relational database.

## Tech Stack

- **Python:** ETL pipeline development
- **Open-Meteo API:** Weather data source
- **httpx:** HTTP requests and API integration
- **Pandas:** Data cleaning and transformation
- **PostgreSQL:** Relational data storage
- **psycopg:** Python-to-PostgreSQL connectivity
- **Docker:** Containerized PostgreSQL environment
- **SQL:** Data validation and querying
- **Environment Variables:** Database configuration and credentials

## Pipeline Architecture

```text
Open-Meteo Weather API
          |
          v
    Python + httpx
      (Extract)
          |
          v
       Pandas
     (Transform)
          |
          v
       psycopg
        (Load)
          |
          v
   PostgreSQL Database
     (Docker Container)
          |
          v
    SQL Validation
      & Analysis
```

## ETL Workflow

### 1. Extract

The pipeline requests hourly weather forecast data from the Open-Meteo API.

The extracted data includes:

- Temperature
- Relative humidity
- Apparent temperature
- Precipitation
- Weather codes
- Wind speed
- Geographic coordinates and timezone information

The API returns JSON data, which is processed using Python.

### 2. Transform

Pandas is used to convert the API response into a structured dataset.

The transformation process includes:

- Converting timestamps into appropriate datetime formats.
- Organizing hourly weather observations into tabular records.
- Preparing numeric weather measurements.
- Structuring the data for database insertion.

### 3. Load

The transformed records are loaded into PostgreSQL using psycopg.

The database runs inside a Docker container, providing a consistent and isolated environment.

The pipeline uses PostgreSQL's `ON CONFLICT` functionality to support upsert operations, allowing existing records to be updated rather than duplicated when the pipeline is executed again.

## Database

The project uses a PostgreSQL database named `weather_db`.

The database stores hourly weather data for Messina, Italy.

The ETL workflow was successfully tested with 24 hourly weather records, including a successful pipeline rerun.

## Data Validation

The pipeline was verified through:

- Successful API extraction.
- Successful transformation of hourly weather records.
- PostgreSQL connection testing.
- Successful insertion of 24 records.
- SQL verification of stored records.
- Successful ETL rerun using upsert logic.

These checks demonstrate the basic reliability of the extraction and loading workflow.

## Running the Pipeline

### Prerequisites

- Python
- Docker Desktop
- PostgreSQL Python driver (`psycopg`)
- Pandas
- httpx

### 1. Start PostgreSQL

Start the configured PostgreSQL Docker container.

The development environment uses PostgreSQL on local port `5433`.

### 2. Configure Environment Variables

Create a `.env` file containing the database connection settings.

Example:

```env
DB_HOST=localhost
DB_PORT=5433
DB_NAME=weather_db
DB_USER=weather_user
DB_PASSWORD=your_password
```

Do not commit your `.env` file to GitHub.

### 3. Run the ETL Pipeline

Execute the Python script:

```bash
python weather_etl.py
```

The pipeline retrieves weather data, transforms it, and loads it into PostgreSQL.

## Key Learning Outcomes

This project provides hands-on experience with:

- Extracting data from REST APIs.
- Processing JSON responses using Python.
- Transforming datasets with Pandas.
- Connecting Python applications to PostgreSQL.
- Running databases inside Docker containers.
- Implementing upsert operations.
- Validating data using SQL.
- Developing reusable ETL workflows.

## Future Improvements

- Add automated scheduling using Kestra or another orchestration tool.
- Implement additional data-quality checks.
- Introduce structured logging and error handling.
- Collect historical weather observations.
- Build weather analytics dashboards.
- Add monitoring and alerting for pipeline failures.
- Expand the pipeline to support multiple cities.

## Project Purpose

Developed as a hands-on Data Engineering portfolio project to strengthen skills in API ingestion, Python ETL development, PostgreSQL, Docker, and data pipeline reliability.
