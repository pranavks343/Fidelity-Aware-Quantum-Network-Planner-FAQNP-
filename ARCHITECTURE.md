# System Architecture

## Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│  (executor.py, command line, Python API, quick_start)          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      GameExecutor                               │
│  • Player registration                                          │
│  • Starting node selection                                      │
│  • Agent creation and configuration                             │
│  • Execution orchestration                                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                   QuantumNetworkAgent                           │
│  • Autonomous decision making                                   │
│  • Protocol selection (BBPSSW vs DEJMPS)                       │
│  • Bell pair count determination                                │
│  • Circuit creation and submission                              │
│  • Result tracking and learning                                 │
└──┬────────────┬────────────┬────────────┬────────────┬──────────┘
   │            │            │            │            │
   │            │            │            │            │
   ▼            ▼            ▼            ▼            ▼
┌─────┐   ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│Edge │   │Budget   │  │Distill   │  │Circuit   │  │Game      │
│Strat│   │Manager  │  │Planner   │  │Simulator │  │Client    │
│egy  │   │         │  │          │  │          │  │          │
└─────┘   └─────────┘  └──────────┘  └──────────┘  └────┬─────┘
   │            │            │            │              │
   │            │            │            │              │
   └────────────┴────────────┴────────────┴──────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  Game Server   │
                    │  (IonQ API)    │
                    └────────────────┘
```

---

## Component Details

### 1. User Interface Layer

**Files:** `executor.py`, command line

**Responsibilities:**
- Provide simple entry points
- Handle user input
- Display results

**Interfaces:**
```python
# Quick start
quick_start(player_id, name, location, agent_type, max_iterations)

# Command line
python executor.py player_id name location agent_type

# Full control
executor = GameExecutor(player_id, name, location)
executor.run(agent_type, max_iterations, verbose)
```

---

### 2. Orchestration Layer

**File:** `executor.py` (GameExecutor class)

**Responsibilities:**
- Player registration
- Starting node selection
- Agent creation
- Execution management
- Results reporting

**Key Methods:**
```python
register() -> Dict
select_starting_node(node_id, strategy) -> Dict
create_agent(agent_type, config) -> QuantumNetworkAgent
run(agent_type, max_iterations, verbose) -> Dict
get_leaderboard(top_n) -> None
restart() -> Dict
```

---

### 3. Decision Layer

**File:** `agent.py` (QuantumNetworkAgent class)

**Responsibilities:**
- Autonomous decision making
- Protocol selection
- Bell pair determination
- Circuit creation
- Submission management
- Result tracking

**Decision Pipeline:**
```
run_iteration():
  1. Get claimable edges
  2. Rank by priority (EdgeSelectionStrategy)
  3. Select best edge (budget constraints)
  4. Check approval (BudgetManager)
  5. Select protocol (BBPSSW vs DEJMPS)
  6. Determine bell pairs (AdaptiveDistillationPlanner)
  7. Create circuit (distillation.py)
  8. Simulate locally (DistillationSimulator)
  9. Submit to server (if approved)
  10. Record results
```

**Key Methods:**
```python
select_protocol(edge_score, attempt_number) -> str
create_circuit(protocol, num_bell_pairs) -> (QuantumCircuit, int)
attempt_edge_claim(edge_score, attempt_number) -> Dict
run_iteration() -> Dict
run_autonomous(max_iterations, verbose) -> Dict
```

---

### 4. Strategy Layer

**File:** `strategy.py`

#### 4.1 EdgeSelectionStrategy

**Responsibilities:**
- Score edges by priority
- Rank claimable edges
- Select best edge

**Scoring Function:**
```python
priority = utility_weight × utility_qubits
         + success_prob_weight × success_probability × 10
         - difficulty_weight × difficulty
         - cost_weight × expected_cost
         + ROI × 2.0
