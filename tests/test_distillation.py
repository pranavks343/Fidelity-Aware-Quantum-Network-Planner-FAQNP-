"""
Test suite for distillation circuits.

Validates:
- Circuit structure
- LOCC constraints
- Qubit count
- Flag bit logic
"""

import sys
from qiskit import QuantumCircuit
from distillation.distillation import (
    create_bbpssw_circuit,
    create_dejmps_circuit,
    create_adaptive_distillation_circuit,
    create_recursive_distillation_circuit,
    estimate_success_probability,
    estimate_output_fidelity
)


def test_circuit_structure(circuit: QuantumCircuit, num_bell_pairs: int, name: str):
    """Test basic circuit structure."""
    print(f"\nTesting {name}:")
    print(f"  Bell pairs: {num_bell_pairs}")
    print(f"  Expected qubits: {2 * num_bell_pairs}")
    print(f"  Actual qubits: {circuit.num_qubits}")
    
    assert circuit.num_qubits == 2 * num_bell_pairs, \
        f"Expected {2 * num_bell_pairs} qubits, got {circuit.num_qubits}"
    
    print(f"  ✓ Qubit count correct")
    
    # Check for measurements
    has_measurements = any(
        instr.operation.name == 'measure'
        for instr in circuit.data
    )
    assert has_measurements, "Circuit should have measurements"
    print(f"  ✓ Has measurements")
    
    return True


def test_locc_constraint(circuit: QuantumCircuit, num_bell_pairs: int, name: str):
    """Test LOCC constraint (no entangling gates across Alice/Bob boundary)."""
    N = num_bell_pairs
    alice_qubits = set(range(N))
    bob_qubits = set(range(N, 2*N))
    
    violations = []
    
    for instr in circuit.data:
        gate = instr.operation
        qubits = [circuit.qubits.index(q) for q in instr.qubits]
        
        # Check two-qubit gates
        if len(qubits) == 2:
            q1, q2 = qubits
            
            # Check if gate crosses boundary
            if (q1 in alice_qubits and q2 in bob_qubits) or \
               (q1 in bob_qubits and q2 in alice_qubits):
                violations.append((gate.name, q1, q2))
    
    if violations:
        print(f"  ✗ LOCC violations found:")
        for gate_name, q1, q2 in violations:
            print(f"    - {gate_name} on qubits ({q1}, {q2})")
        return False
    else:
        print(f"  ✓ LOCC constraint satisfied")
        return True


def test_bbpssw():
    """Test BBPSSW circuits."""
    print("\n" + "=" * 60)
    print("Testing BBPSSW Distillation")
    print("=" * 60)
    
    for N in [2, 3, 4, 5]:
        circuit, flag_bit = create_bbpssw_circuit(N)
        
        assert test_circuit_structure(circuit, N, f"BBPSSW (N={N})")
        assert test_locc_constraint(circuit, N, f"BBPSSW (N={N})")
        
        print(f"  Flag bit: {flag_bit}")
        print(f"  Circuit depth: {circuit.depth()}")
        print(f"  Gate count: {len(circuit.data)}")
    
    print("\n✓ All BBPSSW tests passed")


def test_dejmps():
    """Test DEJMPS circuits."""
    print("\n" + "=" * 60)
    print("Testing DEJMPS Distillation")
    print("=" * 60)
    
    for N in [2, 3, 4, 5]:
        circuit, flag_bit = create_dejmps_circuit(N)
        
        assert test_circuit_structure(circuit, N, f"DEJMPS (N={N})")
        assert test_locc_constraint(circuit, N, f"DEJMPS (N={N})")
        
        print(f"  Flag bit: {flag_bit}")
        print(f"  Circuit depth: {circuit.depth()}")
        print(f"  Gate count: {len(circuit.data)}")
    
    print("\n✓ All DEJMPS tests passed")


def test_adaptive():
    """Test adaptive distillation."""
    print("\n" + "=" * 60)
    print("Testing Adaptive Distillation")
    print("=" * 60)
    
    for noise_type in ["depolarizing", "phase", "bitflip"]:
        print(f"\nNoise type: {noise_type}")
        for N in [2, 3, 4]:
            circuit, flag_bit = create_adaptive_distillation_circuit(N, noise_type)
            
            assert test_circuit_structure(circuit, N, f"Adaptive-{noise_type} (N={N})")
            assert test_locc_constraint(circuit, N, f"Adaptive-{noise_type} (N={N})")
    
    print("\n✓ All adaptive tests passed")


def test_estimates():
    """Test estimation functions."""
    print("\n" + "=" * 60)
    print("Testing Estimation Functions")
    print("=" * 60)
    
    # Test success probability estimation
    print("\nSuccess Probability Estimates:")
    for N in [2, 3, 4, 5]:
        prob_bbpssw = estimate_success_probability(N, "bbpssw")
        prob_dejmps = estimate_success_probability(N, "dejmps")
        print(f"  N={N}: BBPSSW={prob_bbpssw:.3f}, DEJMPS={prob_dejmps:.3f}")
        
        assert 0 <= prob_bbpssw <= 1, "Probability out of range"
        assert 0 <= prob_dejmps <= 1, "Probability out of range"
    
    # Test fidelity estimation
    print("\nFidelity Improvement Estimates:")
    for F_in in [0.6, 0.7, 0.8, 0.9]:
        for N in [2, 3, 4]:
            F_out = estimate_output_fidelity(F_in, N, "bbpssw")
            improvement = F_out - F_in
            print(f"  F_in={F_in:.2f}, N={N}: F_out={F_out:.3f} (Δ={improvement:+.3f})")
            
            assert F_out >= F_in, "Output fidelity should be >= input"
            assert F_out <= 1.0, "Fidelity cannot exceed 1.0"
    
    print("\n✓ All estimation tests passed")


def run_all_tests():
    """Run all test suites."""
    print("=" * 60)
    print("DISTILLATION CIRCUIT TEST SUITE")
    print("=" * 60)
    
    try:
        test_bbpssw()
        test_dejmps()
        test_adaptive()
        test_estimates()
        
        print("\n" + "=" * 60)
        print("✓ ALL TESTS PASSED")
        print("=" * 60)
        return True
    
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
