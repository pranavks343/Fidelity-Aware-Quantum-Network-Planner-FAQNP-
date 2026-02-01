"""
Main Execution Module

Provides high-level interface for running the quantum network optimization agent.
"""

from typing import Optional, Dict, Any
from client import GameClient
from agent import (
    QuantumNetworkAgent,
    AgentConfig,
    create_default_agent,
    create_aggressive_agent,
    create_conservative_agent
)


class GameExecutor:
    """
    High-level executor for the quantum networking game.
    
    Handles:
    - Player registration
    - Starting node selection
    - Agent execution
    - Results reporting
    """
    
    def __init__(
        self,
        player_id: str,
        name: str,
        location: str = "remote",
        base_url: Optional[str] = None
    ):
        """
        Initialize executor.
        
        Args:
            player_id: Unique player identifier
            name: Player name
            location: "in_person" or "remote"
            base_url: Optional custom server URL
        """
        self.player_id = player_id
        self.name = name
        self.location = location
        
        # Create client
        if base_url:
            self.client = GameClient(base_url=base_url)
        else:
            self.client = GameClient()
        
        self.agent: Optional[QuantumNetworkAgent] = None
    
    def register(self) -> Dict[str, Any]:
        """
        Register player with server.
        
        Returns:
            Registration response
        """
        print(f"Registering player: {self.player_id} ({self.name})")
        result = self.client.register(self.player_id, self.name, self.location)
        
        if result.get('ok'):
            print("✓ Registration successful")
            
            # Show starting node candidates if available
            if 'data' in result and 'starting_node_candidates' in result['data']:
                candidates = result['data']['starting_node_candidates']
                print(f"\nStarting node candidates: {len(candidates)}")
                for node_id in candidates:
                    node_info = self.client.get_node_info(node_id)
                    if node_info:
                        utility = node_info.get('utility_qubits', 0)
                        bonus = node_info.get('bonus_bell_pairs', 0)
                        print(f"  - {node_id}: {utility} utility qubits, {bonus} bonus bell pairs")
        else:
            error = result.get('error', {})
            print(f"✗ Registration failed: {error.get('message', 'Unknown error')}")
        
        return result
    
    def select_starting_node(
        self,
        node_id: Optional[str] = None,
        strategy: str = "balanced"
    ) -> Dict[str, Any]:
        """
        Select starting node.
        
        Args:
            node_id: Specific node ID, or None to auto-select
            strategy: "balanced", "utility", or "bonus" (if auto-selecting)
            
        Returns:
            Selection response
        """
        if node_id is None:
            # Auto-select based on strategy
            node_id = self._auto_select_starting_node(strategy)
            if node_id is None:
                return {'ok': False, 'error': 'No starting node candidates available'}
        
        print(f"Selecting starting node: {node_id}")
        result = self.client.select_starting_node(node_id)
        
        if result.get('ok'):
            print("✓ Starting node selected")
            self.client.print_status()
        else:
            error = result.get('error', {})
            print(f"✗ Selection failed: {error.get('message', 'Unknown error')}")
        
        return result
    
    def _auto_select_starting_node(self, strategy: str) -> Optional[str]:
        """
        Automatically select best starting node based on strategy.
        
        Args:
            strategy: "balanced", "utility", or "bonus"
            
        Returns:
            Selected node ID or None
        """
        status = self.client.get_status()
        candidates = status.get('starting_node_candidates', [])
        
        if not candidates:
            return None
        
        # Score each candidate
        best_node = None
        best_score = -1
        
        for node_id in candidates:
            node_info = self.client.get_node_info(node_id)
            if not node_info:
                continue
            
            utility = node_info.get('utility_qubits', 0)
            bonus = node_info.get('bonus_bell_pairs', 0)
            
            # Calculate score based on strategy
            if strategy == "utility":
                score = utility
            elif strategy == "bonus":
                score = bonus
            else:  # balanced
                score = utility + bonus * 0.5
            
            if score > best_score:
                best_score = score
                best_node = node_id
        
        return best_node
    
    def create_agent(
        self,
        agent_type: str = "default",
        config: Optional[AgentConfig] = None
    ) -> QuantumNetworkAgent:
        """
        Create and configure agent.
        
        Args:
            agent_type: "default", "aggressive", or "conservative"
            config: Optional custom configuration
            
        Returns:
            Configured agent
        """
        if config:
            self.agent = QuantumNetworkAgent(self.client, config)
        elif agent_type == "aggressive":
            self.agent = create_aggressive_agent(self.client)
        elif agent_type == "conservative":
            self.agent = create_conservative_agent(self.client)
        else:
            self.agent = create_default_agent(self.client)
        
        print(f"✓ Created {agent_type} agent")
        return self.agent
    
    def run(
        self,
        agent_type: str = "default",
        max_iterations: int = 100,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete game execution.
        
        Steps:
        1. Register (if not already registered)
        2. Select starting node (if not already selected)
        3. Create agent
        4. Run autonomous agent
        5. Report results
        
        Args:
            agent_type: "default", "aggressive", or "conservative"
            max_iterations: Maximum iterations for agent
            verbose: Print progress
            
        Returns:
            Execution summary
        """
        # Check if already registered
        status = self.client.get_status()
        if not status:
            # Register
            reg_result = self.register()
            if not reg_result.get('ok'):
                return {'success': False, 'error': 'Registration failed'}
        
        # Check if starting node selected
        status = self.client.get_status()
        if not status.get('starting_node'):
            # Select starting node
            select_result = self.select_starting_node(strategy="balanced")
            if not select_result.get('ok'):
                return {'success': False, 'error': 'Starting node selection failed'}
        
        # Create agent
        if self.agent is None:
            self.create_agent(agent_type)
        
        # Run agent
        if verbose:
            print("\nStarting autonomous execution...")
        
        summary = self.agent.run_autonomous(
            max_iterations=max_iterations,
            verbose=verbose
        )
        
        # Add success flag
        summary['success'] = True
        
        return summary
    
    def get_leaderboard(self, top_n: int = 10):
        """
        Display leaderboard.
        
        Args:
            top_n: Number of top players to show
        """
        leaderboard = self.client.get_leaderboard()
        
        print("\n" + "=" * 60)
        print("LEADERBOARD")
        print("=" * 60)
        print(f"{'Rank':<6} {'Player':<20} {'Score':<10} {'Nodes':<8}")
        print("-" * 60)
        
        for i, entry in enumerate(leaderboard[:top_n], 1):
            player = entry.get('player_id', 'Unknown')
            score = entry.get('score', 0)
            nodes = entry.get('owned_nodes', 0)
            
            # Highlight our player
            if player == self.player_id:
                print(f"{'→ ' + str(i):<6} {player:<20} {score:<10} {nodes:<8} ← YOU")
            else:
                print(f"{i:<6} {player:<20} {score:<10} {nodes:<8}")
        
        print("=" * 60)
    
    def restart(self):
        """Restart game (reset progress)."""
        print("Restarting game...")
        result = self.client.restart()
        
        if result.get('ok'):
            print("✓ Game restarted")
            self.agent = None  # Reset agent
        else:
            error = result.get('error', {})
            print(f"✗ Restart failed: {error.get('message', 'Unknown error')}")
        
        return result


def quick_start(
    player_id: str,
    name: str,
    location: str = "remote",
    agent_type: str = "default",
    max_iterations: int = 100
) -> Dict[str, Any]:
    """
    Quick start function for immediate execution.
    
    Args:
        player_id: Unique player identifier
        name: Player name
        location: "in_person" or "remote"
        agent_type: "default", "aggressive", or "conservative"
        max_iterations: Maximum iterations
        
    Returns:
        Execution summary
    """
    executor = GameExecutor(player_id, name, location)
    return executor.run(agent_type=agent_type, max_iterations=max_iterations)


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python executor.py <player_id> <name> [location] [agent_type]")
        print("  location: 'in_person' or 'remote' (default: remote)")
        print("  agent_type: 'default', 'aggressive', or 'conservative' (default: default)")
        sys.exit(1)
    
    player_id = sys.argv[1]
    name = sys.argv[2]
    location = sys.argv[3] if len(sys.argv) > 3 else "remote"
    agent_type = sys.argv[4] if len(sys.argv) > 4 else "default"
    
    # Run
    summary = quick_start(player_id, name, location, agent_type)
    
    # Show results
    if summary.get('success'):
        print("\n✓ Execution completed successfully")
        print(f"Final score: {summary['final_score']}")
    else:
        print(f"\n✗ Execution failed: {summary.get('error', 'Unknown error')}")
