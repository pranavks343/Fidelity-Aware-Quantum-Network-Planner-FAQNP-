#!/usr/bin/env python3
"""
Complete System Visualization: Network Graph + Distillation Circuits + Results
Shows the full quantum network game with claimable/unclaimable edges and nodes.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import networkx as nx
import numpy as np

from distillation.distillation import create_bbpssw_circuit, create_dejmps_circuit

def create_example_network_graph():
    """Create an example quantum network graph"""
    G = nx.Graph()
    
    # Create a network with 15 nodes
    nodes = {
        'A': {'utility_qubits': 3, 'owned': True},
        'B': {'utility_qubits': 2, 'owned': True},
        'C': {'utility_qubits': 4, 'owned': False},
        'D': {'utility_qubits': 2, 'owned': False},
        'E': {'utility_qubits': 3, 'owned': False},
        'F': {'utility_qubits': 5, 'owned': False},
        'G': {'utility_qubits': 2, 'owned': False},
        'H': {'utility_qubits': 3, 'owned': True},
        'I': {'utility_qubits': 2, 'owned': False},
        'J': {'utility_qubits': 4, 'owned': False},
        'K': {'utility_qubits': 3, 'owned': False},
        'L': {'utility_qubits': 2, 'owned': False},
    }
    
    # Add nodes
    for node_id, attrs in nodes.items():
        G.add_node(node_id, **attrs)
    
    # Add edges with difficulty ratings
    edges = [
        ('A', 'B', {'difficulty': 2, 'threshold': 0.65}),
        ('A', 'C', {'difficulty': 3, 'threshold': 0.70}),
        ('A', 'D', {'difficulty': 4, 'threshold': 0.75}),
        ('B', 'E', {'difficulty': 3, 'threshold': 0.68}),
        ('B', 'H', {'difficulty': 2, 'threshold': 0.65}),
        ('C', 'F', {'difficulty': 5, 'threshold': 0.80}),
        ('D', 'G', {'difficulty': 3, 'threshold': 0.70}),
        ('E', 'F', {'difficulty': 4, 'threshold': 0.75}),
        ('F', 'J', {'difficulty': 6, 'threshold': 0.85}),
        ('G', 'I', {'difficulty': 3, 'threshold': 0.68}),
        ('H', 'I', {'difficulty': 2, 'threshold': 0.65}),
        ('H', 'K', {'difficulty': 4, 'threshold': 0.72}),
        ('I', 'L', {'difficulty': 3, 'threshold': 0.70}),
        ('J', 'K', {'difficulty': 5, 'threshold': 0.78}),
        ('K', 'L', {'difficulty': 3, 'threshold': 0.68}),
    ]
    
    for u, v, attrs in edges:
        G.add_edge(u, v, **attrs)
    
    return G, nodes

def visualize_complete_system():
    """Create comprehensive system visualization"""
    
    # Create figure with multiple subplots
    fig = plt.figure(figsize=(24, 16))
    
    # Main title
    fig.suptitle('Complete Quantum Network Distillation System', 
                 fontsize=22, fontweight='bold', y=0.98)
    
    # ==================== NETWORK GRAPH ====================
    ax_graph = plt.subplot(2, 3, (1, 4))
    
    G, nodes = create_example_network_graph()
    
    # Get owned nodes
    owned_nodes = {n for n, attrs in nodes.items() if attrs['owned']}
    unowned_nodes = set(G.nodes()) - owned_nodes
    
    # Get claimable edges
    claimable_edges = []
    for node in owned_nodes:
        for neighbor in G.neighbors(node):
            if neighbor not in owned_nodes:
                claimable_edges.append((node, neighbor))
    
    # Layout
    pos = nx.spring_layout(G, seed=42, k=1.5)
    
    # Draw nodes
    node_colors_owned = ['#4CAF50' if nodes[n]['owned'] else '#2196F3' for n in G.nodes()]
    node_sizes = [300 + nodes[n]['utility_qubits'] * 150 for n in G.nodes()]
    
    nx.draw_networkx_nodes(G, pos, node_color=node_colors_owned, 
                          node_size=node_sizes, ax=ax_graph, alpha=0.9,
                          edgecolors='black', linewidths=2)
    
    # Draw edges with different colors
    # Owned edges (both nodes owned)
    owned_edges = [(u, v) for u, v in G.edges() if u in owned_nodes and v in owned_nodes]
    nx.draw_networkx_edges(G, pos, edgelist=owned_edges, 
                          edge_color='#4CAF50', width=3, ax=ax_graph, alpha=0.8)
    
    # Claimable edges (one owned, one not)
    nx.draw_networkx_edges(G, pos, edgelist=claimable_edges, 
                          edge_color='#FF9800', width=4, ax=ax_graph, alpha=0.9,
                          style='dashed')
    
    # Unclaimable edges (both unowned)
    unclaimable_edges = [(u, v) for u, v in G.edges() 
                        if u not in owned_nodes and v not in owned_nodes]
    nx.draw_networkx_edges(G, pos, edgelist=unclaimable_edges, 
                          edge_color='#9E9E9E', width=1.5, ax=ax_graph, alpha=0.5)
    
    # Labels
    labels = {n: f"{n}\n({nodes[n]['utility_qubits']}Q)" for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold', ax=ax_graph)
    
    # Edge labels (difficulty)
    edge_labels = {(u, v): f"D{G[u][v]['difficulty']}" for u, v in G.edges()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=8, ax=ax_graph)
    
    ax_graph.set_title('Quantum Network Graph', fontsize=16, fontweight='bold', pad=20)
    ax_graph.axis('off')
    
    # Legend for graph
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4CAF50', 
                  markersize=15, label='Owned Nodes', markeredgecolor='black', markeredgewidth=2),
        plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#2196F3', 
                  markersize=15, label='Unowned Nodes', markeredgecolor='black', markeredgewidth=2),
        plt.Line2D([0], [0], color='#FF9800', linewidth=4, linestyle='--',
                  label='Claimable Edges', alpha=0.9),
        plt.Line2D([0], [0], color='#9E9E9E', linewidth=2, 
                  label='Unclaimable Edges', alpha=0.5),
        plt.Line2D([0], [0], color='#4CAF50', linewidth=3, 
                  label='Owned Edges', alpha=0.8),
    ]
    ax_graph.legend(handles=legend_elements, loc='upper left', fontsize=10, framealpha=0.9)
    
    # Add statistics box
    stats_text = f"""Network Statistics:
    
