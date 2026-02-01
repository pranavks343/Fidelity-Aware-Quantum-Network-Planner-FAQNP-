"""
Test suite for core logic (without Qiskit dependency).

Tests strategy, budget management, and decision logic.
"""

import sys
from strategy import (
    EdgeSelectionStrategy,
    BudgetManager,
    AdaptiveDistillationPlanner,
    EdgeScore
)


def test_edge_selection():
    """Test edge selection strategy."""
    print("\n" + "=" * 60)
    print("Testing Edge Selection Strategy")
    print("=" * 60)
    
    strategy = EdgeSelectionStrategy(
        utility_weight=1.0,
        difficulty_weight=0.5,
        cost_weight=0.3,
        success_prob_weight=0.4
    )
    
    # Create mock edges
    edges = [
        {
            'edge_id': ('A', 'B'),
            'difficulty_rating': 3.0,
            'base_threshold': 0.85
        },
        {
            'edge_id': ('B', 'C'),
            'difficulty_rating': 7.0,
            'base_threshold': 0.92
        },
        {
            'edge_id': ('C', 'D'),
            'difficulty_rating': 2.0,
            'base_threshold': 0.80
        }
    ]
    
    # Mock graph
    graph = {
        'nodes': [
            {'node_id': 'A', 'utility_qubits': 5, 'bonus_bell_pairs': 10},
            {'node_id': 'B', 'utility_qubits': 10, 'bonus_bell_pairs': 5},
            {'node_id': 'C', 'utility_qubits': 15, 'bonus_bell_pairs': 8},
            {'node_id': 'D', 'utility_qubits': 8, 'bonus_bell_pairs': 12}
        ]
    }
    
    # Mock status
    status = {
        'owned_nodes': ['A'],
        'budget': 75
    }
    
    # Rank edges
    ranked = strategy.rank_edges(edges, graph, status)
    
    print(f"\nRanked {len(ranked)} edges:")
    for i, score in enumerate(ranked, 1):
        print(f"{i}. {score.edge_id}")
        print(f"   Priority: {score.priority:.2f}")
        print(f"   ROI: {score.roi:.2f}")
        print(f"   Utility: {score.target_node_utility}")
        print(f"   Difficulty: {score.difficulty:.1f}")
        print(f"   Expected cost: {score.expected_cost:.1f}")
    
    # Verify ranking makes sense
    assert len(ranked) == 3, "Should rank all 3 edges"
    assert ranked[0].priority >= ranked[1].priority >= ranked[2].priority, \
        "Edges should be sorted by priority"
    
    print("\n✓ Edge selection tests passed")
    return True


def test_budget_manager():
    """Test budget management."""
    print("\n" + "=" * 60)
    print("Testing Budget Manager")
    print("=" * 60)
    
    manager = BudgetManager(
        min_reserve=10,
        max_retries_per_edge=3,
        risk_tolerance=0.5
    )
    
    # Create test edge scores
    good_edge = EdgeScore(
        edge_id=('A', 'B'),
        priority=10.0,
        expected_utility=15.0,
        expected_cost=3.0,
        roi=5.0,
        difficulty=3.0,
        threshold=0.85,
        target_node_utility=10,
        estimated_success_prob=0.8
    )
    
    expensive_edge = EdgeScore(
        edge_id=('B', 'C'),
        priority=8.0,
        expected_utility=8.0,
        expected_cost=50.0,
        roi=0.16,
        difficulty=7.0,
        threshold=0.92,
        target_node_utility=5,
        estimated_success_prob=0.4
    )
    
    low_roi_edge = EdgeScore(
        edge_id=('C', 'D'),
        priority=5.0,
        expected_utility=5.0,
        expected_cost=3.0,
        roi=0.3,
        difficulty=5.0,
        threshold=0.88,
        target_node_utility=3,
        estimated_success_prob=0.5
    )
    
    # Test decisions
    current_budget = 50
    
    print(f"\nCurrent budget: {current_budget}")
    print(f"Min reserve: {manager.min_reserve}")
    print(f"Risk tolerance: {manager.risk_tolerance}")
    
    print("\nTest 1: Good edge (high ROI, affordable)")
    should_attempt, reason = manager.should_attempt_edge(good_edge, current_budget)
    print(f"  Decision: {'APPROVE' if should_attempt else 'REJECT'}")
    print(f"  Reason: {reason}")
    assert should_attempt, "Should approve good edge"
    
    print("\nTest 2: Expensive edge (exceeds budget)")
    should_attempt, reason = manager.should_attempt_edge(expensive_edge, current_budget)
    print(f"  Decision: {'APPROVE' if should_attempt else 'REJECT'}")
    print(f"  Reason: {reason}")
    assert not should_attempt, "Should reject expensive edge"
    
    print("\nTest 3: Low ROI edge (below risk tolerance)")
    should_attempt, reason = manager.should_attempt_edge(low_roi_edge, current_budget)
    print(f"  Decision: {'APPROVE' if should_attempt else 'REJECT'}")
    print(f"  Reason: {reason}")
    assert not should_attempt, "Should reject low ROI edge"
    
    print("\nTest 4: Retry limit")
    # Record multiple attempts
    for i in range(3):
        manager.record_attempt(good_edge.edge_id, False, 0)
    
    should_attempt, reason = manager.should_attempt_edge(good_edge, current_budget)
    print(f"  Decision after 3 attempts: {'APPROVE' if should_attempt else 'REJECT'}")
    print(f"  Reason: {reason}")
    assert not should_attempt, "Should reject after max retries"
    
    print("\nTest 5: Risk tolerance adjustment")
    manager.adjust_risk_tolerance(10, 100)  # 10% budget remaining
    print(f"  Risk tolerance after low budget: {manager.risk_tolerance}")
    assert manager.risk_tolerance > 0.5, "Should be more conservative with low budget"
    
    print("\n✓ Budget manager tests passed")
    return True


