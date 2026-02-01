# IBM Quantum Hardware - Quick Start Guide

Get started with IBM Quantum hardware validation in 5 minutes!

---

## Prerequisites

1. **IBM Quantum Account**
   - Sign up at: https://quantum.ibm.com/
   - Get your API token from: https://quantum.ibm.com/account

2. **Python Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

---

## Option 1: Run Example Script (Fastest)

### Step 1: Configure API Token

Edit `ibm_example.py`:
```python
IBM_API_TOKEN = "your_token_here"  # Replace with your token
```

### Step 2: Run with Simulator (No Queue Time)

```bash
python ibm_example.py
```

This runs in ~30 seconds and generates:
- `ibm_validation_report.json` - Detailed results
- `fidelity_comparison.png` - Visualization

### Step 3: Run on Real Hardware (Optional)

Edit `ibm_example.py`:
```python
USE_REAL_HARDWARE = True  # Enable real hardware
```

Then run:
```bash
python ibm_example.py
```

⚠️ This uses real quantum hardware and may take 5-15 minutes (queue time + execution).

---

## Option 2: Interactive Notebook (Recommended)

### Step 1: Start Jupyter

```bash
jupyter notebook ibm_hardware_demo.ipynb
```

### Step 2: Follow the Notebook

The notebook walks you through:
1. Connecting to IBM Quantum
2. Selecting the best backend
3. Creating distillation circuits
4. Executing on hardware
5. Analyzing results

### Step 3: Experiment!

Try:
- Different backends
- Different shot counts
- Real hardware vs simulation
- Custom circuits

---

## Option 3: Programmatic Usage

### Minimal Example

```python
from ibm_hardware import IBMQuantumHardwareValidator

# Initialize
validator = IBMQuantumHardwareValidator(api_token="your_token")

# Select backend (simulator for testing)
validator.select_best_backend(min_qubits=5, simulator=True)

# Run validation
report = validator.run_hardware_validation(
    shots=4096,
    compare_with_simulation=True,
    verbose=True
)

# Access results
fidelity = report['hardware_results']['fidelity']['fidelity']
print(f"Fidelity: {fidelity:.4f}")
```

---

## Expected Output

```
╔══════════════════════════════════════════════════════════════════════╗
║  IBM Quantum Hardware Validation                                    ║
║  Entanglement Distillation Circuit Testing                          ║
╚══════════════════════════════════════════════════════════════════════╝

✓ Connected to IBM Quantum: ibm-q/open/main

✓ Selected backend: aer_simulator
  Qubits: 32

[1/5] Creating hardware-compatible circuits...
  ✓ Created 3 measurement circuits

[2/5] Executing on IBM Quantum hardware...
  ✓ Execution complete

[3/5] Estimating Bell state fidelity...
  ✓ Hardware fidelity: 0.8234 ± 0.0156

[4/5] Analyzing post-selection success rate...
  ✓ Success probability: 67.34%

[5/5] Running simulation for comparison...
  ✓ Simulation fidelity: 0.8456 ± 0.0142

╔══════════════════════════════════════════════════════════════════════╗
║  VALIDATION COMPLETE                                                 ║
╚══════════════════════════════════════════════════════════════════════╝

Hardware: aer_simulator
Fidelity: 0.8234 ± 0.0156
Success rate: 67.34%

✓ Validation complete!
```

---

## Understanding Results

### Fidelity

- **F > 0.5**: Entanglement detected! ✓
- **F > 0.7**: High-quality entanglement ✓✓
- **F > 0.9**: Excellent (rare on NISQ hardware)

### Success Probability

- **50-80%**: Typical for BBPSSW distillation
- Higher success = lower fidelity improvement
- Lower success = higher fidelity improvement

### Hardware vs Simulation

- Simulation usually 2-5% higher
- Real hardware has additional noise
- Gap indicates hardware quality

---

## Troubleshooting

### "No backends available"

**Solution**: Use simulator
```python
validator.select_best_backend(simulator=True)
```

### "Invalid token"

**Solution**: Check your token
1. Go to https://quantum.ibm.com/account
2. Copy the token (click "Copy token")
3. Paste into `ibm_example.py`

### "Job failed"

**Solution**: Try different backend or simulator
```python
validator.select_best_backend(simulator=True)
```

### Import errors

**Solution**: Reinstall dependencies
```bash
pip install --upgrade qiskit qiskit-ibm-runtime qiskit-aer
```

---

## Next Steps

1. **Read Full Documentation**
   - `IBM_HARDWARE_README.md` - Complete guide
   - `NISQ_LIMITATIONS.md` - Reality check

2. **Run Tests**
   ```bash
   python test_ibm_hardware.py
   ```

3. **Experiment**
   - Try different backends
   - Compare multiple devices
   - Optimize circuit depth
   - Vary shot counts

4. **Integrate with Game**
   - Validate your distillation circuits
   - Compare with game server results
   - Optimize for real hardware

---

## Key Files

| File | Purpose |
|------|---------|
| `ibm_hardware.py` | Main implementation |
| `ibm_example.py` | Quick start script |
| `ibm_hardware_demo.ipynb` | Interactive tutorial |
| `IBM_HARDWARE_README.md` | Full documentation |
| `NISQ_LIMITATIONS.md` | Reality check |
| `test_ibm_hardware.py` | Test suite |

---

## Getting Help

1. **Check Documentation**
   - Start with `IBM_HARDWARE_README.md`
   - Read `NISQ_LIMITATIONS.md` for context

2. **Run Tests**
   ```bash
   python test_ibm_hardware.py
   ```

3. **Check IBM Quantum Status**
   - https://quantum.ibm.com/services/resources

4. **Qiskit Documentation**
   - https://docs.quantum.ibm.com/

---

## Tips for Success

### 1. Start with Simulator
- No queue time
- Fast iteration
- Free testing

### 2. Use Least Busy Backend
```python
from qiskit_ibm_runtime import QiskitRuntimeService
service = QiskitRuntimeService()
backend = service.least_busy(min_num_qubits=5)
```

### 3. Optimize Shots
- Quick test: 1024 shots
- Standard: 4096 shots
- High precision: 8192+ shots

### 4. Monitor Queue
```python
status = backend.status()
print(f"Queue: {status.pending_jobs} jobs")
```

### 5. Run During Off-Peak
- US: Late night / early morning
- Europe: Afternoon / evening
- Asia: Morning / midday

---

## Example Session

```bash
# 1. Install
pip install -r requirements.txt

# 2. Quick test with simulator
python ibm_example.py

# 3. Check results
cat ibm_validation_report.json
open fidelity_comparison.png

# 4. Run tests
python test_ibm_hardware.py

# 5. Try notebook
jupyter notebook ibm_hardware_demo.ipynb
```

**Time: ~5 minutes total**

---

## Success Checklist

- [ ] IBM Quantum account created
- [ ] API token obtained
- [ ] Dependencies installed
- [ ] Example script runs successfully
- [ ] Results generated (JSON + PNG)
- [ ] Tests pass
- [ ] Notebook explored
- [ ] Documentation read

---

## Ready to Go!

You're now ready to validate entanglement distillation circuits on IBM Quantum hardware!

**Remember:**
- Start with simulator (fast, free)
- Read `NISQ_LIMITATIONS.md` for context
- Use real hardware sparingly (queue time)
- Have fun exploring quantum computing!

**Questions?** Check `IBM_HARDWARE_README.md` for detailed documentation.

**Happy quantum computing! 🚀**
