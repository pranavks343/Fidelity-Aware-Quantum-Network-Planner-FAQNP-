# IBM Quantum Hardware Integration

## Overview

This module adapts the quantum network entanglement distillation project to execute on **real IBM Quantum hardware** for validation and benchmarking.

### ⚠️ Important Limitations

- **IBM Quantum does NOT support real quantum networking**
- **No inter-device entanglement distribution**
- **This is a HARDWARE-VALIDATION PROTOTYPE**

### Purpose

1. ✅ Validate entanglement distillation circuits on real noisy quantum hardware
2. ✅ Compare real hardware results with simulated fidelity estimates
3. ✅ Demonstrate NISQ-era quantum circuit design
4. ✅ Understand hardware noise characteristics

---

## Architecture

### Phase 1: Hardware-Compatible Distillation Circuits

**Implementation**: `create_hardware_bbpssw_circuit()`

- Uses **2 Bell pairs** (4 qubits total)
- Native IBM gate set: `CX`, `RZ`, `SX`, `X`, `Measurement`
- Low circuit depth for NISQ devices
- BBPSSW-style bilateral CNOT protocol

**Circuit Structure**:
```
Pair 0 (q0, q1): Data pair (target)
Pair 1 (q2, q3): Ancilla pair

Protocol:
1. Prepare Bell pairs: H-CX on each pair
2. Bilateral CNOT: q0→q2, q1→q3
3. Measure ancilla qubits (q2, q3)
4. Post-select on ancilla = |00⟩
```

### Phase 2: Backend Selection & Calibration Awareness

**Implementation**: `select_best_backend()`

Automatically selects the best available IBM backend based on:
- ✅ Minimum qubit count (≥5 qubits)
- ✅ Lowest average CX error rate
- ✅ Shortest queue time
- ✅ Active operational status

**Calibration Data Extracted**:
- T1, T2 coherence times
- Gate error rates (CX, single-qubit)
- Readout error
- Calibration timestamp

### Phase 3: Execution via Qiskit Runtime

**Implementation**: `execute_on_hardware()`

- Uses **Qiskit Runtime Sampler** for efficient execution
- Transpiles circuits to native gate set
- Optimization level 3 (maximum optimization)
- Supports both real hardware and Aer simulation

### Phase 4: Fidelity Estimation

**Implementation**: `estimate_bell_state_fidelity()`

Estimates Bell state fidelity using multi-basis measurements:

1. **ZZ basis**: Computational basis measurement
   - Expect P(00) + P(11) ≈ 1 for |Φ+⟩

2. **XX basis**: X-basis measurement (apply H before measuring)
   - Expect P(++) ≈ 1 for |Φ+⟩

3. **YY basis**: Y-basis measurement (apply S†H before measuring)
   - Provides additional correlation information

**Fidelity Formula**:
```
F = (1 + ⟨ZZ⟩ + ⟨XX⟩ + ⟨YY⟩) / 4
```

**Post-Selection**:
- Keep only shots where ancilla qubits measure |00⟩
- Reports success probability
- Estimates effective fidelity improvement

### Phase 5: Integration with Existing Project

**Implementation**: `run_hardware_validation()`

Complete workflow:
1. Create hardware-compatible circuits
2. Execute on IBM Quantum hardware
3. Estimate fidelity from measurement statistics
4. Compare with noisy simulation (using backend noise model)
5. Generate comprehensive validation report

---

## Installation

### 1. Install Dependencies

```bash
pip install qiskit qiskit-ibm-runtime qiskit-aer matplotlib numpy
```

### 2. Get IBM Quantum API Token

1. Go to https://quantum.ibm.com/account
2. Copy your API token
3. Set it in `ibm_example.py`:

```python
IBM_API_TOKEN = "your_token_here"
```

---

## Usage

### Quick Start (Simulation)

```bash
python ibm_example.py
```

This runs the validation using **AerSimulator** (local simulation with noise model).

### Real Hardware Execution

Edit `ibm_example.py`:

```python
USE_REAL_HARDWARE = True  # Enable real hardware
```

Then run:

```bash
python ibm_example.py
```

⚠️ **Warning**: This uses real quantum hardware queue time!

### Programmatic Usage

