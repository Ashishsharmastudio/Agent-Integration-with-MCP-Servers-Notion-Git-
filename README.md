# Alignment-Driven Development (ADD) Agent 
### Implementing an Intent-to-Code Traceability Protocol via MCP

A closed-loop AI governance architecture designed to bridge business intent (Notion) and execution state (GitHub) using the Model Context Protocol (MCP).

## 🛑 The Problem: Spec Entropy
In AI-assisted software development, teams often ship generated code faster than they can govern it. A feature is defined in a spec, passed to an LLM, and merged. Over time, the codebase drifts from the original business intent, creating a massive vacuum of stateful memory. 

This repository provides an **Intent-to-Code Traceability Protocol** to solve this. It forces the LLM to govern its code against the original intent, ensuring that the AI reads the manual before it touches the codebase. Instead of bolting an LLM onto a task tracker, this agent acts as a stateful governance bridge between your documentation and your codebase.

## 🏗️ Core Architecture: The Governance Loop
This system operates on a 4-step orchestration loop, leveraging MCP servers to maintain context isolation and data security.

1. **The Intent Layer (Notion MCP):** We treat Notion as the immutable source of truth for specs and architectural decisions. The agent is forced to read the manual before touching the code.
2. **The Governance Bridge (Reasoning Engine):** A semantic router (`reasoning.py`) analyzes the query, selects the appropriate MCP tools, and maps the business logic to the codebase, ensuring context isn't lost in translation.
3. **The Execution State (GitHub MCP):** The agent walks the repository tree and reads the current state of the code (`mcp_manager.py`).
4. **The Audit Trail:** The agent facilitates a decision ledger that survives team turnover by embedding the exact Notion spec URL into the resulting Git commit message, establishing permanent traceability from product intent to merged commit.

---

### 🧠 The "Alignment Gate" Implementation (`feature_diff.py`)
At the core of the governance loop is the Alignment Gate. Before execution, the system performs a deterministic feature diff between the Notion spec and the GitHub repository to halt "fixes" that violate the documented intent.
* It extracts structured requirement lists from the Notion markdown.
* It extracts implemented features from the Git blob.
* It computes a deterministic intersection (`overlap`, `only_in_notion`, `only_in_code`).
* It surfaces the top 3 architectural gaps that the engineering team (or AI) needs to prioritize to realign with the spec.

---

## 🚀 Quickstart & Deployment
This architecture is production-ready and containerized.

### Option 1: Single-Command Docker Execution (Recommended)
Launch the fully containerized governance bridge:
```bash
# Linux/macOS
./run_with_docker.sh

# Windows
run_with_docker.bat
```

### Option 2: Manual Setup
```bash
cp .env.example .env
# Fill in required tokens
pip install -r requirements.txt
python app.py
```

---

## 🔌 API & Alignment Gates in Action
The agent operates via a central unified endpoint (`GET /agent`) and has access to 35+ granular tools across your intent and execution layers.

**Example Workflows:**

* **Triggering the Alignment Gate:** 
  `GET /agent?query=compare%20features%20between%20docs%20and%20code`
  *Returns a strict feature diff evaluating code reality against the Notion spec.*
* **Auditing the Ledger:** 
  `GET /agent?query=how%20many%20commits%20are%20in%20the%20repository`
  *Direct tool execution returning the current state of the execution layer.*
* **Verifying Intent:** 
  `GET /agent?query=Find%20documentation%20about%20the%20API`
  *Forces the agent to synthesize a response from the designated source of truth.*

---

## 🔑 Environment Configuration
To secure the Governance Bridge, the following keys must be supplied in your `.env`:

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Orchestrates the Semantic Router & Alignment Diff | ✅ |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | Grants the Execution Layer read access | ✅ |
| `GITHUB_TOOLSETS` | GitHub toolsets (default: repos) | ✅ |
| `GITHUB_REPO` | Target repository in `owner/repo` format | ✅ |
| `GITHUB_DEFAULT_REF` | Default branch (default: master) | ✅ |
| `NOTION_TOKEN` | Grants the Intent Layer read access | ✅ |
| `PORT` | Application port (default: 5000) | ❌ |
| `FLASK_ENV` | Flask environment (default: development) | ❌ |

---

## 🧪 Testing the Traceability Protocol
The repository includes a comprehensive test suite covering the reasoning engine, the alignment gates, and the MCP state managers.

```bash
# Test the unified workflow
python test_workflow.py

# Run all unit and integration tests
python run_tests.py
```
