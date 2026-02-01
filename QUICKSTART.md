# Quick Start Guide - Quantum Network Optimization

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
cd /Users/pranavks/MIT/2026-IonQ
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Run the Agent

**Option A: Quick Start (Easiest)**

```python
from executor import quick_start

summary = quick_start(
    player_id="your_unique_id",
    name="Your Name",
    location="remote",  # or "in_person"
    agent_type="default",  # or "aggressive" or "conservative"
    max_iterations=100
)

print(f"Final score: {summary['final_score']}")
print(f"Successful claims: {summary['successful_claims']}")
```

**Option B: Command Line**

```bash
python executor.py your_player_id "Your Name" remote default
```

**Option C: Full Control**

```python
from executor import GameExecutor

executor = GameExecutor("your_player_id", "Your Name", "remote")

# Register
executor.register()

# Select starting node (auto-select balanced)
executor.select_starting_node(strategy="balanced")

# Create agent
executor.create_agent(agent_type="default")

# Run
summary = executor.run(max_iterations=100, verbose=True)

# View leaderboard
executor.get_leaderboard(top_n=10)
```

---

## 🎮 Agent Types

### Default Agent (Balanced)
```python
agent_type="default"
```
- Balanced approach
- Good for most scenarios
- Risk tolerance: 0.5

### Aggressive Agent (High Risk, High Reward)
```python
agent_type="aggressive"
```
- Prioritizes high-value nodes
- Lower reserve budget
- Tries advanced protocols
- Risk tolerance: 0.3

### Conservative Agent (Steady Progress)
```python
agent_type="conservative"
```
- Avoids difficult edges
- Higher reserve budget
- More thorough simulation
- Risk tolerance: 0.7

---

## 🛠️ Custom Configuration

```python
from client import GameClient
from agent import QuantumNetworkAgent, AgentConfig

# Create client
client = GameClient()
client.register("player_id", "Name", "remote")
client.select_starting_node("node_id")

# Custom configuration
config = AgentConfig(
    # Strategy weights
    utility_weight=1.0,           # Importance of utility qubits
    difficulty_weight=0.5,        # Penalty for difficulty
    cost_weight=0.3,              # Penalty for cost
    success_prob_weight=0.4,      # Importance of success probability
    
    # Budget management
    min_reserve=10,               # Minimum bell pairs to keep
    max_retries_per_edge=3,       # Max attempts per edge
    risk_tolerance=0.5,           # 0=aggressive, 1=conservative
    
    # Simulation
    enable_simulation=True,       # Simulate before submission
    simulation_shots=1000,        # Simulation accuracy
    
    # Protocol selection
    prefer_dejmps=False,          # Prefer DEJMPS over BBPSSW
    
    # Adaptive behavior
    adaptive_risk=True,           # Adjust risk based on budget
    adaptive_pairs=True           # Adjust bell pairs based on attempts
)

# Create agent
agent = QuantumNetworkAgent(client, config)

# Run
summary = agent.run_autonomous(max_iterations=100, verbose=True)
```

---

## 📊 Understanding the Output

### Iteration Output
```
[1] ✓ Claimed ('A', 'B') (priority=10.52, ROI=4.23, bbpssw, 2 pairs)
[2] ✗ Failed ('B', 'C'): Estimated fidelity (0.82) below threshold (0.85)
[3] Skipped ('C', 'D'): ROI (0.35) below risk tolerance (0.5)
```

- `✓` = Successful claim
- `✗` = Failed attempt
- `Skipped` = Rejected by decision engine

### Final Summary
```
Iterations: 45
Successful claims: 12
Failed attempts: 3
Final score: 156
Final budget: 23
Owned nodes: 13
Owned edges: 12
```

---

## 🎯 Strategy Tips

### For Maximum Score

1. **Use Aggressive Agent**
   ```python
   agent_type="aggressive"
   ```

2. **Prioritize High-Value Nodes**
   ```python
   config.utility_weight = 1.5
   ```

3. **Accept Some Risk**
   ```python
   config.risk_tolerance = 0.3
   ```