```python
from ibm_hardware import IBMQuantumHardwareValidator

# Initialize
validator = IBMQuantumHardwareValidator(api_token="your_token")

# Select backend
validator.select_best_backend(min_qubits=5, simulator=False)

# Create circuit
circuit, metadata = validator.create_hardware_bbpssw_circuit()

# Run validation
report = validator.run_hardware_validation(
    shots=4096,
    compare_with_simulation=True
)

# Access results
fidelity = report['hardware_results']['fidelity']['fidelity']
success_rate = report['hardware_results']['post_selection']['success_probability']

print(f"Fidelity: {fidelity:.4f}")
print(f"Success rate: {success_rate:.2%}")
```

---

## Example Output

```
╔══════════════════════════════════════════════════════════════════════╗
║  IBM Quantum Hardware Validation                                    ║
║  Entanglement Distillation Circuit Testing                          ║
╚══════════════════════════════════════════════════════════════════════╝

✓ Connected to IBM Quantum: ibm-q/open/main

✓ Selected backend: ibm_brisbane
  Qubits: 127
  Avg CX error: 0.0089
  Avg T1: 145.3 μs
  Avg T2: 98.7 μs
  Queue: 3 jobs
  Calibration: 2026-02-01 10:23:45

[1/5] Creating hardware-compatible circuits...
  ✓ Created 3 measurement circuits
    - ZZ: 4 qubits, depth 5
    - XX: 4 qubits, depth 7
    - YY: 4 qubits, depth 9

[2/5] Executing on IBM Quantum hardware...
  Transpiling circuit for ibm_brisbane...
  Original depth: 5
  Transpiled depth: 12
  Transpile time: 1.23s

  Submitting to ibm_brisbane (4096 shots)...
  Job ID: abc123xyz
  Status: JobStatus.RUNNING
  ✓ Execution complete
  Execution time: 45.67s

[3/5] Estimating Bell state fidelity...
  ✓ Hardware fidelity: 0.8234 ± 0.0156

[4/5] Analyzing post-selection success rate...
  ✓ Success probability: 67.34%
    (2758/4096 shots passed)

[5/5] Running simulation for comparison...
  ✓ Simulation fidelity: 0.8456 ± 0.0142
    Difference: 0.0222

╔══════════════════════════════════════════════════════════════════════╗
║  VALIDATION COMPLETE                                                 ║
╚══════════════════════════════════════════════════════════════════════╝

Hardware: ibm_brisbane
Fidelity: 0.8234 ± 0.0156
Success rate: 67.34%

Simulation fidelity: 0.8456
Difference: 0.0222

Files generated:
  - ibm_validation_report.json
  - fidelity_comparison.png

✓ Validation complete!
```

---

## Understanding the Results

### Fidelity Interpretation

- **F > 0.5**: Entanglement present (above classical threshold)
- **F = 0.5**: Maximally mixed state (no entanglement)
- **F < 0.5**: Worse than random (measurement/calibration issues)

**Typical Results**:
- **Ideal**: F = 1.0 (perfect Bell state)
- **Simulation (noisy)**: F = 0.80-0.90
- **Real hardware**: F = 0.70-0.85 (depends on backend quality)

### Success Probability

Post-selection success rate depends on:
- Input Bell pair fidelity
- Hardware noise levels
- Number of ancilla measurements

**Typical Range**: 50-80%

**Trade-off**: 
- Higher success rate → Lower fidelity improvement
- Lower success rate → Higher fidelity improvement

### Hardware vs Simulation

**Expected Behavior**:
- Simulation usually predicts slightly **higher** fidelity
- Real hardware has additional noise sources not captured in noise model
- Difference of 2-5% is typical

**If hardware is better**:
- May indicate overly pessimistic noise model
- Or statistical fluctuation (run more shots)

---

## Integration with Game Server

### Important Notes

1. **Game server remains simulated** - IBM Quantum is used ONLY for validation
2. **No network-wide execution** - Cannot distribute Bell pairs between devices
3. **No score updates from hardware** - Hardware runs are for research/validation only

### Validation Workflow

```python
from ibm_hardware import IBMQuantumHardwareValidator
from distillation import create_bbpssw_circuit

# 1. Design circuit for game
game_circuit, flag_bit = create_bbpssw_circuit(num_bell_pairs=2)

# 2. Validate on hardware (optional)
validator = IBMQuantumHardwareValidator(api_token="...")
validator.select_best_backend(simulator=True)

# Create hardware-compatible version
hw_circuit, metadata = validator.create_hardware_bbpssw_circuit()

# Run validation
report = validator.run_hardware_validation(shots=1024)

# 3. Submit to game server (original circuit)
client.claim_edge(edge, game_circuit, flag_bit, num_bell_pairs=2)
```

