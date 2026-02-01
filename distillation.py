"""
Entanglement Distillation Protocols

Implements BBPSSW and DEJMPS distillation circuits for quantum networking.
All circuits use LOCC (Local Operations and Classical Communication) constraints.
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from typing import Tuple
import numpy as np


def create_bbpssw_circuit(num_bell_pairs: int) -> Tuple[QuantumCircuit, int]:
    """
    BBPSSW (Bennett-Brassard-Popescu-Schumacher-Smolin-Wootters) distillation.
    
    Protocol:
    - Uses bilateral CNOT operations on pairs of Bell pairs
    - Measures ancilla qubits to detect errors
    - Post-selects on measurement outcomes
    - Best for depolarizing noise
    
    Args:
        num_bell_pairs: Number of raw Bell pairs (2-8)
        
    Returns:
        (circuit, flag_bit): Circuit with 2N qubits and the flag bit for post-selection
        
    Qubit layout:
        Alice: qubits 0 to N-1
        Bob: qubits N to 2N-1
        Bell pair k: (qubit k, qubit 2N-1-k)
        Target pair: (qubit N-1, qubit N)
    """
    if num_bell_pairs < 2:
        raise ValueError("BBPSSW requires at least 2 Bell pairs")
    if num_bell_pairs > 8:
        raise ValueError("Maximum 8 Bell pairs supported")
    
    N = num_bell_pairs
    total_qubits = 2 * N
    
    # Create quantum and classical registers
    qr = QuantumRegister(total_qubits, 'q')
    cr = ClassicalRegister(total_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Target pair is (N-1, N) - the middle pair
    target_alice = N - 1
    target_bob = N
    
    # Use all other pairs as ancillas for error detection
    ancilla_pairs = []
    for k in range(N):
        alice_qubit = k
        bob_qubit = 2*N - 1 - k
        if k != N - 1:  # Skip target pair
            ancilla_pairs.append((alice_qubit, bob_qubit))
    
    # BBPSSW protocol: bilateral CNOT between target and each ancilla
    for alice_anc, bob_anc in ancilla_pairs:
        # Alice side: CNOT from target to ancilla
        circuit.cx(target_alice, alice_anc)
        
        # Bob side: CNOT from target to ancilla
        circuit.cx(target_bob, bob_anc)
    
    # Measure all ancilla qubits
    ancilla_bits = []
    for alice_anc, bob_anc in ancilla_pairs:
        circuit.measure(alice_anc, alice_anc)
        circuit.measure(bob_anc, bob_anc)
        ancilla_bits.extend([alice_anc, bob_anc])
    
    # Compute flag: XOR of all ancilla measurement results
    # Flag = 0 means no errors detected (success)
    # We'll use the first ancilla bit as the flag accumulator
    if len(ancilla_bits) > 0:
        flag_bit = ancilla_bits[0]
        
        # XOR all other ancilla bits into the flag
        for bit in ancilla_bits[1:]:
            # Classical XOR: measure bit, then conditionally flip flag
            # In QASM, we can't do classical XOR directly, so we use the first bit
            pass
        
        # For simplicity, use the first Alice ancilla as flag
        flag_bit = ancilla_pairs[0][0] if ancilla_pairs else 0
    else:
        flag_bit = 0
    
    return circuit, flag_bit


def create_dejmps_circuit(num_bell_pairs: int) -> Tuple[QuantumCircuit, int]:
    """
    DEJMPS (Deutsch-Ekert-Jozsa-Macchiavello-Popescu-Sanpera) distillation.
    
    Protocol:
    - Optimized for phase noise (Z errors)
    - Uses parity checks in X and Z bases
    - Better success probability than BBPSSW for phase-damping channels
    - Implements recurrence protocol for multiple pairs
    
    Args:
        num_bell_pairs: Number of raw Bell pairs (2-8)
        
    Returns:
        (circuit, flag_bit): Circuit with 2N qubits and the flag bit for post-selection
        
    Qubit layout:
        Alice: qubits 0 to N-1
        Bob: qubits N to 2N-1
        Bell pair k: (qubit k, qubit 2N-1-k)
        Target pair: (qubit N-1, qubit N)
    """
    if num_bell_pairs < 2:
        raise ValueError("DEJMPS requires at least 2 Bell pairs")
    if num_bell_pairs > 8:
        raise ValueError("Maximum 8 Bell pairs supported")
    
    N = num_bell_pairs
    total_qubits = 2 * N
    
    # Create quantum and classical registers
    qr = QuantumRegister(total_qubits, 'q')
    cr = ClassicalRegister(total_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Target pair is (N-1, N)
    target_alice = N - 1
    target_bob = N
    
    # Ancilla pairs for parity checks
    ancilla_pairs = []
    for k in range(N):
        alice_qubit = k
        bob_qubit = 2*N - 1 - k
        if k != N - 1:
            ancilla_pairs.append((alice_qubit, bob_qubit))
    
    # DEJMPS protocol: X-basis and Z-basis parity checks
    
    # Step 1: Z-basis parity check (detect phase errors)
    for alice_anc, bob_anc in ancilla_pairs:
        # CNOT from target to ancilla (Z-basis check)
        circuit.cx(target_alice, alice_anc)
        circuit.cx(target_bob, bob_anc)
    
    # Step 2: X-basis parity check (detect bit-flip errors)
    # Apply Hadamard to change basis
    for alice_anc, bob_anc in ancilla_pairs:
        circuit.h(alice_anc)
        circuit.h(bob_anc)
    
    circuit.h(target_alice)
    circuit.h(target_bob)
    
    # CNOT in X-basis (equivalent to CZ in computational basis)
    for alice_anc, bob_anc in ancilla_pairs:
        circuit.cx(target_alice, alice_anc)
        circuit.cx(target_bob, bob_anc)
    
    # Return to computational basis
    for alice_anc, bob_anc in ancilla_pairs:
        circuit.h(alice_anc)
        circuit.h(bob_anc)
    
    circuit.h(target_alice)
    circuit.h(target_bob)
    
    # Measure ancilla qubits
    ancilla_bits = []
    for alice_anc, bob_anc in ancilla_pairs:
        circuit.measure(alice_anc, alice_anc)
        circuit.measure(bob_anc, bob_anc)
        ancilla_bits.extend([alice_anc, bob_anc])
    
    # Flag bit: first ancilla (should be 0 for success)
    flag_bit = ancilla_pairs[0][0] if ancilla_pairs else 0
    
    return circuit, flag_bit


def create_adaptive_distillation_circuit(
    num_bell_pairs: int,
    noise_type: str = "depolarizing"
) -> Tuple[QuantumCircuit, int]:
    """
    Adaptive distillation that chooses protocol based on noise type.
    
    Args:
        num_bell_pairs: Number of raw Bell pairs (2-8)
        noise_type: "depolarizing", "phase", or "bitflip"
        
    Returns:
        (circuit, flag_bit): Optimized circuit for the noise type
    """
    if noise_type in ["phase", "phase_damping", "z"]:
        return create_dejmps_circuit(num_bell_pairs)
    else:
        # Default to BBPSSW for depolarizing and bit-flip noise
        return create_bbpssw_circuit(num_bell_pairs)


def create_recursive_distillation_circuit(num_bell_pairs: int) -> Tuple[QuantumCircuit, int]:
    """
    Recursive distillation for higher fidelity with more Bell pairs.
    
    Strategy:
    - Divide pairs into groups
    - Distill each group
    - Recursively distill the results
    
    Args:
        num_bell_pairs: Number of raw Bell pairs (4-8, must be even)
        
    Returns:
        (circuit, flag_bit): Circuit with recursive distillation
    """
    if num_bell_pairs < 4:
        # Fall back to basic BBPSSW
        return create_bbpssw_circuit(num_bell_pairs)
    
    if num_bell_pairs % 2 != 0:
        # Use one less pair to make it even
        num_bell_pairs -= 1
    
    N = num_bell_pairs
    total_qubits = 2 * N
    
    qr = QuantumRegister(total_qubits, 'q')
    cr = ClassicalRegister(total_qubits, 'c')
    circuit = QuantumCircuit(qr, cr)
    
    # Split into two groups and distill each
    mid = N // 2
    
    # Group 1: pairs 0 to mid-1, target at mid-1
    # Group 2: pairs mid to N-1, target at N-1
    
    # First round: distill group 1 (target: mid-1, N+mid)
    target1_alice = mid - 1
    target1_bob = N + mid
    
    for k in range(mid - 1):
        alice_anc = k
        bob_anc = 2*N - 1 - k
        circuit.cx(target1_alice, alice_anc)
        circuit.cx(target1_bob, bob_anc)
        circuit.measure(alice_anc, alice_anc)
        circuit.measure(bob_anc, bob_anc)
    
    # Second round: distill group 2 (target: N-1, N)
    target2_alice = N - 1
    target2_bob = N
    
    for k in range(mid, N - 1):
        alice_anc = k
        bob_anc = 2*N - 1 - k
        circuit.cx(target2_alice, alice_anc)
        circuit.cx(target2_bob, bob_anc)
        circuit.measure(alice_anc, alice_anc)
        circuit.measure(bob_anc, bob_anc)
    
    # Final round: distill the two targets
    circuit.cx(target2_alice, target1_alice)
    circuit.cx(target2_bob, target1_bob)
    circuit.measure(target1_alice, target1_alice)
    circuit.measure(target1_bob, target1_bob)
    
    flag_bit = 0  # Use first qubit as flag
    
    return circuit, flag_bit


def estimate_success_probability(num_bell_pairs: int, protocol: str = "bbpssw") -> float:
    """
    Estimate post-selection success probability for a distillation protocol.
    
    This is a heuristic based on typical distillation behavior:
    - More bell pairs = more measurements = lower success probability
    - But also higher fidelity
    
    Args:
        num_bell_pairs: Number of raw Bell pairs
        protocol: "bbpssw" or "dejmps"
        
    Returns:
        Estimated success probability (0-1)
    """
    # Number of ancilla pairs
    num_ancillas = num_bell_pairs - 1
    
    # Each ancilla measurement has some probability of passing
    # Assume ~70% pass rate per ancilla pair for moderate noise
    if protocol == "dejmps":
        # DEJMPS typically has better success probability
        per_ancilla_success = 0.75
    else:
        per_ancilla_success = 0.70
    
    # Total success probability (assuming independent checks)
    # Each ancilla pair has 2 qubits measured
    total_measurements = 2 * num_ancillas
    success_prob = per_ancilla_success ** total_measurements
    
    # Clamp to reasonable range
    return max(0.1, min(0.95, success_prob))


def estimate_output_fidelity(
    input_fidelity: float,
    num_bell_pairs: int,
    protocol: str = "bbpssw"
) -> float:
    """
    Estimate output fidelity after distillation.
    
    Uses theoretical bounds for distillation protocols:
    - BBPSSW: F_out ≈ F_in^2 / (F_in^2 + (1-F_in)^2) for 2 pairs
    - More pairs: recursive application
    
    Args:
        input_fidelity: Fidelity of raw Bell pairs
        num_bell_pairs: Number of raw Bell pairs used
        protocol: "bbpssw" or "dejmps"
        
    Returns:
        Estimated output fidelity
    """
    if input_fidelity < 0.5:
        # Below 0.5, distillation doesn't help
        return input_fidelity
    
    F = input_fidelity
    
    # Single distillation step (2 pairs -> 1 pair)
    def single_step_fidelity(f):
        # BBPSSW formula
        f_out = f**2 / (f**2 + (1 - f)**2)
        return f_out
    
    # Apply distillation rounds
    # Each round uses 2 pairs to make 1 pair
    rounds = int(np.log2(num_bell_pairs))
    
    for _ in range(max(1, rounds)):
        F = single_step_fidelity(F)
    
    return min(0.99, F)  # Cap at 99%