Total Nodes: {len(G.nodes())}
Owned Nodes: {len(owned_nodes)}
Unowned Nodes: {len(unowned_nodes)}

Total Edges: {len(G.edges())}
Claimable Edges: {len(claimable_edges)}
Owned Edges: {len(owned_edges)}
Unclaimable: {len(unclaimable_edges)}

Claimable Targets:
"""
    
    for u, v in claimable_edges[:5]:
        diff = G[u][v]['difficulty']
        thresh = G[u][v]['threshold']
        stats_text += f"  {u}→{v}: D{diff}, F≥{thresh:.2f}\n"
    
    if len(claimable_edges) > 5:
        stats_text += f"  ... +{len(claimable_edges)-5} more"
    
    ax_graph.text(0.02, 0.98, stats_text, transform=ax_graph.transAxes,
                 fontsize=9, verticalalignment='top', family='monospace',
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # ==================== DISTILLATION CIRCUITS ====================
    ax_bbpssw = plt.subplot(2, 3, 2)
    circuit_bbpssw, _ = create_bbpssw_circuit(3)
    circuit_bbpssw.draw('mpl', ax=ax_bbpssw, style='iqp', fold=-1)
    ax_bbpssw.set_title('BBPSSW Circuit (3 pairs)\nFor claiming edges', 
                       fontsize=13, fontweight='bold', pad=10)
    
    ax_dejmps = plt.subplot(2, 3, 3)
    circuit_dejmps, _ = create_dejmps_circuit(3)
    circuit_dejmps.draw('mpl', ax=ax_dejmps, style='iqp', fold=-1)
    ax_dejmps.set_title('DEJMPS Circuit (3 pairs)\nFor phase noise', 
                       fontsize=13, fontweight='bold', pad=10)
    
    # ==================== WORKFLOW DIAGRAM ====================
    ax_workflow = plt.subplot(2, 3, 5)
    ax_workflow.set_xlim(0, 10)
    ax_workflow.set_ylim(0, 10)
    ax_workflow.axis('off')
    ax_workflow.set_title('Game Workflow', fontsize=14, fontweight='bold', pad=15)
    
    # Workflow steps
    steps = [
        (5, 9, "1. Select Claimable Edge", '#FF9800'),
        (5, 7.5, "2. Check Difficulty & Threshold", '#2196F3'),
        (5, 6, "3. Design Distillation Circuit", '#9C27B0'),
        (5, 4.5, "4. Run Circuit & Measure", '#FF5722'),
        (5, 3, "5. Post-Select Results", '#FFC107'),
        (5, 1.5, "6. Claim Edge if F ≥ Threshold", '#4CAF50'),
    ]
    
    for x, y, text, color in steps:
        box = FancyBboxPatch((x-2, y-0.3), 4, 0.6,
                            boxstyle="round,pad=0.1",
                            edgecolor=color, facecolor=color,
                            linewidth=2, alpha=0.3)
        ax_workflow.add_patch(box)
        ax_workflow.text(x, y, text, ha='center', va='center',
                        fontsize=10, fontweight='bold')
        
        # Arrow to next step
        if y > 2:
            ax_workflow.annotate('', xy=(x, y-0.8), xytext=(x, y-0.4),
                               arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # ==================== RESULTS EXPLANATION ====================
    ax_results = plt.subplot(2, 3, 6)
    ax_results.axis('off')
    ax_results.set_title('Expected Results', fontsize=14, fontweight='bold', pad=15)
    
    results_text = """
