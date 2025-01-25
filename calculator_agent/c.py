# main.py
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from openai import AzureOpenAI
import json
import math

# Load environment variables
load_dotenv()

# FastAPI and Pydantic setup
app = FastAPI(title='Calculator AI Agent')

class CalculatorRequest(BaseModel):
    model_name: str
    system_prompt: str
    messages: List[str]

class CalculatorAssistant:
    def __init__(self):
        """Initialize Azure OpenAI client."""
        self.client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2024-08-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )

    def calculate(self, operation: str, x: float, y: float = None) -> float:
        """Perform mathematical operations."""
        operations = {
            'add': lambda x, y: x + y,
            'subtract': lambda x, y: x - y,
            'multiply': lambda x, y: x * y,
            'divide': lambda x, y: x / y if y != 0 else "Error: Division by zero",
            'power': lambda x, y: x ** y,
            'sqrt': lambda x, _: math.sqrt(x),
            'log': lambda x, _: math.log(x),
            'sin': lambda x, _: math.sin(x),
            'cos': lambda x, _: math.cos(x)
        }
        
        if operation not in operations:
            raise ValueError(f"Unsupported operation: {operation}")
        
        return operations[operation](x, y) if y is not None else operations[operation](x, None)

    def calculator_function_call(self, user_message: str) -> str:
        """Process user message and perform calculator function call."""
        functions = [
            {
                "type": "function",
                "function": {
                    "name": "calculate",
                    "description": "Perform mathematical calculations",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "operation": {
                                "type": "string",
                                "enum": [
                                    "add", "subtract", "multiply", "divide", 
                                    "power", "sqrt", "log", "sin", "cos"
                                ],
                                "description": "Mathematical operation to perform"
                            },
                            "x": {
                                "type": "number",
                                "description": "First number for calculation"
                            },
                            "y": {
                                "type": "number",
                                "description": "Second number for binary operations"
                            }
                        },
                        "required": ["operation", "x"]
                    }
                }
            }
        ]

        # Generate response using OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful calculator assistant. Translate user requests into mathematical operations."
                },
                {"role": "user", "content": user_message}
            ],
            tools=functions
        )

        # Process the response
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            if tool_call.function.name == "calculate":
                # Parse function arguments
                args = json.loads(tool_call.function.arguments)
                
                try:
                    result = self.calculate(
                        operation=args["operation"],
                        x=args["x"],
                        y=args.get("y")
                    )
                    return f"Result: {result}"
                except Exception as e:
                    return f"Calculation error: {str(e)}"
        
        return message.content

# Create calculator assistant instance
calculator_assistant = CalculatorAssistant()

@app.post("/calculate")
def calculate_endpoint(request: CalculatorRequest):
    """
    API endpoint to handle calculator requests.
    """
    # Validate input
    if not request.messages:
        return {"error": "No messages provided"}

    # Process the first message
    result = calculator_assistant.calculator_function_call(request.messages[0])
    
    return {
        "messages": [
            {"type": "ai", "content": result}
        ]
    }
