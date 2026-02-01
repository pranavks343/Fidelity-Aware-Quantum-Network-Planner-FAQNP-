"""
Test suite for LangGraph-based deterministic agent.

Validates:
- State transitions
- Node execution
- Control flow
- Budget constraints
- No infinite loops
"""

import sys
from typing import Dict, Any
from agentic.langgraph_deterministic_agent import (
    LangGraphQuantumAgent,
    LangGraphAgentConfig,
    AgentState,
    EdgeSelectionNode,
    ResourceAllocationNode,
    DistillationStrategyNode,
    SimulationCheckNode
)
from strategy.strategy import EdgeSelectionStrategy, BudgetManager, AdaptiveDistillationPlanner, EdgeScore
from distillation.simulator import DistillationSimulator


def test_state_initialization():
    """Test that agent state initializes correctly."""
    print("\n" + "=" * 60)
    print("Testing State Initialization")
    print("=" * 60)
    
    # Create mock state
    state: AgentState = {
        'current_budget': 75,
        'current_score': 0,
        'owned_nodes': ['A'],
        'owned_edges': [],
        'claimable_edges': [],
        'graph': {'nodes': [], 'edges': []},
        'selected_edge': None,
        'num_bell_pairs': 0,
        'protocol': '',
        'circuit': None,
        'flag_bit': 0,
        'estimated_fidelity': 0.0,
        'estimated_success_prob': 0.0,
        'should_submit': False,
        'simulation_reason': '',
        'execution_success': False,
        'execution_response': {},
        'iteration': 0,
        'attempt_history': {},
        'successful_claims': 0,
        'failed_attempts': 0,
        'initial_budget': 75,
        'action': 'continue',
        'stop_reason': ''
    }
    
    # Verify all required fields present
    required_fields = [
        'current_budget', 'current_score', 'owned_nodes', 'owned_edges',
        'claimable_edges', 'graph', 'selected_edge', 'num_bell_pairs',
        'protocol', 'circuit', 'flag_bit', 'action'
    ]
    
    for field in required_fields:
        assert field in state, f"Missing required field: {field}"
    
    print("✓ All required state fields present")
    print(f"  Initial budget: {state['current_budget']}")
    print(f"  Initial action: {state['action']}")
    
    return True


def test_edge_selection_node():
    """Test edge selection node logic."""
    print("\n" + "=" * 60)
    print("Testing Edge Selection Node")
    print("=" * 60)
    
    # Create components
    strategy = EdgeSelectionStrategy()
    budget_manager = BudgetManager(min_reserve=10)
    node = EdgeSelectionNode(strategy, budget_manager)
    
    # Test 1: No claimable edges
    state: AgentState = {
        'current_budget': 75,
        'current_score': 0,
        'owned_nodes': ['A'],
        'owned_edges': [],
        'claimable_edges': [],
        'graph': {'nodes': [], 'edges': []},
        'selected_edge': None,
        'num_bell_pairs': 0,
        'protocol': '',
        'circuit': None,
        'flag_bit': 0,
        'estimated_fidelity': 0.0,
        'estimated_success_prob': 0.0,
        'should_submit': False,
        'simulation_reason': '',
        'execution_success': False,
        'execution_response': {},
        'iteration': 0,
        'attempt_history': {},
        'successful_claims': 0,
        'failed_attempts': 0,
        'initial_budget': 75,
        'action': 'continue',
        'stop_reason': ''
    }
    
    result = node(state)
    assert result['action'] == 'stop', "Should stop when no edges available"
    assert result['selected_edge'] is None
    print("✓ Correctly stops when no claimable edges")
    
    # Test 2: With claimable edges
    state['claimable_edges'] = [
        {'edge_id': ('A', 'B'), 'difficulty_rating': 3.0, 'base_threshold': 0.85}
    ]
    state['graph'] = {
        'nodes': [
            {'node_id': 'A', 'utility_qubits': 10, 'bonus_bell_pairs': 5},
            {'node_id': 'B', 'utility_qubits': 15, 'bonus_bell_pairs': 8}
        ],
        'edges': []
    }
    state['action'] = 'continue'
    
    result = node(state)
    assert result['action'] == 'continue', "Should continue when edge available"
    assert result['selected_edge'] is not None, "Should select an edge"
    print("✓ Correctly selects edge when available")
    print(f"  Selected: {result['selected_edge'].edge_id}")
    
    return True