CLAIMING AN EDGE:

Example: Claim edge A→C (Difficulty 3, Threshold 0.70)

Step 1: Prepare Circuit
  • Use 3 Bell pairs (6 qubits)
  • Choose BBPSSW (general noise)
  • Input fidelity ≈ 0.65

Step 2: Run Distillation
  • Execute circuit (1000 shots)
  • Measure all qubits
  • Get outcomes like:
    000000: 180 counts
    111111: 165 counts
    010101: 95 counts
    ... (other outcomes)

Step 3: Post-Selection
  • Keep only: ancilla qubits = 0
  • Success rate: ~45%
  • Successful shots: 450/1000

Step 4: Calculate Fidelity
  • From successful outcomes
  • Output fidelity: 0.87
  • F = 0.87 ≥ 0.70 ✓

Step 5: Claim Edge!
  • Edge A→C now owned
  • Node C becomes claimable
  • Score increases
  • New edges available

KEY METRICS:
  Input F:  0.65 (noisy)
  Output F: 0.87 (improved!)
  Success:  45% (good!)
  Result:   EDGE CLAIMED ✓
    """
    
    ax_results.text(0.05, 0.95, results_text, transform=ax_results.transAxes,
                   fontsize=9, verticalalignment='top', family='monospace',
                   bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.3))
    
    plt.tight_layout()
    return fig

def create_detailed_edge_claiming_diagram():
    """Create detailed diagram showing edge claiming process"""
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 14))
    fig.suptitle('Edge Claiming Process: Step-by-Step', 
                 fontsize=20, fontweight='bold')
    
    # Step 1: Before claiming
    ax1 = axes[0, 0]
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    ax1.set_title('BEFORE: Network State', fontsize=14, fontweight='bold')
    
    # Draw simple network
    node_a = plt.Circle((2, 5), 0.5, color='#4CAF50', ec='black', lw=2)
    node_c = plt.Circle((8, 5), 0.5, color='#2196F3', ec='black', lw=2)
    ax1.add_patch(node_a)
    ax1.add_patch(node_c)
    
    ax1.plot([2.5, 7.5], [5, 5], 'o--', color='#FF9800', linewidth=4, markersize=0)
    
    ax1.text(2, 5, 'A', ha='center', va='center', fontsize=16, fontweight='bold', color='white')
    ax1.text(8, 5, 'C', ha='center', va='center', fontsize=16, fontweight='bold', color='white')
    ax1.text(2, 3.5, 'OWNED', ha='center', fontsize=10, fontweight='bold', color='#4CAF50')
    ax1.text(8, 3.5, 'UNOWNED', ha='center', fontsize=10, fontweight='bold', color='#2196F3')
    ax1.text(5, 5.5, 'CLAIMABLE', ha='center', fontsize=11, fontweight='bold', color='#FF9800')
    ax1.text(5, 4.5, 'D3, F≥0.70', ha='center', fontsize=9, style='italic')
    
    # Step 2: Circuit execution
    ax2 = axes[0, 1]
    ax2.axis('off')
    ax2.set_title('DURING: Run Distillation', fontsize=14, fontweight='bold')
    
    circuit, _ = create_bbpssw_circuit(3)
    circuit.draw('mpl', ax=ax2, style='iqp', fold=-1)
    
    # Step 3: Results
    ax3 = axes[1, 0]
    ax3.set_title('RESULTS: Measurement Outcomes', fontsize=14, fontweight='bold')
    
    # Simulated measurement results
    outcomes = ['000000', '111111', '001100', '110011', '010101', '101010', '111000', '000111']
    counts = [180, 165, 95, 85, 75, 65, 45, 40]
    colors = ['green' if o in ['000000', '111111'] else 'lightblue' for o in outcomes]
    
    ax3.bar(range(len(outcomes)), counts, color=colors, alpha=0.7, edgecolor='black', linewidth=2)
    ax3.set_xlabel('Measurement Outcome', fontsize=12, fontweight='bold')
    ax3.set_ylabel('Counts (out of 1000 shots)', fontsize=12, fontweight='bold')
    ax3.set_xticks(range(len(outcomes)))
    ax3.set_xticklabels(outcomes, rotation=45, ha='right')
    ax3.grid(axis='y', alpha=0.3)
    
    # Add annotation
    ax3.text(0.5, 0.95, 'Post-select: Keep green outcomes\nOutput Fidelity: 0.87 ✓', 
            transform=ax3.transAxes, fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5),
            verticalalignment='top')
    
    # Step 4: After claiming
    ax4 = axes[1, 1]
    ax4.set_xlim(0, 10)
    ax4.set_ylim(0, 10)
    ax4.axis('off')
    ax4.set_title('AFTER: Edge Claimed!', fontsize=14, fontweight='bold')
    
    # Draw updated network
    node_a2 = plt.Circle((2, 5), 0.5, color='#4CAF50', ec='black', lw=2)
    node_c2 = plt.Circle((8, 5), 0.5, color='#4CAF50', ec='black', lw=2)
    ax4.add_patch(node_a2)
    ax4.add_patch(node_c2)
    
    ax4.plot([2.5, 7.5], [5, 5], '-', color='#4CAF50', linewidth=4)
    
    ax4.text(2, 5, 'A', ha='center', va='center', fontsize=16, fontweight='bold', color='white')
    ax4.text(8, 5, 'C', ha='center', va='center', fontsize=16, fontweight='bold', color='white')
    ax4.text(2, 3.5, 'OWNED', ha='center', fontsize=10, fontweight='bold', color='#4CAF50')
    ax4.text(8, 3.5, 'NOW OWNED!', ha='center', fontsize=10, fontweight='bold', color='#4CAF50')
    ax4.text(5, 5.5, 'OWNED EDGE', ha='center', fontsize=11, fontweight='bold', color='#4CAF50')
    
    # Success message
    ax4.text(5, 2, '✓ EDGE CLAIMED SUCCESSFULLY!\n+10 Points', 
            ha='center', fontsize=14, fontweight='bold', color='darkgreen',
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7, pad=0.5))
    
    plt.tight_layout()
    return fig

def main():
    print("="*80)
    print("GENERATING COMPLETE SYSTEM VISUALIZATION")
    print("="*80)
    
    output_dir = os.path.dirname(__file__)
    
    print("\n1. Creating complete system overview...")
    fig1 = visualize_complete_system()
    path1 = os.path.join(output_dir, 'complete_system_overview.png')
    fig1.savefig(path1, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {path1}")
    plt.close(fig1)
    
    print("\n2. Creating edge claiming process diagram...")
    fig2 = create_detailed_edge_claiming_diagram()
    path2 = os.path.join(output_dir, 'edge_claiming_process.png')
    fig2.savefig(path2, dpi=300, bbox_inches='tight')
    print(f"   ✓ Saved: {path2}")
    plt.close(fig2)
    
    print("\n" + "="*80)
    print("SYSTEM COMPONENTS EXPLAINED")
    print("="*80)
    
    print("""
