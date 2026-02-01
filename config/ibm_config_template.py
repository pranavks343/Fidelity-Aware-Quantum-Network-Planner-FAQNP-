"""
IBM Quantum Configuration Template

Copy this file to 'ibm_config.py' and add your API token.

To get your API token:
1. Go to https://quantum.ibm.com/account
2. Click "Copy token"
3. Paste it below

IMPORTANT: Never commit ibm_config.py to git!
"""

# IBM Quantum API Token
# Get yours from: https://quantum.ibm.com/account
IBM_API_TOKEN = "QQ5jnejkbzeJDKr_dXvghu-jfAin88S2hRCQAMCxEG1x"

# IBM Quantum Hub/Group/Project
# Default is the free tier
IBM_HUB = "ibm-q"
IBM_GROUP = "open"
IBM_PROJECT = "main"

# Execution Settings
DEFAULT_SHOTS = 4096
USE_REAL_HARDWARE = False  # Set to True to use real quantum hardware
MIN_QUBITS = 5
