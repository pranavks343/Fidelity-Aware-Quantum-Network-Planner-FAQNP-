# Security Verification Checklist

## ✅ API Token Protection Verification

This guide helps you verify that your IBM Quantum API token is properly protected.

---

## Quick Verification

Run these commands to verify security:

```bash
# 1. Check if config file is ignored
git status | grep ibm_config.py
# Expected: NO OUTPUT (file should not appear)

# 2. Check .gitignore
cat .gitignore | grep ibm_config
# Expected: ibm_config.py

# 3. Verify token is not in committed files
git log --all --full-history --source --pretty=format: -- ibm_config.py | wc -l
# Expected: 0 (no history for this file)

# 4. Check for hardcoded tokens in tracked files
git grep -i "QQ5jnejkbzeJDKr" -- '*.py' '*.ipynb' '*.md'
# Expected: NO MATCHES (or only in this verification doc)
```

---

## Detailed Verification Steps

### Step 1: Verify .gitignore

```bash
cat .gitignore
```

**Should contain**:
```
# IBM Quantum API credentials
ibm_config.py
ibm_config.json
.ibm_quantum_token
*.token
```

### Step 2: Check Git Status

```bash
git status
```

**Should NOT show**:
- `ibm_config.py`
- Any `*.token` files
- `ibm_validation_report.json`
- `fidelity_comparison.png`

### Step 3: Verify Template File

```bash
cat ibm_config_template.py | grep IBM_API_TOKEN
```

**Should show**:
```python
IBM_API_TOKEN = "your_token_here"
```

**Should NOT show** your actual token.

### Step 4: Check Committed Files

```bash
# Check example script
cat ibm_example.py | grep -A 5 "IBM_API_TOKEN"
```

**Should show** import statement, NOT hardcoded token:
```python
from ibm_config import IBM_API_TOKEN
```

### Step 5: Verify Config File Exists Locally

```bash
ls -la ibm_config.py
```

**Expected**: File exists (for your local use)

```bash
git ls-files | grep ibm_config.py
```

**Expected**: NO OUTPUT (not tracked by git)

---

## Security Checklist

- [ ] ✅ `ibm_config.py` is in `.gitignore`
- [ ] ✅ `ibm_config.py` does NOT appear in `git status`
- [ ] ✅ `ibm_config_template.py` has placeholder only
- [ ] ✅ No hardcoded tokens in `ibm_example.py`
- [ ] ✅ No hardcoded tokens in `ibm_hardware_demo.ipynb`
- [ ] ✅ Token is loaded from config file or environment variable
- [ ] ✅ `ibm_config.py` has never been committed (check git log)
- [ ] ✅ Generated reports are in `.gitignore`

---

## What's Protected

### Files in .gitignore (NOT committed):
- ✅ `ibm_config.py` - Your actual token
- ✅ `ibm_config.json` - Alternative config
- ✅ `.ibm_quantum_token` - Token files
- ✅ `*.token` - Any token files
- ✅ `ibm_validation_report.json` - Generated reports
- ✅ `fidelity_comparison.png` - Generated plots
- ✅ `.ipynb_checkpoints/` - Jupyter checkpoints
- ✅ `.env` - Environment variables

### Files Committed (Safe):
- ✅ `ibm_config_template.py` - Template with placeholder
- ✅ `ibm_example.py` - Imports from config
- ✅ `ibm_hardware_demo.ipynb` - Imports from config
- ✅ `.gitignore` - Protection rules
- ✅ `IBM_CONFIG_README.md` - Configuration guide
- ✅ `SECURITY_VERIFICATION.md` - This file

---

## Common Issues

### Issue: `ibm_config.py` appears in git status

**Cause**: File was added before .gitignore was updated

**Solution**:
```bash
# Remove from git tracking (keeps local file)
git rm --cached ibm_config.py

# Verify it's gone
git status

# Commit the removal
git commit -m "Remove ibm_config.py from tracking"
git push
```

### Issue: Token was committed in the past

**Cause**: Token was committed before security measures

**Solution**:
1. **Rotate your token immediately**:
   - Go to https://quantum.ibm.com/account
   - Generate a new token
   - Update `ibm_config.py`

2. **Remove from git history** (advanced):
   ```bash
   # WARNING: This rewrites history
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch ibm_config.py" \
     --prune-empty --tag-name-filter cat -- --all
   
   # Force push (use with caution)
   git push origin --force --all
   ```

3. **Alternative**: Use BFG Repo-Cleaner:
   ```bash
   # Install BFG
   brew install bfg  # Mac
   
   # Remove file from history
   bfg --delete-files ibm_config.py
   
   # Clean up
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive
   
   # Force push
   git push origin --force --all
   ```

### Issue: Token in notebook output

**Cause**: Notebook was run and saved with token in output

**Solution**:
```bash
# Clear all notebook outputs
jupyter nbconvert --clear-output --inplace ibm_hardware_demo.ipynb

# Verify
git diff ibm_hardware_demo.ipynb

# Commit
git add ibm_hardware_demo.ipynb
git commit -m "Clear notebook outputs"
git push
```

