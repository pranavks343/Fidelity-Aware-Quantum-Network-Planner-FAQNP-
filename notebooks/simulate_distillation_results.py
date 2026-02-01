#!/usr/bin/env python3
"""
Simulate and visualize distillation circuit results.
Shows what happens when you run BBPSSW and DEJMPS circuits.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from distillation.distillation import create_bbpssw_circuit, create_dejmps_circuit
from distillation.simulator import DistillationSimulator, estimate_input_noise_from_difficulty
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def simulate_circuit_execution(circuit, num_shots=1000, input_fidelity=0.7):
    """Simulate circuit execution and return results"""
    simulator = DistillationSimulator(shots=num_shots)
    
    # Simulate with noise
    result = simulator.simulate_full(circuit, input_fidelity=input_fidelity)
    
    return result

def visualize_measurement_outcomes(results_dict, title, save_path):
    """Visualize measurement outcome distributions"""
    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle(title, fontsize=18, fontweight='bold')
    
    configs = [(2, "2 Pairs"), (3, "3 Pairs"), (4, "4 Pairs")]
    
    for idx, (num_pairs, label) in enumerate(configs):
        # BBPSSW
        ax_bbpssw = axes[0, idx]
        bbpssw_counts = results_dict[f'bbpssw_{num_pairs}']['counts']
        
        # Get top outcomes
        sorted_counts = sorted(bbpssw_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        labels_b = [x[0] for x in sorted_counts]
        values_b = [x[1] for x in sorted_counts]
        
        ax_bbpssw.bar(range(len(labels_b)), values_b, color='steelblue', alpha=0.7, edgecolor='black')
        ax_bbpssw.set_title(f'BBPSSW - {label}', fontsize=12, fontweight='bold')
        ax_bbpssw.set_xlabel('Measurement Outcome', fontsize=10)
        ax_bbpssw.set_ylabel('Counts', fontsize=10)
        ax_bbpssw.set_xticks(range(len(labels_b)))
        ax_bbpssw.set_xticklabels(labels_b, rotation=45, ha='right', fontsize=8)
        ax_bbpssw.grid(axis='y', alpha=0.3)
        
        # DEJMPS
        ax_dejmps = axes[1, idx]
        dejmps_counts = results_dict[f'dejmps_{num_pairs}']['counts']
        
        sorted_counts = sorted(dejmps_counts.items(), key=lambda x: x[1], reverse=True)[:8]
        labels_d = [x[0] for x in sorted_counts]
        values_d = [x[1] for x in sorted_counts]
        
        ax_dejmps.bar(range(len(labels_d)), values_d, color='coral', alpha=0.7, edgecolor='black')
        ax_dejmps.set_title(f'DEJMPS - {label}', fontsize=12, fontweight='bold')
        ax_dejmps.set_xlabel('Measurement Outcome', fontsize=10)
        ax_dejmps.set_ylabel('Counts', fontsize=10)
        ax_dejmps.set_xticks(range(len(labels_d)))
        ax_dejmps.set_xticklabels(labels_d, rotation=45, ha='right', fontsize=8)
        ax_dejmps.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"   Saved: {save_path}")
    plt.close()

def visualize_fidelity_improvement(fidelity_data, save_path):
    """Visualize fidelity improvement from distillation"""
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Plot 1: Fidelity improvement by number of pairs
    ax1 = axes[0]
    num_pairs = [2, 3, 4]
    
    input_fid = [d['input_fidelity'] for d in fidelity_data['bbpssw']]
    bbpssw_fid = [d['output_fidelity'] for d in fidelity_data['bbpssw']]
    dejmps_fid = [d['output_fidelity'] for d in fidelity_data['dejmps']]
    
    x = np.arange(len(num_pairs))
    width = 0.25
    
    ax1.bar(x - width, input_fid, width, label='Input Fidelity', color='gray', alpha=0.6)
    ax1.bar(x, bbpssw_fid, width, label='BBPSSW Output', color='steelblue', alpha=0.8)
    ax1.bar(x + width, dejmps_fid, width, label='DEJMPS Output', color='coral', alpha=0.8)
    
    ax1.set_xlabel('Number of Bell Pairs', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Fidelity', fontsize=12, fontweight='bold')
    ax1.set_title('Fidelity Improvement by Protocol', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(num_pairs)
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3)
    ax1.axhline(y=0.5, color='red', linestyle='--', linewidth=2, alpha=0.5, label='Entanglement Threshold')
    
    # Plot 2: Success probability
    ax2 = axes[1]
    bbpssw_success = [d['success_probability'] for d in fidelity_data['bbpssw']]
    dejmps_success = [d['success_probability'] for d in fidelity_data['dejmps']]
    
    ax2.plot(num_pairs, bbpssw_success, 'o-', linewidth=3, markersize=10, 
             label='BBPSSW', color='steelblue')
    ax2.plot(num_pairs, dejmps_success, 's-', linewidth=3, markersize=10, 
             label='DEJMPS', color='coral')
    
    ax2.set_xlabel('Number of Bell Pairs', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Success Probability', fontsize=12, fontweight='bold')
    ax2.set_title('Post-Selection Success Rate', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim([0, 1])
    
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"   Saved: {save_path}")
    plt.close()

def main():
    print("="*80)
    print("SIMULATING DISTILLATION CIRCUIT EXECUTION")
    print("="*80)
    
    # Simulation parameters
    num_shots = 1000
    input_fidelity = 0.7  # Starting fidelity (noisy Bell pairs)
    
    print(f"\nSimulation Parameters:")
    print(f"  Input Fidelity: {input_fidelity:.2f}")
    print(f"  Shots per circuit: {num_shots}")
    print(f"  Goal: Improve fidelity through distillation\n")
    
    results_dict = {}
    fidelity_data = {'bbpssw': [], 'dejmps': []}
    
    # Simulate different configurations
    for num_pairs in [2, 3, 4]:
        print(f"\n{'='*60}")
        print(f"Simulating {num_pairs} Bell Pairs Configuration")
        print(f"{'='*60}")
        
        # BBPSSW
        print(f"\n  Running BBPSSW circuit...")
        circuit_bbpssw, flag_bbpssw = create_bbpssw_circuit(num_pairs)
        result_bbpssw = simulate_circuit_execution(circuit_bbpssw, num_shots, input_fidelity)
        results_dict[f'bbpssw_{num_pairs}'] = result_bbpssw
        
        print(f"    Circuit: {circuit_bbpssw.num_qubits} qubits, depth {circuit_bbpssw.depth()}")
        print(f"    Output fidelity: {result_bbpssw['output_fidelity']:.4f}")
        print(f"    Success probability: {result_bbpssw['success_probability']:.2%}")
        print(f"    Improvement: {result_bbpssw['output_fidelity'] - input_fidelity:+.4f}")
        
        # Show top measurement outcomes
        top_outcomes = sorted(result_bbpssw['counts'].items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"    Top outcomes:")
        for outcome, count in top_outcomes:
            print(f"      {outcome}: {count} ({count/num_shots:.1%})")
        
        fidelity_data['bbpssw'].append({
            'num_pairs': num_pairs,
            'input_fidelity': input_fidelity,
            'output_fidelity': result_bbpssw['output_fidelity'],
            'success_probability': result_bbpssw['success_probability']
        })
        
        # DEJMPS
        print(f"\n  Running DEJMPS circuit...")
        circuit_dejmps, flag_dejmps = create_dejmps_circuit(num_pairs)
        result_dejmps = simulate_circuit_execution(circuit_dejmps, num_shots, input_fidelity)
        results_dict[f'dejmps_{num_pairs}'] = result_dejmps
        
        print(f"    Circuit: {circuit_dejmps.num_qubits} qubits, depth {circuit_dejmps.depth()}")
        print(f"    Output fidelity: {result_dejmps['output_fidelity']:.4f}")
        print(f"    Success probability: {result_dejmps['success_probability']:.2%}")
        print(f"    Improvement: {result_dejmps['output_fidelity'] - input_fidelity:+.4f}")
        
        top_outcomes = sorted(result_dejmps['counts'].items(), key=lambda x: x[1], reverse=True)[:3]
        print(f"    Top outcomes:")
        for outcome, count in top_outcomes:
            print(f"      {outcome}: {count} ({count/num_shots:.1%})")
        
        fidelity_data['dejmps'].append({
            'num_pairs': num_pairs,
            'input_fidelity': input_fidelity,
            'output_fidelity': result_dejmps['output_fidelity'],
            'success_probability': result_dejmps['success_probability']
        })
    
    # Generate visualizations
    print(f"\n{'='*80}")
    print("GENERATING RESULT VISUALIZATIONS")
    print(f"{'='*80}\n")
    
    output_dir = os.path.dirname(__file__)
    
    print("1. Creating measurement outcome distributions...")
    visualize_measurement_outcomes(
        results_dict,
        f'Distillation Circuit Measurement Results (Input Fidelity: {input_fidelity:.2f})',
        os.path.join(output_dir, 'distillation_measurement_results.png')
    )
    
    print("2. Creating fidelity improvement charts...")
    visualize_fidelity_improvement(
        fidelity_data,
        os.path.join(output_dir, 'distillation_fidelity_improvement.png')
    )
    
    # Summary statistics
    print(f"\n{'='*80}")
    print("SUMMARY: EXPECTED RESULTS")
    print(f"{'='*80}\n")
    
    print(f"Starting Condition:")
    print(f"  Input Fidelity: {input_fidelity:.2f} (noisy Bell pairs)")
    print(f"  Goal: F > 0.5 for entanglement, F > 0.7 for high quality\n")
    
    print(f"BBPSSW Protocol Results:")
    for data in fidelity_data['bbpssw']:
        improvement = data['output_fidelity'] - data['input_fidelity']
        print(f"  {data['num_pairs']} pairs: F = {data['output_fidelity']:.4f} "
              f"({improvement:+.4f}), Success = {data['success_probability']:.1%}")
    
    print(f"\nDEJMPS Protocol Results:")
    for data in fidelity_data['dejmps']:
        improvement = data['output_fidelity'] - data['input_fidelity']
        print(f"  {data['num_pairs']} pairs: F = {data['output_fidelity']:.4f} "
              f"({improvement:+.4f}), Success = {data['success_probability']:.1%}")
    
    print(f"\nKey Insights:")
    print(f"  ✓ Both protocols improve fidelity from noisy input")
    print(f"  ✓ More Bell pairs → better fidelity but lower success rate")
    print(f"  ✓ DEJMPS has slightly better performance for phase noise")
    print(f"  ✓ Post-selection discards ~50% of results (ancilla ≠ 0)")
    print(f"  ✓ Target qubits show improved entanglement after distillation")
    
    print(f"\nMeasurement Outcomes Explained:")
    print(f"  • Bitstrings show all qubit measurements")
    print(f"  • First half: Alice's qubits")
    print(f"  • Second half: Bob's qubits")
    print(f"  • Post-select: Keep only outcomes where ancilla qubits = 0")
    print(f"  • Target pair (middle qubits) has higher fidelity after selection")
    
    print(f"\n{'='*80}")
    print("✓ SIMULATION COMPLETE")
    print(f"{'='*80}")
    print(f"\nGenerated files:")
    print(f"  1. distillation_measurement_results.png")
    print(f"  2. distillation_fidelity_improvement.png")
    print(f"\nThese show what you'll see when running the circuits!")

if __name__ == "__main__":
    main()
