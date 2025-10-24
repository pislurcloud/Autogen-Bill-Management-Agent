"""
Vision Language Model Provider - FIXED VERSION
Multi-provider abstraction with automatic fallback
Properly configured for OpenRouter Gemini and Groq
"""

import os
import base64
import time
import json
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

from src.config.model_config import MODEL_PROVIDERS, DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL


class VLMProvider:
    """Vision Language Model provider interface"""
    
    def __init__(self, provider_config: Dict[str, Any]):
        self.config = provider_config
        self.provider_name = provider_config["provider"]
        self.model_name = provider_config["model"]
        self.client = self._initialize_client()
        
        print(f"✅ Initialized VLM: {self.provider_name} - {self.model_name}")
    
    def _initialize_client(self) -> OpenAI:
        """Initialize OpenAI-compatible client for OpenRouter or Groq"""
        api_key_env = self.config["api_key_env"]
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            raise ValueError(
                f"API key not found: {api_key_env}. "
                f"Please set it in your .env file.\n"
                f"For OpenRouter: Get key from https://openrouter.ai/keys\n"
                f"For Groq: Get key from https://console.groq.com/keys"
            )
        
        # Verify key format
        if api_key_env == "OPENROUTER_API_KEY" and not api_key.startswith("sk-or-"):
            print(f"⚠️  Warning: OpenRouter API key should start with 'sk-or-'")
            print(f"   Current key starts with: {api_key[:10]}...")
        
        if api_key_env == "GROQ_API_KEY" and not api_key.startswith("gsk_"):
            print(f"⚠️  Warning: Groq API key should start with 'gsk_'")
            print(f"   Current key starts with: {api_key[:10]}...")
        
        # Initialize OpenAI-compatible client
        # Both OpenRouter and Groq use OpenAI-compatible API
        client = OpenAI(
            api_key=api_key,
            base_url=self.config["base_url"]
        )
        
        print(f"   API Base URL: {self.config['base_url']}")
        print(f"   Model: {self.model_name}")
        
        return client
    
    def analyze_image(self, image_path: str, prompt: str, temperature: float = 0.1) -> str:
        """
        Analyze image using VLM
        
        Args:
            image_path: Path to image file
            prompt: Analysis prompt
            temperature: Sampling temperature
            
        Returns:
            Model response as string
        """
        print(f"📸 Analyzing image with {self.provider_name} ({self.model_name})...")
        
        # Read and encode image
        with open(image_path, "rb") as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Get image format
        ext = image_path.split('.')[-1].lower()
        image_format = 'jpeg' if ext == 'jpg' else ext
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,  # Use the actual model name from config
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/{image_format};base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_tokens=2000
            )
            
            result = response.choices[0].message.content
            print(f"✅ Got response from {self.provider_name} ({len(result)} chars)")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Error with {self.provider_name}: {error_msg}")
            
            # Provide helpful error messages
            if "401" in error_msg or "unauthorized" in error_msg.lower():
                raise Exception(
                    f"Authentication failed with {self.provider_name}.\n"
                    f"Check your {self.config['api_key_env']} in .env file.\n"
                    f"Make sure the API key is valid and active."
                )
            elif "404" in error_msg or "not found" in error_msg.lower():
                raise Exception(
                    f"Model not found: {self.model_name}\n"
                    f"Provider: {self.provider_name}\n"
                    f"This model might not be available or has been renamed."
                )
            elif "rate limit" in error_msg.lower():
                raise Exception(
                    f"Rate limit exceeded on {self.provider_name}.\n"
                    f"Please wait a moment and try again."
                )
            else:
                raise Exception(f"VLM Error ({self.model_name}): {error_msg}")
    
    def generate_text(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Generate text response (for non-vision tasks)
        
        Args:
            prompt: Text prompt
            temperature: Sampling temperature
            
        Returns:
            Model response as string
        """
        print(f"💬 Generating text with {self.provider_name}...")
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,  # Use the actual model name
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content
            print(f"✅ Got text response ({len(result)} chars)")
            return result
            
        except Exception as e:
            raise Exception(f"Text Generation Error ({self.model_name}): {str(e)}")


class ModelManager:
    """Manages multiple VLM providers with automatic fallback"""
    
    def __init__(
        self, 
        primary_model: str = DEFAULT_VISION_MODEL,
        fallback_model: Optional[str] = FALLBACK_VISION_MODEL
    ):
        self.primary_model_name = primary_model
        self.fallback_model_name = fallback_model
        
        print(f"\n🤖 Initializing Model Manager")
        print(f"   Primary: {primary_model}")
        print(f"   Fallback: {fallback_model if fallback_model else 'None'}")
        print()
        
        # Initialize providers
        try:
            self.primary = VLMProvider(MODEL_PROVIDERS[primary_model])
        except Exception as e:
            print(f"❌ Failed to initialize primary model: {e}")
            raise
        
        if fallback_model:
            try:
                self.fallback = VLMProvider(MODEL_PROVIDERS[fallback_model])
            except Exception as e:
                print(f"⚠️  Failed to initialize fallback model: {e}")
                self.fallback = None
        else:
            self.fallback = None
        
        print()
    
    def analyze_image_with_fallback(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyze image with automatic fallback
        
        Args:
            image_path: Path to bill image
            prompt: Analysis prompt
            
        Returns:
            Dict with response and metadata
        """
        start_time = time.time()
        
        # Try primary model
        try:
            response = self.primary.analyze_image(image_path, prompt)
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "model_used": self.primary_model_name,
                "fallback_used": False,
                "processing_time": elapsed
            }
        
        except Exception as primary_error:
            print(f"\n⚠️ Primary model ({self.primary_model_name}) failed: {primary_error}\n")
            
            # Try fallback if available
            if self.fallback:
                try:
                    print(f"🔄 Trying fallback model ({self.fallback_model_name})...\n")
                    response = self.fallback.analyze_image(image_path, prompt)
                    elapsed = time.time() - start_time
                    
                    return {
                        "success": True,
                        "response": response,
                        "model_used": self.fallback_model_name,
                        "fallback_used": True,
                        "primary_error": str(primary_error),
                        "processing_time": elapsed
                    }
                
                except Exception as fallback_error:
                    elapsed = time.time() - start_time
                    return {
                        "success": False,
                        "error": f"Both models failed.\nPrimary ({self.primary_model_name}): {primary_error}\nFallback ({self.fallback_model_name}): {fallback_error}",
                        "fallback_used": True,
                        "processing_time": elapsed
                    }
            else:
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "error": str(primary_error),
                    "fallback_used": False,
                    "processing_time": elapsed
                }
    
    def generate_text_with_fallback(self, prompt: str) -> Dict[str, Any]:
        """
        Generate text with automatic fallback
        
        Args:
            prompt: Text prompt
            
        Returns:
            Dict with response and metadata
        """
        start_time = time.time()
        
        # Try primary
        try:
            response = self.primary.generate_text(prompt)
            elapsed = time.time() - start_time
            
            return {
                "success": True,
                "response": response,
                "model_used": self.primary_model_name,
                "fallback_used": False,
                "processing_time": elapsed
            }
        
        except Exception as primary_error:
            # Try fallback
            if self.fallback:
                try:
                    response = self.fallback.generate_text(prompt)
                    elapsed = time.time() - start_time
                    
                    return {
                        "success": True,
                        "response": response,
                        "model_used": self.fallback_model_name,
                        "fallback_used": True,
                        "processing_time": elapsed
                    }
                
                except Exception as fallback_error:
                    elapsed = time.time() - start_time
                    return {
                        "success": False,
                        "error": f"Both failed. Primary: {primary_error}. Fallback: {fallback_error}",
                        "processing_time": elapsed
                    }
            else:
                elapsed = time.time() - start_time
                return {
                    "success": False,
                    "error": str(primary_error),
                    "processing_time": elapsed
                }


def extract_json_from_response(response: str) -> Dict[str, Any]:
    """
    Extract JSON from VLM response (handles markdown)
    
    Args:
        response: Model response string
        
    Returns:
        Parsed JSON dictionary
    """
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try extracting from markdown code block
        if "```json" in response:
            start = response.find("```json") + 7
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        elif "```" in response:
            start = response.find("```") + 3
            end = response.find("```", start)
            json_str = response[start:end].strip()
            return json.loads(json_str)
        else:
            # Try finding JSON object
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                raise ValueError("No valid JSON found in response")