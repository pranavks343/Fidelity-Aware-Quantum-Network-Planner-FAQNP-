"""
Autonomous Decision Agent for Quantum Network Optimization (LEGACY)

⚠️  DEPRECATION NOTICE:
This is the original monolithic agent implementation. For new projects, use the
LangGraph-based agent in `langgraph_deterministic_agent.py` which provides:
- Modular architecture with independent nodes
- Better testability and debuggability
- Explicit control flow
- Same functionality with minimal overhead

See AGENT_ARCHITECTURE_COMPARISON.md for migration guide.

---

Implements a rule-based agent that:
- Selects edges to claim
- Chooses distillation protocols
- Determines bell pair counts
- Manages budget and risk

NOTE: This is the rule-based variant using pure algorithmic decision making.
For LLM-based reasoning, see langgraph_agent.py (requires OpenAI API key).
For modular architecture, see langgraph_deterministic_agent.py (recommended).
"""

from typing import Dict, Any, Optional, Tuple, List
from dataclasses import dataclass
import numpy as np

from core.client import GameClient
from distillation.distillation import (
    create_bbpssw_circuit,
    create_dejmps_circuit,
    create_adaptive_distillation_circuit,
    estimate_success_probability,
    estimate_output_fidelity
)
from strategy.strategy import (
    EdgeSelectionStrategy,
    BudgetManager,
    AdaptiveDistillationPlanner,
    EdgeScore
)
from distillation.simulator import (
    DistillationSimulator,
    estimate_input_noise_from_difficulty
)


@dataclass
class AgentConfig:
    """Configuration for the autonomous agent."""
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
    prefer_dejmps: bool = False  # Prefer DEJMPS over BBPSSW
    
    # Adaptive behavior
    adaptive_risk: bool = True  # Adjust risk based on budget
    adaptive_pairs: bool = True  # Adjust bell pairs based on attempts