---

## Best Practices

### ✅ DO:

1. **Use config file for local development**:
   ```bash
   cp ibm_config_template.py ibm_config.py
   # Edit ibm_config.py with your token
   ```

2. **Use environment variables for CI/CD**:
   ```bash
   export IBM_QUANTUM_TOKEN="your_token"
   ```

3. **Verify before committing**:
   ```bash
   git status  # Check what's being committed
   git diff    # Review changes
   ```

4. **Clear notebook outputs before committing**:
   ```bash
   jupyter nbconvert --clear-output --inplace *.ipynb
   ```

5. **Rotate tokens periodically**:
   - Every 3-6 months
   - After any security incident
   - When team members leave

### ❌ DON'T:

1. **Never hardcode tokens**:
   ```python
   # BAD
   IBM_API_TOKEN = "actual_token_here"
   
   # GOOD
   from ibm_config import IBM_API_TOKEN
   ```

2. **Never commit config files with tokens**:
   ```bash
   # BAD
   git add ibm_config.py
   
   # GOOD
   git add ibm_config_template.py
   ```

3. **Never share tokens publicly**:
   - Don't post in issues
   - Don't include in screenshots
   - Don't share in chat/email

4. **Never commit notebook outputs with tokens**:
   ```bash
   # Clear outputs before committing
   jupyter nbconvert --clear-output --inplace *.ipynb
   ```

---

## Emergency Response

### If Token is Exposed

1. **Immediately rotate token**:
   - Go to https://quantum.ibm.com/account
   - Generate new token
   - Update `ibm_config.py`

2. **Remove from git history** (if committed):
   - See "Token was committed in the past" above

3. **Notify IBM Quantum** (if public exposure):
   - Contact support: https://quantum.ibm.com/support

4. **Review access logs**:
   - Check for unauthorized usage
   - Monitor your account activity

---

## Automated Verification

### Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash

# Check for hardcoded tokens
if git diff --cached | grep -i "QQ5jnejkbzeJDKr"; then
    echo "ERROR: Hardcoded token detected!"
    echo "Please use ibm_config.py instead."
    exit 1
fi

# Check if ibm_config.py is being committed
if git diff --cached --name-only | grep "ibm_config.py"; then
    echo "ERROR: ibm_config.py should not be committed!"
    echo "This file is in .gitignore for security."
    exit 1
fi

echo "✓ Security checks passed"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions (CI/CD)

Add to `.github/workflows/security-check.yml`:

```yaml
name: Security Check

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Check for hardcoded tokens
        run: |
          if grep -r "QQ5jnejkbzeJDKr" --include="*.py" --include="*.ipynb" .; then
            echo "ERROR: Hardcoded token found!"
            exit 1
          fi
          echo "✓ No hardcoded tokens found"
      
      - name: Verify .gitignore
        run: |
          if ! grep -q "ibm_config.py" .gitignore; then
            echo "ERROR: ibm_config.py not in .gitignore!"
            exit 1
          fi
          echo "✓ .gitignore configured correctly"
```

---

## Verification Report

Run this script to generate a security report:

```bash
#!/bin/bash

echo "================================"
echo "Security Verification Report"
echo "================================"
echo ""

echo "1. Checking .gitignore..."
if grep -q "ibm_config.py" .gitignore; then
    echo "   ✓ ibm_config.py is in .gitignore"
else
    echo "   ✗ ibm_config.py NOT in .gitignore"
fi

echo ""
echo "2. Checking git status..."
if git status | grep -q "ibm_config.py"; then
    echo "   ✗ ibm_config.py appears in git status (should be ignored)"
else
    echo "   ✓ ibm_config.py is properly ignored"
fi

echo ""
echo "3. Checking for hardcoded tokens..."
if git grep -i "QQ5jnejkbzeJDKr" -- '*.py' '*.ipynb' | grep -v "SECURITY_VERIFICATION.md"; then
    echo "   ✗ Hardcoded token found!"
else
    echo "   ✓ No hardcoded tokens in tracked files"
fi

echo ""
echo "4. Checking config file exists locally..."
if [ -f "ibm_config.py" ]; then
    echo "   ✓ ibm_config.py exists locally"
else
    echo "   ⚠ ibm_config.py not found (create from template)"
fi

echo ""
echo "5. Checking template file..."
if grep -q "your_token_here" ibm_config_template.py; then
    echo "   ✓ Template has placeholder only"
else
    echo "   ✗ Template may contain actual token"
fi

echo ""
echo "================================"
echo "Verification Complete"
echo "================================"
```

Save as `verify_security.sh` and run:
```bash
chmod +x verify_security.sh
./verify_security.sh
```

---

## Summary

Your API token is now properly protected:

✅ **Not committed to git** (in .gitignore)  
✅ **Not hardcoded** (loaded from config)  
✅ **Template provided** (easy setup)  
✅ **Multiple options** (config file, env var)  
✅ **Clear documentation** (this guide)  

**Status**: 🔒 **SECURE**

For questions, see `IBM_CONFIG_README.md`.