def test_resource_allocation_node():
    """Test resource allocation node logic."""
    print("\n" + "=" * 60)
    print("Testing Resource Allocation Node")
    print("=" * 60)
    
    planner = AdaptiveDistillationPlanner()
    node = ResourceAllocationNode(planner)
    
    # Create mock edge score
    edge_score = EdgeScore(
        edge_id=('A', 'B'),
        priority=10.0,
        expected_utility=15.0,
        expected_cost=3.0,
        roi=5.0,
        difficulty=5.0,
        threshold=0.85,
        target_node_utility=15,
        estimated_success_prob=0.7
    )
    
    state: AgentState = {
        'current_budget': 75,
        'current_score': 0,
        'owned_nodes': ['A'],
        'owned_edges': [],
        'claimable_edges': [],
        'graph': {},
        'selected_edge': edge_score,
        'num_bell_pairs': 0,
        'protocol': '',
        'circuit': None,
        'flag_bit': 0,
        'estimated_fidelity': 0.0,
        'estimated_success_prob': 0.0,
        'should_submit': False,
        'simulation_reason': '',
        'execution_success': False,
        'execution_response': {},
        'iteration': 0,
        'attempt_history': {},
        'successful_claims': 0,
        'failed_attempts': 0,
        'initial_budget': 75,
        'action': 'continue',
        'stop_reason': ''
    }
    
    result = node(state)
    assert result['num_bell_pairs'] >= 2, "Should allocate at least 2 pairs"
    assert result['num_bell_pairs'] <= 8, "Should not exceed 8 pairs"
    print(f"✓ Allocated {result['num_bell_pairs']} Bell pairs")
    
    # Test retry behavior (should increase pairs)
    state['attempt_history'] = {('A', 'B'): 1}
    result2 = node(state)
    assert result2['num_bell_pairs'] >= result['num_bell_pairs'], "Should increase pairs on retry"
    print(f"✓ Retry increases pairs: {result['num_bell_pairs']} → {result2['num_bell_pairs']}")
    
    return True


def test_distillation_strategy_node():
    """Test distillation strategy node logic."""
    print("\n" + "=" * 60)
    print("Testing Distillation Strategy Node")
    print("=" * 60)
    
    config = LangGraphAgentConfig()
    node = DistillationStrategyNode(config)
    
    edge_score = EdgeScore(
        edge_id=('A', 'B'),
        priority=10.0,
        expected_utility=15.0,
        expected_cost=3.0,
        roi=5.0,
        difficulty=5.0,
        threshold=0.85,
        target_node_utility=15,
        estimated_success_prob=0.7
    )
    
    state: AgentState = {
        'current_budget': 75,
        'current_score': 0,
        'owned_nodes': ['A'],
        'owned_edges': [],
        'claimable_edges': [],
        'graph': {},
        'selected_edge': edge_score,
        'num_bell_pairs': 3,
        'protocol': '',
        'circuit': None,
        'flag_bit': 0,
        'estimated_fidelity': 0.0,
        'estimated_success_prob': 0.0,
        'should_submit': False,
        'simulation_reason': '',
        'execution_success': False,
        'execution_response': {},
        'iteration': 0,
        'attempt_history': {},
        'successful_claims': 0,
        'failed_attempts': 0,
        'initial_budget': 75,
        'action': 'continue',
        'stop_reason': ''
    }
    
    result = node(state)
    assert result['protocol'] in ['bbpssw', 'dejmps'], "Should select valid protocol"
    assert result['circuit'] is not None, "Should create circuit"
    assert result['circuit'].num_qubits == 6, "Circuit should have 2N qubits"
    print(f"✓ Selected protocol: {result['protocol'].upper()}")
    print(f"✓ Created circuit: {result['circuit'].num_qubits} qubits")
    
    return True