---

## Advanced Usage

### Custom Fidelity Measurements

```python
# Create custom measurement circuits
circuits = validator.create_fidelity_measurement_circuits(
    prepare_bell_pairs=True
)

# Execute batch
results = validator.execute_multiple_circuits(
    circuits,
    shots=8192,
    optimization_level=3
)

# Analyze
fidelity = validator.estimate_bell_state_fidelity(results)
```

### Noise Model Extraction

```python
# Get noise model from backend calibration
validator.select_best_backend(simulator=False)
noise_model = validator.get_noise_model_from_backend()

# Use for local simulation
from qiskit_aer import AerSimulator
noisy_sim = AerSimulator(noise_model=noise_model)
```

### Backend Comparison

```python
# Test multiple backends
backends = ['ibm_brisbane', 'ibm_kyoto', 'ibm_osaka']
results = {}

for backend_name in backends:
    validator.backend = validator.service.backend(backend_name)
    report = validator.run_hardware_validation(shots=2048)
    results[backend_name] = report['hardware_results']['fidelity']

# Find best backend
best = max(results.items(), key=lambda x: x[1]['fidelity'])
print(f"Best backend: {best[0]} (F = {best[1]['fidelity']:.4f})")
```

---

## Troubleshooting

### "No backends available"

**Problem**: No IBM backends meet the requirements

**Solutions**:
1. Lower `min_qubits` requirement
2. Use simulator: `select_best_backend(simulator=True)`
3. Check your IBM Quantum account access level

### "Job failed" or "Job cancelled"

**Problem**: Hardware job failed during execution

**Solutions**:
1. Check backend status: https://quantum.ibm.com/services/resources
2. Reduce circuit depth (lower optimization level)
3. Try a different backend
4. Retry after some time (transient errors)

### "Invalid token"

**Problem**: API token is incorrect or expired

**Solutions**:
1. Get new token from https://quantum.ibm.com/account
2. Check token is copied correctly (no extra spaces)
3. Verify account is active

### Fidelity < 0.5

**Problem**: Results worse than classical threshold

**Solutions**:
1. Check circuit is correct (print circuit diagram)
2. Increase number of shots (reduce statistical noise)
3. Try different backend (current one may have high errors)
4. Check calibration timestamp (may need recalibration)

---

## Performance Tips

### Optimize Queue Time

1. **Check queue before submitting**:
   ```python
   backend = validator.backend
   status = backend.status()
   print(f"Queue: {status.pending_jobs} jobs")
   ```

2. **Use least busy backend**:
   ```python
   from qiskit_ibm_runtime import QiskitRuntimeService
   service = QiskitRuntimeService()
   backend = service.least_busy(min_num_qubits=5)
   ```

3. **Run during off-peak hours** (US: late night / early morning)

### Optimize Shots

- **Quick test**: 1024 shots (~10s execution)
- **Standard**: 4096 shots (~40s execution)
- **High precision**: 8192+ shots (~80s+ execution)

**Diminishing returns**: Error scales as 1/√shots

### Optimize Circuit Depth

- Use `optimization_level=3` for maximum transpiler optimization
- Minimize Hadamard gates (expensive on IBM hardware)
- Use native gates when possible (CX, RZ, SX)

---

## Citation

If you use this hardware validation module in your research, please cite:

```bibtex
@software{ibm_quantum_distillation_2026,
  title = {IBM Quantum Hardware Validation for Entanglement Distillation},
  author = {iQuHack 2026 Team},
  year = {2026},
  url = {https://github.com/pranavks343/Fidelity-Aware-Quantum-Network-Planner-FAQNP-}
}
```

---

## References

1. **BBPSSW Protocol**: Bennett et al., "Purification of noisy entanglement and faithful teleportation via noisy channels" (1996)
2. **IBM Quantum**: https://quantum.ibm.com/
3. **Qiskit Runtime**: https://docs.quantum.ibm.com/api/qiskit-ibm-runtime
4. **Bell State Tomography**: James et al., "Measurement of qubits" (2001)

---

## Support

For issues or questions:
1. Check this README
2. Review `ibm_example.py` for working code
3. Consult IBM Quantum documentation
4. Open an issue on GitHub

---

## License

MIT License - See LICENSE file for details
