"""
Edge selection and budget management.

Scores edges based on utility, difficulty, cost, and success probability.
Constants are tuned for the game's mechanics—adjust if rules change.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from dataclasses import dataclass

# Game constraints
DIFFICULTY_SCALE = 10.0
THRESHOLD_MIN = 0.5
THRESHOLD_MAX = 0.99

# Heuristics (based on observed distillation behavior)
BASE_SUCCESS_RATE = 0.7  # ~70% pass rate per ancilla measurement
MIN_SUCCESS_PROB = 0.1
MAX_SUCCESS_PROB = 0.95

# Cost estimation
MIN_BELL_PAIRS = 2
MAX_BELL_PAIRS = 8  # Game limit
BASE_COST = 2.0
DIFFICULTY_COST_FACTOR = 3.0  # Higher difficulty → more pairs needed
THRESHOLD_COST_FACTOR = 2.0   # Higher threshold → more pairs needed


@dataclass
class EdgeScore:
    """Scoring information for an edge."""
    edge_id: Tuple[str, str]
    priority: float
    expected_utility: float
    expected_cost: float
    roi: float
    difficulty: float
    threshold: float
    target_node_utility: int
    estimated_success_prob: float


class EdgeSelectionStrategy:
    """
    Multi-factor edge scoring.
    
    Balances utility (reward), difficulty (effort), cost (Bell pairs), and
    success probability. Weights are tunable—aggressive strategies increase
    utility_weight, conservative strategies increase cost_weight.
    """
    
    def __init__(
        self,
        utility_weight: float = 1.0,
        difficulty_weight: float = 0.5,
        cost_weight: float = 0.3,
        success_prob_weight: float = 0.4
    ):
        self.utility_weight = utility_weight
        self.difficulty_weight = difficulty_weight
        self.cost_weight = cost_weight
        self.success_prob_weight = success_prob_weight
    
    def score_edge(
        self,
        edge: Dict[str, Any],
        graph: Dict[str, Any],
        status: Dict[str, Any],
        owned_nodes: set
    ) -> EdgeScore:
        """
        Calculate priority score for an edge.
        
        Args:
            edge: Edge information from graph
            graph: Full graph structure
            status: Current player status
            owned_nodes: Set of owned node IDs
            
        Returns:
            EdgeScore with priority and metadata
        """
        edge_id = tuple(edge['edge_id'])
        n1, n2 = edge_id
        
        # Determine target node (the one we don't own yet)
        target_node_id = n2 if n1 in owned_nodes else n1
        
        # Get target node info
        target_node = self._get_node_info(target_node_id, graph)
        if not target_node:
            return EdgeScore(
                edge_id=edge_id,
                priority=0.0,
                expected_utility=0.0,
                expected_cost=0.0,
                roi=0.0,
                difficulty=edge.get('difficulty_rating', 5.0),
                threshold=edge.get('base_threshold', 0.9),
                target_node_utility=0,
                estimated_success_prob=0.5
            )
        
        # Extract edge properties
        difficulty = edge.get('difficulty_rating', 5.0)
        threshold = edge.get('base_threshold', 0.9)
        
        # Extract node properties
        utility_qubits = target_node.get('utility_qubits', 0)
        bonus_bell_pairs = target_node.get('bonus_bell_pairs', 0)
        
        # Estimate success probability based on difficulty
        success_prob = self._estimate_success_probability(difficulty, threshold)
        
        # Estimate bell pair cost (higher difficulty = more pairs needed)
        expected_cost = self._estimate_bell_pair_cost(difficulty, threshold)
        
        # Calculate expected utility (utility + bonus, weighted by success prob)
        expected_utility = (utility_qubits + bonus_bell_pairs * 0.5) * success_prob
        
        # Calculate ROI (return on investment)
        roi = expected_utility / max(1, expected_cost) if expected_cost > 0 else 0
        
        # Multi-factor priority score
        priority = (
            self.utility_weight * utility_qubits +
            self.success_prob_weight * success_prob * 10 +
            -self.difficulty_weight * difficulty +
            -self.cost_weight * expected_cost +
            roi * 2.0  # ROI is important
        )
        
        return EdgeScore(
            edge_id=edge_id,
            priority=priority,
            expected_utility=expected_utility,
            expected_cost=expected_cost,
            roi=roi,
            difficulty=difficulty,
            threshold=threshold,
            target_node_utility=utility_qubits,
            estimated_success_prob=success_prob
        )
    
    def rank_edges(
        self,
        claimable_edges: List[Dict[str, Any]],
        graph: Dict[str, Any],
        status: Dict[str, Any]
    ) -> List[EdgeScore]:
        """
        Rank all claimable edges by priority.
        
        Args:
            claimable_edges: List of claimable edges
            graph: Full graph structure
            status: Current player status
            
        Returns:
            List of EdgeScore objects, sorted by priority (descending)
        """
        owned_nodes = set(status.get('owned_nodes', []))
        
        scores = []
        for edge in claimable_edges:
            score = self.score_edge(edge, graph, status, owned_nodes)
            scores.append(score)
        
        # Sort by priority (highest first)
        scores.sort(key=lambda s: s.priority, reverse=True)
        
        return scores
    
    def select_best_edge(
        self,
        claimable_edges: List[Dict[str, Any]],
        graph: Dict[str, Any],
        status: Dict[str, Any],
        budget_threshold: int = 10
    ) -> Optional[EdgeScore]:
        """
        Select the best edge to attempt, considering budget constraints.
        
        Args:
            claimable_edges: List of claimable edges
            graph: Full graph structure
            status: Current player status
            budget_threshold: Minimum budget to reserve
            
        Returns:
            Best EdgeScore or None if no good options
        """
        if not claimable_edges:
            return None
        
        current_budget = status.get('budget', 0)
        
        # Rank all edges
        ranked = self.rank_edges(claimable_edges, graph, status)
        
        # Filter by budget constraints
        for score in ranked:
            # Check if we have enough budget
            if current_budget - score.expected_cost >= budget_threshold:
                return score
        
        # If no edges meet budget threshold, return best if we have any budget
        if current_budget > 0 and ranked:
            return ranked[0]
        
        return None
    
    def _get_node_info(self, node_id: str, graph: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get node information from graph."""
        for node in graph.get('nodes', []):
            if node['node_id'] == node_id:
                return node
        return None
    
    def _estimate_success_probability(self, difficulty: float, threshold: float) -> float:
        """
        Estimate success probability based on difficulty and threshold.
        
        Higher difficulty and threshold = lower success probability.
        
        Formula explanation:
        - Normalize difficulty using DIFFICULTY_SCALE (1-10 range)
        - Base probability decreases linearly with difficulty
        - Threshold penalty accounts for higher fidelity requirements
        - Clamped to MIN_SUCCESS_PROB and MAX_SUCCESS_PROB
        """
        # Normalize difficulty using game scale
        norm_difficulty = difficulty / DIFFICULTY_SCALE
        
        # Base success probability decreases with difficulty
        base_prob = 1.0 - norm_difficulty * 0.5
        
        # Threshold also affects success (higher threshold = harder)
        # Penalty scales with distance from minimum threshold
        threshold_penalty = (threshold - THRESHOLD_MIN) * 0.3
        
        success_prob = base_prob - threshold_penalty
        
        # Clamp to acceptable range
        return max(MIN_SUCCESS_PROB, min(MAX_SUCCESS_PROB, success_prob))
    
    def _estimate_bell_pair_cost(self, difficulty: float, threshold: float) -> float:
        """
        Estimate number of bell pairs needed based on difficulty and threshold.
        
        Returns expected cost (can be fractional for averaging).
        
        Formula explanation:
        - BASE_COST: Minimum 2 pairs required for any distillation
        - Difficulty contribution: Scales with DIFFICULTY_COST_FACTOR
        - Threshold contribution: Scales with THRESHOLD_COST_FACTOR
        - Result clamped to game limits [MIN_BELL_PAIRS, MAX_BELL_PAIRS]
        """
        # Normalize difficulty
        difficulty_factor = difficulty / DIFFICULTY_SCALE
        
        # Normalize threshold (distance from minimum)
        threshold_factor = (threshold - THRESHOLD_MIN) * 2.0
        
        # Combined cost estimate using tuned factors
        estimated_cost = (BASE_COST + 
                         difficulty_factor * DIFFICULTY_COST_FACTOR + 
                         threshold_factor * THRESHOLD_COST_FACTOR)
        
        # Clamp to valid game range
        return max(float(MIN_BELL_PAIRS), min(float(MAX_BELL_PAIRS), estimated_cost))


