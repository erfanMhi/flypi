
# Circuit Analysis API

A FastAPI application for analyzing electronic circuit components using Llama vision model through Groq API.

## Prerequisites

- Python 3.9 or higher
- Poetry for dependency management
- Groq API key

## Setup

1. Install Poetry if you haven't already:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd circuit-analysis-api
```

3. Install dependencies using Poetry:
```bash
poetry install
```

4. Create a `.env` file in the project root with the following content:
```bash
GROQ_API_KEY=your_groq_api_key_here
```

## Running the Application

1. Activate the Poetry virtual environment:
```bash
poetry shell
```

2. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Interactive API documentation (Swagger UI): `http://localhost:8000/docs`
- Alternative API documentation (ReDoc): `http://localhost:8000/redoc`

## API Endpoints

### POST /api/v1/retrieve-circuit-schema

Analyzes a circuit image and returns component information.

- Request: Multipart form data with an image file
- Maximum image size: 10MB
- Supported formats: Common image formats (PNG, JPEG, etc.)

## Running Tests

```bash
poetry run pytest
```

This will run the test suite and generate coverage reports.
