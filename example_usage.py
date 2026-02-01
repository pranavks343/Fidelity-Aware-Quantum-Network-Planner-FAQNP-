"""
Example Usage of Quantum Network Optimization System

Demonstrates:
1. Manual circuit creation and testing
2. Strategy-based edge selection
3. Autonomous agent execution
4. Custom agent configuration
"""

from client import GameClient
from distillation import (
    create_bbpssw_circuit,
    create_dejmps_circuit,
    estimate_output_fidelity
)
from strategy import EdgeSelectionStrategy, BudgetManager
from simulator import DistillationSimulator, estimate_input_noise_from_difficulty
from agent import QuantumNetworkAgent, AgentConfig
from executor import GameExecutor, quick_start


# ============================================================================
# EXAMPLE 1: Manual Circuit Creation and Testing
# ============================================================================

def example_manual_circuit():
    """Example: Create and test distillation circuits manually."""
    print("=" * 60)
    print("EXAMPLE 1: Manual Circuit Creation")
    print("=" * 60)
    
    # Create BBPSSW circuit with 3 Bell pairs
    print("\nCreating BBPSSW circuit (3 Bell pairs)...")
    circuit, flag_bit = create_bbpssw_circuit(num_bell_pairs=3)
    
    print(f"Circuit created:")
    print(f"  - Qubits: {circuit.num_qubits}")
    print(f"  - Depth: {circuit.depth()}")
    print(f"  - Gates: {len(circuit.data)}")
    print(f"  - Flag bit: {flag_bit}")
    
    # Simulate locally
    print("\nSimulating circuit...")
    simulator = DistillationSimulator()
    
    results = simulator.simulate_circuit(
        circuit=circuit,
        flag_bit=flag_bit,
        num_bell_pairs=3,
        input_noise=0.15
    )
    
    print(f"Simulation results:")
    print(f"  - Estimated fidelity: {results['estimated_fidelity']:.3f}")
    print(f"  - Success probability: {results['success_probability']:.3f}")
    print(f"  - Valid: {results['valid']}")
    
    # Create DEJMPS circuit
    print("\nCreating DEJMPS circuit (4 Bell pairs)...")
    circuit2, flag_bit2 = create_dejmps_circuit(num_bell_pairs=4)
    
    print(f"Circuit created:")
    print(f"  - Qubits: {circuit2.num_qubits}")
    print(f"  - Depth: {circuit2.depth()}")
    print(f"  - Flag bit: {flag_bit2}")


# ============================================================================
# EXAMPLE 2: Strategy-Based Edge Selection
# ============================================================================

def example_edge_selection():
    """Example: Use strategy to rank and select edges."""
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Strategy-Based Edge Selection")
    print("=" * 60)
    
    # Create client (read-only operations)
    client = GameClient()
    
    # Get graph structure
    print("\nFetching graph structure...")
    graph = client.get_graph()
    
    print(f"Graph loaded:")
    print(f"  - Nodes: {len(graph.get('nodes', []))}")
    print(f"  - Edges: {len(graph.get('edges', []))}")
    
    # Create strategy
    strategy = EdgeSelectionStrategy(
        utility_weight=1.0,
        difficulty_weight=0.5,
        cost_weight=0.3,
        success_prob_weight=0.4
    )
    
    # Simulate owned nodes (for demonstration)
    owned_nodes = set()
    if graph.get('nodes'):
        # Pretend we own the first node
        owned_nodes.add(graph['nodes'][0]['node_id'])
    
    # Mock status
    status = {
        'owned_nodes': list(owned_nodes),
        'budget': 75
    }
    
    # Find claimable edges
    claimable = []
    for edge in graph.get('edges', []):
        n1, n2 = edge['edge_id']
        if (n1 in owned_nodes) != (n2 in owned_nodes):
            claimable.append(edge)
    
    if claimable:
        print(f"\nFound {len(claimable)} claimable edges")
        
        # Rank edges
        ranked = strategy.rank_edges(claimable, graph, status)
        
        print("\nTop 5 edges by priority:")
        for i, score in enumerate(ranked[:5], 1):
            print(f"{i}. {score.edge_id}")
            print(f"   Priority: {score.priority:.2f}")
            print(f"   ROI: {score.roi:.2f}")
            print(f"   Difficulty: {score.difficulty:.1f}")
            print(f"   Threshold: {score.threshold:.3f}")
            print(f"   Target utility: {score.target_node_utility}")
    else:
        print("\nNo claimable edges (need to own at least one node)")


