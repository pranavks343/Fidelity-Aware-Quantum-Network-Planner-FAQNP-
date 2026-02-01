# IBM Quantum API Configuration

## Security Best Practices

Your IBM Quantum API token is **sensitive information** and should **NEVER** be committed to version control.

---

## Setup Instructions

### Option 1: Configuration File (Recommended)

1. **Copy the template**:
   ```bash
   cp ibm_config_template.py ibm_config.py
   ```

2. **Edit `ibm_config.py`**:
   ```python
   IBM_API_TOKEN = "your_actual_token_here"
   ```

3. **Get your token**:
   - Go to https://quantum.ibm.com/account
   - Click "Copy token"
   - Paste into `ibm_config.py`

4. **Verify it's ignored by git**:
   ```bash
   git status  # ibm_config.py should NOT appear
   ```

### Option 2: Environment Variable

Set the environment variable:

**Linux/Mac**:
```bash
export IBM_QUANTUM_TOKEN="your_token_here"
```

**Windows (PowerShell)**:
```powershell
$env:IBM_QUANTUM_TOKEN="your_token_here"
```

**Windows (CMD)**:
```cmd
set IBM_QUANTUM_TOKEN=your_token_here
```

### Option 3: Manual Entry (Notebook Only)

In the Jupyter notebook, directly set:
```python
IBM_API_TOKEN = "your_token_here"
```

⚠️ **Warning**: Don't save the notebook with your token if sharing!

---

## Files

### Committed to Git ✅
- `ibm_config_template.py` - Template with placeholder
- `.gitignore` - Ignores `ibm_config.py`
- `IBM_CONFIG_README.md` - This file

### NOT Committed (In .gitignore) ❌
- `ibm_config.py` - Your actual token
- `ibm_config.json` - Alternative JSON config
- `.ibm_quantum_token` - Token file
- `*.token` - Any token files
- `ibm_validation_report.json` - Generated reports
- `fidelity_comparison.png` - Generated plots

---

## Verification

### Check if config is loaded:

**Python script**:
```bash
python ibm_example.py
```

You should see:
```
✓ Loaded configuration from ibm_config.py
```

**Jupyter notebook**:
Run the configuration cell and check for:
```
✓ Loaded configuration from ibm_config.py
```

### Check git status:

```bash
git status
```

`ibm_config.py` should **NOT** appear in the list!

---

## Configuration Options

### `ibm_config.py` Structure

```python
# IBM Quantum API Token
IBM_API_TOKEN = "your_token_here"

# IBM Quantum Hub/Group/Project
IBM_HUB = "ibm-q"          # Your hub
IBM_GROUP = "open"         # Your group
IBM_PROJECT = "main"       # Your project

# Execution Settings
DEFAULT_SHOTS = 4096       # Number of measurement shots
USE_REAL_HARDWARE = False  # True = real hardware, False = simulator
MIN_QUBITS = 5            # Minimum qubits required
```

### Customization

**For premium access**:
```python
IBM_HUB = "ibm-q-research"
IBM_GROUP = "your-institution"
IBM_PROJECT = "your-project"
```

**For quick testing**:
```python
DEFAULT_SHOTS = 1024
USE_REAL_HARDWARE = False
```

**For production runs**:
```python
DEFAULT_SHOTS = 8192
USE_REAL_HARDWARE = True
MIN_QUBITS = 127  # Use large backends only
```

---

## Troubleshooting

### "ibm_config.py not found"

**Solution**: Create the config file
```bash
cp ibm_config_template.py ibm_config.py
# Edit ibm_config.py with your token
```

### "Invalid token"

**Solutions**:
1. Get a fresh token from https://quantum.ibm.com/account
2. Check for extra spaces or quotes
3. Verify token is copied completely

### "Config file appears in git status"

**Solution**: Check `.gitignore`
```bash
cat .gitignore | grep ibm_config
```

Should show:
```
ibm_config.py
```

If not, add it:
```bash
echo "ibm_config.py" >> .gitignore
```

### "Environment variable not working"

**Check if set**:
```bash
echo $IBM_QUANTUM_TOKEN  # Linux/Mac
echo %IBM_QUANTUM_TOKEN%  # Windows CMD
echo $env:IBM_QUANTUM_TOKEN  # Windows PowerShell
```

**Set permanently**:

**Linux/Mac** (add to `~/.bashrc` or `~/.zshrc`):
```bash
export IBM_QUANTUM_TOKEN="your_token_here"
```

**Windows** (System Properties → Environment Variables):
- Variable name: `IBM_QUANTUM_TOKEN`
- Variable value: `your_token_here`

---

## Security Checklist

- [ ] `ibm_config.py` is in `.gitignore`
- [ ] Token is NOT hardcoded in example scripts
- [ ] Token is NOT in Jupyter notebooks (if sharing)
- [ ] `ibm_config.py` does NOT appear in `git status`
- [ ] Template file (`ibm_config_template.py`) has placeholder only
- [ ] Token is stored securely (not in plain text files in public repos)

---

## Multiple Tokens (Advanced)

If you have multiple IBM Quantum accounts:

### Option 1: Multiple Config Files

```python
# ibm_config_personal.py
IBM_API_TOKEN = "personal_token"

# ibm_config_work.py
IBM_API_TOKEN = "work_token"
```

Load specific config:
```python
from ibm_config_personal import IBM_API_TOKEN
# or
from ibm_config_work import IBM_API_TOKEN
```

### Option 2: Environment-Based

```bash
# Development
export IBM_QUANTUM_TOKEN="dev_token"

# Production
export IBM_QUANTUM_TOKEN="prod_token"
```

---

## Best Practices

### ✅ DO:
- Use `ibm_config.py` for local development
- Use environment variables for CI/CD
- Keep token secure and private
- Rotate tokens periodically
- Use `.gitignore` to prevent commits

### ❌ DON'T:
- Commit tokens to git
- Share tokens publicly
- Hardcode tokens in scripts
- Store tokens in plain text in public repos
- Include tokens in screenshots or logs

---

## Getting Your Token

1. **Sign up** (if you haven't):
   - Go to https://quantum.ibm.com/
   - Click "Sign up" or "Log in"
   - Create a free account

2. **Access your account**:
   - Go to https://quantum.ibm.com/account
   - You'll see your API token

3. **Copy the token**:
   - Click "Copy token"
   - Paste into `ibm_config.py`

4. **Verify access**:
   ```bash
   python ibm_example.py
   ```

---

## Support

### Token Issues
- IBM Quantum Support: https://quantum.ibm.com/support
- Account Management: https://quantum.ibm.com/account

### Configuration Issues
- Check `IBM_CONFIG_README.md` (this file)
- Review `IBM_QUICKSTART.md`
- See `IBM_HARDWARE_README.md` for detailed docs

---

## Summary

**Quick Setup**:
```bash
# 1. Copy template
cp ibm_config_template.py ibm_config.py

# 2. Edit with your token
nano ibm_config.py  # or use any editor

# 3. Verify
python ibm_example.py

# 4. Check git (should not show ibm_config.py)
git status
```

**Security**: ✅ Token is protected by `.gitignore`

**Ready**: ✅ You can now run all examples safely!