### For Budget Conservation

1. **Use Conservative Agent**
   ```python
   agent_type="conservative"
   ```

2. **Avoid Difficult Edges**
   ```python
   config.difficulty_weight = 0.8
   ```

3. **Higher Reserve**
   ```python
   config.min_reserve = 20
   ```

### For Fast Execution

1. **Disable Simulation**
   ```python
   config.enable_simulation = False
   ```

2. **Fewer Retries**
   ```python
   config.max_retries_per_edge = 2
   ```

---

## 🔧 Manual Circuit Creation

If you want to create circuits manually:

```python
from distillation import create_bbpssw_circuit, create_dejmps_circuit
from simulator import DistillationSimulator

# Create BBPSSW circuit
circuit, flag_bit = create_bbpssw_circuit(num_bell_pairs=3)

# Simulate locally
simulator = DistillationSimulator()
results = simulator.simulate_circuit(
    circuit=circuit,
    flag_bit=flag_bit,
    num_bell_pairs=3,
    input_noise=0.15
)

print(f"Estimated fidelity: {results['estimated_fidelity']:.3f}")
print(f"Success probability: {results['success_probability']:.3f}")

# Submit to server
from client import GameClient
client = GameClient()
# ... register and select starting node ...

result = client.claim_edge(
    edge=('A', 'B'),
    circuit=circuit,
    flag_bit=flag_bit,
    num_bell_pairs=3
)
```

---

## 🧪 Testing

### Test Core Logic
```bash
python test_logic.py
```

### Test Distillation Circuits (requires Qiskit)
```bash
python test_distillation.py
```

### Run Examples
```bash
python example_usage.py
```

---

## 📚 Key Files

| File | Purpose |
|------|---------|
| `executor.py` | High-level execution (START HERE) |
| `agent.py` | Autonomous agent |
| `distillation.py` | Quantum circuits (BBPSSW, DEJMPS) |
| `strategy.py` | Edge selection & budget management |
| `simulator.py` | Local simulation |
| `client.py` | Server API wrapper |
| `IMPLEMENTATION.md` | Technical documentation |
| `SUMMARY.md` | Implementation summary |

---

## 🐛 Troubleshooting

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Invalid token"
Re-register:
```python
client.register("player_id", "Name", "remote")
```

### "No claimable edges"
You need to own at least one node:
```python
client.select_starting_node("node_id")
```

### "Insufficient budget"
Lower the minimum reserve:
```python
config.min_reserve = 5
```

---

## 📞 Quick Reference

### Import Everything
```python
from client import GameClient
from agent import QuantumNetworkAgent, AgentConfig
from executor import GameExecutor, quick_start
from distillation import create_bbpssw_circuit, create_dejmps_circuit
from strategy import EdgeSelectionStrategy, BudgetManager
from simulator import DistillationSimulator
```

### Common Operations
```python
# Register
client = GameClient()
client.register("player_id", "Name", "remote")

# Select starting node
client.select_starting_node("node_id")

# Get status
status = client.get_status()
print(f"Budget: {status['budget']}")
print(f"Score: {status['score']}")

# Get claimable edges
claimable = client.get_claimable_edges()
print(f"Claimable: {len(claimable)}")

# Create circuit
circuit, flag_bit = create_bbpssw_circuit(3)

# Claim edge
result = client.claim_edge(
    edge=('A', 'B'),
    circuit=circuit,
    flag_bit=flag_bit,
    num_bell_pairs=3
)

# Check leaderboard
leaderboard = client.get_leaderboard()
```

---

## 🎉 You're Ready!

**Three ways to start:**

1. **Quickest:**
   ```bash
   python executor.py your_id "Your Name" remote default
   ```

2. **Python:**
   ```python
   from executor import quick_start
   quick_start("your_id", "Your Name", "remote", "default", 100)
   ```

3. **Custom:**
   - Read `IMPLEMENTATION.md` for details
   - Customize `AgentConfig`
   - Run with your configuration

**Good luck in the hackathon! 🚀**
