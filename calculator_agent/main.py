import os 
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from groq import Groq
import json
import math



load_dotenv()

app = FastAPI(title="Calculator Agent")

class CalculatorRequest(BaseModel):
    # model_name: str
    calculator_model: str
    system_prompt: str
    messages: list[str]

class CalculatorAssistant:

    def __init__(self):

        self.client = Groq(
            api_key=os.getenv("GROQ_API_KEY")
        )

    def calculate(self, operation: str, x:float, y:float =None)-> float:

        operations={
            'add': lambda x, y: x+y,
            'subtract': lambda x, y: x-y,
            'multiply': lambda x, y: x*y,
            'divide': lambda x, y: x/y if y !=0 else "Error: Division by zero",
            'power': lambda x, y: x**y, 
            'sqrt': lambda x, _: math.sqrt(x)

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
            model="llama-3.3-70b-versatile",
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

# flask app
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





# For running this in terminal
def main():
    """CLI interface for calculator assistant"""
    # Verify API key
    if not os.getenv("GROQ_API_KEY"):
        print("Error: GROQ_API_KEY not found in environment variables")
        return

    assistant = CalculatorAssistant()
    
    print("Calculator CLI - Type 'exit' to quit")
    while True:
        try:
            user_input = input("\nEnter calculation request: ").strip()
            if user_input.lower() in ('exit', 'quit'):
                break
                
            if not user_input:
                continue
                
            response = assistant.calculator_function_call(user_input)
            print(f"Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()




# ui.py (Streamlit)
# import streamlit as st
# import requests

# # Streamlit App Configuration
# st.set_page_config(page_title="Calculator AI", layout="centered")

# # API Endpoint
# API_URL = "http://127.0.0.1:8000/calculate"

# # Predefined models (placeholder)
# MODEL_NAMES = [
#    "llama-3.3-70b-versatile"
   
# ]

# # Streamlit UI
# st.title("Calculator AI Agent")
# st.write("Perform mathematical calculations using AI")

# # Input for system prompt (optional)
# system_prompt = st.text_area(
#     "Custom Instructions:", 
#     height=100, 
#     placeholder="Provide optional context or special instructions for calculations..."
# )

# # Model selection
# selected_model = st.selectbox("Select Model:", MODEL_NAMES)

# # User input for calculation
# user_input = st.text_input("Enter your calculation:")

# # Calculate button
# if st.button("Calculate"):
#     if user_input.strip():
#         try:
#             # Prepare payload
#             payload = {
#                 "messages": [user_input],
#                 "model_name": selected_model,
#                 "system_prompt": system_prompt
#             }
            
#             # Send request
#             response = requests.post(API_URL, json=payload)
            
#             # Process response
#             if response.status_code == 200:
#                 response_data = response.json()
                
#                 if "error" in response_data:
#                     st.error(response_data["error"])
#                 else:
#                     # Display result
#                     ai_response = response_data.get("messages", [{}])[0].get("content", "No result")
#                     st.success(ai_response)
#             else:
#                 st.error(f"Request failed with status code {response.status_code}")
        
#         except Exception as e:
#             st.error(f"An error occurred: {e}")
#     else:
#         st.warning("Please enter a calculation")

# # If running as main script
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host='127.0.0.1', port=8000)