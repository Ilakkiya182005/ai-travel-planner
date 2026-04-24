# Setup Instructions After Removing Secrets

## 1. Create .env file
Copy `.env.example` to `.env` and add your actual API keys:

```bash
copy .env.example .env
```

Then edit `.env` and add:
```
GROQ_API_KEY=gsk_xxxxxxxxxxxxx
OPENAI_API_KEY=sk-xxxxxxxxxxxxx (if using OpenAI)
```

## 2. Fix Git History (Remove Exposed Secrets)

The exposed API keys need to be removed from git history. You have two options:

### Option A: Force Push (Simpler, for personal repos)
```powershell
# Remove all cached files
git rm -r --cached .

# Re-add files (git will respect .gitignore now)
git add .

# Commit
git commit -m "Remove hardcoded secrets and use environment variables"

# Force push to overwrite history
git push -u origin main --force-with-lease
```

### Option B: Use BFG Repo Cleaner (More thorough)
```powershell
# Install BFG (if you have it)
bfg --delete-files ".env" --no-blob-protection

# Force push
git push -u origin main --force-with-lease
```

## 3. Regenerate Your API Keys
⚠️ **Important**: Since the API key is now public in git history, you should:
1. Go to https://console.groq.com and regenerate your API key
2. Update your `.env` file with the new key
3. Never commit `.env` to version control again

## 4. Verify Before Pushing
```powershell
# Check what would be pushed
git log --oneline -5

# Push
git push -u origin main
```

## Files Changed:
✅ `config/settings.py` - Now loads from environment
✅ `llm/llm_client.py` - Accepts api_key parameter
✅ `services/intent_service.py` - Accepts api_key parameter
✅ `.env.example` - Template for environment variables
✅ `.gitignore` - Excludes .env files
