"""
Model Provider Configuration for Vision Language Models
Multi-provider support with automatic fallback
"""

# Available Vision Language Model Providers
MODEL_PROVIDERS = {
    "openrouter_gemini": {
        "provider": "openrouter",
        "model": "google/gemini-2.5-flash",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "supports_vision": True,
        "cost_per_1k_tokens": 0.0,
        "speed": "fast",
        "recommended_for": "primary",
        "description": "Google Gemini Flash - Best for bill processing"
    },
    
    "groq_llama_scout": {
        "provider": "groq",
        "model": "meta-llama/llama-4-scout-17b-16e-instruct",
        "api_key_env": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "supports_vision": True,
        "cost_per_1k_tokens": 0.0,
        "speed": "very_fast",
        "recommended_for": "fallback",
        "description": "Llama 4 Scout - Fast fallback"
    },
    
    "openrouter_llama_vision": {
        "provider": "openrouter",
        "model": "meta-llama/llama-3.2-11b-vision-instruct:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "supports_vision": True,
        "cost_per_1k_tokens": 0.0,
        "speed": "medium",
        "recommended_for": "alternative",
        "description": "Llama Vision - Alternative option"
    },
    
    "openrouter_qwen": {
        "provider": "openrouter",
        "model": "qwen/qwen-2-vl-7b-instruct:free",
        "api_key_env": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "supports_vision": True,
        "cost_per_1k_tokens": 0.0,
        "speed": "medium",
        "recommended_for": "alternative",
        "description": "Qwen Vision - Another alternative"
    }
}

# Default model configuration
DEFAULT_VISION_MODEL = "openrouter_gemini"
FALLBACK_VISION_MODEL = "groq_llama_scout"

# Expense categories
EXPENSE_CATEGORIES = [
    "groceries",
    "dining",
    "utilities",
    "shopping",
    "entertainment",
    "uncategorized"
]

# Quality thresholds
MIN_CONFIDENCE_SCORE = 0.5
GOOD_CONFIDENCE_SCORE = 0.7
EXCELLENT_CONFIDENCE_SCORE = 0.85

# Processing limits
MAX_PROCESSING_TIME = 120