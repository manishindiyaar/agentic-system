
Option 1: API Server

Save code as main.py
Start server:
uvicorn main:app --reload --port 8000

Test with Curl:

curl -X POST "http://localhost:8000/calculate" \
-H "Content-Type: application/json" \
-d '{"calculator_model": "llama-3.3-70b-versatile", "system_prompt": "Calculate precisely", "messages": ["What is 200 cubed?"]}'


----------------------------------------------------------------

Option 2: Streamlit UI
streamlit run main.py



----------------------------------------------------------------

# Calculator Agent Documentation

## Architecture
- **Backend**: FastAPI (REST API)
- **AI Core**: groq/llama-3.3-70b-versatile
- **Interfaces**: 
  - REST API
  - Streamlit Web UI
  - Command Line Interface

## Environment Variables
| Variable | Purpose | Required |
|----------|---------|----------|
| GROQ_API_KEY | Groq cloud access | Yes |

## API Endpoints
`POST /calculate`
- **Request Body**:
  ```json
  {
    "calculator_model": "llama-3.3-70b-versatile",
    "system_prompt": "Calculation instructions",
    "messages": ["User query"]
  }

  