# ============================================================================
# EXAMPLE 3: Budget-Aware Decision Making
# ============================================================================

def example_budget_management():
    """Example: Use budget manager to make decisions."""
    print("\n" + "=" * 60)
    print("EXAMPLE 3: Budget Management")
    print("=" * 60)
    
    # Create budget manager
    budget_manager = BudgetManager(
        min_reserve=10,
        max_retries_per_edge=3,
        risk_tolerance=0.5
    )
    
    # Simulate edge scores
    from strategy import EdgeScore
    
    edges = [
        EdgeScore(
            edge_id=("A", "B"),
            priority=10.0,
            expected_utility=15.0,
            expected_cost=3.0,
            roi=5.0,
            difficulty=3.0,
            threshold=0.85,
            target_node_utility=10,
            estimated_success_prob=0.8
        ),
        EdgeScore(
            edge_id=("B", "C"),
            priority=8.0,
            expected_utility=8.0,
            expected_cost=5.0,
            roi=1.6,
            difficulty=7.0,
            threshold=0.92,
            target_node_utility=5,
            estimated_success_prob=0.4
        ),
        EdgeScore(
            edge_id=("C", "D"),
            priority=12.0,
            expected_utility=20.0,
            expected_cost=2.0,
            roi=10.0,
            difficulty=2.0,
            threshold=0.80,
            target_node_utility=15,
            estimated_success_prob=0.9
        ),
    ]
    
    current_budget = 50
    
    print(f"\nCurrent budget: {current_budget}")
    print(f"Min reserve: {budget_manager.min_reserve}")
    print(f"Risk tolerance: {budget_manager.risk_tolerance}")
    
    print("\nEvaluating edges:")
    for edge_score in edges:
        should_attempt, reason = budget_manager.should_attempt_edge(
            edge_score, current_budget
        )
        
        status = "✓ APPROVE" if should_attempt else "✗ REJECT"
        print(f"\n{edge_score.edge_id}: {status}")
        print(f"  ROI: {edge_score.roi:.2f}")
        print(f"  Cost: {edge_score.expected_cost:.1f}")
        print(f"  Success prob: {edge_score.estimated_success_prob:.2%}")
        print(f"  Reason: {reason}")


# ============================================================================
# EXAMPLE 4: Autonomous Agent Execution (Dry Run)
# ============================================================================

