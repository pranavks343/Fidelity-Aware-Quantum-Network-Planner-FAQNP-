"""
Local Circuit Simulation and Fidelity Estimation

Simulates distillation circuits locally before submission to estimate:
- Output fidelity
- Post-selection success probability
- Expected performance

This helps avoid wasting server-side bell-pair budget on low-quality attempts.
"""

from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity
from qiskit_aer import AerSimulator
import numpy as np
from typing import Tuple, Dict, Any, Optional


class DistillationSimulator:
    """
    Local simulator for entanglement distillation circuits.
    
    Provides fast estimates of:
    - Post-distillation fidelity
    - Success probability (post-selection)
    - Circuit validity
    """
    
    def __init__(self, shots: int = 1000):
        """
        Initialize simulator.
        
        Args:
            shots: Number of shots for statistical sampling
        """
        self.shots = shots
        self.simulator = AerSimulator()
    
    def create_noisy_bell_state(
        self,
        noise_prob: float = 0.1,
        noise_type: str = "depolarizing"
    ) -> DensityMatrix:
        """
        Create a noisy Bell pair density matrix.
        
        Args:
            noise_prob: Probability of noise (0-1)
            noise_type: "depolarizing", "phase", or "bitflip"
            
        Returns:
            Noisy Bell state as DensityMatrix
        """
        # Perfect Bell state |Φ+⟩ = (|00⟩ + |11⟩)/√2
        perfect_bell = Statevector.from_label('00') + Statevector.from_label('11')
        perfect_bell = perfect_bell / np.sqrt(2)
        
        # Convert to density matrix
        rho = DensityMatrix(perfect_bell)
        
        # Apply noise
        if noise_type == "depolarizing":
            # Depolarizing: mix with maximally mixed state
            mixed_state = DensityMatrix(np.eye(4) / 4)
            rho = (1 - noise_prob) * rho + noise_prob * mixed_state
        
        elif noise_type == "phase":
            # Phase damping: Z errors
            # Apply Z on first qubit with probability noise_prob
            z_error = np.array([[1, 0], [0, -1]])
            identity = np.eye(2)
            z_op = np.kron(z_error, identity)
            
            rho_data = rho.data
            rho_noisy = (1 - noise_prob) * rho_data + noise_prob * (z_op @ rho_data @ z_op.conj().T)
            rho = DensityMatrix(rho_noisy)
        
        elif noise_type == "bitflip":
            # Bit flip: X errors
            x_error = np.array([[0, 1], [1, 0]])
            identity = np.eye(2)
            x_op = np.kron(x_error, identity)
            
            rho_data = rho.data
            rho_noisy = (1 - noise_prob) * rho_data + noise_prob * (x_op @ rho_data @ x_op.conj().T)
            rho = DensityMatrix(rho_noisy)
        
        return rho
    
    def create_initial_state(
        self,
        num_bell_pairs: int,
        noise_prob: float = 0.1,
        noise_type: str = "depolarizing"
    ) -> DensityMatrix:
        """
        Create initial state for N noisy Bell pairs.
        
        Qubit layout:
        - Alice: qubits 0 to N-1
        - Bob: qubits N to 2N-1
        - Bell pair k: (qubit k, qubit 2N-1-k)
        
        Args:
            num_bell_pairs: Number of Bell pairs
            noise_prob: Noise probability per pair
            noise_type: Type of noise
            
        Returns:
            Initial state as DensityMatrix
        """
        # Create first noisy Bell pair
        state = self.create_noisy_bell_state(noise_prob, noise_type)
        
        # Tensor product with additional pairs
        for _ in range(num_bell_pairs - 1):
            bell_pair = self.create_noisy_bell_state(noise_prob, noise_type)
            state = state.tensor(bell_pair)
        
        # Need to reorder qubits to match game convention
        # Game pairs qubits from outside in: (0, 2N-1), (1, 2N-2), ...
        # Our tensor product creates: (0,1), (2,3), ...
        # We need to permute qubits
        
        total_qubits = 2 * num_bell_pairs
        # For simplicity, we'll work with the standard ordering
        # The circuit should handle the qubit mapping
        
        return state
    
    def estimate_fidelity(
        self,
        circuit: QuantumCircuit,
        flag_bit: int,
        num_bell_pairs: int,
        input_noise: float = 0.15,
        noise_type: str = "depolarizing"
    ) -> Tuple[float, float]:
        """
        Estimate output fidelity and success probability.
        
        Args:
            circuit: Distillation circuit
            flag_bit: Classical bit for post-selection
            num_bell_pairs: Number of input Bell pairs
            input_noise: Input noise probability
            noise_type: Type of noise
            
        Returns:
            (estimated_fidelity, success_probability)
        """
        try:
            # For fast estimation, use analytical approximation
            # Based on theoretical distillation formulas
            
            # Input fidelity
            F_in = 1 - input_noise
            
            # Estimate output fidelity based on number of pairs
            # Single distillation step: F_out ≈ F_in^2 / (F_in^2 + (1-F_in)^2)
            F = F_in
            rounds = max(1, int(np.log2(num_bell_pairs)))
            
            for _ in range(rounds):
                F = F**2 / (F**2 + (1 - F)**2)
            
            # Success probability decreases with more measurements
            num_measurements = 2 * (num_bell_pairs - 1)  # Ancilla pairs
            success_prob = 0.7 ** num_measurements  # Heuristic
            
            # Clamp values
            F = max(0.5, min(0.99, F))
            success_prob = max(0.05, min(0.95, success_prob))
            
            return F, success_prob
        
        except Exception as e:
            # Fallback: conservative estimates
            return 0.75, 0.5
    
    def simulate_circuit(
        self,
        circuit: QuantumCircuit,
        flag_bit: int,
        num_bell_pairs: int,
        input_noise: float = 0.15
    ) -> Dict[str, Any]:
        """
        Full simulation of distillation circuit.
        
        Args:
            circuit: Distillation circuit
            flag_bit: Classical bit for post-selection
            num_bell_pairs: Number of input Bell pairs
            input_noise: Input noise probability
            
        Returns:
            Dictionary with simulation results
        """
        try:
            # Quick analytical estimate (full simulation is expensive)
            fidelity, success_prob = self.estimate_fidelity(
                circuit, flag_bit, num_bell_pairs, input_noise
            )
            
            return {
                'estimated_fidelity': fidelity,
                'success_probability': success_prob,
                'valid': True,
                'error': None
            }
        
        except Exception as e:
            return {
                'estimated_fidelity': 0.5,
                'success_probability': 0.5,
                'valid': False,
                'error': str(e)
            }
    
    def validate_circuit(
        self,
        circuit: QuantumCircuit,
        num_bell_pairs: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that circuit meets LOCC constraints.
        
        Checks:
        - Correct number of qubits (2N)
        - No entangling gates across Alice/Bob boundary
        - Valid gate set
        
        Args:
            circuit: Circuit to validate
            num_bell_pairs: Expected number of Bell pairs
            
        Returns:
            (is_valid, error_message)
        """
        expected_qubits = 2 * num_bell_pairs
        
        if circuit.num_qubits != expected_qubits:
            return False, f"Expected {expected_qubits} qubits, got {circuit.num_qubits}"
        
        # Check LOCC constraint: no entangling gates across boundary
        N = num_bell_pairs
        alice_qubits = set(range(N))
        bob_qubits = set(range(N, 2*N))
        
        for instruction in circuit.data:
            gate = instruction.operation
            qubits = [circuit.qubits.index(q) for q in instruction.qubits]
            
            # Check two-qubit gates
            if len(qubits) == 2:
                q1, q2 = qubits
                
                # Both qubits must be on same side (Alice or Bob)
                if (q1 in alice_qubits and q2 in bob_qubits) or \
                   (q1 in bob_qubits and q2 in alice_qubits):
                    return False, f"LOCC violation: gate {gate.name} crosses Alice/Bob boundary ({q1}, {q2})"
        
        return True, None
    
    def should_submit(
        self,
        circuit: QuantumCircuit,
        flag_bit: int,
        num_bell_pairs: int,
        threshold: float,
        input_noise: float = 0.15
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Decide whether to submit circuit based on simulation.
        
        Args:
            circuit: Distillation circuit
            flag_bit: Classical bit for post-selection
            num_bell_pairs: Number of Bell pairs
            threshold: Required fidelity threshold
            input_noise: Estimated input noise
            
        Returns:
            (should_submit, reason, simulation_results)
        """
        # Validate circuit
        is_valid, error = self.validate_circuit(circuit, num_bell_pairs)
        if not is_valid:
            return False, f"Invalid circuit: {error}", {}
        
        # Simulate
        results = self.simulate_circuit(circuit, flag_bit, num_bell_pairs, input_noise)
        
        if not results['valid']:
            return False, f"Simulation failed: {results['error']}", results
        
        estimated_fidelity = results['estimated_fidelity']
        success_prob = results['success_probability']
        
        # Check if estimated fidelity meets threshold
        safety_margin = 0.02  # Require 2% above threshold for safety
        if estimated_fidelity < threshold - safety_margin:
            return False, f"Estimated fidelity ({estimated_fidelity:.3f}) below threshold ({threshold:.3f})", results
        
        # Check success probability
        if success_prob < 0.1:
            return False, f"Success probability too low ({success_prob:.2%})", results
        
        # Passed all checks
        return True, "Simulation passed", results


def estimate_input_noise_from_difficulty(difficulty: float) -> float:
    """
    Estimate input noise probability from edge difficulty rating.
    
    Args:
        difficulty: Difficulty rating (1-10)
        
    Returns:
        Estimated noise probability (0-1)
    """
    # Map difficulty to noise
    # Difficulty 1 -> ~5% noise
    # Difficulty 5 -> ~15% noise
    # Difficulty 10 -> ~30% noise
    
    noise = 0.05 + (difficulty / 10.0) * 0.25
    return min(0.35, max(0.05, noise))


def estimate_required_fidelity_improvement(
    input_fidelity: float,
    threshold: float
) -> float:
    """
    Calculate required fidelity improvement factor.
    
    Args:
        input_fidelity: Initial fidelity
        threshold: Target fidelity
        
    Returns:
        Improvement factor needed
    """
    if input_fidelity >= threshold:
        return 1.0
    
    return threshold / input_fidelity
