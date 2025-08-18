"""
Ollama client for running gpt-oss-20b locally
"""

import requests
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class OllamaResponse:
    """Response from Ollama API"""
    response: str
    done: bool
    total_duration: Optional[int] = None
    load_duration: Optional[int] = None

class OllamaClient:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gpt-oss:20b"):
        self.base_url = base_url
        self.model = model
    
    def generate(self, prompt: str, stream: bool = False) -> OllamaResponse:
        """Generate response from gpt-oss model"""
        url = f"{self.base_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 1.0,  # OpenAI recommended settings
                "top_p": 1.0
            }
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            
            if stream:
                # Handle streaming responses
                return self._handle_stream_response(response)
            else:
                data = response.json()
                return OllamaResponse(
                    response=data.get("response", ""),
                    done=data.get("done", False),
                    total_duration=data.get("total_duration"),
                    load_duration=data.get("load_duration")
                )
                
        except requests.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
    
    def _handle_stream_response(self, response):
        """Handle streaming response from Ollama"""
        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    full_response += data["response"]
                if data.get("done", False):
                    return OllamaResponse(response=full_response, done=True)
        return OllamaResponse(response=full_response, done=True)
    
    def is_available(self) -> bool:
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            models = response.json().get("models", [])
            return any(self.model in model.get("name", "") for model in models)
        except requests.RequestException:
            return False