def test_simulation_check_node():
    """Test simulation check node logic."""
    print("\n" + "=" * 60)
    print("Testing Simulation Check Node")
    print("=" * 60)
    
    simulator = DistillationSimulator(shots=100)
    node = SimulationCheckNode(simulator)
    
    from distillation.distillation import create_bbpssw_circuit
    circuit, flag_bit = create_bbpssw_circuit(3)
    
    edge_score = EdgeScore(
        edge_id=('A', 'B'),
        priority=10.0,
        expected_utility=15.0,
        expected_cost=3.0,
        roi=5.0,
        difficulty=3.0,  # Low difficulty
        threshold=0.85,
        target_node_utility=15,
        estimated_success_prob=0.7
    )
    
    state: AgentState = {
        'current_budget': 75,
        'current_score': 0,
        'owned_nodes': ['A'],
        'owned_edges': [],
        'claimable_edges': [],
        'graph': {},
        'selected_edge': edge_score,
        'num_bell_pairs': 3,
        'protocol': 'bbpssw',
        'circuit': circuit,
        'flag_bit': flag_bit,
        'estimated_fidelity': 0.0,
        'estimated_success_prob': 0.0,
        'should_submit': False,
        'simulation_reason': '',
        'execution_success': False,
        'execution_response': {},
        'iteration': 0,
        'attempt_history': {},
        'successful_claims': 0,
        'failed_attempts': 0,
        'initial_budget': 75,
        'action': 'continue',
        'stop_reason': ''
    }
    
    result = node(state)
    assert 'should_submit' in result, "Should have submission decision"
    assert 'estimated_fidelity' in result, "Should estimate fidelity"
    assert 'estimated_success_prob' in result, "Should estimate success probability"
    print(f"✓ Simulation decision: {'PASS' if result['should_submit'] else 'REJECT'}")
    print(f"  Estimated fidelity: {result['estimated_fidelity']:.3f}")
    print(f"  Success probability: {result['estimated_success_prob']:.2%}")
    
    return True


def test_control_flow():
    """Test that control flow prevents infinite loops."""
    print("\n" + "=" * 60)
    print("Testing Control Flow & Loop Prevention")
    print("=" * 60)
    
    # Test 1: Budget depletion stops execution
    state: AgentState = {
        'current_budget': 5,  # Below min_reserve
        'current_score': 0,
        'owned_nodes': ['A'],
        'owned_edges': [],
        'claimable_edges': [{'edge_id': ('A', 'B'), 'difficulty_rating': 3.0, 'base_threshold': 0.85}],
        'graph': {'nodes': [], 'edges': []},
        'selected_edge': None,
        'num_bell_pairs': 0,
        'protocol': '',
        'circuit': None,
        'flag_bit': 0,
        'estimated_fidelity': 0.0,
        'estimated_success_prob': 0.0,
        'should_submit': False,
        'simulation_reason': '',
        'execution_success': False,
        'execution_response': {},
        'iteration': 0,
        'attempt_history': {},
        'successful_claims': 0,
        'failed_attempts': 0,
        'initial_budget': 75,
        'action': 'continue',
        'stop_reason': ''
    }
    
    config = LangGraphAgentConfig(min_reserve=10)
    budget_manager = BudgetManager(min_reserve=10)
    
    from core.client import GameClient
    # Mock client for testing
    class MockClient:
        def get_status(self):
            return {'budget': 5, 'score': 0, 'owned_nodes': ['A'], 'owned_edges': []}
        def get_claimable_edges(self):
            return []
    
    mock_client = MockClient()
    update_node = UpdateStateNode(budget_manager, config, mock_client)
    
    result = update_node(state)
    assert result['action'] == 'stop', "Should stop when budget is low"
    print("✓ Correctly stops when budget depleted")
    
    # Test 2: No claimable edges stops execution
    state['current_budget'] = 75
    state['claimable_edges'] = []
    result = update_node(state)
    assert result['action'] == 'stop', "Should stop when no edges available"
    print("✓ Correctly stops when no claimable edges")
    
    return True


def test_budget_constraints():
    """Test that budget constraints are enforced."""
    print("\n" + "=" * 60)
    print("Testing Budget Constraints")
    print("=" * 60)
    
    budget_manager = BudgetManager(min_reserve=10, max_retries_per_edge=3)
    
    # Test 1: Insufficient budget
    edge_score = EdgeScore(
        edge_id=('A', 'B'),
        priority=10.0,
        expected_utility=15.0,
        expected_cost=50.0,  # High cost
        roi=0.3,
        difficulty=5.0,
        threshold=0.85,
        target_node_utility=15,
        estimated_success_prob=0.7
    )
    
    should_attempt, reason = budget_manager.should_attempt_edge(edge_score, 20)
    assert not should_attempt, "Should reject when budget insufficient"
    print(f"✓ Rejects high-cost edge: {reason}")
    
    # Test 2: Retry limit
    edge_score.expected_cost = 3.0
    budget_manager.attempt_history[('A', 'B')] = 3  # Max retries reached
    should_attempt, reason = budget_manager.should_attempt_edge(edge_score, 75)
    assert not should_attempt, "Should reject when retry limit reached"
    print(f"✓ Enforces retry limit: {reason}")
    
    # Test 3: Valid attempt
    budget_manager.attempt_history[('A', 'B')] = 0
    should_attempt, reason = budget_manager.should_attempt_edge(edge_score, 75)
    assert should_attempt, "Should approve valid attempt"
    print(f"✓ Approves valid attempt: {reason}")
    
    return True