```

**Key Methods:**
```python
score_edge(edge, graph, status, owned_nodes) -> EdgeScore
rank_edges(claimable_edges, graph, status) -> List[EdgeScore]
select_best_edge(claimable_edges, graph, status, budget_threshold) -> EdgeScore
```

#### 4.2 BudgetManager

**Responsibilities:**
- Budget-aware decisions
- Retry management
- Risk assessment
- Adaptive risk tolerance

**Decision Criteria:**
```python
should_attempt_edge(edge_score, current_budget):
  ✓ Check retry limit (≤ 3)
  ✓ Check budget constraint (cost + reserve ≤ budget)
  ✓ Check expected value (utility - cost > 0)
  ✓ Check ROI threshold (ROI ≥ risk_tolerance)
  ✓ Check success probability (prob ≥ 0.2)
```

**Key Methods:**
```python
should_attempt_edge(edge_score, current_budget) -> (bool, str)
record_attempt(edge_id, success, actual_cost) -> None
adjust_risk_tolerance(current_budget, initial_budget) -> None
```

#### 4.3 AdaptiveDistillationPlanner

**Responsibilities:**
- Determine bell pair count
- Adaptive allocation
- Budget constraints

**Allocation Algorithm:**
```python
determine_bell_pair_count(edge_score, current_budget, attempt_number):
  base = difficulty_based_estimate()  # 2, 3, or 4
  pairs = base + attempt_number
  if threshold > 0.85: pairs += 1
  if threshold > 0.92: pairs += 1
  pairs = clamp(pairs, 2, min(8, budget // 2))
  return pairs
```

**Key Methods:**
```python
determine_bell_pair_count(edge_score, budget, attempt) -> int
should_increase_pairs(current_pairs, fidelity, threshold, budget) -> bool
```

---

### 5. Distillation Layer

**File:** `distillation.py`

**Responsibilities:**
- Create quantum circuits
- Implement distillation protocols
- Estimate performance

**Protocols:**

#### 5.1 BBPSSW
```python
create_bbpssw_circuit(num_bell_pairs) -> (QuantumCircuit, int)
```
- Bilateral CNOT operations
- Ancilla-based error detection
- Best for depolarizing noise

#### 5.2 DEJMPS
```python
create_dejmps_circuit(num_bell_pairs) -> (QuantumCircuit, int)
```
- X and Z basis parity checks
- Optimized for phase noise
- Higher success probability

#### 5.3 Adaptive
```python
create_adaptive_distillation_circuit(num_bell_pairs, noise_type) -> (QuantumCircuit, int)
```
- Automatic protocol selection

**Estimation Functions:**
```python
estimate_success_probability(num_bell_pairs, protocol) -> float
estimate_output_fidelity(input_fidelity, num_bell_pairs, protocol) -> float
```

---

### 6. Simulation Layer

**File:** `simulator.py` (DistillationSimulator class)

**Responsibilities:**
- Circuit validation
- Fidelity estimation
- Success probability estimation
- Pre-submission filtering

**Validation:**
```python
validate_circuit(circuit, num_bell_pairs) -> (bool, str)
  ✓ Check qubit count (2N)
  ✓ Check LOCC constraints (no gates across boundary)
  ✓ Check gate set
```

**Estimation:**
```python
estimate_fidelity(circuit, flag_bit, num_bell_pairs, input_noise) -> (float, float)
  # Uses theoretical formula: F_out = F_in² / (F_in² + (1-F_in)²)
```

**Decision:**
```python
should_submit(circuit, flag_bit, num_bell_pairs, threshold, input_noise) -> (bool, str, Dict)
  ✓ Validate circuit
  ✓ Estimate fidelity
  ✓ Check threshold (with safety margin)
  ✓ Check success probability (≥ 10%)
```

**Key Methods:**
```python
validate_circuit(circuit, num_bell_pairs) -> (bool, str)
estimate_fidelity(circuit, flag_bit, num_bell_pairs, input_noise) -> (float, float)
simulate_circuit(circuit, flag_bit, num_bell_pairs, input_noise) -> Dict
should_submit(circuit, flag_bit, num_bell_pairs, threshold, input_noise) -> (bool, str, Dict)
```

---

### 7. API Layer

**File:** `client.py` (GameClient class)

**Responsibilities:**
- Server communication
- API wrapper
- Graph caching

**API Methods:**
```python
register(player_id, name, location) -> Dict
select_starting_node(node_id) -> Dict
claim_edge(edge, circuit, flag_bit, num_bell_pairs) -> Dict
get_status() -> Dict
get_graph() -> Dict
get_leaderboard() -> List[Dict]
restart() -> Dict
```

**Convenience Methods:**
```python
get_cached_graph(force) -> Dict
get_claimable_edges() -> List[Dict]
get_node_info(node_id) -> Dict
get_edge_info(node_a, node_b) -> Dict
print_status() -> None
```

---

## Data Flow

### 1. Initialization Flow

```
User
  │
  ├─> GameExecutor.register()
  │     └─> GameClient.register()
  │           └─> POST /v1/register
  │
  ├─> GameExecutor.select_starting_node()
  │     └─> GameClient.select_starting_node()
  │           └─> POST /v1/select_starting_node
  │
  └─> GameExecutor.create_agent()
        └─> QuantumNetworkAgent.__init__()
              ├─> EdgeSelectionStrategy.__init__()
              ├─> BudgetManager.__init__()
              ├─> AdaptiveDistillationPlanner.__init__()
              └─> DistillationSimulator.__init__()
```

### 2. Decision Flow (Single Iteration)

```
QuantumNetworkAgent.run_iteration()
  │
  ├─> GameClient.get_status()
  │     └─> GET /v1/status/{player_id}
  │
  ├─> GameClient.get_claimable_edges()
  │     └─> GET /v1/graph (cached)
  │
  ├─> EdgeSelectionStrategy.rank_edges()
  │     ├─> score_edge() for each edge
  │     └─> sort by priority
  │
  ├─> EdgeSelectionStrategy.select_best_edge()
  │     └─> filter by budget constraints
  │
  ├─> BudgetManager.should_attempt_edge()
  │     ├─> check retry limit
  │     ├─> check budget constraint
  │     ├─> check expected value
  │     ├─> check ROI threshold
  │     └─> check success probability
  │
  ├─> QuantumNetworkAgent.select_protocol()
  │     └─> choose BBPSSW or DEJMPS
  │
  ├─> AdaptiveDistillationPlanner.determine_bell_pair_count()
  │     └─> calculate optimal pairs
  │
  ├─> create_circuit() (distillation.py)
  │     └─> create_bbpssw_circuit() or create_dejmps_circuit()
  │
  ├─> DistillationSimulator.should_submit()
  │     ├─> validate_circuit()
  │     ├─> estimate_fidelity()
  │     └─> check threshold
  │
  ├─> GameClient.claim_edge()
  │     └─> POST /v1/claim_edge
  │
  └─> BudgetManager.record_attempt()
        └─> update attempt history
```

### 3. Autonomous Execution Flow

```
QuantumNetworkAgent.run_autonomous()
  │
  ├─> for iteration in range(max_iterations):
  │     │
  │     ├─> run_iteration()
  │     │     └─> (see Decision Flow above)
  │     │
  │     ├─> check stopping conditions
  │     │     ├─> no claimable edges?
  │     │     ├─> budget exhausted?
  │     │     └─> max iterations reached?
  │     │
  │     └─> if should_stop: break
  │
  └─> return summary
        ├─> iterations
        ├─> successful_claims
        ├─> failed_attempts
        ├─> final_score
        ├─> final_budget
        ├─> owned_nodes
        └─> owned_edges
```

---

## Configuration Flow

### AgentConfig

```python
AgentConfig
  │
  ├─> EdgeSelectionStrategy
  │     ├─> utility_weight
  │     ├─> difficulty_weight
  │     ├─> cost_weight
  │     └─> success_prob_weight
  │
  ├─> BudgetManager
  │     ├─> min_reserve
  │     ├─> max_retries_per_edge
  │     └─> risk_tolerance
  │
  ├─> AdaptiveDistillationPlanner
  │     ├─> min_pairs (2)
  │     └─> max_pairs (8)
  │
  └─> DistillationSimulator
        ├─> enable_simulation
        └─> simulation_shots
```

### Preset Configurations

```
Default Agent
  ├─> utility_weight: 1.0
  ├─> difficulty_weight: 0.5
  ├─> cost_weight: 0.3
  ├─> success_prob_weight: 0.4
  ├─> min_reserve: 10
  ├─> max_retries_per_edge: 3
  ├─> risk_tolerance: 0.5
  └─> enable_simulation: True

Aggressive Agent
  ├─> utility_weight: 1.5
  ├─> difficulty_weight: 0.2
  ├─> cost_weight: 0.2
  ├─> min_reserve: 5
  ├─> max_retries_per_edge: 2
  ├─> risk_tolerance: 0.3
  └─> prefer_dejmps: True

Conservative Agent
  ├─> utility_weight: 0.8
  ├─> difficulty_weight: 0.8
  ├─> cost_weight: 0.6
  ├─> min_reserve: 20
  ├─> max_retries_per_edge: 4
  ├─> risk_tolerance: 0.7
  └─> simulation_shots: 2000
```

---

## Error Handling

### Validation Errors

```
Circuit Validation
  ├─> Wrong qubit count → reject
  ├─> LOCC violation → reject
  └─> Invalid gate set → reject

Budget Validation
  ├─> Insufficient budget → skip
  ├─> Max retries reached → skip
  └─> Negative expected value → skip

Simulation Validation
  ├─> Estimated fidelity < threshold → skip
  ├─> Success probability < 10% → skip
  └─> Circuit invalid → skip
```

### Server Errors

```
API Errors
  ├─> Connection error → retry
  ├─> Authentication error → re-register
  ├─> Rate limit → backoff
  └─> Server error → log and continue
```

---

## Performance Optimization

### Caching

```
GameClient
  └─> _cached_graph
        ├─> Graph structure (static)
        └─> Invalidate on force=True
```

### Analytical Approximation

```
DistillationSimulator
  └─> estimate_fidelity()
        ├─> Use theoretical formula (O(1))
        └─> Avoid exponential state simulation
```

### Parallel Operations

```
Not currently implemented, but possible:
  ├─> Parallel edge scoring
  ├─> Parallel circuit creation
  └─> Parallel simulation
```

---

## Extensibility

### Adding New Protocols

```python
# In distillation.py
def create_new_protocol_circuit(num_bell_pairs):
    # Implement new distillation protocol
    circuit = QuantumCircuit(...)
    flag_bit = ...
    return circuit, flag_bit

# In agent.py
def select_protocol(self, edge_score, attempt_number):
    # Add new protocol to selection logic
    if some_condition:
        return "new_protocol"
```

### Adding New Strategies

```python
# In strategy.py
class NewSelectionStrategy(EdgeSelectionStrategy):
    def score_edge(self, edge, graph, status, owned_nodes):
        # Implement new scoring function
        return EdgeScore(...)
```

### Adding New Agent Configurations

```python
# In agent.py
def create_custom_agent(client: GameClient) -> QuantumNetworkAgent:
    config = AgentConfig(
        # Custom parameters
    )
    return QuantumNetworkAgent(client, config)
```

---

## Testing Architecture

```
test_logic.py
  ├─> test_edge_selection()
  │     └─> EdgeSelectionStrategy
  │
  ├─> test_budget_manager()
  │     └─> BudgetManager
  │
  ├─> test_distillation_planner()
  │     └─> AdaptiveDistillationPlanner
  │
  └─> test_integration()
        └─> Full pipeline

test_distillation.py
  ├─> test_bbpssw()
  │     └─> create_bbpssw_circuit()
  │
  ├─> test_dejmps()
  │     └─> create_dejmps_circuit()
  │
  ├─> test_adaptive()
  │     └─> create_adaptive_distillation_circuit()
  │
  └─> test_estimates()
        ├─> estimate_success_probability()
        └─> estimate_output_fidelity()
```

---

## Deployment

### Local Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python test_logic.py
python executor.py player_id "Name" remote default
```

### Production Deployment

```bash
# Same as local, but with:
# - Proper error logging
# - Monitoring
# - Backup strategies
```

---

## Summary

This architecture provides:

✅ **Modularity** - Clear separation of concerns
✅ **Testability** - Each component independently testable
✅ **Extensibility** - Easy to add new protocols/strategies
✅ **Performance** - Efficient algorithms, caching
✅ **Reliability** - Error handling, validation
✅ **Usability** - Simple interfaces, good defaults

**Total: 2000+ lines of production-quality code across 7 modules**