1. NETWORK GRAPH:
   • Green nodes: Owned by you
   • Blue nodes: Unowned (not yet claimed)
   • Orange dashed edges: CLAIMABLE (adjacent to your nodes)
   • Gray edges: Unclaimable (no owned nodes nearby)
   • Green solid edges: Owned (both nodes owned)

2. CLAIMABLE vs UNCLAIMABLE:
   • CLAIMABLE: At least one endpoint is owned
     Example: You own A, edge A→C is claimable
   • UNCLAIMABLE: Neither endpoint is owned
     Example: You don't own D or G, edge D→G is unclaimable
   
3. EDGE PROPERTIES:
   • Difficulty (D): How hard to claim (2-6)
   • Threshold (F): Minimum fidelity required (0.65-0.85)
   • Higher difficulty → need more Bell pairs

4. CLAIMING PROCESS:
   Step 1: Pick a claimable edge (orange)
   Step 2: Design distillation circuit
   Step 3: Run circuit and measure
   Step 4: Post-select successful outcomes
   Step 5: Calculate output fidelity
   Step 6: If F ≥ threshold → CLAIM EDGE!

5. AFTER CLAIMING:
   • Edge becomes owned (green)
   • Target node becomes owned (green)
   • New edges become claimable (orange)
   • Your network expands!
    """)
    
    print("="*80)
    print("✓ COMPLETE SYSTEM VISUALIZATION GENERATED")
    print("="*80)
    print("\nGenerated files:")
    print("  1. complete_system_overview.png - Full system with graph + circuits")
    print("  2. edge_claiming_process.png - Step-by-step claiming process")
    print("\nThese show the complete quantum network game system!")

if __name__ == "__main__":
    main()