def test_full_graph_execution():
    """Test complete graph execution with mock client."""
    print("\n" + "=" * 60)
    print("Testing Full Graph Execution")
    print("=" * 60)
    
    from agentic.langgraph_deterministic_agent import LangGraphQuantumAgent, LangGraphAgentConfig
    
    # Create comprehensive mock client
    class FullMockClient:
        def __init__(self):
            self.budget = 75
            self.score = 0
            self.owned_nodes = ['A']
            self.owned_edges = []
            self.call_count = 0
        
        def get_status(self):
            return {
                'budget': self.budget,
                'score': self.score,
                'owned_nodes': self.owned_nodes,
                'owned_edges': self.owned_edges
            }
        
        def get_cached_graph(self):
            return {
                'nodes': [
                    {'node_id': 'A', 'utility_qubits': 10, 'bonus_bell_pairs': 5},
                    {'node_id': 'B', 'utility_qubits': 15, 'bonus_bell_pairs': 8}
                ],
                'edges': [
                    {'edge_id': ('A', 'B'), 'difficulty_rating': 3.0, 'base_threshold': 0.85}
                ]
            }
        
        def get_claimable_edges(self):
            if self.call_count < 2:  # Return edges for first 2 iterations
                return [
                    {'edge_id': ('A', 'B'), 'difficulty_rating': 3.0, 'base_threshold': 0.85}
                ]
            return []  # No more edges after 2 iterations
        
        def claim_edge(self, edge, circuit, flag_bit, num_bell_pairs):
            self.call_count += 1
            # Simulate successful claim
            self.budget -= num_bell_pairs
            self.score += 10
            self.owned_edges.append(edge)
            return {'ok': True, 'data': {'fidelity': 0.9, 'success_probability': 0.8}}
    
    # Create agent with mock client
    mock_client = FullMockClient()
    config = LangGraphAgentConfig(
        min_reserve=10,
        max_retries_per_edge=2,
        enable_simulation=False  # Disable for faster testing
    )
    
    agent = LangGraphQuantumAgent(mock_client, config)
    
    # Run for limited iterations
    summary = agent.run_autonomous(max_iterations=5, verbose=False)
    
    # Verify execution
    assert summary['iterations'] > 0, "Should have run at least one iteration"
    assert 'final_score' in summary, "Should have final score"
    assert 'final_budget' in summary, "Should have final budget"
    assert summary['stop_reason'], "Should have stop reason"
    
    print(f"✓ Graph executed successfully")
    print(f"  Iterations: {summary['iterations']}")
    print(f"  Final score: {summary['final_score']}")
    print(f"  Final budget: {summary['final_budget']}")
    print(f"  Stop reason: {summary['stop_reason']}")
    
    return True


def run_all_tests():
    """Run all test suites."""
    print("\n" + "=" * 70)
    print("LangGraph Deterministic Agent Test Suite")
    print("=" * 70)
    
    tests = [
        ("State Initialization", test_state_initialization),
        ("Edge Selection Node", test_edge_selection_node),
        ("Resource Allocation Node", test_resource_allocation_node),
        ("Distillation Strategy Node", test_distillation_strategy_node),
        ("Simulation Check Node", test_simulation_check_node),
        ("Control Flow", test_control_flow),
        ("Budget Constraints", test_budget_constraints),
        ("Full Graph Execution", test_full_graph_execution),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"✗ {name} FAILED")
        except Exception as e:
            failed += 1
            print(f"✗ {name} FAILED with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 All tests passed!")
        return True
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return False


# Import UpdateStateNode for testing
from agentic.langgraph_deterministic_agent import UpdateStateNode


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
