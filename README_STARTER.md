# MCP Agent - Starter Files

This directory contains several helper files to get you started with the MCP Agent:

## Documentation
- `STARTER_GUIDE.md` - Comprehensive guide for setup, running, and testing
- `README.md` - Main project documentation with features and usage

## Scripts
- `run_with_docker.sh` - Bash script to build and run with Docker (Linux/macOS)
- `run_with_docker.bat` - Batch script to build and run with Docker (Windows)
- `test_workflow.py` - Python script to test the application endpoints
- `test_docker_setup.py` - Python script to verify Docker setup and environment
- `run_tests.py` - Test runner for all unit tests

## Test Files
All test files are located in the `tests/` directory:
- Unit tests for core components
- Integration tests for MCP functionality
- Test utilities and helpers

## Usage

### Quick Start with Docker (Single Command)
1. Make sure your `.env` file is configured with all required API keys
2. Run the application with a single command:
   ```bash
   # Linux/macOS
   ./run_with_docker.sh
   
   # Windows
   run_with_docker.bat
   ```

### Manual Docker Setup
1. Build the Docker image:
   ```bash
   docker build -t mcp-agent .
   ```

2. Run the container:
   ```bash
   docker run -it --rm \
     -p 5000:8080 \
     --env-file .env \
     mcp-agent
   ```

### Direct Python Execution
```bash
# Install dependencies
pip install -r requirements.txt

# Run directly
python app.py
```

### Testing the Application
```bash
# Test with Docker setup checker
python test_docker_setup.py

# Test application endpoints
python test_workflow.py

# Run all tests
python run_tests.py
```

## Key Features

- **LLM-Powered Tool Selection**: Intelligent tool selection based on tool descriptions and JSON schemas
- **Direct Tool Execution**: Commit count queries return direct answers ("The repository has 3 commits")
- **Feature Comparison**: Compare features between Notion documentation and GitHub code
- **Multi-Source Synthesis**: AI synthesizes responses using data from both Notion and GitHub
- **Docker Support**: Run the application in Docker containers

## Environment Variables Required
- `OPENAI_API_KEY` - OpenAI API key
- `GITHUB_PERSONAL_ACCESS_TOKEN` - GitHub personal access token
- `GITHUB_REPO` - GitHub repository in `owner/repo` format
- `NOTION_TOKEN` - Notion integration token

See `STARTER_GUIDE.md` for detailed instructions and `README.md` for complete feature documentation.