class BudgetManager:
    """
    Manages bell pair budget with risk-aware decision making.
    
    Implements:
    - Expected value calculations
    - Risk assessment
    - Retry limits
    - Early stopping criteria
    """
    
    def __init__(
        self,
        min_reserve: int = 10,
        max_retries_per_edge: int = 3,
        risk_tolerance: float = 0.5
    ):
        """
        Initialize budget manager.
        
        Args:
            min_reserve: Minimum bell pairs to keep in reserve
            max_retries_per_edge: Maximum attempts per edge
            risk_tolerance: 0 (conservative) to 1 (aggressive)
        """
        self.min_reserve = min_reserve
        self.max_retries_per_edge = max_retries_per_edge
        self.risk_tolerance = risk_tolerance
        self.attempt_history: Dict[Tuple[str, str], int] = {}
    
    def should_attempt_edge(
        self,
        edge_score: EdgeScore,
        current_budget: int
    ) -> Tuple[bool, str]:
        """
        Decide whether to attempt claiming an edge.
        
        Args:
            edge_score: Scored edge information
            current_budget: Current bell pair budget
            
        Returns:
            (should_attempt, reason)
        """
        # Check retry limit
        attempts = self.attempt_history.get(edge_score.edge_id, 0)
        if attempts >= self.max_retries_per_edge:
            return False, f"Max retries ({self.max_retries_per_edge}) reached"
        
        # Check budget constraint
        if current_budget < edge_score.expected_cost + self.min_reserve:
            return False, f"Insufficient budget (need {edge_score.expected_cost + self.min_reserve}, have {current_budget})"
        
        # Check expected value
        expected_value = edge_score.expected_utility - edge_score.expected_cost
        if expected_value <= 0:
            return False, f"Negative expected value ({expected_value:.2f})"
        
        # Risk assessment: compare ROI to risk tolerance
        if edge_score.roi < self.risk_tolerance:
            return False, f"ROI ({edge_score.roi:.2f}) below risk tolerance ({self.risk_tolerance})"
        
        # Check success probability
        if edge_score.estimated_success_prob < 0.2:
            return False, f"Success probability too low ({edge_score.estimated_success_prob:.2%})"
        
        return True, "Approved"
    
    def record_attempt(
        self,
        edge_id: Tuple[str, str],
        success: bool,
        actual_cost: int
    ):
        """
        Record an edge claim attempt for learning.
        
        Args:
            edge_id: Edge identifier
            success: Whether the claim succeeded
            actual_cost: Actual bell pairs spent (0 if failed)
        """
        if edge_id not in self.attempt_history:
            self.attempt_history[edge_id] = 0
        self.attempt_history[edge_id] += 1
    
    def get_attempt_count(self, edge_id: Tuple[str, str]) -> int:
        """Get number of attempts for an edge."""
        return self.attempt_history.get(edge_id, 0)
    
    def reset_edge_attempts(self, edge_id: Tuple[str, str]):
        """Reset attempt counter for an edge (e.g., after success)."""
        if edge_id in self.attempt_history:
            del self.attempt_history[edge_id]
    
    def adjust_risk_tolerance(self, current_budget: int, initial_budget: int):
        """
        Dynamically adjust risk tolerance based on remaining budget.
        
        Low budget -> more conservative
        High budget -> more aggressive
        """
        budget_ratio = current_budget / max(1, initial_budget)
        
        if budget_ratio < 0.2:
            # Critical budget: very conservative
            self.risk_tolerance = 0.8
        elif budget_ratio < 0.5:
            # Low budget: conservative
            self.risk_tolerance = 0.6
        else:
            # Healthy budget: normal risk
            self.risk_tolerance = 0.4


