# Purpose: Defines FastAPI endpoints for LEXAI's API.
# Why: Explicitly separates API logic for clarity and deployment.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from controller.query_handler import QueryHandler
from pydantic import BaseModel

# Pydantic model for the query request
class QueryRequest(BaseModel):
    query: str
    session_id: str

# Initialize FastAPI app
app = FastAPI(title="LEXAI API")

# Configure CORS middleware (mirrors MYRAGAGENT)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Allow all origins
    allow_credentials=True,        # Allow cookies
    allow_methods=["GET", "POST"], # Explicitly allow GET and POST
    allow_headers=["*"],           # Allow all headers
)

# Instantiate query handler
query_handler = QueryHandler()

@app.post("/query")
async def query_endpoint(request: QueryRequest):
    """Handles user queries via POST request.
    
    Args:
        request (QueryRequest): The legal question and session ID.
    Returns:
        dict: Query and response.
    Raises:
        HTTPException: If query is empty or processing fails.
    """
    query = request.query
    session_id = request.session_id
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        response = query_handler.handle_query(session_id, query)
        return {"query": query, "response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/health")
async def health_check():
    """Checks the API's health status.
    
    Returns:
        dict: Health status.
    """
    return {"status": "healthy"}