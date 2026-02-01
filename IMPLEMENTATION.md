# Quantum Network Optimization - Core Implementation

## Overview

This implementation provides a complete autonomous system for the iQuHACK 2026 Quantum Entanglement Distillation Game. It includes:

1. **Real entanglement distillation circuits** (BBPSSW, DEJMPS)
2. **Intelligent edge selection strategy** (multi-factor scoring)
3. **Budget-aware decision engine** (ROI optimization)
4. **Adaptive distillation planning** (dynamic bell pair allocation)
5. **Local circuit simulation** (pre-submission validation)
6. **Autonomous agent** (rule-based decision making)

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GameExecutor                         │
│              (High-level orchestration)                 │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              QuantumNetworkAgent                        │
│         (Autonomous decision making)                    │
└──┬──────────────┬──────────────┬──────────────┬────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│Edge  │   │Budget    │   │Distill   │   │Circuit   │
│Select│   │Manager   │   │Planner   │   │Simulator │
└──────┘   └──────────┘   └──────────┘   └──────────┘
   │              │              │              │
   └──────────────┴──────────────┴──────────────┘
                     │
                     ▼
              ┌─────────────┐
              │ GameClient  │
              │   (API)     │
              └─────────────┘
```

---

## Module Descriptions

### 1. `distillation.py` - Entanglement Purification Circuits

**Purpose**: Implements quantum circuits for entanglement distillation.

**Key Functions**:

- `create_bbpssw_circuit(num_bell_pairs)` - BBPSSW protocol
  - Best for depolarizing and bit-flip noise
  - Uses bilateral CNOT operations
  - Post-selects on ancilla measurements
  
- `create_dejmps_circuit(num_bell_pairs)` - DEJMPS protocol
  - Optimized for phase noise (Z errors)
  - Uses X and Z basis parity checks
  - Better success probability for phase-damping channels
  
- `create_adaptive_distillation_circuit(num_bell_pairs, noise_type)` - Adaptive selection
  - Chooses protocol based on noise type
  
- `create_recursive_distillation_circuit(num_bell_pairs)` - Recursive approach
  - For higher fidelity with more bell pairs
  
- `estimate_success_probability(num_bell_pairs, protocol)` - Heuristic estimation
- `estimate_output_fidelity(input_fidelity, num_bell_pairs, protocol)` - Theoretical bounds

**LOCC Constraints**:
- All two-qubit gates respect Alice/Bob boundary
- Qubits 0 to N-1: Alice's side
- Qubits N to 2N-1: Bob's side
- No entangling gates across boundary

**Qubit Layout**:
```
Bell pair k: (qubit k, qubit 2N-1-k)
Target pair: (qubit N-1, qubit N)
```

---

### 2. `strategy.py` - Edge Selection and Budget Management

**Purpose**: Intelligent decision-making for edge selection and resource allocation.

#### EdgeSelectionStrategy

**Multi-factor scoring function**:
```
priority = utility_weight × utility_qubits
         + success_prob_weight × success_probability × 10
         - difficulty_weight × difficulty
         - cost_weight × expected_cost
         + ROI × 2.0
