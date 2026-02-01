#!/usr/bin/env python3
"""
Quick-start script for LangGraph-based deterministic agent.

Usage:
    python run_langgraph_agent.py --player-id my_player --name "Alice"
    python run_langgraph_agent.py --player-id my_player --strategy aggressive
    python run_langgraph_agent.py --player-id my_player --max-iterations 50
"""

import argparse
import sys
from core.client import GameClient
from agentic.langgraph_deterministic_agent import (
    LangGraphQuantumAgent,
    LangGraphAgentConfig,
    create_default_langgraph_agent,
    create_aggressive_langgraph_agent,
    create_conservative_langgraph_agent
)


def main():
    parser = argparse.ArgumentParser(description="Run LangGraph quantum network agent")
    
    # Player configuration
    parser.add_argument("--player-id", type=str, required=True, help="Player ID")
    parser.add_argument("--name", type=str, default="LangGraph Agent", help="Player name")
    parser.add_argument("--location", type=str, default="remote", choices=["in_person", "remote"], help="Player location")
    
    # Agent strategy
    parser.add_argument("--strategy", type=str, default="default", 
                       choices=["default", "aggressive", "conservative"],
                       help="Agent strategy preset")
    
    # Execution parameters
    parser.add_argument("--max-iterations", type=int, default=100, help="Maximum iterations")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    # Custom configuration
    parser.add_argument("--min-reserve", type=int, help="Minimum Bell pair reserve")
    parser.add_argument("--max-retries", type=int, help="Max retries per edge")
    parser.add_argument("--no-simulation", action="store_true", help="Disable local simulation")
    
    # Node selection
    parser.add_argument("--starting-node", type=str, help="Starting node ID (auto-select if not provided)")
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("LangGraph Quantum Network Agent")
    print("=" * 70)
    
    # Create client
    client = GameClient()
    
    # Register player
    print(f"\nRegistering player: {args.player_id} ({args.name})")
    result = client.register(args.player_id, args.name, args.location)
    
    if not result.get('ok') and result.get('error', {}).get('code') != 'PLAYER_EXISTS':
        print(f"Registration failed: {result.get('error', {}).get('message', 'Unknown error')}")
        return 1
    
    print("✓ Registered successfully")
    
    # Select starting node
    status = client.get_status()
    if not status.get('starting_node'):
        if args.starting_node:
            node_id = args.starting_node
        else:
            # Auto-select first candidate
            candidates = status.get('starting_node_candidates', [])
            if not candidates:
                print("No starting node candidates available")
                return 1
            node_id = candidates[0]
        
        print(f"\nSelecting starting node: {node_id}")
        result = client.select_starting_node(node_id)
        
        if not result.get('ok'):
            print(f"Node selection failed: {result.get('error', {}).get('message', 'Unknown error')}")
            return 1
        
        print("✓ Starting node selected")
    else:
        print(f"\nUsing existing starting node: {status.get('starting_node')}")
    
    # Print initial status
    client.print_status()
    
    # Create agent based on strategy
    print(f"\nCreating agent with '{args.strategy}' strategy...")
    
    if args.strategy == "aggressive":
        agent = create_aggressive_langgraph_agent(client)
    elif args.strategy == "conservative":
        agent = create_conservative_langgraph_agent(client)
    else:  # default
        agent = create_default_langgraph_agent(client)
    
    # Apply custom configuration if provided
    if args.min_reserve is not None:
        agent.config.min_reserve = args.min_reserve
    if args.max_retries is not None:
        agent.config.max_retries_per_edge = args.max_retries
    if args.no_simulation:
        agent.config.enable_simulation = False
        agent.simulator = None
    
    print("✓ Agent created")
    print(f"  Min reserve: {agent.config.min_reserve}")
    print(f"  Max retries: {agent.config.max_retries_per_edge}")
    print(f"  Simulation: {'enabled' if agent.config.enable_simulation else 'disabled'}")
    
    # Run agent
    print(f"\nRunning agent (max {args.max_iterations} iterations)...")
    print("=" * 70)
    
    try:
        summary = agent.run_autonomous(
            max_iterations=args.max_iterations,
            verbose=args.verbose
        )
        
        # Print final summary
        print("\n" + "=" * 70)
        print("Execution Complete")
        print("=" * 70)
        print(f"Iterations:        {summary['iterations']}")
        print(f"Successful claims: {summary['successful_claims']}")
        print(f"Failed attempts:   {summary['failed_attempts']}")
        print(f"Final score:       {summary['final_score']}")
        print(f"Final budget:      {summary['final_budget']}")
        print(f"Owned nodes:       {summary['owned_nodes']}")
        print(f"Owned edges:       {summary['owned_edges']}")
        print(f"Stop reason:       {summary['stop_reason']}")
        print("=" * 70)
        
        return 0
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
