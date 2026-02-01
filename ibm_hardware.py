"""
IBM Quantum Hardware Integration for Entanglement Distillation

This module adapts the quantum network distillation project to execute
on REAL IBM Quantum hardware for validation and benchmarking.

IMPORTANT LIMITATIONS:
- IBM Quantum does NOT support real quantum networking
- No inter-device entanglement distribution
- This is a HARDWARE-VALIDATION PROTOTYPE

Purpose:
- Validate distillation circuits on real noisy quantum hardware
- Compare real hardware results with simulated fidelity estimates
- Demonstrate NISQ-era quantum circuit design

Phases:
1. Hardware-compatible distillation circuits (BBPSSW)
2. Backend selection with calibration awareness
3. Execution via Qiskit Runtime
4. Fidelity estimation from measurement statistics
5. Integration with existing simulation framework
"""

from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import Initialize
from qiskit.quantum_info import Statevector, DensityMatrix, state_fidelity
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler, Session
from qiskit_ibm_runtime.options import SamplerOptions
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel

import numpy as np
from typing import Tuple, Dict, List, Optional, Any
from datetime import datetime
import time


class IBMQuantumHardwareValidator:
    """
    Validates entanglement distillation circuits on IBM Quantum hardware.
    
    This class provides:
    - Hardware-compatible circuit generation
    - Backend selection and calibration monitoring
    - Real hardware execution via Qiskit Runtime
    - Fidelity estimation from measurement statistics
    - Comparison with simulated results
    """
    
    def __init__(self, api_token: str, hub: str = "ibm-q", group: str = "open", project: str = "main"):
        """
        Initialize IBM Quantum hardware validator.
        
        Args:
            api_token: IBM Quantum API token
            hub: IBM Quantum hub (default: "ibm-q")
            group: IBM Quantum group (default: "open")
            project: IBM Quantum project (default: "main")
        """
        self.api_token = api_token
        self.hub = hub
        self.group = group
        self.project = project
        
        # Initialize service
        try:
            self.service = QiskitRuntimeService(
                channel="ibm_quantum",
                token=api_token,
                instance=f"{hub}/{group}/{project}"
            )
            print(f"✓ Connected to IBM Quantum: {hub}/{group}/{project}")
        except Exception as e:
            print(f"✗ Failed to connect to IBM Quantum: {e}")
            print("Attempting to save account...")
            QiskitRuntimeService.save_account(
                channel="ibm_quantum",
                token=api_token,
                instance=f"{hub}/{group}/{project}",
                overwrite=True
            )
            self.service = QiskitRuntimeService(channel="ibm_quantum")
            print("✓ Account saved and service initialized")
        
        self.backend = None
        self.backend_properties = {}
        self.calibration_timestamp = None
        
    # ========================================================================
    # PHASE 1: Hardware-Compatible Distillation Circuits
    # ========================================================================
    
    def create_hardware_bbpssw_circuit(
        self,
        prepare_bell_pairs: bool = True,
        measure_output: bool = True
    ) -> Tuple[QuantumCircuit, Dict[str, Any]]:
        """
        Create hardware-compatible BBPSSW distillation circuit.
        
        Uses 2 Bell pairs (4 qubits total):
        - Pair 0 (q0, q1): Data pair (target)
        - Pair 1 (q2, q3): Ancilla pair
        
        Native IBM gate set: CX, RZ, SX, X, Measurement
        
        Args:
            prepare_bell_pairs: If True, include Bell pair preparation
            measure_output: If True, measure output pair
            
        Returns:
            (circuit, metadata): Hardware-compatible circuit and metadata
        """
        # 4 qubits: 2 Bell pairs
        qr = QuantumRegister(4, 'q')
        cr_ancilla = ClassicalRegister(2, 'ancilla')  # Ancilla measurements
        cr_output = ClassicalRegister(2, 'output')    # Output measurements (optional)
        
        if measure_output:
            circuit = QuantumCircuit(qr, cr_ancilla, cr_output)
        else:
            circuit = QuantumCircuit(qr, cr_ancilla)
        
        # Step 1: Prepare Bell pairs (if requested)
        if prepare_bell_pairs:
            # Bell pair 0: |Φ+⟩ on (q0, q1)
            circuit.h(0)
            circuit.cx(0, 1)
            
            # Bell pair 1: |Φ+⟩ on (q2, q3)
            circuit.h(2)
            circuit.cx(2, 3)
            
            circuit.barrier()
        
        # Step 2: BBPSSW distillation protocol
        # Bilateral CNOT: target pair (q0, q1) controls ancilla pair (q2, q3)
        
        # Alice side: q0 (target) controls q2 (ancilla)
        circuit.cx(0, 2)
        
        # Bob side: q1 (target) controls q3 (ancilla)
        circuit.cx(1, 3)
        
        circuit.barrier()
        
        # Step 3: Measure ancilla qubits
        circuit.measure(2, cr_ancilla[0])
        circuit.measure(3, cr_ancilla[1])
        
        # Step 4: Optionally measure output pair (for fidelity estimation)
        if measure_output:
            circuit.barrier()
            circuit.measure(0, cr_output[0])
            circuit.measure(1, cr_output[1])
        
        metadata = {
            'num_qubits': 4,
            'num_bell_pairs': 2,
            'protocol': 'BBPSSW',
            'target_qubits': [0, 1],
            'ancilla_qubits': [2, 3],
            'gate_count': {
                'h': 2 if prepare_bell_pairs else 0,
                'cx': 4 if prepare_bell_pairs else 2,
                'measure': 4 if measure_output else 2
            },
            'depth': circuit.depth(),
            'success_condition': 'ancilla[0] == 0 AND ancilla[1] == 0'
        }
        
        return circuit, metadata
    
    def create_fidelity_measurement_circuits(
        self,
        prepare_bell_pairs: bool = True
    ) -> Dict[str, QuantumCircuit]:
        """
        Create circuits for Bell state fidelity estimation.
        
        Measures in different bases to estimate fidelity:
        - ZZ basis: Measure both qubits in computational basis
        - XX basis: Apply H before measurement
        - YY basis: Apply S†H before measurement
        
        Args:
            prepare_bell_pairs: If True, include Bell pair preparation
            
        Returns:
            Dictionary of measurement circuits
        """
        circuits = {}
        
        # Base circuit: distillation without output measurement
        base_circuit, _ = self.create_hardware_bbpssw_circuit(
            prepare_bell_pairs=prepare_bell_pairs,
            measure_output=False
        )
        
        # ZZ measurement (computational basis)
        qc_zz = base_circuit.copy()
        qc_zz.measure([0, 1], [0, 1])
        circuits['ZZ'] = qc_zz
        
        # XX measurement
        qc_xx = base_circuit.copy()
        qc_xx.h(0)
        qc_xx.h(1)
        qc_xx.measure([0, 1], [0, 1])
        circuits['XX'] = qc_xx
        
        # YY measurement
        qc_yy = base_circuit.copy()
        qc_yy.sdg(0)
        qc_yy.sdg(1)
        qc_yy.h(0)
        qc_yy.h(1)
        qc_yy.measure([0, 1], [0, 1])
        circuits['YY'] = qc_yy
        
        return circuits
    
    # ========================================================================
    # PHASE 2: Backend Selection & Calibration Awareness
    # ========================================================================
    
    def select_best_backend(
        self,
        min_qubits: int = 5,
        simulator: bool = False,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Select best available IBM backend based on calibration data.
        
        Selection criteria:
        - Minimum number of qubits
        - Lowest average CX error rate
        - Shortest queue time
        - Active status
        
        Args:
            min_qubits: Minimum number of qubits required
            simulator: If True, use simulator backend
            verbose: Print backend information
            
        Returns:
            Backend information dictionary
        """
        if simulator:
            # Use Aer simulator
            self.backend = AerSimulator()
            if verbose:
                print("✓ Using AerSimulator (local simulation)")
            
            return {
                'name': 'aer_simulator',
                'num_qubits': 32,
                'simulator': True,
                'properties': {}
            }
        
        # Get available backends
        backends = self.service.backends(
            filters=lambda b: (
                b.num_qubits >= min_qubits and
                b.status().operational and
                not b.configuration().simulator
            )
        )
        
        if not backends:
            raise RuntimeError(f"No operational backends with >= {min_qubits} qubits found")
        
        # Rank backends by quality
        backend_scores = []
        
        for backend in backends:
            try:
                # Get backend properties
                props = backend.properties()
                config = backend.configuration()
                status = backend.status()
                
                # Calculate average CX error
                cx_errors = []
                for gate in props.gates:
                    if gate.gate == 'cx':
                        cx_errors.append(gate.parameters[0].value)
                
                avg_cx_error = np.mean(cx_errors) if cx_errors else 1.0
                
                # Calculate average T1 and T2
                t1_values = [q.t1 for q in props.qubits]
                t2_values = [q.t2 for q in props.qubits]
                avg_t1 = np.mean(t1_values)
                avg_t2 = np.mean(t2_values)
                
                # Get queue length
                pending_jobs = status.pending_jobs
                
                # Score: lower is better
                # Prioritize low CX error, then queue time
                score = avg_cx_error * 1000 + pending_jobs * 0.01
                
                backend_scores.append({
                    'backend': backend,
                    'name': backend.name,
                    'num_qubits': config.num_qubits,
                    'avg_cx_error': avg_cx_error,
                    'avg_t1': avg_t1,
                    'avg_t2': avg_t2,
                    'pending_jobs': pending_jobs,
                    'score': score
                })
                
            except Exception as e:
                if verbose:
                    print(f"Warning: Could not get properties for {backend.name}: {e}")
                continue
        
        if not backend_scores:
            raise RuntimeError("Could not retrieve properties for any backend")
        
        # Sort by score (lower is better)
        backend_scores.sort(key=lambda x: x['score'])
        best = backend_scores[0]
        
        # Set backend
        self.backend = best['backend']
        self.calibration_timestamp = datetime.now()
        
        # Store properties
        self.backend_properties = {
            'name': best['name'],
            'num_qubits': best['num_qubits'],
            'avg_cx_error': best['avg_cx_error'],
            'avg_t1_us': best['avg_t1'] * 1e6,  # Convert to microseconds
            'avg_t2_us': best['avg_t2'] * 1e6,
            'pending_jobs': best['pending_jobs'],
            'calibration_timestamp': self.calibration_timestamp.isoformat()
        }
        
        if verbose:
            print(f"\n✓ Selected backend: {best['name']}")
            print(f"  Qubits: {best['num_qubits']}")
            print(f"  Avg CX error: {best['avg_cx_error']:.4f}")
            print(f"  Avg T1: {best['avg_t1']*1e6:.1f} μs")
            print(f"  Avg T2: {best['avg_t2']*1e6:.1f} μs")
            print(f"  Queue: {best['pending_jobs']} jobs")
            print(f"  Calibration: {self.calibration_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
            
            if len(backend_scores) > 1:
                print(f"\n  Other available backends:")
                for b in backend_scores[1:4]:  # Show top 3 alternatives
                    print(f"    - {b['name']}: CX={b['avg_cx_error']:.4f}, Queue={b['pending_jobs']}")
        
        return self.backend_properties
    
    def get_noise_model_from_backend(self) -> Optional[NoiseModel]:
        """
        Create Aer noise model from backend calibration data.
        
        Returns:
            NoiseModel for simulation, or None if backend not set
        """
        if self.backend is None:
            return None
        
        if isinstance(self.backend, AerSimulator):
            return None
        
        try:
            from qiskit_aer.noise import NoiseModel
            noise_model = NoiseModel.from_backend(self.backend)
            return noise_model
        except Exception as e:
            print(f"Warning: Could not create noise model: {e}")
            return None
    
    # ========================================================================
    # PHASE 3: Execution via Qiskit Runtime
    # ========================================================================
    
    def execute_on_hardware(
        self,
        circuit: QuantumCircuit,
        shots: int = 4096,
        optimization_level: int = 3,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Execute circuit on IBM Quantum hardware via Qiskit Runtime.
        
        Args:
            circuit: Circuit to execute
            shots: Number of measurement shots
            optimization_level: Transpiler optimization level (0-3)
            verbose: Print execution information
            
        Returns:
            Execution results dictionary
        """
        if self.backend is None:
            raise RuntimeError("No backend selected. Call select_best_backend() first.")
        
        start_time = time.time()
        
        # Transpile circuit for backend
        if verbose:
            print(f"\nTranspiling circuit for {self.backend.name}...")
        
        pm = generate_preset_pass_manager(
            optimization_level=optimization_level,
            backend=self.backend
        )
        transpiled = pm.run(circuit)
        
        transpile_time = time.time() - start_time
        
        if verbose:
            print(f"  Original depth: {circuit.depth()}")
            print(f"  Transpiled depth: {transpiled.depth()}")
            print(f"  Transpile time: {transpile_time:.2f}s")
            print(f"\nSubmitting to {self.backend.name} ({shots} shots)...")
        
        # Execute using Sampler
        execution_start = time.time()
        
        if isinstance(self.backend, AerSimulator):
            # Local simulation
            from qiskit import transpile as basic_transpile
            transpiled_sim = basic_transpile(circuit, self.backend)
            job = self.backend.run(transpiled_sim, shots=shots)
            result = job.result()
            counts = result.get_counts()
            
        else:
            # Real hardware via Runtime
            with Session(service=self.service, backend=self.backend) as session:
                sampler = Sampler(session=session)
                
                # Run circuit
                job = sampler.run([transpiled], shots=shots)
                
                if verbose:
                    print(f"  Job ID: {job.job_id()}")
                    print(f"  Status: {job.status()}")
                
                # Wait for result
                result = job.result()
                
                # Extract counts from PubResult
                pub_result = result[0]
                counts = pub_result.data.meas.get_counts()
        
        execution_time = time.time() - execution_start
        total_time = time.time() - start_time
        
        if verbose:
            print(f"✓ Execution complete")
            print(f"  Execution time: {execution_time:.2f}s")
            print(f"  Total time: {total_time:.2f}s")
        
        return {
            'counts': counts,
            'shots': shots,
            'backend': self.backend.name,
            'transpiled_depth': transpiled.depth(),
            'original_depth': circuit.depth(),
            'transpile_time': transpile_time,
            'execution_time': execution_time,
            'total_time': total_time,
            'timestamp': datetime.now().isoformat()
        }
    
    def execute_multiple_circuits(
        self,
        circuits: Dict[str, QuantumCircuit],
        shots: int = 4096,
        optimization_level: int = 3,
        verbose: bool = True
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute multiple circuits on hardware (batch execution).
        
        Args:
            circuits: Dictionary of {name: circuit}
            shots: Number of shots per circuit
            optimization_level: Transpiler optimization level
            verbose: Print execution information
            
        Returns:
            Dictionary of {name: results}
        """
        results = {}
        
        for name, circuit in circuits.items():
            if verbose:
                print(f"\n{'='*60}")
                print(f"Executing circuit: {name}")
                print(f"{'='*60}")
            
            result = self.execute_on_hardware(
                circuit,
                shots=shots,
                optimization_level=optimization_level,
                verbose=verbose
            )
            results[name] = result
        
        return results
    
    # ========================================================================
    # PHASE 4: Fidelity Estimation
    # ========================================================================
    
    def estimate_bell_state_fidelity(
        self,
        measurement_results: Dict[str, Dict[str, Any]],
        target_state: str = 'phi_plus'
    ) -> Dict[str, Any]:
        """
        Estimate Bell state fidelity from measurement statistics.
        
        Uses measurements in ZZ, XX, YY bases to reconstruct fidelity.
        
        For |Φ+⟩ = (|00⟩ + |11⟩)/√2:
        - ZZ: Expect |00⟩ and |11⟩ with equal probability
        - XX: Expect |++⟩ (both in |+⟩ state)
        - YY: Expect specific correlations
        
        Args:
            measurement_results: Results from fidelity measurement circuits
            target_state: Target Bell state ('phi_plus', 'phi_minus', 'psi_plus', 'psi_minus')
            
        Returns:
            Fidelity estimation dictionary
        """
        # Extract counts
        counts_zz = measurement_results.get('ZZ', {}).get('counts', {})
        counts_xx = measurement_results.get('XX', {}).get('counts', {})
        counts_yy = measurement_results.get('YY', {}).get('counts', {})
        
        # Total shots
        total_shots = sum(counts_zz.values())
        
        # For |Φ+⟩ = (|00⟩ + |11⟩)/√2
        if target_state == 'phi_plus':
            # ZZ basis: P(00) + P(11) should be high
            # Note: measurement results are in format 'ancilla_bits output_bits'
            # We need to extract the output bits (last 2 bits)
            
            p_00 = 0
            p_11 = 0
            p_01 = 0
            p_10 = 0
            
            for bitstring, count in counts_zz.items():
                # Extract output bits (last 2 bits after ancilla measurements)
                # Format: 'ancilla[0] ancilla[1]' or just 'output[0] output[1]'
                bits = bitstring.replace(' ', '')
                if len(bits) >= 2:
                    output_bits = bits[-2:]  # Last 2 bits
                    if output_bits == '00':
                        p_00 += count
                    elif output_bits == '11':
                        p_11 += count
                    elif output_bits == '01':
                        p_01 += count
                    elif output_bits == '10':
                        p_10 += count
            
            # Normalize
            p_00 /= total_shots
            p_11 /= total_shots
            p_01 /= total_shots
            p_10 /= total_shots
            
            # Fidelity estimate from ZZ measurements
            # F ≈ P(00) + P(11) for |Φ+⟩
            fidelity_zz = p_00 + p_11
            
            # XX basis: Should see mostly |++⟩ (both 0 in X basis)
            p_xx_00 = 0
            for bitstring, count in counts_xx.items():
                bits = bitstring.replace(' ', '')
                if len(bits) >= 2:
                    output_bits = bits[-2:]
                    if output_bits == '00':
                        p_xx_00 += count
            p_xx_00 /= total_shots
            
            # YY basis
            p_yy_00 = 0
            for bitstring, count in counts_yy.items():
                bits = bitstring.replace(' ', '')
                if len(bits) >= 2:
                    output_bits = bits[-2:]
                    if output_bits == '00':
                        p_yy_00 += count
            p_yy_00 /= total_shots
            
            # Combined fidelity estimate
            # F = (1 + <ZZ> + <XX> + <YY>) / 4 for |Φ+⟩
            # <ZZ> = P(00) + P(11) - P(01) - P(10)
            # <XX> = 2*P(++) - 1
            # <YY> = 2*P(++) - 1 (similar)
            
            zz_expectation = p_00 + p_11 - p_01 - p_10
            xx_expectation = 2 * p_xx_00 - 1
            yy_expectation = 2 * p_yy_00 - 1
            
            fidelity = (1 + zz_expectation + xx_expectation + yy_expectation) / 4
            
            # Clamp to [0, 1]
            fidelity = max(0.0, min(1.0, fidelity))
            
            # Error bars (simple binomial error)
            error = np.sqrt(fidelity * (1 - fidelity) / total_shots)
            
            return {
                'fidelity': fidelity,
                'error': error,
                'fidelity_lower': max(0, fidelity - 2*error),
                'fidelity_upper': min(1, fidelity + 2*error),
                'zz_expectation': zz_expectation,
                'xx_expectation': xx_expectation,
                'yy_expectation': yy_expectation,
                'probabilities': {
                    'p_00': p_00,
                    'p_11': p_11,
                    'p_01': p_01,
                    'p_10': p_10
                },
                'total_shots': total_shots,
                'target_state': target_state
            }
        
        else:
            raise NotImplementedError(f"Fidelity estimation for {target_state} not implemented")
    
    def apply_post_selection(
        self,
        counts: Dict[str, int],
        success_condition: str = 'ancilla_00'
    ) -> Tuple[Dict[str, int], float]:
        """
        Apply post-selection based on ancilla measurement outcomes.
        
        Args:
            counts: Measurement counts
            success_condition: Post-selection condition
                - 'ancilla_00': Keep only outcomes where ancilla qubits are |00⟩
                
        Returns:
            (post_selected_counts, success_probability)
        """
        total_shots = sum(counts.values())
        post_selected = {}
        success_shots = 0
        
        if success_condition == 'ancilla_00':
            # Keep only outcomes where first 2 bits (ancilla) are 00
            for bitstring, count in counts.items():
                bits = bitstring.replace(' ', '')
                if len(bits) >= 2:
                    ancilla_bits = bits[:2]  # First 2 bits
                    if ancilla_bits == '00':
                        post_selected[bitstring] = count
                        success_shots += count
        
        success_probability = success_shots / total_shots if total_shots > 0 else 0.0
        
        return post_selected, success_probability
    
    # ========================================================================
    # PHASE 5: Integration & Comparison
    # ========================================================================
    
    def run_hardware_validation(
        self,
        shots: int = 4096,
        compare_with_simulation: bool = True,
        verbose: bool = True
    ) -> Dict[str, Any]:
        """
        Complete hardware validation workflow.
        
        Steps:
        1. Create hardware-compatible circuits
        2. Execute on real hardware
        3. Estimate fidelity from measurements
        4. Compare with simulation (if requested)
        5. Generate report
        
        Args:
            shots: Number of measurement shots
            compare_with_simulation: If True, run simulation for comparison
            verbose: Print detailed information
            
        Returns:
            Complete validation results
        """
        if verbose:
            print("\n" + "="*70)
            print("IBM QUANTUM HARDWARE VALIDATION")
            print("Entanglement Distillation Circuit")
            print("="*70)
        
        # Step 1: Create circuits
        if verbose:
            print("\n[1/5] Creating hardware-compatible circuits...")
        
        fidelity_circuits = self.create_fidelity_measurement_circuits(
            prepare_bell_pairs=True
        )
        
        if verbose:
            print(f"  ✓ Created {len(fidelity_circuits)} measurement circuits")
            for name, circ in fidelity_circuits.items():
                print(f"    - {name}: {circ.num_qubits} qubits, depth {circ.depth()}")
        
        # Step 2: Execute on hardware
        if verbose:
            print("\n[2/5] Executing on IBM Quantum hardware...")
        
        hardware_results = self.execute_multiple_circuits(
            fidelity_circuits,
            shots=shots,
            optimization_level=3,
            verbose=verbose
        )
        
        # Step 3: Estimate fidelity
        if verbose:
            print("\n[3/5] Estimating Bell state fidelity...")
        
        fidelity_estimate = self.estimate_bell_state_fidelity(
            hardware_results,
            target_state='phi_plus'
        )
        
        if verbose:
            print(f"  ✓ Hardware fidelity: {fidelity_estimate['fidelity']:.4f} ± {fidelity_estimate['error']:.4f}")
            print(f"    95% CI: [{fidelity_estimate['fidelity_lower']:.4f}, {fidelity_estimate['fidelity_upper']:.4f}]")
        
        # Step 4: Post-selection analysis
        if verbose:
            print("\n[4/5] Analyzing post-selection success rate...")
        
        # Check ZZ measurement for post-selection
        zz_counts = hardware_results['ZZ']['counts']
        post_selected, success_prob = self.apply_post_selection(zz_counts)
        
        if verbose:
            print(f"  ✓ Success probability: {success_prob:.2%}")
            print(f"    ({sum(post_selected.values())}/{sum(zz_counts.values())} shots passed)")
        
        # Step 5: Simulation comparison
        simulation_results = None
        if compare_with_simulation:
            if verbose:
                print("\n[5/5] Running simulation for comparison...")
            
            # Create noise model from backend
            noise_model = self.get_noise_model_from_backend()
            
            # Run simulation
            simulator = AerSimulator(noise_model=noise_model) if noise_model else AerSimulator()
            
            sim_results = {}
            for name, circuit in fidelity_circuits.items():
                from qiskit import transpile as basic_transpile
                transpiled = basic_transpile(circuit, simulator)
                job = simulator.run(transpiled, shots=shots)
                result = job.result()
                sim_results[name] = {
                    'counts': result.get_counts(),
                    'shots': shots
                }
            
            # Estimate fidelity from simulation
            sim_fidelity = self.estimate_bell_state_fidelity(
                sim_results,
                target_state='phi_plus'
            )
            
            simulation_results = {
                'fidelity': sim_fidelity,
                'noise_model': 'backend_calibration' if noise_model else 'ideal'
            }
            
            if verbose:
                print(f"  ✓ Simulation fidelity: {sim_fidelity['fidelity']:.4f} ± {sim_fidelity['error']:.4f}")
                print(f"    Difference: {abs(fidelity_estimate['fidelity'] - sim_fidelity['fidelity']):.4f}")
        
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'backend': self.backend_properties,
            'circuits': {
                name: {
                    'depth': circ.depth(),
                    'num_qubits': circ.num_qubits
                }
                for name, circ in fidelity_circuits.items()
            },
            'hardware_results': {
                'fidelity': fidelity_estimate,
                'post_selection': {
                    'success_probability': success_prob,
                    'successful_shots': sum(post_selected.values()),
                    'total_shots': sum(zz_counts.values())
                },
                'execution_info': {
                    name: {
                        'transpiled_depth': res['transpiled_depth'],
                        'execution_time': res['execution_time']
                    }
                    for name, res in hardware_results.items()
                }
            },
            'simulation_results': simulation_results,
            'comparison': {
                'fidelity_difference': abs(
                    fidelity_estimate['fidelity'] - simulation_results['fidelity']['fidelity']
                ) if simulation_results else None,
                'hardware_better': fidelity_estimate['fidelity'] > simulation_results['fidelity']['fidelity']
                if simulation_results else None
            } if simulation_results else None
        }
        
        if verbose:
            print("\n" + "="*70)
            print("VALIDATION COMPLETE")
            print("="*70)
            print(f"\nHardware: {self.backend_properties['name']}")
            print(f"Fidelity: {fidelity_estimate['fidelity']:.4f} ± {fidelity_estimate['error']:.4f}")
            print(f"Success rate: {success_prob:.2%}")
            if simulation_results:
                print(f"\nSimulation fidelity: {simulation_results['fidelity']['fidelity']:.4f}")
                print(f"Difference: {report['comparison']['fidelity_difference']:.4f}")
        
        return report


# ============================================================================
# Utility Functions
# ============================================================================

def save_validation_report(report: Dict[str, Any], filename: str = "hardware_validation_report.json"):
    """Save validation report to JSON file."""
    import json
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    print(f"✓ Report saved to {filename}")


def plot_fidelity_comparison(
    hardware_fidelity: float,
    hardware_error: float,
    simulation_fidelity: Optional[float] = None,
    simulation_error: Optional[float] = None,
    save_path: Optional[str] = None
):
    """
    Plot fidelity comparison between hardware and simulation.
    
    Args:
        hardware_fidelity: Hardware fidelity estimate
        hardware_error: Hardware error bars
        simulation_fidelity: Simulation fidelity (optional)
        simulation_error: Simulation error bars (optional)
        save_path: Path to save plot (optional)
    """
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x_pos = [0]
    fidelities = [hardware_fidelity]
    errors = [hardware_error]
    labels = ['Hardware']
    colors = ['#1f77b4']
    
    if simulation_fidelity is not None:
        x_pos.append(1)
        fidelities.append(simulation_fidelity)
        errors.append(simulation_error if simulation_error else 0)
        labels.append('Simulation')
        colors.append('#ff7f0e')
    
    ax.bar(x_pos, fidelities, yerr=errors, capsize=10, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Fidelity', fontsize=14)
    ax.set_title('Entanglement Distillation: Hardware vs Simulation', fontsize=16, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim([0, 1])
    ax.axhline(y=0.5, color='r', linestyle='--', alpha=0.5, label='Classical threshold')
    ax.grid(axis='y', alpha=0.3)
    ax.legend()
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"✓ Plot saved to {save_path}")
    
    plt.show()