class AdaptiveDistillationPlanner:
    """
    Determines optimal number of bell pairs for distillation attempts.
    
    Implements adaptive strategy:
    - Start with minimum (2 pairs)
    - Increase if estimated fidelity < threshold
    - Cap at maximum (5-8 pairs depending on budget)
    """
    
    def __init__(self):
        self.min_pairs = 2
        self.max_pairs = 8
    
    def determine_bell_pair_count(
        self,
        edge_score: EdgeScore,
        current_budget: int,
        attempt_number: int = 0
    ) -> int:
        """
        Determine optimal number of bell pairs for an attempt.
        
        Strategy:
        - First attempt: start with 2 pairs
        - If failed: increase by 1-2 pairs
        - Consider difficulty and threshold
        - Respect budget constraints
        
        Args:
            edge_score: Edge scoring information
            current_budget: Available bell pairs
            attempt_number: Which attempt this is (0-indexed)
            
        Returns:
            Number of bell pairs to use (2-8)
        """
        # Base number from difficulty
        if edge_score.difficulty <= 3:
            base_pairs = 2
        elif edge_score.difficulty <= 6:
            base_pairs = 3
        else:
            base_pairs = 4
        
        # Increase with attempt number (retry with more resources)
        pairs = base_pairs + attempt_number
        
        # Threshold adjustment
        if edge_score.threshold > 0.85:
            pairs += 1
        if edge_score.threshold > 0.92:
            pairs += 1
        
        # Budget constraint
        affordable_pairs = min(current_budget // 2, self.max_pairs)
        pairs = min(pairs, affordable_pairs)
        
        # Clamp to valid range
        return max(self.min_pairs, min(self.max_pairs, pairs))
    
    def should_increase_pairs(
        self,
        current_pairs: int,
        estimated_fidelity: float,
        threshold: float,
        budget: int
    ) -> bool:
        """
        Decide if we should increase bell pair count.
        
        Args:
            current_pairs: Current number of pairs
            estimated_fidelity: Estimated output fidelity
            threshold: Required threshold
            budget: Available budget
            
        Returns:
            True if should increase pairs
        """
        # Don't increase if at max or budget constrained
        if current_pairs >= self.max_pairs or budget < current_pairs + 2:
            return False
        
        # Increase if estimated fidelity is below threshold
        if estimated_fidelity < threshold:
            return True
        
        # Increase if very close to threshold (need safety margin)
        if estimated_fidelity < threshold + 0.05:
            return True
        
        return False
