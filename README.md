# 🎛️ Circuit Analysis API

Welcome to the **Circuit Analysis API** — a cutting-edge FastAPI application designed to analyze electronic circuit components using the Llama vision model via the Groq API. This project was a standout at the Meta Llama Hackathon: Toronto, clinching the **1st Prize** among ~45 teams and 150 attendees.


## 🎥 Demo Video

Experience the capabilities of our API by watching the demo video:

[![Demo Video](https://img.youtube.com/vi/jtmZiq072Vw/0.jpg)](https://www.youtube.com/watch?v=jtmZiq072Vw)


## 📋 Prerequisites

Ensure you have the following before getting started:

- **Python**: Version 3.9 or higher
- **Poetry**: For dependency management
- **Groq API Key**: For Llama 3.2 90B
- **FastAPI**: For building the API
- **Python-dotenv**: For managing environment variables
- **Uvicorn**: For running the ASGI server
- **Pydantic**: For data validation and settings management
- **Loguru**: For logging
- **OpenCV**: For image processing
- **Pillow**: For image handling
- **Requests**: For making HTTP requests
- **Pytest**: For testing
- **litellm**: Allows switching between different language model APIs easily.


## 🚀 Setup

Follow these steps to set up the project:

1. **Install Poetry** if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. **Clone the repository** and navigate to the project directory:
   ```bash
   git clone <repository-url>
   cd circuit-analysis-api
   ```

3. **Install dependencies** using Poetry:
   ```bash
   poetry install
   ```

4. **Create a `.env` file** in the project root with the following content:
   ```bash
   GROQ_API_KEY=your_groq_api_key_here
   ```

> **Note**: The `litellm` library is used to facilitate switching between different language model APIs.


## 🏃‍♂️ Running the Application

1. **Activate the Poetry virtual environment**:
   ```bash
   poetry shell
   ```

2. **Start the Phoenix server**:
   ```bash
   phoenix serve
   ```

3. **Start the FastAPI server**:
   ```bash
   python run.py
   ```

- The API will be available at `http://localhost:8000`
- The Phoenix server will be available at `http://localhost:6006`


## 📚 API Documentation

Once the server is running, access the following documentation:

- **Interactive API documentation (Swagger UI)**: `http://localhost:8000/docs`
- **Alternative API documentation (ReDoc)**: `http://localhost:8000/redoc`


## 🏗️ Architecture

The Circuit Analysis API is structured into several key components, each responsible for a specific aspect of the circuit analysis process:

1. **Component Identifier**: Detects and identifies various electronic components within a circuit diagram using machine learning models and predefined prompts.

2. **Sheet Identifier**: Detects and extracts the circuit diagram from an image using a two-stage approach.

3. **Connection Identifier**: Determines the connections between identified components in the circuit.

Each component works in tandem to provide a comprehensive analysis of circuit diagrams, leveraging advanced machine learning techniques and robust service orchestration to deliver accurate and reliable results.

## 🧪 Running Tests

Run the test suite and generate coverage reports with:
```bash
poetry run pytest
```

## 📊 Running Benchmarks

Evaluate the accuracy and performance of the API's detection capabilities with benchmark tests:

### Running Component Detection Benchmarks
```bash
python -m tests.benchmarks.circuit_components_benchmark
```

### Running Connection Identification Benchmarks
```bash
python -m tests.benchmarks.circuit_connections_benchmark
```

### Running Sheet Detection Benchmarks
```bash
python -m tests.benchmarks.sheet_detector_benchmark
```

Each benchmark script will output detailed logs and statistics, including accuracy rates and any errors encountered during the tests.


## 📚 Lessons Learned

- **Prompt Engineering**: Not the optimal solution for this problem.
- **Model Fine-Tuning**: Extensive fine-tuning is required for models to perform well on these examples.
- **Future Solutions**: Consider using architectures like YOLOv5 for initial detection and Llama for reasoning between detected components.


## 📜 License

This project is licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for details.


