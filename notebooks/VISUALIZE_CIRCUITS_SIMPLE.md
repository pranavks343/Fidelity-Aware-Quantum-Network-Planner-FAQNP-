# Entanglement Distillation Circuit Visualizations

## Quick Setup Guide

Since you're getting the ipykernel error, here are your options:

### Option 1: Use Existing Python Environment (Recommended)

If you already have qiskit installed somewhere, you can run the visualization directly:

```bash
cd /Users/pranavks/MIT/2026-IonQ/notebooks

# If you have conda:
conda activate your_quantum_env
jupyter notebook SHOW_CIRCUITS.ipynb

# Or if you have a system Python with qiskit:
python3 -m jupyter notebook SHOW_CIRCUITS.ipynb
```

### Option 2: Install in User Space

```bash
pip3 install --user qiskit qiskit-aer matplotlib ipykernel jupyter
python3 -m jupyter notebook SHOW_CIRCUITS.ipynb
```

### Option 3: Run the Standalone Script

I've created a simpler Python script that you can run directly:

```bash
cd /Users/pranavks/MIT/2026-IonQ/notebooks
python3 generate_circuit_diagrams.py
```

This will generate PNG images of all the circuits without needing Jupyter.

---

## What You'll See

The visualizations show the **EXACT** circuits from your implementation:

### BBPSSW Protocol
- **Purpose**: Distillation for depolarizing noise
- **Method**: Bilateral CNOT gates
- **Configurations**: 2, 3, and 4 Bell pairs
- **Key Feature**: Simple, robust implementation

### DEJMPS Protocol  
- **Purpose**: Distillation for phase noise
- **Method**: X and Z basis parity checks
- **Configurations**: 2, 3, and 4 Bell pairs
- **Key Feature**: Better for phase-damping channels

### Circuit Details Shown:
- Complete quantum circuit diagrams
- Qubit counts and circuit depths
- Gate counts (CNOT, H, Measure)
- Target and ancilla qubit assignments
- Flag bits for post-selection

---

## Alternative: View Text Representation

If you just want to see the circuit structure without graphics, run:

```bash
cd /Users/pranavks/MIT/2026-IonQ
python3 -c "
import sys
sys.path.insert(0, '.')
from distillation.distillation import create_bbpssw_circuit, create_dejmps_circuit

print('='*80)
print('BBPSSW CIRCUIT (3 Bell Pairs)')
print('='*80)
circuit, flag = create_bbpssw_circuit(3)
print(circuit.draw(output='text', fold=-1))
print(f'\nDepth: {circuit.depth()}, Gates: {circuit.count_ops()}, Flag: {flag}')

print('\n' + '='*80)
print('DEJMPS CIRCUIT (3 Bell Pairs)')
print('='*80)
circuit2, flag2 = create_dejmps_circuit(3)
print(circuit2.draw(output='text', fold=-1))
print(f'\nDepth: {circuit2.depth()}, Gates: {circuit2.count_ops()}, Flag: {flag2}')
"
```

This will show ASCII art representations of the circuits in your terminal!