def test_distillation_planner():
    """Test adaptive distillation planner."""
    print("\n" + "=" * 60)
    print("Testing Adaptive Distillation Planner")
    print("=" * 60)
    
    planner = AdaptiveDistillationPlanner()
    
    # Test cases
    test_cases = [
        {
            'name': 'Easy edge, first attempt',
            'edge': EdgeScore(
                edge_id=('A', 'B'),
                priority=10.0,
                expected_utility=10.0,
                expected_cost=2.0,
                roi=5.0,
                difficulty=2.0,
                threshold=0.80,
                target_node_utility=10,
                estimated_success_prob=0.9
            ),
            'budget': 50,
            'attempt': 0,
            'expected_min': 2,
            'expected_max': 3
        },
        {
            'name': 'Hard edge, first attempt',
            'edge': EdgeScore(
                edge_id=('B', 'C'),
                priority=8.0,
                expected_utility=8.0,
                expected_cost=5.0,
                roi=1.6,
                difficulty=8.0,
                threshold=0.92,
                target_node_utility=5,
                estimated_success_prob=0.4
            ),
            'budget': 50,
            'attempt': 0,
            'expected_min': 4,
            'expected_max': 7
        },
        {
            'name': 'Medium edge, retry',
            'edge': EdgeScore(
                edge_id=('C', 'D'),
                priority=9.0,
                expected_utility=12.0,
                expected_cost=3.0,
                roi=4.0,
                difficulty=5.0,
                threshold=0.87,
                target_node_utility=8,
                estimated_success_prob=0.7
            ),
            'budget': 50,
            'attempt': 2,
            'expected_min': 4,
            'expected_max': 6
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['name']}")
        pairs = planner.determine_bell_pair_count(
            test['edge'],
            test['budget'],
            test['attempt']
        )
        print(f"  Difficulty: {test['edge'].difficulty}")
        print(f"  Threshold: {test['edge'].threshold}")
        print(f"  Attempt: {test['attempt']}")
        print(f"  Determined pairs: {pairs}")
        
        assert test['expected_min'] <= pairs <= test['expected_max'], \
            f"Expected {test['expected_min']}-{test['expected_max']}, got {pairs}"
        assert 2 <= pairs <= 8, "Pairs should be in valid range [2, 8]"
    
    print("\n✓ Distillation planner tests passed")
    return True


def test_integration():
    """Test integration of components."""
    print("\n" + "=" * 60)
    print("Testing Component Integration")
    print("=" * 60)
    
    # Create components
    strategy = EdgeSelectionStrategy()
    manager = BudgetManager()
    planner = AdaptiveDistillationPlanner()
    
    # Mock data
    edges = [
        {'edge_id': ('A', 'B'), 'difficulty_rating': 3.0, 'base_threshold': 0.85},
        {'edge_id': ('B', 'C'), 'difficulty_rating': 5.0, 'base_threshold': 0.88},
        {'edge_id': ('C', 'D'), 'difficulty_rating': 2.0, 'base_threshold': 0.82}
    ]
    
    graph = {
        'nodes': [
            {'node_id': 'A', 'utility_qubits': 5, 'bonus_bell_pairs': 10},
            {'node_id': 'B', 'utility_qubits': 10, 'bonus_bell_pairs': 5},
            {'node_id': 'C', 'utility_qubits': 15, 'bonus_bell_pairs': 8},
            {'node_id': 'D', 'utility_qubits': 8, 'bonus_bell_pairs': 12}
        ]
    }
    
    status = {'owned_nodes': ['A'], 'budget': 75}
    
    # Workflow
    print("\nSimulating decision workflow:")
    
    # 1. Rank edges
    print("\n1. Ranking edges...")
    ranked = strategy.rank_edges(edges, graph, status)
    print(f"   Top edge: {ranked[0].edge_id} (priority={ranked[0].priority:.2f})")
    
    # 2. Check budget approval
    print("\n2. Checking budget approval...")
    should_attempt, reason = manager.should_attempt_edge(ranked[0], status['budget'])
    print(f"   Decision: {'APPROVE' if should_attempt else 'REJECT'}")
    print(f"   Reason: {reason}")
    
    if should_attempt:
        # 3. Determine bell pairs
        print("\n3. Determining bell pair count...")
        pairs = planner.determine_bell_pair_count(ranked[0], status['budget'], 0)
        print(f"   Bell pairs: {pairs}")
        
        # 4. Simulate success
        print("\n4. Simulating claim attempt...")
        print(f"   Would claim edge {ranked[0].edge_id} with {pairs} bell pairs")
        
        # 5. Record result
        manager.record_attempt(ranked[0].edge_id, True, pairs)
        print(f"   Recorded successful attempt")
    
    print("\n✓ Integration tests passed")
    return True


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("CORE LOGIC TEST SUITE")
    print("=" * 60)
    
    try:
        test_edge_selection()
        test_budget_manager()
        test_distillation_planner()
        test_integration()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
