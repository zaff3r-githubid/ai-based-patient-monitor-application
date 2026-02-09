# 🔒 GitHub Security Guide - Protecting Your API Key

## ⚠️ CRITICAL: Never Commit Your API Key!

Your API key is like a password - if exposed on GitHub:
- ✅ Anyone can use it
- ✅ You'll get charged for their usage
- ✅ Your account could be suspended
- ✅ Bots scan GitHub 24/7 for exposed keys

---

## ✅ Safe Method for Your Assignment

### Step 1: Create `.gitignore` File

In your project root, create `.gitignore`:

```gitignore
# Protect secrets
.streamlit/secrets.toml
.env
*.env
api_keys.txt

# Python
__pycache__/
*.pyc
venv/
```

This tells Git to **NEVER** track these files.

---

### Step 2: Use Environment Variables (RECOMMENDED for Demo)

**For your assignment video**, use environment variables temporarily:

#### Windows (PowerShell):
```powershell
$env:OPENAI_API_KEY="sk-your-key-here"
streamlit run app_improved.py
```

#### Windows (Command Prompt):
```cmd
set OPENAI_API_KEY=sk-your-key-here
streamlit run app_improved.py
```

#### Mac/Linux:
```bash
export OPENAI_API_KEY="sk-your-key-here"
streamlit run app_improved.py
```

**This key only lives in your terminal session** - not in any file!

---

### Step 3: Document Setup WITHOUT Exposing Key

In your README, write:

```markdown
## Setup Instructions

1. Get an OpenAI API key from https://platform.openai.com/api-keys

2. Set the environment variable:
   - Windows: `set OPENAI_API_KEY=your-key-here`
   - Mac/Linux: `export OPENAI_API_KEY=your-key-here`

3. Run the app:
   ```bash
   streamlit run app_improved.py
   ```
```

---

## 📋 Safe GitHub Submission Checklist

Before pushing to GitHub:

- [ ] ✅ `.gitignore` file created
- [ ] ✅ Run `git status` - verify `secrets.toml` is NOT listed
- [ ] ✅ Include `secrets.toml.example` (with placeholder)
- [ ] ✅ README explains how to add API key (without showing yours)
- [ ] ✅ Test: Clone your repo to another folder and verify no secrets

---

## 🎥 For Your Demo Video

**Option 1: Use Environment Variable** (Safest)
```bash
set OPENAI_API_KEY=sk-yourkey
streamlit run app_improved.py
# Record video
```

**Option 2: Blur API Key in Video**
- If your key appears on screen, blur it in video editing
- Or crop the screen recording to hide the terminal

**Option 3: Use Free Tier**
- Create a temporary API key just for the demo
- Set spending limit to $5
- Delete it after assignment submission

---

## 🚨 What If You Already Committed Your Key?

### Immediate Action:
1. **Revoke the key** at https://platform.openai.com/api-keys
2. **Generate a new key**
3. **Remove from Git history**:

```bash
# Install BFG Repo-Cleaner or use git filter-branch
# Remove secrets from ALL commits
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch .streamlit/secrets.toml" \
  --prune-empty --tag-name-filter cat -- --all

# Force push (WARNING: This rewrites history)
git push origin --force --all
```

4. **Add `.gitignore`** to prevent it happening again

---

## 📁 Files to Include in GitHub

✅ **DO INCLUDE:**
- `app_improved.py`
- `requirements.txt` or `requirements_windows.txt`
- `patient1_sepsis.csv`
- `patient2_vtach.csv`
- `patient3_respfailure.csv`
- `README.md`
- `.gitignore`
- `secrets.toml.example` (with placeholder)
- Architecture diagram (as image)

❌ **DO NOT INCLUDE:**
- `.streamlit/secrets.toml` (your actual key)
- `.env` files
- `__pycache__/` folders
- `venv/` or `env/` folders

---

## 🎓 For Professor Review

Add this note to your README:

```markdown
## ⚠️ Note for Reviewers

This app requires an OpenAI API key to function. For security reasons, 
the key is not included in this repository.

To test the app:
1. Obtain an API key from https://platform.openai.com/api-keys
2. Set environment variable: `export OPENAI_API_KEY="your-key"`
3. Run: `streamlit run app_improved.py`

The demo video shows the app working with all features enabled.
```

---

## 🔐 Best Practices Summary

1. ✅ **Always use `.gitignore`**
2. ✅ **Use environment variables for demo**
3. ✅ **Include `.example` files for documentation**
4. ✅ **Check `git status` before every commit**
5. ✅ **Never hardcode secrets in code**
6. ✅ **Revoke keys if accidentally exposed**

---

## 📝 Quick Commands

```bash
# Before first commit
echo ".streamlit/secrets.toml" >> .gitignore
echo ".env" >> .gitignore

# Check what will be committed
git status

# If secrets.toml appears in the list, you forgot .gitignore!

# Verify gitignore is working
git add .
git status
# secrets.toml should NOT appear in "Changes to be committed"
```

---

**Remember: Your API key = Your money. Protect it like your credit card!** 💳🔒
