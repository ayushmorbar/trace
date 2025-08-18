from setuptools import setup, find_packages

setup(
    name="trace_offbeats",
    version="0.1.0",
    description="TRACE_OFFBEATS: Transparent Rules & Audit Compliance Engine",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "openai-harmony>=0.0.4",
        "ollama>=0.5.3",
        "fastapi>=0.116.1",
        "uvicorn>=0.35.0",
        "typer>=0.16.0",
        "sqlalchemy>=2.0.43",
        "pydantic>=2.11.7",
        "pytest>=8.4.1",
        "python-multipart>=0.0.20",
        "requests>=2.32.4",
        "pandas>=2.3.1",
        "jinja2>=3.1.6",
    ],
    entry_points={
        "console_scripts": [
            "trace_offbeats=trace_offbeats.cli:app",
            "trace=trace_offbeats.cli:app",
        ],
    },
)
