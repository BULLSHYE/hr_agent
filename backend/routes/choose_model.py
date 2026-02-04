from fastapi import APIRouter, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from core.llm import set_model, get_llm, get_available_models, get_current_model, current_provider
from pydantic import BaseModel
from schema.choose_model import SetModelRequest

router = APIRouter()

# Set LLM model
@router.post("/set-model")
async def set_llm_model(request: SetModelRequest):
    try:
        set_model(request.provider, request.model, request.api_key)
        llm = get_llm()
        return {"message": f"Model set to {request.model} from {request.provider}", "model": str(llm)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# To check current LLM model
@router.get("/current-model")
async def get_current_model_endpoint():
    return get_current_model()

# Get list of available models
@router.get("/available-models")
async def get_available_models_endpoint():
    return {"providers": get_available_models()}

@router.post("/stream-chat")
async def stream_chat(request: dict):
    from core.llm import current_provider
    llm = get_llm()
    messages = request.get("messages", [])
    
    # For local models, format messages as string
    if current_provider == "local":
        prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "system":
                prompt += f"System: {content}\n"
            elif role == "user":
                prompt += f"User: {content}\n"
            elif role == "assistant":
                prompt += f"Assistant: {content}\n"
        prompt += "Assistant: "
        
        def generate():
            try:
                response = llm.invoke(prompt)
                yield f"data: {response}\n\n"
            except Exception as e:
                yield f"data: Error: {str(e)}\n\n"
    else:
        # For API models
        async def generate():
            async for chunk in llm.astream(messages):
                yield f"data: {chunk.content}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")