class QuantumNetworkAgent:
    """
    Autonomous agent for quantum network optimization.
    
    Makes intelligent decisions about:
    - Which edges to claim
    - Which distillation protocol to use
    - How many bell pairs to use
    - When to retry or skip
    """
    
    def __init__(
        self,
        client: GameClient,
        config: Optional[AgentConfig] = None
    ):
        """
        Initialize agent.
        
        Args:
            client: GameClient instance
            config: Agent configuration
        """
        self.client = client
        self.config = config or AgentConfig()
        
        # Initialize strategy components
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
        
        # State tracking
        self.initial_budget: Optional[int] = None
        self.iteration_count = 0
        self.successful_claims = 0
        self.failed_attempts = 0
    
    def select_protocol(
        self,
        edge_score: EdgeScore,
        attempt_number: int = 0
    ) -> str:
        """
        Select distillation protocol based on edge properties.
        
        Decision factors:
        - Difficulty level
        - Threshold
        - Attempt number (try different protocol on retry)
        - Configuration preferences
        
        Args:
            edge_score: Edge scoring information
            attempt_number: Which attempt this is
            
        Returns:
            Protocol name: "bbpssw", "dejmps", or "adaptive"
        """
        # On first attempt, use heuristics
        if attempt_number == 0:
            # High difficulty -> try DEJMPS (better for phase noise)
            if edge_score.difficulty >= 7:
                return "dejmps"
            
            # High threshold -> try DEJMPS
            if edge_score.threshold >= 0.9:
                return "dejmps"
            
            # Default to BBPSSW (more robust for general noise)
            if self.config.prefer_dejmps:
                return "dejmps"
            else:
                return "bbpssw"
        
        # On retry, alternate protocols
        else:
            # If we tried BBPSSW, try DEJMPS
            # If we tried DEJMPS, try BBPSSW
            # This explores different approaches
            if attempt_number % 2 == 0:
                return "bbpssw"
            else:
                return "dejmps"
    
    def create_circuit(
        self,
        protocol: str,
        num_bell_pairs: int
    ) -> Tuple[Any, int]:
        """
        Create distillation circuit for chosen protocol.
        
        Args:
            protocol: Protocol name
            num_bell_pairs: Number of bell pairs
            
        Returns:
            (circuit, flag_bit)
        """
        if protocol == "dejmps":
            return create_dejmps_circuit(num_bell_pairs)
        elif protocol == "bbpssw":
            return create_bbpssw_circuit(num_bell_pairs)
        elif protocol == "adaptive":
            return create_adaptive_distillation_circuit(num_bell_pairs)
        else:
            # Default to BBPSSW
            return create_bbpssw_circuit(num_bell_pairs)
    
    def attempt_edge_claim(
        self,
        edge_score: EdgeScore,
        attempt_number: int = 0
    ) -> Dict[str, Any]:
        """
        Attempt to claim an edge with full decision pipeline.
        
        Steps:
        1. Check budget constraints
        2. Select protocol
        3. Determine bell pair count
        4. Create circuit
        5. Simulate (if enabled)
        6. Submit to server
        7. Record results
        
        Args:
            edge_score: Edge to attempt
            attempt_number: Which attempt this is
            
        Returns:
            Result dictionary with success status and metadata
        """
        status = self.client.get_status()
        current_budget = status.get('budget', 0)
        
        # Check if we should attempt
        should_attempt, reason = self.budget_manager.should_attempt_edge(
            edge_score, current_budget
        )
        
        if not should_attempt:
            return {
                'success': False,
                'skipped': True,
                'reason': reason,
                'edge': edge_score.edge_id
            }
        
        # Select protocol
        protocol = self.select_protocol(edge_score, attempt_number)
        
        # Determine bell pair count
        num_bell_pairs = self.distillation_planner.determine_bell_pair_count(
            edge_score, current_budget, attempt_number
        )
        
        # Create circuit
        circuit, flag_bit = self.create_circuit(protocol, num_bell_pairs)
        
        # Simulate if enabled
        if self.simulator:
            input_noise = estimate_input_noise_from_difficulty(edge_score.difficulty)
            
            should_submit, sim_reason, sim_results = self.simulator.should_submit(
                circuit, flag_bit, num_bell_pairs, edge_score.threshold, input_noise
            )
            
            if not should_submit:
                return {
                    'success': False,
                    'skipped': True,
                    'reason': f"Simulation rejected: {sim_reason}",
                    'edge': edge_score.edge_id,
                    'simulation': sim_results
                }
        
        # Submit to server
        try:
            result = self.client.claim_edge(
                edge_score.edge_id,
                circuit,
                flag_bit,
                num_bell_pairs
            )
            
            success = result.get('ok', False)
            
            # Record attempt
            actual_cost = num_bell_pairs if success else 0
            self.budget_manager.record_attempt(
                edge_score.edge_id, success, actual_cost
            )
            
            if success:
                self.successful_claims += 1
                self.budget_manager.reset_edge_attempts(edge_score.edge_id)
            else:
                self.failed_attempts += 1
            
            return {
                'success': success,
                'skipped': False,
                'edge': edge_score.edge_id,
                'protocol': protocol,
                'num_bell_pairs': num_bell_pairs,
                'server_response': result
            }
        
        except Exception as e:
            return {
                'success': False,
                'skipped': False,
                'error': str(e),
                'edge': edge_score.edge_id
            }
    
    def run_iteration(self) -> Dict[str, Any]:
        """
        Run one iteration of the agent's decision loop.
        
        Steps:
        1. Get current status
        2. Get claimable edges
        3. Rank edges by priority
        4. Select best edge
        5. Attempt to claim
        6. Update state
        
        Returns:
            Iteration results
        """
        self.iteration_count += 1
        
        # Get current state
        status = self.client.get_status()
        current_budget = status.get('budget', 0)
        
        # Track initial budget
        if self.initial_budget is None:
            self.initial_budget = current_budget
        
        # Adjust risk tolerance if adaptive
        if self.config.adaptive_risk:
            self.budget_manager.adjust_risk_tolerance(
                current_budget, self.initial_budget
            )
        
        # Get claimable edges
        claimable_edges = self.client.get_claimable_edges()
        
        if not claimable_edges:
            return {
                'iteration': self.iteration_count,
                'action': 'none',
                'reason': 'No claimable edges',
                'budget': current_budget
            }
        
        # Select best edge
        graph = self.client.get_cached_graph()
        best_edge = self.edge_strategy.select_best_edge(
            claimable_edges, graph, status, self.config.min_reserve
        )
        
        if not best_edge:
            return {
                'iteration': self.iteration_count,
                'action': 'none',
                'reason': 'No suitable edges (budget constraints)',
                'budget': current_budget
            }
        
        # Get attempt count for this edge
        attempt_number = self.budget_manager.get_attempt_count(best_edge.edge_id)
        
        # Attempt to claim
        result = self.attempt_edge_claim(best_edge, attempt_number)
        
        return {
            'iteration': self.iteration_count,
            'action': 'claim_attempt',
            'edge': best_edge.edge_id,
            'priority': best_edge.priority,
            'roi': best_edge.roi,
            'attempt_number': attempt_number,
            'result': result,
            'budget': current_budget
        }
    
    def run_autonomous(
        self,
        max_iterations: int = 100,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run agent autonomously until completion or max iterations.
        
        Stopping conditions:
        - No more claimable edges
        - Budget exhausted
        - Max iterations reached
        
        Args:
            max_iterations: Maximum iterations to run
            verbose: Print progress
            
        Returns:
            Final summary
        """
        if verbose:
            print("=" * 60)
            print("Starting Autonomous Quantum Network Agent")
            print("=" * 60)
        
        for i in range(max_iterations):
            # Run iteration
            result = self.run_iteration()
            
            if verbose:
                self._print_iteration_result(result)
            
            # Check stopping conditions
            if result['action'] == 'none':
                if verbose:
                    print(f"\nStopping: {result['reason']}")
                break
            
            # Check budget
            if result['budget'] <= self.config.min_reserve:
                if verbose:
                    print(f"\nStopping: Budget at minimum reserve ({self.config.min_reserve})")
                break
        
        # Final summary
        final_status = self.client.get_status()
        
        summary = {
            'iterations': self.iteration_count,
            'successful_claims': self.successful_claims,
            'failed_attempts': self.failed_attempts,
            'final_score': final_status.get('score', 0),
            'final_budget': final_status.get('budget', 0),
            'owned_nodes': len(final_status.get('owned_nodes', [])),
            'owned_edges': len(final_status.get('owned_edges', []))
        }
        
        if verbose:
            print("\n" + "=" * 60)
            print("Agent Execution Complete")
            print("=" * 60)
            print(f"Iterations: {summary['iterations']}")
            print(f"Successful claims: {summary['successful_claims']}")
            print(f"Failed attempts: {summary['failed_attempts']}")
            print(f"Final score: {summary['final_score']}")
            print(f"Final budget: {summary['final_budget']}")
            print(f"Owned nodes: {summary['owned_nodes']}")
            print(f"Owned edges: {summary['owned_edges']}")
            print("=" * 60)
        
        return summary
    
    def _print_iteration_result(self, result: Dict[str, Any]):
        """Print iteration result in readable format."""
        iteration = result['iteration']
        action = result['action']
        
        if action == 'none':
            print(f"[{iteration}] No action: {result['reason']}")
        else:
            edge = result['edge']
            priority = result.get('priority', 0)
            roi = result.get('roi', 0)
            attempt = result.get('attempt_number', 0)
            claim_result = result.get('result', {})
            
            success = claim_result.get('success', False)
            skipped = claim_result.get('skipped', False)
            
            if skipped:
                print(f"[{iteration}] Skipped {edge}: {claim_result.get('reason', 'Unknown')}")
            elif success:
                protocol = claim_result.get('protocol', 'unknown')
                pairs = claim_result.get('num_bell_pairs', 0)
                print(f"[{iteration}] ✓ Claimed {edge} (priority={priority:.2f}, ROI={roi:.2f}, {protocol}, {pairs} pairs)")
            else:
                error = claim_result.get('error', claim_result.get('reason', 'Failed'))
                print(f"[{iteration}] ✗ Failed {edge}: {error}")


def create_default_agent(client: GameClient) -> QuantumNetworkAgent:
    """
    Create agent with default configuration.
    
    Args:
        client: GameClient instance
        
    Returns:
        Configured agent
    """
    config = AgentConfig(
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
    
    return QuantumNetworkAgent(client, config)


def create_aggressive_agent(client: GameClient) -> QuantumNetworkAgent:
    """
    Create aggressive agent (high risk, high reward).
    
    Args:
        client: GameClient instance
        
    Returns:
        Configured agent
    """
    config = AgentConfig(
        utility_weight=1.5,  # Prioritize high utility nodes
        difficulty_weight=0.2,  # Less concerned about difficulty
        cost_weight=0.2,  # Less concerned about cost
        success_prob_weight=0.3,
        min_reserve=5,  # Lower reserve
        max_retries_per_edge=2,  # Fewer retries
        risk_tolerance=0.3,  # More aggressive (lower threshold)
        enable_simulation=True,
        simulation_shots=500,  # Faster simulation
        prefer_dejmps=True,  # Try advanced protocol
        adaptive_risk=True,
        adaptive_pairs=True
    )
    
    return QuantumNetworkAgent(client, config)


def create_conservative_agent(client: GameClient) -> QuantumNetworkAgent:
    """
    Create conservative agent (low risk, steady progress).
    
    Args:
        client: GameClient instance
        
    Returns:
        Configured agent
    """
    config = AgentConfig(
        utility_weight=0.8,
        difficulty_weight=0.8,  # Avoid difficult edges
        cost_weight=0.6,  # Minimize cost
        success_prob_weight=0.7,  # Prioritize high success probability
        min_reserve=20,  # Higher reserve
        max_retries_per_edge=4,  # More retries
        risk_tolerance=0.7,  # Conservative (higher threshold)
        enable_simulation=True,
        simulation_shots=2000,  # More thorough simulation
        prefer_dejmps=False,
        adaptive_risk=True,
        adaptive_pairs=True
    )
    
    return QuantumNetworkAgent(client, config)
