from fastapi import FastAPI
from pydantic import BaseModel,conlist
from typing import List,Optional
import pandas as pd
from model import recommend,output_recommended_recipes
import google.generativeai as genai
import os
dataset=pd.read_csv('../Data/dataset.csv',compression='gzip')

app = FastAPI()


class params(BaseModel):
    n_neighbors:int=5
    return_distance:bool=False

class PredictionIn(BaseModel):
    nutrition_input:conlist(float, min_items=9, max_items=9)
    ingredients:list[str]=[]
    params:Optional[params]


class Recipe(BaseModel):
    Name:str
    CookTime:str
    PrepTime:str
    TotalTime:str
    RecipeIngredientParts:list[str]
    Calories:float
    FatContent:float
    SaturatedFatContent:float
    CholesterolContent:float
    SodiumContent:float
    CarbohydrateContent:float
    FiberContent:float
    SugarContent:float
    ProteinContent:float
    RecipeInstructions:list[str]

class PredictionOut(BaseModel):
    output: Optional[List[Recipe]] = None
# Message model to represent conversation history
class Message(BaseModel):
    role: str  # 'user' or 'ai'
    content: str

# Request model for chat
class ChatRequest(BaseModel):
    message: str
    conversation_history: List[Message] = []
    context: str = ""  # Added context field

# Response model for chat
class ChatResponse(BaseModel):
    response: str
    conversation_history: List[Message]
    context: str  # Return updated context

@app.get("/")
def home():
    return {"health_check": "OK"}


@app.post("/predict/",response_model=PredictionOut)
def update_item(prediction_input:PredictionIn):
    recommendation_dataframe=recommend(dataset,prediction_input.nutrition_input,prediction_input.ingredients,prediction_input.params.dict())
    output=output_recommended_recipes(recommendation_dataframe)
    if output is None:
        return {"output":None}
    else:
        return {"output":output}



# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-pro')

        # Prepare context-aware prompt
        context_prompt = request.context + "\n\n" if request.context else ""
        
        # Gather relevant previous messages (last 3-4 to prevent token overflow)
        history_context = "\n".join([
            f"{msg.role.upper()}: {msg.content}" 
            for msg in request.conversation_history[-4:]
        ])

        # Construct full prompt with context and history
        full_prompt = (
            f"{context_prompt}"
            f"Conversation History:\n{history_context}\n\n"
            f"Latest User Query: {request.message}\n\n"
            "Please provide a response that considers the entire conversation context."
        )

        # Generate response
        response = model.generate_content(full_prompt)

        # Prepare updated conversation history
        updated_history = request.conversation_history + [
            Message(role='user', content=request.message),
            Message(role='ai', content=response.text)
        ]

        # Generate new context based on conversation
        context_generation_prompt = (
            f"Summarize the key points and context from this conversation. "
            f"Provide a concise summary that captures the main topic and important details:\n\n"
            f"{full_prompt}\n\n"
            f"Response: {response.text}"
        )
        
        context_response = model.generate_content(context_generation_prompt)
        new_context = context_response.text[:500]  # Limit context length

        return {
            "response": response.text,
            "conversation_history": updated_history,
            "context": new_context
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
