import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import HuggingFacePipeline
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from dotenv import load_dotenv

load_dotenv()

providers = {
    "openai": {
        "class": ChatOpenAI,
        "models": [
            {"name": "gpt-5.2", "display": "GPT-5.2 (Latest)"},
            {"name": "gpt-5.1", "display": "GPT-5.1"},
            {"name": "gpt-5-nano", "display": "GPT-5 Nano"}
        ],
        "api_key": os.getenv('open_ai_key')
    },
    "anthropic": {
        "class": ChatAnthropic,
        "models": [
            {"name": "claude-sonnet-4-5-20250929", "display": "Claude Sonnet 4.5"},
            {"name": "claude-4-sonnet-20250514", "display": "Claude 4 Sonnet"},
            {"name": "claude-opus-4-5-20251101", "display": "Claude Opus 4.5"}
        ],
        "api_key": os.getenv('anthropic_key', '')
    },
    "gemini": {
        "class": ChatGoogleGenerativeAI,
        "models": [
            {"name": "gemini-3-flash-preview", "display": "Gemini 3 Flash"},
            {"name": "gemini-3-pro-preview", "display": "Gemini 3 Pro"},
            {"name": "gemini-2.5-pro", "display": "Gemini 2.5 Pro"}
        ],
        "google_api_key": os.getenv('gemini_api_key')
    },
    "local": {
        "class": HuggingFacePipeline,
        "models": [
            {"name": "microsoft/Phi-3-mini-4k-instruct", "display": "Phi-3 Mini (3.8B)"},
            {"name": "mistralai/Mistral-7B-Instruct-v0.1", "display": "Mistral 7B Instruct"},
            {"name": "meta-llama/Llama-2-7b-chat-hf", "display": "LLaMA 2 7B Chat"}
        ],
        "api_key": None  
    }
}

current_provider = "gemini"
current_model = "gemini-2.5-pro"

# Cache for loaded local models
loaded_models = {}

def set_model(provider: str, model: str, api_key: str = None):
    global current_provider, current_model
    if provider in providers and model in [m["name"] for m in providers[provider]["models"]]:
        current_provider = provider
        current_model = model
        if api_key:
            if provider == "openai":
                providers[provider]["api_key"] = api_key
            elif provider == "anthropic":
                providers[provider]["api_key"] = api_key
            elif provider == "gemini":
                providers[provider]["google_api_key"] = api_key

def get_llm():
    p = providers[current_provider]
    cls = p["class"]
    
    if current_provider == "local":
        # Handle local models
        if current_model not in loaded_models:
            try:
                print(f"Downloading local model: {current_model}")
                tokenizer = AutoTokenizer.from_pretrained(current_model)
                model = AutoModelForCausalLM.from_pretrained(current_model)
                pipe = pipeline(
                    "text-generation",
                    model=model,
                    tokenizer=tokenizer,
                    max_new_tokens=512,
                    temperature=0.7,
                    do_sample=True,
                    pad_token_id=tokenizer.eos_token_id
                )
                loaded_models[current_model] = HuggingFacePipeline(pipeline=pipe)
                print(f"Model {current_model} loaded and ready for offline use.")
            except Exception as e:
                raise Exception(f"Failed to load local model {current_model}: {str(e)}")
        return loaded_models[current_model]
    else:
        # Handle API-based models
        kwargs = {"model": current_model}
        if "api_key" in p and p["api_key"]:
            kwargs["api_key" if current_provider != "gemini" else "google_api_key"] = p["api_key" if current_provider != "gemini" else "google_api_key"]
        elif "google_api_key" in p:
            kwargs["google_api_key"] = p["google_api_key"]
        return cls(**kwargs)

def get_available_models():
    return {provider: data["models"] for provider, data in providers.items()}

def get_current_model():
    models = providers.get(current_provider, {}).get("models", [])
    model_info = next((m for m in models if m["name"] == current_model), None)
    display = model_info["display"] if model_info else current_model
    return {"model": current_model, "display": display, "provider": current_provider}