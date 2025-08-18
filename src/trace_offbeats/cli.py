#!/usr/bin/env python3
"""
TRACE_OFFBEATS: Transparent Rules & Audit Compliance Engine
CLI interface for the OpenAI Hackathon project
"""

import typer
import json
from typing import Optional
from pathlib import Path

from .policy_compiler import PolicyCompiler

app = typer.Typer(
	name="trace_offbeats",
	help="TRACE: Transparent Rules & Audit Compliance Engine",
	add_completion=False
)

@app.command()
def init(
	name: str = typer.Argument(..., help="Project name"),
	path: Optional[Path] = typer.Option(None, help="Project directory")
):
	"""Initialize a new TRACE_OFFBEATS policy project."""
	if path is None:
		path = Path.cwd() / name
    
	path.mkdir(exist_ok=True)
    
	# Create project structure
	(path / "norms").mkdir(exist_ok=True)
	(path / "cases").mkdir(exist_ok=True)
	(path / "output").mkdir(exist_ok=True)
    
	# Create sample files
	sample_norms = """# Content Moderation Norms
1. No hate speech or harassment toward any individual or group
2. No spam or excessive promotional content
3. No explicit adult content or nudity
4. Respect user privacy and personal data
5. No misinformation or deliberately false claims
6. No copyright infringement
"""
    
	(path / "norms" / "sample_norms.txt").write_text(sample_norms)
    
	typer.echo(f"✅ TRACE_OFFBEATS project '{name}' initialized at {path}")
	typer.echo(f"📝 Edit {path}/norms/sample_norms.txt to define your policies")

@app.command()
def compile(
	norms_file: Path = typer.Argument(..., help="Path to norms text file"),
	domain: str = typer.Option("content_moderation", help="Policy domain"),
	effort: str = typer.Option("high", help="Reasoning effort: low/medium/high"),
	output: Optional[Path] = typer.Option(None, help="Output JSON file")
):
	"""Compile text norms into structured policy pack."""
    
	if not norms_file.exists():
		typer.echo(f"❌ Norms file not found: {norms_file}")
		raise typer.Exit(1)
    
	# Set default output path
	if output is None:
		output = norms_file.parent / "output" / f"{domain}_policy.json"
    
	typer.echo(f"🔄 Compiling norms from {norms_file}")
	typer.echo(f"📋 Domain: {domain}")
	typer.echo(f"🧠 Reasoning effort: {effort}")
    
	try:
		# Read norms
		norms_text = norms_file.read_text()
        
		# Compile using gpt-oss
		compiler = PolicyCompiler(reasoning_effort=effort)
		policy_pack = compiler.compile_norms(norms_text, domain=domain)
        
		# Save result
		compiler.save_policy_pack(policy_pack, output)
        
		typer.echo(f"✅ Policy pack compiled successfully!")
		typer.echo(f"📄 Output: {output}")
		typer.echo(f"📊 Generated {len(policy_pack.rules)} rules")
        
		# Show summary
		for rule in policy_pack.rules[:3]:  # Show first 3 rules
			typer.echo(f"   • {rule.id}: {rule.description}")
        
		if len(policy_pack.rules) > 3:
			typer.echo(f"   ... and {len(policy_pack.rules) - 3} more rules")
            
	except Exception as e:
		typer.echo(f"❌ Compilation failed: {e}")
		raise typer.Exit(1)

@app.command()
def version():
	"""Show TRACE_OFFBEATS version."""
	typer.echo("TRACE_OFFBEATS v0.1.0 - OpenAI Hackathon Edition")


@app.command()
def test(
	policy_file: Path = typer.Argument(..., help="Path to policy JSON file"),
	cases_file: Path = typer.Argument(..., help="Path to test cases JSON file"),
	output: Optional[Path] = typer.Option(None, help="Output report file")
):
	"""Run tests against compiled policy."""
    
	if not policy_file.exists():
		typer.echo(f"❌ Policy file not found: {policy_file}")
		raise typer.Exit(1)
    
	if not cases_file.exists():
		typer.echo(f"❌ Test cases file not found: {cases_file}")
		raise typer.Exit(1)
    
	try:
		from tests.test_runner import PolicyTestRunner
		from .policy_compiler import PolicyPack
        
		# Load policy pack
		with open(policy_file, 'r') as f:
			policy_data = json.load(f)
        
		# Convert back to PolicyPack object (simplified)
		policy_pack = PolicyPack(
			name=policy_data["name"],
			version=policy_data["version"], 
			domain=policy_data["domain"],
			rules=[],  # We'll implement proper deserialization later
			metadata=policy_data["metadata"]
		)
        
		# Run tests
		test_runner = PolicyTestRunner()
		test_cases = test_runner.load_test_cases(cases_file)
		results = test_runner.run_tests(policy_pack, test_cases)
		report = test_runner.generate_report()
        
		# Display results
		typer.echo(f"🧪 Ran {report['summary']['total_tests']} tests")
		typer.echo(f"✅ Passed: {report['summary']['passed']}")
		typer.echo(f"❌ Failed: {report['summary']['failed']}")
		typer.echo(f"⚠️  Warnings: {report['summary']['warnings']}")
		typer.echo(f"📊 Pass rate: {report['summary']['pass_rate']:.1%}")
        
		# Save report if requested
		if output:
			with open(output, 'w') as f:
				json.dump(report, f, indent=2)
			typer.echo(f"📄 Report saved to: {output}")
            
	except Exception as e:
		typer.echo(f"❌ Testing failed: {e}")
		raise typer.Exit(1)

if __name__ == "__main__":
	app()
