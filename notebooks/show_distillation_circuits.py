#!/usr/bin/env python3
"""
Generate and display the EXACT entanglement distillation circuits used in the project.
Shows BBPSSW and DEJMPS protocols with detailed circuit diagrams.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from distillation.distillation import create_bbpssw_circuit, create_dejmps_circuit
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

# Configure matplotlib
plt.rcParams['figure.figsize'] = (20, 14)
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def create_protocol_comparison_diagram():
    """Create a comparison diagram of BBPSSW vs DEJMPS"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis('off')
    
    # Title
    ax.text(5, 11.5, 'Entanglement Distillation Protocols Comparison', 
            ha='center', va='center', fontsize=20, fontweight='bold')
    
    # BBPSSW Section
    bbpssw_y = 9
    ax.text(5, bbpssw_y + 0.8, 'BBPSSW Protocol', 
            ha='center', va='center', fontsize=16, fontweight='bold', color='steelblue')
    
    bbpssw_box = FancyBboxPatch((0.5, bbpssw_y - 1.5), 9, 2, 
                                boxstyle="round,pad=0.15", 
                                edgecolor='steelblue', facecolor='lightblue', 
                                linewidth=3, alpha=0.3)
    ax.add_patch(bbpssw_box)
    
    bbpssw_text = """
    Bennett-Brassard-Popescu-Schumacher-Smolin-Wootters Protocol
    
    • Target: Depolarizing noise
    • Method: Bilateral CNOT gates between target and ancilla pairs
    • Detection: Measures ancillas to detect errors
    • Success: Post-select on ancilla measurements = 0
    
    Key Features:
    ✓ Robust for general noise
    ✓ Simple implementation
    ✓ Works well for depolarizing channels
    ✓ Success probability ~50% for 2 pairs
    
    Circuit Structure:
    1. Target pair: (N-1, N) - middle qubits
    2. Ancilla pairs: All other pairs
    3. Apply CNOT: target → each ancilla (Alice & Bob sides)
    4. Measure ancillas
    5. Keep if all ancilla measurements = 0
    """
    
    ax.text(5, bbpssw_y - 0.3, bbpssw_text, ha='center', va='center', 
            fontsize=9, family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # DEJMPS Section
    dejmps_y = 4.5
    ax.text(5, dejmps_y + 0.8, 'DEJMPS Protocol', 
            ha='center', va='center', fontsize=16, fontweight='bold', color='coral')
    
    dejmps_box = FancyBboxPatch((0.5, dejmps_y - 1.5), 9, 2, 
                                boxstyle="round,pad=0.15", 
                                edgecolor='coral', facecolor='lightyellow', 
                                linewidth=3, alpha=0.3)
    ax.add_patch(dejmps_box)
    
    dejmps_text = """
    Deutsch-Ekert-Jozsa-Macchiavello-Popescu-Sanpera Protocol
    
    • Target: Phase noise (Z errors)
    • Method: Parity checks in both X and Z bases
    • Detection: Dual-basis error detection
    • Success: Post-select on parity check results
    
    Key Features:
    ✓ Optimized for phase-damping channels
    ✓ Better success probability than BBPSSW for phase noise
    ✓ Uses Hadamard gates for basis changes
    ✓ Detects both bit-flip and phase-flip errors
    
    Circuit Structure:
    1. Z-basis parity check (CNOT gates)
    2. Change to X-basis (Hadamard gates)
    3. X-basis parity check (CNOT in X-basis)
    4. Return to computational basis
    5. Measure ancillas and post-select
    """
    
    ax.text(5, dejmps_y - 0.3, dejmps_text, ha='center', va='center', 
            fontsize=9, family='monospace',
            bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    # Comparison table
    table_y = 0.8
    ax.text(5, table_y + 0.5, 'Quick Comparison', 
            ha='center', va='center', fontsize=14, fontweight='bold')
    
    comparison_text = """
    Property          │ BBPSSW                    │ DEJMPS
    ──────────────────┼───────────────────────────┼────────────────────────────
    Best for          │ Depolarizing noise        │ Phase noise (Z errors)
    Gate complexity   │ Lower (CNOT only)         │ Higher (CNOT + H)
    Success rate      │ ~50% (2 pairs)            │ ~60% (2 pairs, phase noise)
    Fidelity gain     │ F² / (F² + (1-F)²)        │ Better for phase errors
    Implementation    │ Simpler                   │ More complex
    """
    
    ax.text(5, table_y - 0.5, comparison_text, ha='center', va='center', 
            fontsize=8, family='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.6, 
                     edgecolor='black', linewidth=2))
    
    plt.tight_layout()
    return fig

def main():
    """Generate all circuit visualizations"""
    
    print("="*80)
    print("ENTANGLEMENT DISTILLATION CIRCUIT VISUALIZATION")
    print("="*80)
    print("\nGenerating actual circuits from your codebase...\n")
    
    # Test different numbers of Bell pairs
    test_configs = [
        (2, "Minimum (2 pairs)"),
        (3, "Standard (3 pairs)"),
        (4, "Enhanced (4 pairs)")
    ]
    
    # Create main figure
    fig = plt.figure(figsize=(20, 16))
    fig.suptitle('Entanglement Distillation Circuits - Actual Implementation', 
                 fontsize=22, fontweight='bold', y=0.98)
    
    # BBPSSW Circuits
    for idx, (num_pairs, label) in enumerate(test_configs):
        print(f"Creating BBPSSW circuit: {label}...")
        circuit, flag_bit = create_bbpssw_circuit(num_pairs)
        
        ax = plt.subplot(3, 2, idx*2 + 1)
        circuit.draw('mpl', ax=ax, style='iqp', fold=-1)
        ax.set_title(f'BBPSSW - {label}\n{circuit.num_qubits} qubits, depth {circuit.depth()}, flag bit: {flag_bit}', 
                    fontsize=12, fontweight='bold', pad=15)
        
        print(f"  ✓ Qubits: {circuit.num_qubits}, Depth: {circuit.depth()}, Gates: {sum(circuit.count_ops().values())}")
    
    # DEJMPS Circuits
    for idx, (num_pairs, label) in enumerate(test_configs):
        print(f"Creating DEJMPS circuit: {label}...")
        circuit, flag_bit = create_dejmps_circuit(num_pairs)
        
        ax = plt.subplot(3, 2, idx*2 + 2)
        circuit.draw('mpl', ax=ax, style='iqp', fold=-1)
        ax.set_title(f'DEJMPS - {label}\n{circuit.num_qubits} qubits, depth {circuit.depth()}, flag bit: {flag_bit}', 
                    fontsize=12, fontweight='bold', pad=15)
        
        print(f"  ✓ Qubits: {circuit.num_qubits}, Depth: {circuit.depth()}, Gates: {sum(circuit.count_ops().values())}")
    
    plt.tight_layout()
    output_path = os.path.join(os.path.dirname(__file__), 'distillation_circuits_actual.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n✓ Saved: {output_path}")
    
    # Create protocol comparison
    print("\nCreating protocol comparison diagram...")
    fig2 = create_protocol_comparison_diagram()
    output_path2 = os.path.join(os.path.dirname(__file__), 'protocol_comparison.png')
    fig2.savefig(output_path2, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path2}")
    
    # Create detailed circuit analysis
    print("\n" + "="*80)
    print("DETAILED CIRCUIT ANALYSIS")
    print("="*80)
    
    for num_pairs in [2, 3, 4]:
        print(f"\n{'='*40}")
        print(f"Configuration: {num_pairs} Bell Pairs")
        print(f"{'='*40}")
        
        # BBPSSW
        circuit_bbpssw, flag_bbpssw = create_bbpssw_circuit(num_pairs)
        print(f"\nBBPSSW Circuit:")
        print(f"  Total qubits: {circuit_bbpssw.num_qubits}")
        print(f"  Circuit depth: {circuit_bbpssw.depth()}")
        print(f"  Gate counts: {dict(circuit_bbpssw.count_ops())}")
        print(f"  Total gates: {sum(circuit_bbpssw.count_ops().values())}")
        print(f"  Flag bit: {flag_bbpssw}")
        print(f"  Target pair: (q{num_pairs-1}, q{num_pairs})")
        print(f"  Ancilla pairs: {num_pairs - 1} pairs")
        
        # DEJMPS
        circuit_dejmps, flag_dejmps = create_dejmps_circuit(num_pairs)
        print(f"\nDEJMPS Circuit:")
        print(f"  Total qubits: {circuit_dejmps.num_qubits}")
        print(f"  Circuit depth: {circuit_dejmps.depth()}")
        print(f"  Gate counts: {dict(circuit_dejmps.count_ops())}")
        print(f"  Total gates: {sum(circuit_dejmps.count_ops().values())}")
        print(f"  Flag bit: {flag_dejmps}")
        print(f"  Target pair: (q{num_pairs-1}, q{num_pairs})")
        print(f"  Ancilla pairs: {num_pairs - 1} pairs")
        
        # Comparison
        print(f"\nComparison:")
        print(f"  Depth difference: {circuit_dejmps.depth() - circuit_bbpssw.depth()} (DEJMPS - BBPSSW)")
        print(f"  Gate count difference: {sum(circuit_dejmps.count_ops().values()) - sum(circuit_bbpssw.count_ops().values())}")
    
    print("\n" + "="*80)
    print("QUBIT LAYOUT CONVENTION")
    print("="*80)
    print("""
For N Bell pairs (2N total qubits):
  • Alice's qubits: 0, 1, 2, ..., N-1
  • Bob's qubits: N, N+1, ..., 2N-1
  • Bell pair k: (qubit k, qubit 2N-1-k)
  • Target pair: (N-1, N) - the middle pair
  • Ancilla pairs: All other pairs

Example with 3 Bell pairs (6 qubits):
  • Alice: q0, q1, q2
  • Bob: q3, q4, q5
  • Pair 0: (q0, q5) - ancilla
  • Pair 1: (q1, q4) - ancilla
  • Pair 2: (q2, q3) - TARGET
    """)
    
    print("\n" + "="*80)
    print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
    print("="*80)
    print("\nGenerated files:")
    print("  1. distillation_circuits_actual.png - Complete circuit diagrams")
    print("  2. protocol_comparison.png - Protocol comparison chart")
    print("\nThese are the EXACT circuits used in your implementation!")
    
    plt.show()

if __name__ == "__main__":
    main()
