
"""
Policy Compiler: Converts free-text norms into structured, executable policies
"""

import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from .harmony_client import HarmonyClient
from .ollama_client import OllamaClient

@dataclass
class PolicyRule:
	"""A single policy rule with metadata"""
	id: str
	description: str
	category: str
	severity: str  # "low", "medium", "high"
	enforcement_type: str  # "require", "forbid", "recommend"
	rationale: str
	test_cases: List[str]
	exceptions: List[str]

@dataclass 
class PolicyPack:
	"""Complete policy specification"""
	name: str
	version: str
	domain: str
	rules: List[PolicyRule]
	metadata: Dict[str, Any]

class PolicyCompiler:
	"""Compiles free-text norms into structured policies using gpt-oss"""
    
	def __init__(self, reasoning_effort: str = "high"):
		self.harmony_client = HarmonyClient(reasoning_effort=reasoning_effort)
		self.ollama_client = OllamaClient()
		self.reasoning_effort = reasoning_effort
    
	def compile_norms(self, norms_text: str, domain: str = "general") -> PolicyPack:
		"""Convert free-text norms into structured policy pack"""
        
		# Check if Ollama is available
		if not self.ollama_client.is_available():
			raise Exception("Ollama is not running or gpt-oss:20b model not found. Please run: ollama pull gpt-oss:20b")
        
		developer_message = f"""You are a Policy Compiler for the TRACE system. Your task is to convert free-text organizational norms into structured, executable policy rules.

Domain: {domain}
Reasoning Effort: {self.reasoning_effort}

Output a valid JSON object with this structure:
{{
	"rules": [
		{{
			"id": "unique-rule-id",
			"description": "Clear rule description",
			"category": "content|security|privacy|etc",
			"severity": "low|medium|high",
			"enforcement_type": "require|forbid|recommend",
			"rationale": "Why this rule exists",
			"test_cases": ["example case 1", "example case 2"],
			"exceptions": ["exception case 1"]
		}}
	]
}}

Be thorough and consider edge cases. Show your reasoning process."""
        
		user_message = f"Convert these organizational norms into structured policy rules:\n\n{norms_text}"
        
		# Build Harmony conversation
		conversation = self.harmony_client.build_conversation(
			[user_message], 
			developer_message=developer_message
		)
        
		# Encode for gpt-oss
		tokens = self.harmony_client.encode_conversation(conversation)
        
		# Convert tokens back to text (simplified - in real implementation you'd use proper decoding)
		prompt = f"<system>{developer_message}</system>\n<user>{user_message}</user>\n<assistant>"
        
		# Generate response using Ollama
		response = self.ollama_client.generate(prompt)
        
		# Parse JSON response
		try:
			# Extract JSON from response (may have reasoning text before/after)
			response_text = response.response
			json_start = response_text.find('{')
			json_end = response_text.rfind('}') + 1
            
			if json_start != -1 and json_end > json_start:
				json_text = response_text[json_start:json_end]
				rules_data = json.loads(json_text)
                
				# Convert to PolicyRule objects
				rules = []
				for rule_dict in rules_data.get("rules", []):
					rule = PolicyRule(**rule_dict)
					rules.append(rule)
                
				return PolicyPack(
					name=f"{domain}_policy",
					version="1.0.0",
					domain=domain,
					rules=rules,
					metadata={
						"reasoning_effort": self.reasoning_effort,
						"generated_at": "2025-08-17",
						"raw_response": response_text  # Store for audit trail
					}
				)
			else:
				raise ValueError("No valid JSON found in response")
                
		except json.JSONDecodeError as e:
			raise Exception(f"Failed to parse policy JSON: {e}\nResponse: {response.response}")
    
	def save_policy_pack(self, policy_pack: PolicyPack, output_path: Path):
		"""Save policy pack to JSON file"""
		output_path.parent.mkdir(parents=True, exist_ok=True)
        
		with open(output_path, 'w') as f:
			json.dump(asdict(policy_pack), f, indent=2)
