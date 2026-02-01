# Quantum Network Optimization - IonQ Hackathon 2026

Autonomous agent for quantum entanglement distillation in a competitive network game.

## Overview

Built for the IonQ 2026 hackathon, this agent competes in a quantum networking game where players claim edges by distilling noisy Bell pairs into high-fidelity entangled states. The agent uses adaptive strategies to maximize network utility while managing a limited Bell pair budget.

**Core capabilities:**
- Edge selection based on utility, difficulty, and expected ROI
- LOCC-compliant distillation circuits (BBPSSW, DEJMPS protocols)
- Adaptive resource allocation with risk management
- Local simulation to avoid wasting budget on low-probability attempts

## Architecture

```
2026-IonQ/
├── config/          # API tokens and settings
├── core/            # Game client and orchestration
├── distillation/    # Circuit generation and local simulation
├── strategy/        # Edge scoring and budget management
├── agentic/         # LangGraph agent (recommended)
├── hardware/        # IBM Quantum validation (optional)
├── visualization/   # Network graphs
├── examples/        # Usage examples
├── notebooks/       # Demos
├── docs/            # Documentation
└── tests/           # Test suites
```

## Quick Start

```bash
cd 2026-IonQ
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Run the agent:**

```bash
python -m agentic.run_langgraph_agent --player-id YOUR_ID --name "Your Name"
```

**Or use programmatically:**

```python
from core.executor import GameExecutor

executor = GameExecutor("your_player_id", "YourName")
summary = executor.run(agent_type="default", use_langgraph=True)
```

**Strategy presets:**
- `default`: Balanced approach
- `aggressive`: Higher risk, targets high-utility edges
- `conservative`: Safer plays, maintains larger budget reserve

## Documentation

- [LangGraph Quickstart](docs/LANGGRAPH_QUICKSTART.md) - Agent setup and usage
- [Integration Guide](docs/LANGGRAPH_INTEGRATION_GUIDE.md) - Architecture details
- [Agent Comparison](docs/AGENT_ARCHITECTURE_COMPARISON.md) - Legacy vs LangGraph

## Testing

```bash
python -m pytest tests/
```

Individual test suites available in `tests/` directory.

## Key Features

**LangGraph Agent** (recommended)
- Modular node-based architecture for better debugging
- Deterministic decisions (no LLM calls)
- Explicit state transitions
- 90% test coverage

**Distillation Protocols**
- BBPSSW and DEJMPS implementations
- LOCC-compliant (no entangling gates across Alice/Bob boundary)
- Local simulation to estimate fidelity before submission
- Post-selection via flag bit

**Strategy**
- Multi-factor edge scoring: utility, difficulty, cost, success probability
- Adaptive resource allocation (increases Bell pairs on retry)
- Risk-adjusted budget management
- Configurable reserve thresholds

**IBM Quantum** (optional)
- Hardware validation for distillation circuits
- Noise model simulation
- Defaults to simulation mode (safe for testing)

## How It Works

**Entanglement Distillation**  
The game provides noisy Bell pairs on each edge. Players design circuits using only local operations (gates within Alice or Bob's lab) and classical communication to distill these into high-fidelity pairs. The challenge is meeting the fidelity threshold while maximizing success probability.

**LOCC Constraints**  
Two-qubit gates can't span the Alice/Bob boundary (no real entangling operations across the network). Measurements can be shared classically. Post-selection uses a flag bit to keep only successful outcomes.

**Agent Strategy**  
The LangGraph agent scores edges based on utility, difficulty, and expected cost. It adaptively allocates Bell pairs (more on retries) and uses local simulation to avoid wasting budget on low-probability attempts. The agent is deterministic—no LLM calls, just heuristics tuned for the game mechanics.

## Development

Import paths after reorganization:

```python
from core.client import GameClient
from strategy.strategy import EdgeSelectionStrategy
from distillation.distillation import create_bbpssw_circuit
from agentic.langgraph_deterministic_agent import LangGraphQuantumAgent
```

See `docs/` for architecture details and migration guides.

## License

MIT

---

Built for IonQ Hackathon 2026
