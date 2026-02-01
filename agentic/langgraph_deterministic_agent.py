"""
LangGraph agent for quantum network optimization.

Orchestrates edge claiming decisions using a state machine with explicit nodes
for each decision step. Deterministic (no LLM calls) but modular enough to
debug individual decisions.

Flow:
  EdgeSelection → ResourceAllocation → DistillationStrategy → SimulationCheck
  → Execution → UpdateState → (loop or stop)

Each node returns an immutable state update. The graph handles routing based
on the 'action' field (continue/stop/skip).
"""

from typing import Dict, Any, List, Optional, Tuple, TypedDict, Literal
from dataclasses import dataclass, field
import logging

from langgraph.graph import StateGraph, END

from core.client import GameClient
from strategy.strategy import (
    EdgeSelectionStrategy,
    BudgetManager,
    AdaptiveDistillationPlanner,
    EdgeScore
)
from distillation.distillation import (
    create_bbpssw_circuit,
    create_dejmps_circuit,
)
from distillation.simulator import (
    DistillationSimulator,
    estimate_input_noise_from_difficulty
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    LangGraph state for quantum network agent.
    
    This state is passed between all nodes and tracks the complete
    decision-making context.
    """
    # Game state
    current_budget: int
    current_score: int
    owned_nodes: List[str]
    owned_edges: List[Tuple[str, str]]
    claimable_edges: List[Dict[str, Any]]
    graph: Dict[str, Any]
    
    # Decision state
    selected_edge: Optional[EdgeScore]
    num_bell_pairs: int
    protocol: str
    circuit: Any  # QuantumCircuit
    flag_bit: int
    
    # Simulation results
    estimated_fidelity: float
    estimated_success_prob: float
    should_submit: bool
    simulation_reason: str
    
    # Execution results
    execution_success: bool
    execution_response: Dict[str, Any]
    
    # History & control
    iteration: int
    attempt_history: Dict[Tuple[str, str], int]
    successful_claims: int
    failed_attempts: int
    initial_budget: int
    
    # Control flow
    action: Literal["continue", "stop", "retry", "skip"]
    stop_reason: str


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class LangGraphAgentConfig:
    """Configuration for LangGraph agent."""
    # Strategy weights
    utility_weight: float = 1.0
    difficulty_weight: float = 0.5
    cost_weight: float = 0.3
    success_prob_weight: float = 0.4
    
    # Budget management
    min_reserve: int = 10
    max_retries_per_edge: int = 3
    risk_tolerance: float = 0.5
    
    # Simulation
    enable_simulation: bool = True
    simulation_shots: int = 1000
    
    # Protocol selection
    prefer_dejmps: bool = False
    
    # Adaptive behavior
    adaptive_risk: bool = True
    adaptive_pairs: bool = True


# ============================================================================
# DECISION NODES
# ============================================================================

class EdgeSelectionNode:
    """
    Node: Select the best edge to attempt.
    
    Responsibilities:
    - Rank claimable edges by priority
    - Apply budget constraints
    - Check retry limits
    - Select highest-priority feasible edge
    """
    
    def __init__(self, strategy: EdgeSelectionStrategy, budget_manager: BudgetManager):
        self.strategy = strategy
        self.budget_manager = budget_manager
    
    def __call__(self, state: AgentState) -> AgentState:
        """Select best edge to attempt."""
        logger.info(f"[Iteration {state['iteration']}] EdgeSelection: Evaluating {len(state['claimable_edges'])} edges")
        
        # Check if we have any claimable edges
        if not state['claimable_edges']:
            return {
                **state,
                'action': 'stop',
                'stop_reason': 'No claimable edges available',
                'selected_edge': None
            }
        
        # Build status dict for strategy
        status = {
            'owned_nodes': state['owned_nodes'],
            'budget': state['current_budget']
        }
        
        # Select best edge
        best_edge = self.strategy.select_best_edge(
            state['claimable_edges'],
            state['graph'],
            status,
            self.budget_manager.min_reserve
        )
        
        if not best_edge:
            return {
                **state,
                'action': 'stop',
                'stop_reason': 'No suitable edges (budget constraints)',
                'selected_edge': None
            }
        
        # Check budget approval
        should_attempt, reason = self.budget_manager.should_attempt_edge(
            best_edge,
            state['current_budget']
        )
        
        if not should_attempt:
            return {
                **state,
                'action': 'skip',
                'stop_reason': reason,
                'selected_edge': None
            }
        
        # Edge selected successfully
        logger.info(f"  → Selected edge {best_edge.edge_id} (priority={best_edge.priority:.2f}, ROI={best_edge.roi:.2f})")
        
        return {
            **state,
            'selected_edge': best_edge,
            'action': 'continue'
        }


class ResourceAllocationNode:
    """
    Node: Determine how many Bell pairs to allocate.
    
    Responsibilities:
    - Consider edge difficulty and threshold
    - Check attempt history (increase on retry)
    - Respect budget constraints
    - Apply adaptive strategy
    """
    
    def __init__(self, planner: AdaptiveDistillationPlanner):
        self.planner = planner
    
    def __call__(self, state: AgentState) -> AgentState:
        """Determine optimal Bell pair count."""
        if state['action'] != 'continue' or not state['selected_edge']:
            return state
        
        edge = state['selected_edge']
        attempt_number = state['attempt_history'].get(edge.edge_id, 0)
        
        num_pairs = self.planner.determine_bell_pair_count(
            edge,
            state['current_budget'],
            attempt_number
        )
        
        logger.info(f"  → Allocated {num_pairs} Bell pairs (attempt #{attempt_number})")
        
        return {**state, 'num_bell_pairs': num_pairs}


class DistillationStrategyNode:
    """
    Node: Choose distillation protocol.
    
    Responsibilities:
    - Select BBPSSW vs DEJMPS based on edge properties
    - Consider attempt history (alternate on retry)
    - Generate quantum circuit
    """
    
    def __init__(self, config: LangGraphAgentConfig):
        self.config = config
    
    def __call__(self, state: AgentState) -> AgentState:
        """Select protocol and create circuit."""
        if state['action'] != 'continue' or not state['selected_edge']:
            return state
        
        edge = state['selected_edge']
        attempt_number = state['attempt_history'].get(edge.edge_id, 0)
        
        # Protocol selection logic
        protocol = self._select_protocol(edge, attempt_number)
        
        # Create circuit
        if protocol == "dejmps":
            circuit, flag_bit = create_dejmps_circuit(state['num_bell_pairs'])
        else:  # bbpssw
            circuit, flag_bit = create_bbpssw_circuit(state['num_bell_pairs'])
        
        logger.info(f"  → Protocol: {protocol.upper()}, flag_bit={flag_bit}")
        
        return {
            **state,
            'protocol': protocol,
            'circuit': circuit,
            'flag_bit': flag_bit
        }
    
    def _select_protocol(self, edge: EdgeScore, attempt_number: int) -> str:
        """Select distillation protocol based on edge properties."""
        # First attempt: use heuristics
        if attempt_number == 0:
            # High difficulty or threshold → DEJMPS
            if edge.difficulty >= 7 or edge.threshold >= 0.9:
                return "dejmps"
            # Default or configured preference
            return "dejmps" if self.config.prefer_dejmps else "bbpssw"
        
        # Retry: alternate protocols
        return "bbpssw" if attempt_number % 2 == 0 else "dejmps"


class SimulationCheckNode:
    """
    Node: Run local simulation to validate attempt.
    
    Responsibilities:
    - Estimate output fidelity
    - Estimate success probability
    - Validate LOCC constraints
    - Reject attempts likely to fail
    """
    
    def __init__(self, simulator: Optional[DistillationSimulator]):
        self.simulator = simulator
    
    def __call__(self, state: AgentState) -> AgentState:
        """Simulate circuit and decide whether to submit."""
        if state['action'] != 'continue' or not state['selected_edge']:
            return state
        
        # Skip simulation if disabled
        if not self.simulator:
            return {
                **state,
                'should_submit': True,
                'simulation_reason': "Simulation disabled",
                'estimated_fidelity': 0.0,
                'estimated_success_prob': 0.0
            }
        
        edge = state['selected_edge']
        input_noise = estimate_input_noise_from_difficulty(edge.difficulty)
        
        # Run simulation
        should_submit, reason, sim_results = self.simulator.should_submit(
            state['circuit'],
            state['flag_bit'],
            state['num_bell_pairs'],
            edge.threshold,
            input_noise
        )
        
        estimated_fidelity = sim_results.get('estimated_fidelity', 0.0)
        estimated_success_prob = sim_results.get('success_probability', 0.0)
        
        if not should_submit:
            logger.info(f"  → Simulation REJECTED: {reason}")
            return {
                **state,
                'should_submit': should_submit,
                'simulation_reason': reason,
                'estimated_fidelity': estimated_fidelity,
                'estimated_success_prob': estimated_success_prob,
                'action': 'skip'
            }
        else:
            logger.info(f"  → Simulation PASSED: F={estimated_fidelity:.3f}, P={estimated_success_prob:.2%}")
            return {
                **state,
                'should_submit': should_submit,
                'simulation_reason': reason,
                'estimated_fidelity': estimated_fidelity,
                'estimated_success_prob': estimated_success_prob
            }


class ExecutionNode:
    """
    Node: Execute edge claim on server.
    
    Responsibilities:
    - Submit circuit to game server
    - Handle server response
    - Record success/failure
    """
    
    def __init__(self, client: GameClient):
        self.client = client
    
    def __call__(self, state: AgentState) -> AgentState:
        """Execute edge claim."""
        if state['action'] != 'continue' or not state['selected_edge'] or not state['should_submit']:
            # Skip execution
            return {
                **state,
                'execution_success': False,
                'execution_response': {}
            }
        
        edge = state['selected_edge']
        
        try:
            # Submit to server
            result = self.client.claim_edge(
                edge.edge_id,
                state['circuit'],
                state['flag_bit'],
                state['num_bell_pairs']
            )
            
            success = result.get('ok', False)
            
            if success:
                logger.info(f"  → Execution SUCCESS: Edge {edge.edge_id} claimed")
            else:
                error = result.get('error', {}).get('message', 'Unknown error')
                logger.info(f"  → Execution FAILED: {error}")
            
            return {
                **state,
                'execution_success': success,
                'execution_response': result
            }
            
        except Exception as e:
            logger.error(f"  → Execution ERROR: {e}")
            return {
                **state,
                'execution_success': False,
                'execution_response': {'error': str(e)}
            }


class UpdateStateNode:
    """
    Node: Update agent state after execution.
    
    Responsibilities:
    - Update budget, score, owned nodes/edges
    - Record attempt history
    - Update success/failure counters
    - Adjust risk tolerance (adaptive)
    - Determine next action (continue/stop)
    """
    
    def __init__(self, budget_manager: BudgetManager, config: LangGraphAgentConfig, client: GameClient):
        self.budget_manager = budget_manager
        self.config = config
        self.client = client
    
    def __call__(self, state: AgentState) -> AgentState:
        """Update state after execution."""
        # Increment iteration
        new_iteration = state['iteration'] + 1
        
        # Handle skipped attempts
        if state['action'] == 'skip':
            logger.info(f"[Iteration {new_iteration}] Action: SKIP - {state.get('stop_reason', 'Unknown')}")
            return {
                **state,
                'iteration': new_iteration,
                'action': 'continue'  # Try next edge
            }
        
        # Prepare updated state
        updates = {'iteration': new_iteration}
        
        # Update attempt history (need to create new dict to avoid mutation)
        new_attempt_history = dict(state['attempt_history'])
        
        if state['selected_edge']:
            edge_id = state['selected_edge'].edge_id
            new_attempt_history[edge_id] = new_attempt_history.get(edge_id, 0) + 1
            
            # Record in budget manager
            actual_cost = state['num_bell_pairs'] if state['execution_success'] else 0
            self.budget_manager.record_attempt(
                edge_id,
                state['execution_success'],
                actual_cost
            )
            
            # Update counters
            if state['execution_success']:
                updates['successful_claims'] = state['successful_claims'] + 1
                # Reset retry counter on success
                self.budget_manager.reset_edge_attempts(edge_id)
            else:
                updates['failed_attempts'] = state['failed_attempts'] + 1
        
        updates['attempt_history'] = new_attempt_history
        
        # Refresh game state from server
        status = self.client.get_status()
        updates['current_budget'] = status.get('budget', 0)
        updates['current_score'] = status.get('score', 0)
        updates['owned_nodes'] = status.get('owned_nodes', [])
        updates['owned_edges'] = status.get('owned_edges', [])
        
        # Refresh claimable edges
        updates['claimable_edges'] = self.client.get_claimable_edges()
        
        # Adaptive risk adjustment
        if self.config.adaptive_risk:
            self.budget_manager.adjust_risk_tolerance(
                updates['current_budget'],
                state['initial_budget']
            )
        
        # Determine next action
        if updates['current_budget'] <= self.config.min_reserve:
            updates['action'] = 'stop'
            updates['stop_reason'] = f"Budget at minimum reserve ({self.config.min_reserve})"
        elif not updates['claimable_edges']:
            updates['action'] = 'stop'
            updates['stop_reason'] = "No more claimable edges"
        else:
            updates['action'] = 'continue'
        
        logger.info(f"[Iteration {new_iteration}] State updated: Budget={updates['current_budget']}, Score={updates['current_score']}, Action={updates['action']}")
        
        return {**state, **updates}


# ============================================================================
# LANGGRAPH AGENT
# ============================================================================

class LangGraphQuantumAgent:
    """
    LangGraph-based quantum network agent.
    
    This agent uses a state machine architecture with explicit decision nodes
    and control flow. It replaces the monolithic agent logic with a modular,
    debuggable graph structure.
    """
    
    def __init__(
        self,
        client: GameClient,
        config: Optional[LangGraphAgentConfig] = None
    ):
        """
        Initialize LangGraph agent.
        
        Args:
            client: GameClient instance
            config: Agent configuration
        """
        self.client = client
        self.config = config or LangGraphAgentConfig()
        
        # Initialize strategy components (reuse existing logic)
        self.edge_strategy = EdgeSelectionStrategy(
            utility_weight=self.config.utility_weight,
            difficulty_weight=self.config.difficulty_weight,
            cost_weight=self.config.cost_weight,
            success_prob_weight=self.config.success_prob_weight
        )
        
        self.budget_manager = BudgetManager(
            min_reserve=self.config.min_reserve,
            max_retries_per_edge=self.config.max_retries_per_edge,
            risk_tolerance=self.config.risk_tolerance
        )
        
        self.distillation_planner = AdaptiveDistillationPlanner()
        
        if self.config.enable_simulation:
            self.simulator = DistillationSimulator(shots=self.config.simulation_shots)
        else:
            self.simulator = None
        
        # Build LangGraph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state machine.
        
        Graph structure:
            START → edge_selection → resource_allocation → distillation_strategy
                  → simulation_check → execution → update_state → (conditional)
                  
        Conditional routing:
            - If action == 'stop': → END
            - If action == 'continue': → edge_selection (loop)
        """
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Create node instances
        edge_selection = EdgeSelectionNode(self.edge_strategy, self.budget_manager)
        resource_allocation = ResourceAllocationNode(self.distillation_planner)
        distillation_strategy = DistillationStrategyNode(self.config)
        simulation_check = SimulationCheckNode(self.simulator)
        execution = ExecutionNode(self.client)
        update_state = UpdateStateNode(self.budget_manager, self.config, self.client)
        
        # Add nodes to graph
        workflow.add_node("edge_selection", edge_selection)
        workflow.add_node("resource_allocation", resource_allocation)
        workflow.add_node("distillation_strategy", distillation_strategy)
        workflow.add_node("simulation_check", simulation_check)
        workflow.add_node("execution", execution)
        workflow.add_node("update_state", update_state)
        
        # Define edges (control flow)
        workflow.set_entry_point("edge_selection")
        workflow.add_edge("edge_selection", "resource_allocation")
        workflow.add_edge("resource_allocation", "distillation_strategy")
        workflow.add_edge("distillation_strategy", "simulation_check")
        workflow.add_edge("simulation_check", "execution")
        workflow.add_edge("execution", "update_state")
        
        # Conditional edge: loop or terminate
        workflow.add_conditional_edges(
            "update_state",
            self._should_continue,
            {
                "continue": "edge_selection",  # Loop back
                "stop": END  # Terminate
            }
        )
        
        return workflow.compile()
    
    def _should_continue(self, state: AgentState) -> str:
        """
        Routing function: Decide whether to continue or stop.
        
        Returns:
            "continue" to loop back to edge selection
            "stop" to terminate execution
        """
        return state['action']
    
    def _initialize_state(self) -> AgentState:
        """Initialize agent state from game server."""
        status = self.client.get_status()
        graph = self.client.get_cached_graph()
        claimable_edges = self.client.get_claimable_edges()
        
        initial_budget = status.get('budget', 0)
        
        return AgentState(
            # Game state
            current_budget=initial_budget,
            current_score=status.get('score', 0),
            owned_nodes=status.get('owned_nodes', []),
            owned_edges=status.get('owned_edges', []),
            claimable_edges=claimable_edges,
            graph=graph,
            
            # Decision state (initialized to defaults)
            selected_edge=None,
            num_bell_pairs=0,
            protocol="",
            circuit=None,
            flag_bit=0,
            
            # Simulation results
            estimated_fidelity=0.0,
            estimated_success_prob=0.0,
            should_submit=False,
            simulation_reason="",
            
            # Execution results
            execution_success=False,
            execution_response={},
            
            # History & control
            iteration=0,
            attempt_history={},
            successful_claims=0,
            failed_attempts=0,
            initial_budget=initial_budget,
            
            # Control flow
            action="continue",
            stop_reason=""
        )
    
    def run_iteration(self) -> Dict[str, Any]:
        """
        Run one iteration of the agent.
        
        Returns:
            Iteration results summary
        """
        # Initialize state
        state = self._initialize_state()
        
        # Run one iteration through the graph
        result = self.graph.invoke(state)
        
        return {
            'iteration': result['iteration'],
            'action': result['action'],
            'stop_reason': result.get('stop_reason', ''),
            'selected_edge': result['selected_edge'].edge_id if result['selected_edge'] else None,
            'execution_success': result['execution_success'],
            'budget': result['current_budget'],
            'score': result['current_score']
        }
    
    def run_autonomous(
        self,
        max_iterations: int = 100,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run agent autonomously until completion or max iterations.
        
        Args:
            max_iterations: Maximum iterations to run
            verbose: Print progress
            
        Returns:
            Final summary
        """
        if verbose:
            print("=" * 60)
            print("Starting LangGraph Quantum Network Agent")
            print("=" * 60)
        
        # Initialize state
        state = self._initialize_state()
        
        # Run until termination or max iterations
        for i in range(max_iterations):
            # Execute one step through the graph
            state = self.graph.invoke(state)
            
            # Check termination
            if state['action'] == 'stop':
                if verbose:
                    print(f"\nStopping: {state['stop_reason']}")
                break
        
        # Final summary
        summary = {
            'iterations': state['iteration'],
            'successful_claims': state['successful_claims'],
            'failed_attempts': state['failed_attempts'],
            'final_score': state['current_score'],
            'final_budget': state['current_budget'],
            'owned_nodes': len(state['owned_nodes']),
            'owned_edges': len(state['owned_edges']),
            'stop_reason': state['stop_reason']
        }
        
        if verbose:
            print("\n" + "=" * 60)
            print("LangGraph Agent Execution Complete")
            print("=" * 60)
            print(f"Iterations: {summary['iterations']}")
            print(f"Successful claims: {summary['successful_claims']}")
            print(f"Failed attempts: {summary['failed_attempts']}")
            print(f"Final score: {summary['final_score']}")
            print(f"Final budget: {summary['final_budget']}")
            print(f"Owned nodes: {summary['owned_nodes']}")
            print(f"Owned edges: {summary['owned_edges']}")
            print(f"Stop reason: {summary['stop_reason']}")
            print("=" * 60)
        
        return summary


# ============================================================================
# FACTORY FUNCTIONS (for compatibility with existing code)
# ============================================================================

def create_default_langgraph_agent(client: GameClient) -> LangGraphQuantumAgent:
    """Create agent with default configuration."""
    config = LangGraphAgentConfig(
        utility_weight=1.0,
        difficulty_weight=0.5,
        cost_weight=0.3,
        success_prob_weight=0.4,
        min_reserve=10,
        max_retries_per_edge=3,
        risk_tolerance=0.5,
        enable_simulation=True,
        simulation_shots=1000,
        prefer_dejmps=False,
        adaptive_risk=True,
        adaptive_pairs=True
    )
    return LangGraphQuantumAgent(client, config)


def create_aggressive_langgraph_agent(client: GameClient) -> LangGraphQuantumAgent:
    """Create aggressive agent (high risk, high reward)."""
    config = LangGraphAgentConfig(
        utility_weight=1.5,
        difficulty_weight=0.2,
        cost_weight=0.2,
        success_prob_weight=0.3,
        min_reserve=5,
        max_retries_per_edge=2,
        risk_tolerance=0.3,
        enable_simulation=True,
        simulation_shots=500,
        prefer_dejmps=True,
        adaptive_risk=True,
        adaptive_pairs=True
    )
    return LangGraphQuantumAgent(client, config)


def create_conservative_langgraph_agent(client: GameClient) -> LangGraphQuantumAgent:
    """Create conservative agent (low risk, steady progress)."""
    config = LangGraphAgentConfig(
        utility_weight=0.8,
        difficulty_weight=0.8,
        cost_weight=0.6,
        success_prob_weight=0.7,
        min_reserve=20,
        max_retries_per_edge=4,
        risk_tolerance=0.7,
        enable_simulation=True,
        simulation_shots=2000,
        prefer_dejmps=False,
        adaptive_risk=True,
        adaptive_pairs=True
    )
    return LangGraphQuantumAgent(client, config)
