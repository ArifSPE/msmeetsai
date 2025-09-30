# Agentic Business Rules POC

A Proof of Concept demonstrating a true agentic architecture using LlamaIndex, local Llama models, and Qdrant RAG for dynamic business rule discovery and execution.

## Architecture Overview

This POC demonstrates how an intelligent agent can:
1. Store business rules in a vector database (Qdrant)
2. Use LlamaIndex and local Llama models for natural language understanding
3. Dynamically query and retrieve relevant business rules using RAG
4. Make decisions and execute business logic autonomously

## Features

- **Agentic Architecture**: Self-directed agents that can reason about business scenarios
- **RAG-based Rule Storage**: Business rules stored as embeddings in Qdrant vector DB
- **Local LLM Integration**: Uses Ollama for running Llama models locally
- **Dynamic Rule Discovery**: Agents query RAG to find applicable business rules
- **Rule Execution Engine**: Automated execution of determined business rules
- **FastAPI Interface**: RESTful API for interacting with the agentic system

## Project Structure

```
AgenticPOC/
├── src/
│   ├── agents/           # Agentic components
│   ├── rag/             # RAG implementation
│   ├── business_rules/  # Rule definitions and management
│   ├── execution/       # Rule execution engine
│   └── api/            # FastAPI interface
├── data/
│   └── business_rules/ # Sample business rules
├── config/            # Configuration files
├── tests/            # Unit tests
└── examples/         # Demo scenarios
```

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install and run Ollama with Llama model:
```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull a Llama model
ollama pull llama3.2:1b
```

3. Start Qdrant vector database:
```bash
docker run -p 6333:6333 qdrant/qdrant
```

4. Initialize the system:
```bash
python -m src.main
```

## Usage

See the `examples/` directory for detailed usage scenarios.

## License

MIT License