def example_autonomous_agent_dry_run():
    """Example: Set up autonomous agent (without running)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 4: Autonomous Agent Configuration")
    print("=" * 60)
    
    # Create client
    client = GameClient()
    
    # Create custom agent configuration
    config = AgentConfig(
        utility_weight=1.2,
        difficulty_weight=0.4,
        cost_weight=0.3,
        success_prob_weight=0.5,
        min_reserve=15,
        max_retries_per_edge=3,
        risk_tolerance=0.4,
        enable_simulation=True,
        simulation_shots=1000,
        prefer_dejmps=False,
        adaptive_risk=True,
        adaptive_pairs=True
    )
    
    print("\nAgent Configuration:")
    print(f"  - Utility weight: {config.utility_weight}")
    print(f"  - Difficulty weight: {config.difficulty_weight}")
    print(f"  - Cost weight: {config.cost_weight}")
    print(f"  - Success prob weight: {config.success_prob_weight}")
    print(f"  - Min reserve: {config.min_reserve}")
    print(f"  - Max retries: {config.max_retries_per_edge}")
    print(f"  - Risk tolerance: {config.risk_tolerance}")
    print(f"  - Simulation enabled: {config.enable_simulation}")
    print(f"  - Prefer DEJMPS: {config.prefer_dejmps}")
    print(f"  - Adaptive risk: {config.adaptive_risk}")
    print(f"  - Adaptive pairs: {config.adaptive_pairs}")
    
    # Create agent
    agent = QuantumNetworkAgent(client, config)
    
    print("\n✓ Agent created and configured")
    print("\nTo run the agent:")
    print("  summary = agent.run_autonomous(max_iterations=100, verbose=True)")


# ============================================================================
# EXAMPLE 5: Complete Execution Flow
# ============================================================================

def example_complete_flow():
    """Example: Complete execution flow (requires valid credentials)."""
    print("\n" + "=" * 60)
    print("EXAMPLE 5: Complete Execution Flow")
    print("=" * 60)
    
    print("\nTo run a complete game session:")
    print("\n1. Using GameExecutor:")
    print("""
    from executor import GameExecutor
    
    executor = GameExecutor(
        player_id="your_player_id",
        name="Your Name",
        location="remote"
    )
    
    # Register and select starting node
    executor.register()
    executor.select_starting_node(strategy="balanced")
    
    # Create and run agent
    executor.create_agent(agent_type="default")
    summary = executor.run(max_iterations=100)
    
    # View results
    print(f"Final score: {summary['final_score']}")
    executor.get_leaderboard()
    """)
    
    print("\n2. Using quick_start function:")
    print("""
    from executor import quick_start
    
    summary = quick_start(
        player_id="your_player_id",
        name="Your Name",
        location="remote",
        agent_type="default",
        max_iterations=100
    )
    """)
    
    print("\n3. From command line:")
    print("""
    python executor.py your_player_id "Your Name" remote default
    """)


# ============================================================================
# EXAMPLE 6: Custom Protocol Selection
# ============================================================================

def example_protocol_selection():
    """Example: Compare different distillation protocols."""
    print("\n" + "=" * 60)
    print("EXAMPLE 6: Protocol Comparison")
    print("=" * 60)
    
    # Test parameters
    num_bell_pairs = 3
    input_fidelity = 0.75
    
    print(f"\nInput parameters:")
    print(f"  - Bell pairs: {num_bell_pairs}")
    print(f"  - Input fidelity: {input_fidelity:.3f}")
    
    # BBPSSW
    print("\nBBPSSW Protocol:")
    circuit_bbpssw, flag_bbpssw = create_bbpssw_circuit(num_bell_pairs)
    fidelity_bbpssw = estimate_output_fidelity(input_fidelity, num_bell_pairs, "bbpssw")
    print(f"  - Circuit depth: {circuit_bbpssw.depth()}")
    print(f"  - Estimated output fidelity: {fidelity_bbpssw:.3f}")
    print(f"  - Improvement: {fidelity_bbpssw - input_fidelity:+.3f}")
    
    # DEJMPS
    print("\nDEJMPS Protocol:")
    circuit_dejmps, flag_dejmps = create_dejmps_circuit(num_bell_pairs)
    fidelity_dejmps = estimate_output_fidelity(input_fidelity, num_bell_pairs, "dejmps")
    print(f"  - Circuit depth: {circuit_dejmps.depth()}")
    print(f"  - Estimated output fidelity: {fidelity_dejmps:.3f}")
    print(f"  - Improvement: {fidelity_dejmps - input_fidelity:+.3f}")
    
    # Recommendation
    print("\nRecommendation:")
    if fidelity_bbpssw > fidelity_dejmps:
        print("  → Use BBPSSW for this scenario")
    elif fidelity_dejmps > fidelity_bbpssw:
        print("  → Use DEJMPS for this scenario")
    else:
        print("  → Both protocols perform similarly")


# ============================================================================
# Main
# ============================================================================

def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("QUANTUM NETWORK OPTIMIZATION - EXAMPLE USAGE")
    print("=" * 60)
    
    try:
        example_manual_circuit()
        example_edge_selection()
        example_budget_management()
        example_autonomous_agent_dry_run()
        example_protocol_selection()
        example_complete_flow()
        
        print("\n" + "=" * 60)
        print("✓ ALL EXAMPLES COMPLETED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Run tests: python test_distillation.py")
        print("2. Execute agent: python executor.py <player_id> <name>")
        print("3. Customize agent configuration in agent.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
