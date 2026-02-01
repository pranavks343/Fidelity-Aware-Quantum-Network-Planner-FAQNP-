"""
Visualize Entanglement Distillation Circuits - Simple Version
Creates conceptual diagrams without requiring qiskit installation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrow, Rectangle
import numpy as np

# Configure matplotlib
plt.rcParams['figure.figsize'] = (18, 14)
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def draw_qubit_line(ax, y, label, color='black'):
    """Draw a horizontal qubit line"""
    ax.plot([0, 10], [y, y], color=color, linewidth=2)
    ax.text(-0.5, y, label, ha='right', va='center', fontsize=12, fontweight='bold')

def draw_gate(ax, x, y, gate_type, label='', color='lightblue'):
    """Draw a quantum gate"""
    if gate_type == 'H':
        rect = Rectangle((x-0.2, y-0.2), 0.4, 0.4, 
                        facecolor=color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x, y, 'H', ha='center', va='center', fontsize=10, fontweight='bold')
    elif gate_type == 'X':
        circle = Circle((x, y), 0.15, facecolor='white', edgecolor='black', linewidth=2)
        ax.add_patch(circle)
        ax.plot([x-0.1, x+0.1], [y-0.1, y+0.1], 'k-', linewidth=2)
        ax.plot([x-0.1, x+0.1], [y+0.1, y-0.1], 'k-', linewidth=2)
    elif gate_type == 'measure':
        rect = Rectangle((x-0.25, y-0.2), 0.5, 0.4, 
                        facecolor='lightyellow', edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        # Draw measurement symbol (arc)
        theta = np.linspace(0, np.pi, 20)
        r = 0.15
        mx = x + r * np.cos(theta)
        my = y - 0.1 + r * np.sin(theta)
        ax.plot(mx, my, 'k-', linewidth=1.5)
        ax.plot([x, x+0.1], [y-0.1, y+0.1], 'k-', linewidth=1.5)

def draw_cnot(ax, x, control_y, target_y, color='black'):
    """Draw a CNOT gate"""
    # Control dot
    circle = Circle((x, control_y), 0.1, facecolor='black', edgecolor='black')
    ax.add_patch(circle)
    
    # Target X
    circle = Circle((x, target_y), 0.15, facecolor='white', edgecolor=color, linewidth=2)
    ax.add_patch(circle)
    ax.plot([x-0.1, x+0.1], [target_y, target_y], color=color, linewidth=2)
    ax.plot([x, x], [target_y-0.1, target_y+0.1], color=color, linewidth=2)
    
    # Connecting line
    ax.plot([x, x], [min(control_y, target_y), max(control_y, target_y)], 
            color=color, linewidth=2)

def draw_barrier(ax, x, y_positions):
    """Draw a barrier line"""
    for i in range(len(y_positions)-1):
        ax.plot([x, x], [y_positions[i], y_positions[i+1]], 
                'k--', linewidth=1.5, alpha=0.5)

def create_bbpssw_circuit_diagram():
    """Create BBPSSW circuit diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(16, 8))
    ax.set_xlim(-1, 11)
    ax.set_ylim(-0.5, 4.5)
    ax.axis('off')
    
    # Title
    ax.text(5, 4.2, 'BBPSSW Entanglement Distillation Circuit', 
            ha='center', va='center', fontsize=16, fontweight='bold')
    
    # Qubit lines
    qubit_ys = [3, 2.5, 1.5, 1]
    qubit_labels = ['q₀ (target)', 'q₁ (target)', 'q₂ (ancilla)', 'q₃ (ancilla)']
    colors = ['steelblue', 'steelblue', 'coral', 'coral']
    
    for y, label, color in zip(qubit_ys, qubit_labels, colors):
        draw_qubit_line(ax, y, label, color=color)
    
    # Bell pair 0: H on q0, CNOT q0->q1
    x = 1
    draw_gate(ax, x, qubit_ys[0], 'H', color='lightblue')
    draw_cnot(ax, x+0.5, qubit_ys[0], qubit_ys[1], color='steelblue')
    
    # Bell pair 1: H on q2, CNOT q2->q3
    draw_gate(ax, x, qubit_ys[2], 'H', color='lightyellow')
    draw_cnot(ax, x+0.5, qubit_ys[2], qubit_ys[3], color='coral')
    
    # Barrier
    x = 2.5
    draw_barrier(ax, x, qubit_ys)
    ax.text(x, 3.8, 'Bell Pairs Prepared', ha='center', fontsize=9, style='italic')
    
    # Bilateral CNOT: q0->q2
    x = 4
    draw_cnot(ax, x, qubit_ys[0], qubit_ys[2], color='purple')
    ax.text(x, 3.8, 'Bilateral', ha='center', fontsize=9, fontweight='bold', color='purple')
    
    # Bilateral CNOT: q1->q3
    x = 5
    draw_cnot(ax, x, qubit_ys[1], qubit_ys[3], color='purple')
    ax.text(x, 3.8, 'CNOT', ha='center', fontsize=9, fontweight='bold', color='purple')
    
    # Barrier
    x = 6.5
    draw_barrier(ax, x, qubit_ys)
    ax.text(x, 3.8, 'Entanglement', ha='center', fontsize=9, style='italic')
    
    # Measure ancilla qubits
    x = 8
    draw_gate(ax, x, qubit_ys[2], 'measure')
    draw_gate(ax, x, qubit_ys[3], 'measure')
    ax.text(x, 0.3, 'Ancilla', ha='center', fontsize=9, fontweight='bold', color='green')
    ax.text(x, 0, 'Measurement', ha='center', fontsize=9, fontweight='bold', color='green')
    
    # Measure target qubits
    x = 9.5
    draw_gate(ax, x, qubit_ys[0], 'measure')
    draw_gate(ax, x, qubit_ys[1], 'measure')
    ax.text(x, 3.8, 'Target', ha='center', fontsize=9, fontweight='bold', color='steelblue')
    ax.text(x, 3.5, 'Measurement', ha='center', fontsize=9, fontweight='bold', color='steelblue')
    
    # Add annotations
    annotation_y = -0.2
    ax.text(1.25, annotation_y, '① Prepare\nBell Pairs', ha='center', fontsize=8, 
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    ax.text(4.5, annotation_y, '② Bilateral CNOT\n(Entangle pairs)', ha='center', fontsize=8,
            bbox=dict(boxstyle='round', facecolor='lavender', alpha=0.5))
    ax.text(8, annotation_y, '③ Measure\nAncilla', ha='center', fontsize=8,
            bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
    ax.text(9.5, annotation_y, '④ Measure\nTarget', ha='center', fontsize=8,
            bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.5))
    
    plt.tight_layout()
    return fig

def create_fidelity_measurement_diagrams():
    """Create diagrams for ZZ, XX, YY measurements"""
    fig, axes = plt.subplots(3, 1, figsize=(16, 12))
    
    measurements = [
        ('ZZ Measurement (Computational Basis)', 'No basis rotation', None),
        ('XX Measurement (X Basis)', 'Apply H to target qubits', 'H'),
        ('YY Measurement (Y Basis)', 'Apply S†H to target qubits', 'S†H')
    ]
    
    for idx, (title, subtitle, rotation) in enumerate(measurements):
        ax = axes[idx]
        ax.set_xlim(-1, 11)
        ax.set_ylim(-0.5, 4.5)
        ax.axis('off')
        
        # Title
        ax.text(5, 4.2, title, ha='center', va='center', fontsize=14, fontweight='bold')
        ax.text(5, 3.9, subtitle, ha='center', va='center', fontsize=10, style='italic')
        
        # Qubit lines
        qubit_ys = [3, 2.5, 1.5, 1]
        qubit_labels = ['q₀', 'q₁', 'q₂', 'q₃']
        
        for y, label in zip(qubit_ys, qubit_labels):
            draw_qubit_line(ax, y, label)
        
        # Bell pairs
        x = 1
        draw_gate(ax, x, qubit_ys[0], 'H', color='lightblue')
        draw_cnot(ax, x+0.5, qubit_ys[0], qubit_ys[1])
        draw_gate(ax, x, qubit_ys[2], 'H', color='lightyellow')
        draw_cnot(ax, x+0.5, qubit_ys[2], qubit_ys[3])
        
        # Barrier
        x = 2.5
        draw_barrier(ax, x, qubit_ys)
        
        # Bilateral CNOT
        x = 4
        draw_cnot(ax, x, qubit_ys[0], qubit_ys[2], color='purple')
        x = 5
        draw_cnot(ax, x, qubit_ys[1], qubit_ys[3], color='purple')
        
        # Barrier
        x = 6.5
        draw_barrier(ax, x, qubit_ys)
        
        # Basis rotation (if needed)
        if rotation:
            x = 8
            if rotation == 'H':
                draw_gate(ax, x, qubit_ys[0], 'H', color='lightcoral')
                draw_gate(ax, x, qubit_ys[1], 'H', color='lightcoral')
                ax.text(x, 3.8, 'Rotate to X basis', ha='center', fontsize=9, 
                       fontweight='bold', color='red')
            elif rotation == 'S†H':
                # Draw S† gate
                rect = Rectangle((x-0.2, qubit_ys[0]-0.2), 0.4, 0.4, 
                                facecolor='lightcoral', edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                ax.text(x, qubit_ys[0], 'S†', ha='center', va='center', 
                       fontsize=9, fontweight='bold')
                
                rect = Rectangle((x-0.2, qubit_ys[1]-0.2), 0.4, 0.4, 
                                facecolor='lightcoral', edgecolor='black', linewidth=2)
                ax.add_patch(rect)
                ax.text(x, qubit_ys[1], 'S†', ha='center', va='center', 
                       fontsize=9, fontweight='bold')
                
                # Draw H gate
                x = 8.5
                draw_gate(ax, x, qubit_ys[0], 'H', color='lightcoral')
                draw_gate(ax, x, qubit_ys[1], 'H', color='lightcoral')
                ax.text(x, 3.8, 'Rotate to Y basis', ha='center', fontsize=9, 
                       fontweight='bold', color='red')
        
        # Measurements
        x = 9.5
        for y in qubit_ys:
            draw_gate(ax, x, y, 'measure')
        ax.text(x, 3.8, 'Measure All', ha='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    return fig

def create_protocol_overview():
    """Create protocol overview diagram"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(5, 5.5, 'BBPSSW Protocol Overview', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # Step 1: Initial Bell pairs
    step1_y = 4.2
    ax.text(1, step1_y + 0.5, 'Step 1: Prepare', 
            fontsize=12, fontweight='bold')
    
    bell0 = FancyBboxPatch((0.5, step1_y - 0.3), 1.5, 0.6, 
                           boxstyle="round,pad=0.05", 
                           edgecolor='steelblue', facecolor='lightblue', linewidth=2)
    ax.add_patch(bell0)
    ax.text(1.25, step1_y, '|Φ⁺⟩₀\nq₀, q₁', ha='center', va='center', fontsize=10)
    
    bell1 = FancyBboxPatch((0.5, step1_y - 1.3), 1.5, 0.6, 
                           boxstyle="round,pad=0.05", 
                           edgecolor='coral', facecolor='lightyellow', linewidth=2)
    ax.add_patch(bell1)
    ax.text(1.25, step1_y - 1, '|Φ⁺⟩₁\nq₂, q₃', ha='center', va='center', fontsize=10)
    
    # Arrow
    ax.annotate('', xy=(2.5, step1_y - 0.5), xytext=(2.2, step1_y - 0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Step 2
    step2_y = step1_y
    ax.text(4.5, step2_y + 0.5, 'Step 2: Entangle', 
            fontsize=12, fontweight='bold')
    
    cnot_box = FancyBboxPatch((3, step2_y - 1.3), 2.5, 1.6, 
                              boxstyle="round,pad=0.1", 
                              edgecolor='purple', facecolor='lavender', linewidth=2)
    ax.add_patch(cnot_box)
    ax.text(4.25, step2_y - 0.1, 'CNOT: q₀ → q₂', ha='center', va='center', fontsize=9)
    ax.text(4.25, step2_y - 0.5, 'CNOT: q₁ → q₃', ha='center', va='center', fontsize=9)
    ax.text(4.25, step2_y - 0.9, '(Bilateral CNOT)', ha='center', va='center', 
            fontsize=8, style='italic', color='purple')
    
    # Arrow
    ax.annotate('', xy=(6, step2_y - 0.5), xytext=(5.7, step2_y - 0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Step 3
    step3_y = step1_y
    ax.text(8, step3_y + 0.5, 'Step 3: Post-Select', 
            fontsize=12, fontweight='bold')
    
    measure_box = FancyBboxPatch((6.5, step3_y - 1.3), 2.5, 1.6, 
                                 boxstyle="round,pad=0.1", 
                                 edgecolor='green', facecolor='lightgreen', linewidth=2)
    ax.add_patch(measure_box)
    ax.text(7.75, step3_y - 0.1, 'Measure q₂, q₃', ha='center', va='center', fontsize=9)
    ax.text(7.75, step3_y - 0.5, 'Keep if:', ha='center', va='center', 
            fontsize=9, fontweight='bold')
    ax.text(7.75, step3_y - 0.9, 'Result = |00⟩', ha='center', va='center', 
            fontsize=9, color='green', fontweight='bold')
    
    # Result
    result_y = 1.5
    ax.text(5, result_y + 0.5, 'Output: Distilled Bell Pair', 
            fontsize=12, fontweight='bold', color='darkgreen')
    
    result_box = FancyBboxPatch((3.5, result_y - 0.4), 3, 0.8, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='darkgreen', facecolor='lightgreen', 
                                linewidth=3, linestyle='--')
    ax.add_patch(result_box)
    ax.text(5, result_y, '|Φ⁺⟩ₒᵤₜ on q₀, q₁\n(Higher Fidelity!)', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Add info box
    info_text = """
    Fidelity Formula:
    F = (1 + ⟨ZZ⟩ + ⟨XX⟩ + ⟨YY⟩) / 4
    
    Success Rate: ~50% (ideal)
    Target State: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    """
    ax.text(9.5, 1.5, info_text, ha='right', va='center', fontsize=9,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            family='monospace')
    
    # Legend
    legend_elements = [
        mpatches.Patch(facecolor='lightblue', edgecolor='steelblue', label='Target Pair'),
        mpatches.Patch(facecolor='lightyellow', edgecolor='coral', label='Ancilla Pair'),
        mpatches.Patch(facecolor='lavender', edgecolor='purple', label='Entangling Ops'),
        mpatches.Patch(facecolor='lightgreen', edgecolor='green', label='Post-Selection')
    ]
    ax.legend(handles=legend_elements, loc='lower left', ncol=2, fontsize=9)
    
    plt.tight_layout()
    return fig

def main():
    """Generate all visualizations"""
    
    print("="*70)
    print("GENERATING ENTANGLEMENT DISTILLATION CIRCUIT VISUALIZATIONS")
    print("="*70)
    
    # 1. BBPSSW Circuit
    print("\n1. Creating BBPSSW circuit diagram...")
    fig1 = create_bbpssw_circuit_diagram()
    fig1.savefig('/Users/pranavks/MIT/2026-IonQ/notebooks/bbpssw_circuit.png', 
                 dpi=300, bbox_inches='tight')
    print("   ✓ Saved: bbpssw_circuit.png")
    
    # 2. Fidelity measurements
    print("\n2. Creating fidelity measurement circuits...")
    fig2 = create_fidelity_measurement_diagrams()
    fig2.savefig('/Users/pranavks/MIT/2026-IonQ/notebooks/fidelity_measurements.png', 
                 dpi=300, bbox_inches='tight')
    print("   ✓ Saved: fidelity_measurements.png")
    
    # 3. Protocol overview
    print("\n3. Creating protocol overview...")
    fig3 = create_protocol_overview()
    fig3.savefig('/Users/pranavks/MIT/2026-IonQ/notebooks/protocol_overview.png', 
                 dpi=300, bbox_inches='tight')
    print("   ✓ Saved: protocol_overview.png")
    
    print("\n" + "="*70)
    print("CIRCUIT SPECIFICATIONS")
    print("="*70)
    print("\nBBPSSW Circuit:")
    print("  • Qubits: 4 (2 Bell pairs)")
    print("  • Target qubits: q₀, q₁")
    print("  • Ancilla qubits: q₂, q₃")
    print("  • Gates: H (2), CNOT (4), Measure (4)")
    print("  • Depth: ~7 layers")
    
    print("\nFidelity Measurement:")
    print("  • Three circuits: ZZ, XX, YY")
    print("  • Measures in different bases")
    print("  • Formula: F = (1 + ⟨ZZ⟩ + ⟨XX⟩ + ⟨YY⟩) / 4")
    print("  • Target: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2")
    
    print("\nPost-Selection:")
    print("  • Keep shots where ancilla = |00⟩")
    print("  • Success probability ≈ 50%")
    print("  • Improves fidelity of remaining pairs")
    
    print("\n" + "="*70)
    print("✓ ALL VISUALIZATIONS GENERATED SUCCESSFULLY")
    print("="*70)
    
    plt.show()

if __name__ == "__main__":
    main()