```

**Key Methods**:
- `score_edge(edge, graph, status, owned_nodes)` - Calculate priority score
- `rank_edges(claimable_edges, graph, status)` - Rank all edges
- `select_best_edge(...)` - Select optimal edge with budget constraints

**Factors Considered**:
- Utility qubits of target node
- Bonus bell pairs from target node
- Edge difficulty rating
- Fidelity threshold
- Estimated success probability
- Expected bell pair cost
- Return on investment (ROI)

#### BudgetManager

**Risk-aware resource management**:

**Key Methods**:
- `should_attempt_edge(edge_score, current_budget)` - Approval decision
- `record_attempt(edge_id, success, actual_cost)` - Learning from history
- `adjust_risk_tolerance(current_budget, initial_budget)` - Dynamic adaptation

**Decision Criteria**:
- Retry limits (default: 3 per edge)
- Budget constraints (minimum reserve: 10)
- Expected value (utility - cost > 0)
- ROI threshold (based on risk tolerance)
- Success probability threshold (> 20%)

**Risk Tolerance Adaptation**:
```
Budget ratio < 20%: risk_tolerance = 0.8 (very conservative)
Budget ratio < 50%: risk_tolerance = 0.6 (conservative)
Budget ratio ≥ 50%: risk_tolerance = 0.4 (normal)
```

#### AdaptiveDistillationPlanner

**Dynamic bell pair allocation**:

**Strategy**:
1. Start with minimum (2 pairs)
2. Increase based on difficulty and threshold
3. Increment on retries
4. Cap at budget constraints

**Formula**:
```
base_pairs = 2 (easy) | 3 (medium) | 4 (hard)
pairs = base_pairs + attempt_number
if threshold > 0.85: pairs += 1
if threshold > 0.92: pairs += 1
pairs = min(pairs, budget // 2, 8)
```

---

### 3. `simulator.py` - Local Circuit Simulation

**Purpose**: Estimate circuit performance before server submission.

#### DistillationSimulator

**Key Methods**:
- `estimate_fidelity(circuit, flag_bit, num_bell_pairs, input_noise)` - Fast analytical estimate
- `simulate_circuit(...)` - Full simulation (uses analytical approximation for speed)
- `validate_circuit(circuit, num_bell_pairs)` - LOCC constraint validation
- `should_submit(...)` - Go/no-go decision

**Validation Checks**:
1. Correct qubit count (2N)
2. LOCC constraint (no gates across boundary)
3. Valid gate set
4. Estimated fidelity ≥ threshold - safety_margin
5. Success probability ≥ 10%

**Fidelity Estimation**:
Uses theoretical distillation formula:
```
F_out = F_in² / (F_in² + (1-F_in)²)
```
Applied recursively for multiple rounds.

**Success Probability Estimation**:
```
success_prob = 0.7^(2 × num_ancilla_pairs)
```

---

### 4. `agent.py` - Autonomous Decision Agent

**Purpose**: Rule-based agent for autonomous game execution.

#### QuantumNetworkAgent

**Decision Pipeline**:
```
1. Get claimable edges
2. Rank by priority (EdgeSelectionStrategy)
3. Select best edge (budget constraints)
4. Check approval (BudgetManager)
5. Select protocol (BBPSSW vs DEJMPS)
6. Determine bell pair count (AdaptiveDistillationPlanner)
7. Create circuit
8. Simulate locally (DistillationSimulator)
9. Submit to server (if approved)
10. Record results and learn
```

**Protocol Selection Logic**:
```python
if difficulty >= 7 or threshold >= 0.9:
    protocol = "dejmps"
else:
    protocol = "bbpssw"

# On retry: alternate protocols
if attempt_number % 2 == 1:
    protocol = alternate(protocol)
```

**Key Methods**:
- `select_protocol(edge_score, attempt_number)` - Choose distillation protocol
- `create_circuit(protocol, num_bell_pairs)` - Generate quantum circuit
- `attempt_edge_claim(edge_score, attempt_number)` - Full claim attempt
- `run_iteration()` - Single decision loop iteration
- `run_autonomous(max_iterations, verbose)` - Full autonomous execution

**Agent Configurations**:

1. **Default Agent**: Balanced approach
   - Utility weight: 1.0
   - Risk tolerance: 0.5
   - Min reserve: 10
   - Max retries: 3

2. **Aggressive Agent**: High risk, high reward
   - Utility weight: 1.5 (prioritize high-value nodes)
   - Risk tolerance: 0.3 (lower threshold = more aggressive)
   - Min reserve: 5
   - Prefer DEJMPS protocol

3. **Conservative Agent**: Low risk, steady progress
   - Difficulty weight: 0.8 (avoid hard edges)
   - Risk tolerance: 0.7 (higher threshold = more conservative)
   - Min reserve: 20
   - More thorough simulation (2000 shots)

---

### 5. `executor.py` - High-Level Orchestration

**Purpose**: User-friendly interface for game execution.

#### GameExecutor

**Complete workflow**:
1. Player registration
2. Starting node selection (auto or manual)
3. Agent creation and configuration
4. Autonomous execution
5. Results reporting

**Key Methods**:
- `register()` - Register player
- `select_starting_node(node_id, strategy)` - Choose starting node
- `create_agent(agent_type, config)` - Create configured agent
- `run(agent_type, max_iterations, verbose)` - Full execution
- `get_leaderboard(top_n)` - Display rankings
- `restart()` - Reset game

**Starting Node Selection Strategies**:
- `"utility"`: Maximize utility qubits
- `"bonus"`: Maximize bonus bell pairs
- `"balanced"`: Weighted combination (utility + bonus × 0.5)

**Quick Start Function**:
```python
from executor import quick_start

summary = quick_start(
    player_id="your_id",
    name="Your Name",
    location="remote",
    agent_type="default",
    max_iterations=100
)
```

---

## Usage Examples

### Example 1: Manual Circuit Creation

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
```

### Example 2: Strategy-Based Edge Selection

```python
from client import GameClient
from strategy import EdgeSelectionStrategy

client = GameClient()
client.register("player_id", "Name", "remote")
client.select_starting_node("node_id")

# Get claimable edges
claimable = client.get_claimable_edges()
graph = client.get_cached_graph()
status = client.get_status()

# Rank edges
strategy = EdgeSelectionStrategy()
ranked = strategy.rank_edges(claimable, graph, status)

# Select best
best = strategy.select_best_edge(claimable, graph, status)
print(f"Best edge: {best.edge_id} (priority={best.priority:.2f})")
```

### Example 3: Autonomous Agent

```python
from client import GameClient
from agent import create_default_agent

client = GameClient()
client.register("player_id", "Name", "remote")
client.select_starting_node("node_id")

# Create and run agent
agent = create_default_agent(client)
summary = agent.run_autonomous(max_iterations=100, verbose=True)

print(f"Final score: {summary['final_score']}")
print(f"Successful claims: {summary['successful_claims']}")
```

### Example 4: Complete Execution

```python
from executor import GameExecutor

executor = GameExecutor("player_id", "Name", "remote")
summary = executor.run(agent_type="default", max_iterations=100)

executor.get_leaderboard(top_n=10)
```

### Example 5: Command Line

```bash
python executor.py player_id "Your Name" remote default
```

---

## Testing

### Run Test Suite

```bash
python test_distillation.py
```

**Tests**:
- Circuit structure validation
- LOCC constraint verification
- Qubit count correctness
- Measurement presence
- Success probability estimates
- Fidelity improvement estimates

### Run Examples

```bash
python example_usage.py
```

**Examples**:
- Manual circuit creation
- Edge selection strategy
- Budget management
- Protocol comparison
- Complete execution flow

---

## Key Algorithms

### 1. Edge Priority Scoring

**Objective**: Maximize expected utility per bell pair spent.

**Algorithm**:
```
For each claimable edge:
  1. Calculate expected utility = (utility + bonus × 0.5) × success_prob
  2. Estimate cost = f(difficulty, threshold)
  3. Calculate ROI = expected_utility / cost
  4. Compute priority = weighted_sum(utility, success_prob, -difficulty, -cost, ROI)
  
Return edge with highest priority
```

### 2. Budget-Aware Decision

**Objective**: Avoid budget exhaustion while maximizing score.

**Algorithm**:
```
For each edge attempt:
  1. Check retry limit (max 3 per edge)
  2. Check budget constraint (cost + reserve ≤ budget)
  3. Check expected value (utility - cost > 0)
  4. Check ROI threshold (ROI ≥ risk_tolerance)
  5. Check success probability (prob ≥ 0.2)
  
If all checks pass: APPROVE
Else: REJECT with reason
```

### 3. Adaptive Bell Pair Allocation

**Objective**: Use minimum resources while meeting threshold.

**Algorithm**:
```
base_pairs = difficulty_based_estimate()
pairs = base_pairs + attempt_number

If threshold > 0.85: pairs += 1
If threshold > 0.92: pairs += 1

pairs = clamp(pairs, 2, min(8, budget // 2))

Return pairs
```

### 4. Protocol Selection

**Objective**: Choose optimal distillation protocol for noise type.

**Algorithm**:
```
If first attempt:
  If difficulty ≥ 7 OR threshold ≥ 0.9:
    protocol = "dejmps"  # Better for phase noise
  Else:
    protocol = "bbpssw"  # Robust for general noise
Else:
  protocol = alternate(previous_protocol)  # Explore alternatives

Return protocol
```

---

## Performance Characteristics

### Time Complexity

- **Edge ranking**: O(E log E) where E = number of claimable edges
- **Circuit creation**: O(N²) where N = number of bell pairs
- **Simulation**: O(1) (analytical approximation)
- **Single iteration**: O(E log E + N²)

### Space Complexity

- **Circuit storage**: O(N²) gates
- **Graph cache**: O(V + E) where V = nodes, E = edges
- **Agent state**: O(E) for attempt history

### Scalability

- **Max bell pairs**: 8 (game constraint)
- **Max iterations**: Configurable (default: 100)
- **Max edges**: Scales to thousands
- **Simulation**: Fast analytical estimates (no exponential state simulation)

---

## Configuration Tuning

### For High Scores

```python
config = AgentConfig(
    utility_weight=1.5,      # Prioritize high-value nodes
    difficulty_weight=0.3,   # Accept some difficulty
    risk_tolerance=0.4,      # Moderate risk
    prefer_dejmps=True,      # Try advanced protocol
    adaptive_risk=True       # Adjust based on budget
)
```

### For Budget Conservation

```python
config = AgentConfig(
    difficulty_weight=0.8,   # Avoid hard edges
    cost_weight=0.6,         # Minimize cost
    min_reserve=20,          # Higher reserve
    risk_tolerance=0.7,      # Conservative
    max_retries_per_edge=4   # More attempts on easy edges
)
```

### For Fast Execution

```python
config = AgentConfig(
    enable_simulation=False,  # Skip simulation
    max_retries_per_edge=2,   # Fewer retries
    simulation_shots=500      # Faster simulation if enabled
)
```

---

## Limitations and Future Work

### Current Limitations

1. **Simulation**: Uses analytical approximation instead of full quantum simulation
   - Trade-off: Speed vs accuracy
   - Mitigation: Conservative safety margins

2. **Noise estimation**: Heuristic mapping from difficulty to noise
   - Trade-off: No ground truth noise parameters
   - Mitigation: Adaptive protocol selection

3. **No learning**: Agent doesn't learn from past attempts
   - Trade-off: Simplicity vs optimization
   - Mitigation: Retry mechanism explores alternatives

### Future Enhancements

1. **Machine Learning**:
   - Train fidelity predictor from historical data
   - Learn optimal protocol selection
   - Bayesian optimization for bell pair count

2. **Advanced Protocols**:
   - Pumping protocols for higher fidelity
   - Nested distillation
   - Protocol composition

3. **Multi-Agent Coordination**:
   - Cooperative strategies
   - Resource sharing
   - Competitive analysis

4. **Full Simulation**:
   - Qiskit Aer integration for exact fidelity
   - Noise model calibration
   - Circuit optimization

---

## References

### Distillation Protocols

1. **BBPSSW**: Bennett et al., "Purification of Noisy Entanglement and Faithful Teleportation via Noisy Channels" (1996)
2. **DEJMPS**: Deutsch et al., "Quantum Privacy Amplification and the Security of Quantum Cryptography over Noisy Channels" (1996)

### Quantum Networking

3. Kimble, "The quantum internet" (2008)
4. Wehner et al., "Quantum internet: A vision for the road ahead" (2018)

### LOCC Operations

5. Nielsen & Chuang, "Quantum Computation and Quantum Information" (2010)

---

## License

MIT License - See repository for details.

## Contact

For questions or issues, contact the iQuHACK 2026 organizers.
