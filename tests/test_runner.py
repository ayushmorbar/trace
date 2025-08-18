"""
Test Runner: Executes policy tests and validates compliance
"""

import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass

from src.trace_offbeats.policy_compiler import PolicyPack, PolicyRule

@dataclass
class TestCase:
    """A test case for policy validation"""
    id: str
    description: str
    content: str
    expected_result: str  # "pass", "fail", "warn"
    category: str

@dataclass
class TestResult:
    """Result of running a test case"""
    case_id: str
    rule_id: str
    result: str  # "pass", "fail", "warn"
    confidence: float
    explanation: str

class PolicyTestRunner:
    """Runs tests against compiled policies"""
    
    def __init__(self):
        self.test_cases: List[TestCase] = []
        self.results: List[TestResult] = []
    
    def load_test_cases(self, cases_file: Path) -> List[TestCase]:
        """Load test cases from JSON file"""
        with open(cases_file, 'r') as f:
            cases_data = json.load(f)
        
        cases = []
        for case_dict in cases_data.get("cases", []):
            case = TestCase(**case_dict)
            cases.append(case)
        
        self.test_cases = cases
        return cases
    
    def run_tests(self, policy_pack: PolicyPack, test_cases: List[TestCase]) -> List[TestResult]:
        """Run test cases against policy rules"""
        results = []
        
        for test_case in test_cases:
            for rule in policy_pack.rules:
                # Simple rule matching (we'll enhance this with gpt-oss later)
                result = self._evaluate_rule_against_case(rule, test_case)
                results.append(result)
        
        self.results = results
        return results
    
    def _evaluate_rule_against_case(self, rule: PolicyRule, test_case: TestCase) -> TestResult:
        """Evaluate a single rule against a test case (simplified)"""
        # This is a placeholder - in next session we'll use gpt-oss for evaluation
        
        # Simple keyword matching for now
        keywords = rule.description.lower().split()
        content = test_case.content.lower()
        
        matches = sum(1 for keyword in keywords if keyword in content)
        confidence = min(matches / len(keywords), 1.0)
        
        if confidence > 0.5:
            result = "fail" if rule.enforcement_type == "forbid" else "pass"
        else:
            result = "pass" if rule.enforcement_type == "forbid" else "fail"
        
        return TestResult(
            case_id=test_case.id,
            rule_id=rule.id,
            result=result,
            confidence=confidence,
            explanation=f"Rule '{rule.id}' evaluation: {confidence:.2f} confidence"
        )
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate test report with metrics"""
        if not self.results:
            return {"error": "No test results available"}
        
        total_tests = len(self.results)
        passed = sum(1 for r in self.results if r.result == "pass")
        failed = sum(1 for r in self.results if r.result == "fail")
        warnings = sum(1 for r in self.results if r.result == "warn")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "pass_rate": passed / total_tests if total_tests > 0 else 0
            },
            "results": [
                {
                    "case_id": r.case_id,
                    "rule_id": r.rule_id,
                    "result": r.result,
                    "confidence": r.confidence,
                    "explanation": r.explanation
                } for r in self.results
            ]
        }
