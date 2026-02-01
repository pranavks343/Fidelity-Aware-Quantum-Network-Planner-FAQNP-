"""
Visualize Entanglement Distillation Circuits
Displays the BBPSSW protocol and fidelity measurement circuits
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import matplotlib.patches as mpatches

# Configure matplotlib for high-quality output
plt.rcParams['figure.figsize'] = (16, 12)
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'

def create_bbpssw_circuit():
    """Create the BBPSSW distillation circuit"""
    # Create quantum and classical registers
    qr = QuantumRegister(4, 'q')
    cr = ClassicalRegister(4, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Step 1: Prepare two Bell pairs
    # Bell pair 0: q0, q1 (target/data pair)
    circuit.h(0)
    circuit.cx(0, 1)
    
    # Bell pair 1: q2, q3 (ancilla pair)
    circuit.h(2)
    circuit.cx(2, 3)
    
    circuit.barrier()
    
    # Step 2: Bilateral CNOT operations
    circuit.cx(0, 2)  # Control: q0 (target), Target: q2 (ancilla)
    circuit.cx(1, 3)  # Control: q1 (target), Target: q3 (ancilla)
    
    circuit.barrier()
    
    # Step 3: Measure ancilla qubits
    circuit.measure([2, 3], [2, 3])
    
    # Step 4: Measure target qubits (for verification)
    circuit.measure([0, 1], [0, 1])
    
    return circuit

def create_fidelity_measurement_circuits():
    """Create circuits for measuring in different bases"""
    circuits = {}
    
    # ZZ measurement (computational basis)
    qr = QuantumRegister(4, 'q')
    cr = ClassicalRegister(4, 'c')
    zz_circuit = QuantumCircuit(qr, cr)
    
    # Prepare Bell pairs
    zz_circuit.h(0)
    zz_circuit.cx(0, 1)
    zz_circuit.h(2)
    zz_circuit.cx(2, 3)
    zz_circuit.barrier()
    
    # Bilateral CNOT
    zz_circuit.cx(0, 2)
    zz_circuit.cx(1, 3)
    zz_circuit.barrier()
    
    # Measure in Z basis (no rotation needed)
    zz_circuit.measure([0, 1, 2, 3], [0, 1, 2, 3])
    circuits['ZZ'] = zz_circuit
    
    # XX measurement (X basis)
    xx_circuit = QuantumCircuit(qr, cr)
    xx_circuit.h(0)
    xx_circuit.cx(0, 1)
    xx_circuit.h(2)
    xx_circuit.cx(2, 3)
    xx_circuit.barrier()
    
    xx_circuit.cx(0, 2)
    xx_circuit.cx(1, 3)
    xx_circuit.barrier()
    
    # Rotate to X basis before measurement
    xx_circuit.h([0, 1])
    xx_circuit.measure([0, 1, 2, 3], [0, 1, 2, 3])
    circuits['XX'] = xx_circuit
    
    # YY measurement (Y basis)
    yy_circuit = QuantumCircuit(qr, cr)
    yy_circuit.h(0)
    yy_circuit.cx(0, 1)
    yy_circuit.h(2)
    yy_circuit.cx(2, 3)
    yy_circuit.barrier()
    
    yy_circuit.cx(0, 2)
    yy_circuit.cx(1, 3)
    yy_circuit.barrier()
    
    # Rotate to Y basis before measurement
    yy_circuit.sdg([0, 1])
    yy_circuit.h([0, 1])
    yy_circuit.measure([0, 1, 2, 3], [0, 1, 2, 3])
    circuits['YY'] = yy_circuit
    
    return circuits

def create_protocol_diagram():
    """Create a conceptual diagram of the BBPSSW protocol"""
    fig, ax = plt.subplots(1, 1, figsize=(14, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')
    
    # Title
    ax.text(5, 5.5, 'BBPSSW Entanglement Distillation Protocol', 
            ha='center', va='center', fontsize=18, fontweight='bold')
    
    # Step 1: Initial Bell pairs
    step1_y = 4.2
    ax.text(1, step1_y + 0.5, 'Step 1: Prepare Bell Pairs', 
            fontsize=12, fontweight='bold')
    
    # Bell pair 0 (target)
    bell0 = FancyBboxPatch((0.5, step1_y - 0.3), 1.5, 0.6, 
                           boxstyle="round,pad=0.05", 
                           edgecolor='steelblue', facecolor='lightblue', linewidth=2)
    ax.add_patch(bell0)
    ax.text(1.25, step1_y, '|Φ⁺⟩₀\nq₀, q₁', ha='center', va='center', fontsize=10)
    
    # Bell pair 1 (ancilla)
    bell1 = FancyBboxPatch((0.5, step1_y - 1.3), 1.5, 0.6, 
                           boxstyle="round,pad=0.05", 
                           edgecolor='coral', facecolor='lightyellow', linewidth=2)
    ax.add_patch(bell1)
    ax.text(1.25, step1_y - 1, '|Φ⁺⟩₁\nq₂, q₃', ha='center', va='center', fontsize=10)
    
    # Arrow
    ax.annotate('', xy=(2.5, step1_y - 0.5), xytext=(2.2, step1_y - 0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Step 2: Bilateral CNOT
    step2_y = step1_y
    ax.text(4.5, step2_y + 0.5, 'Step 2: Bilateral CNOT', 
            fontsize=12, fontweight='bold')
    
    # CNOT operations box
    cnot_box = FancyBboxPatch((3, step2_y - 1.3), 2.5, 1.6, 
                              boxstyle="round,pad=0.1", 
                              edgecolor='purple', facecolor='lavender', linewidth=2)
    ax.add_patch(cnot_box)
    ax.text(4.25, step2_y - 0.1, 'CNOT: q₀ → q₂', ha='center', va='center', fontsize=9)
    ax.text(4.25, step2_y - 0.5, 'CNOT: q₁ → q₃', ha='center', va='center', fontsize=9)
    ax.text(4.25, step2_y - 0.9, '(Entangle pairs)', ha='center', va='center', 
            fontsize=8, style='italic', color='purple')
    
    # Arrow
    ax.annotate('', xy=(6, step2_y - 0.5), xytext=(5.7, step2_y - 0.5),
                arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    # Step 3: Measure & Post-select
    step3_y = step1_y
    ax.text(8, step3_y + 0.5, 'Step 3: Measure Ancilla', 
            fontsize=12, fontweight='bold')
    
    # Measurement box
    measure_box = FancyBboxPatch((6.5, step3_y - 1.3), 2.5, 1.6, 
                                 boxstyle="round,pad=0.1", 
                                 edgecolor='green', facecolor='lightgreen', linewidth=2)
    ax.add_patch(measure_box)
    ax.text(7.75, step3_y - 0.1, 'Measure q₂, q₃', ha='center', va='center', fontsize=9)
    ax.text(7.75, step3_y - 0.5, 'Post-select:', ha='center', va='center', 
            fontsize=9, fontweight='bold')
    ax.text(7.75, step3_y - 0.9, 'Keep if |00⟩', ha='center', va='center', 
            fontsize=9, color='green')
    
    # Result
    result_y = 1.5
    ax.text(5, result_y + 0.5, 'Result: Distilled Bell Pair', 
            fontsize=12, fontweight='bold', color='darkgreen')
    
    result_box = FancyBboxPatch((3.5, result_y - 0.4), 3, 0.8, 
                                boxstyle="round,pad=0.1", 
                                edgecolor='darkgreen', facecolor='lightgreen', 
                                linewidth=3, linestyle='--')
    ax.add_patch(result_box)
    ax.text(5, result_y, '|Φ⁺⟩ₒᵤₜ on q₀, q₁\n(Higher fidelity)', 
            ha='center', va='center', fontsize=11, fontweight='bold')
    
    # Add legend
    legend_elements = [
        mpatches.Patch(facecolor='lightblue', edgecolor='steelblue', label='Target Bell Pair'),
        mpatches.Patch(facecolor='lightyellow', edgecolor='coral', label='Ancilla Bell Pair'),
        mpatches.Patch(facecolor='lavender', edgecolor='purple', label='Entangling Operations'),
        mpatches.Patch(facecolor='lightgreen', edgecolor='green', label='Measurement & Post-selection')
    ]
    ax.legend(handles=legend_elements, loc='lower center', ncol=2, fontsize=9)
    
    plt.tight_layout()
    return fig

def main():
    """Generate all circuit visualizations"""
    
    # Create figure with subplots
    fig = plt.figure(figsize=(18, 14))
    
    # Add title
    fig.suptitle('Entanglement Distillation Circuits - BBPSSW Protocol', 
                 fontsize=20, fontweight='bold', y=0.98)
    
    # 1. BBPSSW Circuit
    ax1 = plt.subplot(3, 2, (1, 2))
    bbpssw = create_bbpssw_circuit()
    bbpssw.draw('mpl', ax=ax1, fold=-1, style='iqp')
    ax1.set_title('Complete BBPSSW Distillation Circuit\n(4 qubits: 2 Bell pairs)', 
                  fontsize=14, fontweight='bold', pad=20)
    
    # 2-4. Fidelity measurement circuits
    fidelity_circuits = create_fidelity_measurement_circuits()
    
    positions = [(3, 4, 5), (6,)]
    titles = [
        'ZZ Measurement (Computational Basis)\nNo rotation needed',
        'XX Measurement (X Basis)\nApply H before measurement',
        'YY Measurement (Y Basis)\nApply S†H before measurement'
    ]
    
    for idx, (name, circuit) in enumerate(fidelity_circuits.items()):
        if idx < 2:
            ax = plt.subplot(3, 2, positions[0][idx])
        else:
            ax = plt.subplot(3, 2, positions[1][0])
        
        circuit.draw('mpl', ax=ax, fold=-1, style='iqp')
        ax.set_title(f'{titles[idx]}', fontsize=12, fontweight='bold', pad=15)
    
    # Add text box with explanation
    ax_text = plt.subplot(3, 2, 4)
    ax_text.axis('off')
    
    explanation = """
    Fidelity Estimation Formula:
    
    F = (1 + ⟨ZZ⟩ + ⟨XX⟩ + ⟨YY⟩) / 4
    
    Where:
    • ⟨ZZ⟩ = P(00) + P(11) - P(01) - P(10)
    • ⟨XX⟩ = measured in X basis
    • ⟨YY⟩ = measured in Y basis
    
    Target State: |Φ⁺⟩ = (|00⟩ + |11⟩)/√2
    
    Post-Selection:
    • Keep only shots where ancilla = |00⟩
    • Success probability ≈ 50% for ideal case
    • Improves fidelity of remaining pairs
    
    Key Features:
    ✓ Hardware-compatible (no mid-circuit)
    ✓ Measures in 3 bases for full tomography
    ✓ Post-selects on ancilla measurement
    ✓ Works on IBM Quantum hardware
    """
    
    ax_text.text(0.1, 0.5, explanation, fontsize=10, family='monospace',
                verticalalignment='center', 
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.tight_layout()
    plt.savefig('/Users/pranavks/MIT/2026-IonQ/notebooks/entanglement_distillation_circuits.png', 
                dpi=300, bbox_inches='tight')
    print("✓ Saved: entanglement_distillation_circuits.png")
    
    # Create protocol diagram
    fig2 = create_protocol_diagram()
    fig2.savefig('/Users/pranavks/MIT/2026-IonQ/notebooks/bbpssw_protocol_diagram.png', 
                 dpi=300, bbox_inches='tight')
    print("✓ Saved: bbpssw_protocol_diagram.png")
    
    plt.show()
    
    # Print circuit information
    print("\n" + "="*70)
    print("CIRCUIT INFORMATION")
    print("="*70)
    
    print("\nBBPSSW Circuit:")
    print(f"  Qubits: {bbpssw.num_qubits}")
    print(f"  Depth: {bbpssw.depth()}")
    print(f"  Gates: {bbpssw.count_ops()}")
    print(f"  Target qubits: q0, q1")
    print(f"  Ancilla qubits: q2, q3")
    
    print("\nFidelity Measurement Circuits:")
    for name, circuit in fidelity_circuits.items():
        print(f"\n  {name} Circuit:")
        print(f"    Qubits: {circuit.num_qubits}")
        print(f"    Depth: {circuit.depth()}")
        print(f"    Gates: {circuit.count_ops()}")
    
    print("\n" + "="*70)
    print("Circuit diagrams displayed and saved!")
    print("="*70)

if __name__ == "__main__":
    main()
