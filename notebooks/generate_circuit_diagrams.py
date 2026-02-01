#!/usr/bin/env python3
"""
Standalone script to generate circuit diagrams.
Run this directly without Jupyter: python3 generate_circuit_diagrams.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from distillation.distillation import create_bbpssw_circuit, create_dejmps_circuit
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    HAS_DEPS = True
except ImportError as e:
    HAS_DEPS = False
    print(f"Missing dependency: {e}")
    print("\nPlease install required packages:")
    print("  pip3 install --user qiskit qiskit-aer matplotlib")
    sys.exit(1)

def main():
    print("="*80)
    print("GENERATING ENTANGLEMENT DISTILLATION CIRCUIT DIAGRAMS")
    print("="*80)
    
    output_dir = os.path.dirname(__file__)
    
    # Configuration
    configs = [(2, "Minimum"), (3, "Standard"), (4, "Enhanced")]
    
    # Generate BBPSSW circuits
    print("\n1. Generating BBPSSW circuits...")
    fig, axes = plt.subplots(3, 1, figsize=(18, 16))
    
    for idx, (num_pairs, label) in enumerate(configs):
        circuit, flag_bit = create_bbpssw_circuit(num_pairs)
        circuit.draw('mpl', ax=axes[idx], style='iqp', fold=-1)
        axes[idx].set_title(
            f'BBPSSW - {label} ({num_pairs} Bell Pairs)\n'
            f'Qubits: {circuit.num_qubits}, Depth: {circuit.depth()}, '
            f'Gates: {sum(circuit.count_ops().values())}, Flag: {flag_bit}',
            fontsize=14, fontweight='bold', pad=15
        )
        print(f"   ✓ {label}: {circuit.num_qubits} qubits, depth {circuit.depth()}")
    
    plt.tight_layout()
    path1 = os.path.join(output_dir, 'bbpssw_circuits.png')
    plt.savefig(path1, dpi=300, bbox_inches='tight')
    print(f"   Saved: {path1}")
    plt.close()
    
    # Generate DEJMPS circuits
    print("\n2. Generating DEJMPS circuits...")
    fig, axes = plt.subplots(3, 1, figsize=(18, 16))
    
    for idx, (num_pairs, label) in enumerate(configs):
        circuit, flag_bit = create_dejmps_circuit(num_pairs)
        circuit.draw('mpl', ax=axes[idx], style='iqp', fold=-1)
        axes[idx].set_title(
            f'DEJMPS - {label} ({num_pairs} Bell Pairs)\n'
            f'Qubits: {circuit.num_qubits}, Depth: {circuit.depth()}, '
            f'Gates: {sum(circuit.count_ops().values())}, Flag: {flag_bit}',
            fontsize=14, fontweight='bold', pad=15
        )
        print(f"   ✓ {label}: {circuit.num_qubits} qubits, depth {circuit.depth()}")
    
    plt.tight_layout()
    path2 = os.path.join(output_dir, 'dejmps_circuits.png')
    plt.savefig(path2, dpi=300, bbox_inches='tight')
    print(f"   Saved: {path2}")
    plt.close()
    
    # Generate comparison
    print("\n3. Generating side-by-side comparison...")
    fig, axes = plt.subplots(1, 2, figsize=(20, 8))
    
    circuit_bbpssw, _ = create_bbpssw_circuit(3)
    circuit_dejmps, _ = create_dejmps_circuit(3)
    
    circuit_bbpssw.draw('mpl', ax=axes[0], style='iqp', fold=-1)
    axes[0].set_title(
        f'BBPSSW Protocol\nDepth: {circuit_bbpssw.depth()}, Gates: {sum(circuit_bbpssw.count_ops().values())}',
        fontsize=14, fontweight='bold', color='steelblue'
    )
    
    circuit_dejmps.draw('mpl', ax=axes[1], style='iqp', fold=-1)
    axes[1].set_title(
        f'DEJMPS Protocol\nDepth: {circuit_dejmps.depth()}, Gates: {sum(circuit_dejmps.count_ops().values())}',
        fontsize=14, fontweight='bold', color='coral'
    )
    
    plt.tight_layout()
    path3 = os.path.join(output_dir, 'protocol_comparison.png')
    plt.savefig(path3, dpi=300, bbox_inches='tight')
    print(f"   Saved: {path3}")
    plt.close()
    
    # Print summary
    print("\n" + "="*80)
    print("CIRCUIT ANALYSIS SUMMARY")
    print("="*80)
    
    for num_pairs in [2, 3, 4]:
        print(f"\n{num_pairs} Bell Pairs Configuration:")
        
        c_bbpssw, f_bbpssw = create_bbpssw_circuit(num_pairs)
        c_dejmps, f_dejmps = create_dejmps_circuit(num_pairs)
        
        print(f"  BBPSSW: {c_bbpssw.num_qubits} qubits, depth {c_bbpssw.depth()}, {sum(c_bbpssw.count_ops().values())} gates")
        print(f"          Gates: {dict(c_bbpssw.count_ops())}")
        
        print(f"  DEJMPS: {c_dejmps.num_qubits} qubits, depth {c_dejmps.depth()}, {sum(c_dejmps.count_ops().values())} gates")
        print(f"          Gates: {dict(c_dejmps.count_ops())}")
        
        print(f"  Difference: +{c_dejmps.depth() - c_bbpssw.depth()} depth, +{sum(c_dejmps.count_ops().values()) - sum(c_bbpssw.count_ops().values())} gates (DEJMPS)")
    
    print("\n" + "="*80)
    print("✓ ALL CIRCUIT DIAGRAMS GENERATED SUCCESSFULLY")
    print("="*80)
    print("\nGenerated files:")
    print(f"  1. {path1}")
    print(f"  2. {path2}")
    print(f"  3. {path3}")
    print("\nThese show the EXACT circuits from your implementation!")

if __name__ == "__main__":
    main()
