"""
Example: Running Entanglement Distillation on IBM Quantum Hardware

This script demonstrates how to:
1. Connect to IBM Quantum
2. Select the best available backend
3. Execute distillation circuits
4. Estimate fidelity from measurements
5. Compare with simulation

IMPORTANT: This validates distillation circuits on real hardware.
It does NOT implement actual quantum networking (which IBM doesn't support).
"""

from hardware.ibm_hardware import IBMQuantumHardwareValidator, plot_fidelity_comparison, save_validation_report
import sys
import os

# ============================================================================
# Configuration
# ============================================================================

# Try to import from config file, fall back to environment variable or prompt
try:
    from config.ibm_config import (
        IBM_API_TOKEN,
        IBM_HUB,
        IBM_GROUP,
        IBM_PROJECT,
        DEFAULT_SHOTS,
        USE_REAL_HARDWARE,
        MIN_QUBITS
    )
    print("✓ Loaded configuration from ibm_config.py")
except ImportError:
    print("⚠️  ibm_config.py not found. Checking environment variables...")
    
    # Try environment variable
    IBM_API_TOKEN = os.environ.get('IBM_QUANTUM_TOKEN')
    
    if not IBM_API_TOKEN:
        print("\n" + "="*70)
        print("IBM Quantum API Token Required")
        print("="*70)
        print("\nTo get your token:")
        print("1. Go to https://quantum.ibm.com/account")
        print("2. Click 'Copy token'")
        print("3. Create ibm_config.py from ibm_config_template.py")
        print("   OR set environment variable: export IBM_QUANTUM_TOKEN='your_token'")
        print("\nFor security, the token is NOT hardcoded in this script.")
        print("="*70)
        sys.exit(1)
    
    # Default values
    IBM_HUB = "ibm-q"
    IBM_GROUP = "open"
    IBM_PROJECT = "main"
    DEFAULT_SHOTS = 4096
    USE_REAL_HARDWARE = False
    MIN_QUBITS = 5
    print("✓ Using environment variable IBM_QUANTUM_TOKEN")

# Use configuration
SHOTS = DEFAULT_SHOTS
# Execution parameters can be overridden here if needed


# ============================================================================
# Main Execution
# ============================================================================

def main():
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  IBM Quantum Hardware Validation                                    ║
║  Entanglement Distillation Circuit Testing                          ║
║                                                                      ║
║  This script validates BBPSSW distillation on real quantum hardware ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)
    
    # Step 1: Initialize validator
    print("\n[STEP 1] Initializing IBM Quantum connection...")
    try:
        validator = IBMQuantumHardwareValidator(
            api_token=IBM_API_TOKEN,
            hub=IBM_HUB,
            group=IBM_GROUP,
            project=IBM_PROJECT
        )
    except Exception as e:
        print(f"✗ Failed to initialize: {e}")
        print("\nPlease check:")
        print("  1. Your API token is correct")
        print("  2. You have internet connection")
        print("  3. Your IBM Quantum account is active")
        sys.exit(1)
    
    # Step 2: Select backend
    print("\n[STEP 2] Selecting optimal backend...")
    try:
        backend_info = validator.select_best_backend(
            min_qubits=MIN_QUBITS,
            simulator=not USE_REAL_HARDWARE,
            verbose=True
        )
    except Exception as e:
        print(f"✗ Failed to select backend: {e}")
        sys.exit(1)
    
    # Step 3: Create and inspect circuits
    print("\n[STEP 3] Creating hardware-compatible circuits...")
    circuit, metadata = validator.create_hardware_bbpssw_circuit(
        prepare_bell_pairs=True,
        measure_output=True
    )
    
    print(f"\n✓ Circuit created:")
    print(f"  Protocol: {metadata['protocol']}")
    print(f"  Qubits: {metadata['num_qubits']}")
    print(f"  Depth: {metadata['depth']}")
    print(f"  Target qubits: {metadata['target_qubits']}")
    print(f"  Ancilla qubits: {metadata['ancilla_qubits']}")
    print(f"  Success condition: {metadata['success_condition']}")
    
    print("\n  Circuit diagram:")
    print(circuit.draw(output='text', fold=-1))
    
    # Step 4: Run validation
    print("\n[STEP 4] Running hardware validation...")
    print(f"  Shots: {SHOTS}")
    print(f"  Backend: {backend_info['name']}")
    
    if USE_REAL_HARDWARE:
        print("\n⚠️  WARNING: Using real quantum hardware")
        print("  This will use queue time and may take several minutes.")
        response = input("  Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            sys.exit(0)
    
    try:
        report = validator.run_hardware_validation(
            shots=SHOTS,
            compare_with_simulation=True,
            verbose=True
        )
    except Exception as e:
        print(f"\n✗ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 5: Save results
    print("\n[STEP 5] Saving results...")
    save_validation_report(report, filename="ibm_validation_report.json")
    
    # Step 6: Visualize results
    print("\n[STEP 6] Generating plots...")
    hardware_fid = report['hardware_results']['fidelity']
    sim_fid = report['simulation_results']['fidelity'] if report['simulation_results'] else None
    
    plot_fidelity_comparison(
        hardware_fidelity=hardware_fid['fidelity'],
        hardware_error=hardware_fid['error'],
        simulation_fidelity=sim_fid['fidelity'] if sim_fid else None,
        simulation_error=sim_fid['error'] if sim_fid else None,
        save_path="fidelity_comparison.png"
    )
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nBackend: {backend_info['name']}")
    print(f"Shots: {SHOTS}")
    print(f"\nResults:")
    print(f"  Hardware fidelity: {hardware_fid['fidelity']:.4f} ± {hardware_fid['error']:.4f}")
    print(f"  Post-selection success: {report['hardware_results']['post_selection']['success_probability']:.2%}")
    
    if sim_fid:
        print(f"  Simulation fidelity: {sim_fid['fidelity']:.4f} ± {sim_fid['error']:.4f}")
        print(f"  Difference: {report['comparison']['fidelity_difference']:.4f}")
        
        if hardware_fid['fidelity'] > sim_fid['fidelity']:
            print("  → Hardware performed BETTER than simulation")
        else:
            print("  → Simulation performed better (expected for noisy hardware)")
    
    print(f"\nFiles generated:")
    print(f"  - ibm_validation_report.json")
    print(f"  - fidelity_comparison.png")
    
    print("\n✓ Validation complete!")


if __name__ == "__main__":
    main()
