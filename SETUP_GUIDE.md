# LinkedIn Automation Complete Setup Guide

Your question was exactly right: **A Skill alone doesn't run anything—you need hosting!**

This guide walks you through everything to get daily LinkedIn automation running.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub (Hosting)                      │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  GitHub Actions (Scheduler)                      │   │
│  │  Runs daily at 9:00 AM UTC (Free!)               │   │
│  └─────────────────┬────────────────────────────────┘   │
│                    │                                      │
│                    ↓                                      │
│  ┌──────────────────────────────────────────────────┐   │
│  │  python linkedin_automation.py                   │   │
│  │  ├─ Calls Claude API (generate post)             │   │
│  │  ├─ Calls DALL-E API (create image)              │   │
│  │  └─ Calls LinkedIn API (post content)            │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │  linkedin_posts/ (stored in repo)                │   │
│  │  ├─ post_20250906_090000.json                    │   │
│  │  ├─ linkedin_post_20250906_090000.png            │   │
│  │  └─ linkedin_automation.log                      │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
         │                      │                      │
         ↓                      ↓                      ↓
     Claude API           OpenAI DALL-E API      LinkedIn API
   (Post Generation)      (Image Creation)       (Actual Posting)
```

---

## 📋 Prerequisites

Before starting, you need:

1. **GitHub Account** (free) - For hosting
2. **API Keys**:
   - Claude API key (Anthropic)
   - LinkedIn access token
   - OpenAI API key (for DALL-E)
3. **LinkedIn Developer App** - To get access token & person ID
4. **Git** - To push code to GitHub

---

## 🔑 Step 1: Get Your API Keys

### A. Claude API Key
```
1. Go to: https://console.anthropic.com/
2. Sign up or log in
3. Create API key in Settings → API Keys
4. Copy your key (keep it secret!)
```

### B. LinkedIn Access Token
```
1. Go to: https://www.linkedin.com/developers/apps
2. Create new app
3. Get your LINKEDIN_PERSON_ID (your LinkedIn numeric ID)
   - Visit: https://www.linkedin.com/in/yourprofile/
   - Check page source for "urn:li:person:XXXXX"
   - Copy just the numbers
4. Request API access (LinkedIn is selective)
   - Apply for "Share on LinkedIn" permission
5. Get your access token from app credentials
```

### C. OpenAI API Key (for DALL-E images)
```
1. Go to: https://platform.openai.com/
2. Sign up or log in
3. Create API key in Settings → API keys
4. Copy your key
5. Add billing (DALL-E costs ~$0.04 per image)
```

---

## 🚀 Step 2: Fork/Create Repository on GitHub

### Option A: Start Fresh

```bash
# Create a new directory
mkdir linkedin-automation
cd linkedin-automation

# Initialize git
git init

# Create the folder structure
mkdir -p .github/workflows linkedin_posts

# Copy files from this guide
# (linkedin_automation.py, SKILL.md, requirements.txt, etc.)
```

### Option B: Use as Template

```
Click "Use this template" if you find this as a GitHub repo
```

### Then:
```bash
git add .
git commit -m "Initial commit: LinkedIn automation setup"
git push origin main
```

---

## 🔐 Step 3: Add Secrets to GitHub

GitHub Secrets = Safe place to store API keys (not visible in code)

### Go to your GitHub repo:
```
Settings → Secrets and Variables → Actions
```

### Add these secrets (Copy-paste from Step 1):

| Secret Name | Value |
|---|---|
| `CLAUDE_API_KEY` | Your Claude API key |
| `LINKEDIN_ACCESS_TOKEN` | Your LinkedIn token |
| `LINKEDIN_PERSON_ID` | Your LinkedIn numeric ID |
| `OPENAI_API_KEY` | Your OpenAI API key |

---

## ⚙️ Step 4: Configure Environment Variables

Also in GitHub repo settings, go to:
```
Settings → Secrets and Variables → Variables
```

Add these variables (NOT secrets, these are okay to see):

| Variable | Value | Example |
|---|---|---|
| `DOMAIN_NAME` | Your brand name | "John's Web Design" |
| `DOMAIN_NICHE` | Your specialty | "web design" or "domain strategy" |
| `ENABLE_IMAGE_GENERATION` | true or false | "true" |
| `ENABLE_LINKEDIN_POSTING` | true or false | "false" (until tested) |
| `TEST_MODE` | true or false | "true" (start in test mode) |

### ⚠️ Important: Start with TEST_MODE = true
- This generates posts but doesn't actually post to LinkedIn
- Good for testing the whole system first
- Once working, change to `false` to enable actual posting

---

## 📁 Step 5: File Structure

Your GitHub repo should look like:

```
linkedin-automation/
├── .github/
│   └── workflows/
│       └── linkedin-automation.yml    (workflow file)
├── linkedin_posts/                    (generated automatically)
│   ├── post_20250906_090000.json
│   ├── linkedin_post_20250906_090000.png
│   └── linkedin_automation.log
├── linkedin_automation.py              (main script)
├── SKILL.md                            (Claude skill instructions)
├── requirements.txt                    (Python dependencies)
├── .env.example                        (local testing reference)
└── README.md                           (documentation)
```

---

## 🧪 Step 6: Test Locally First (Optional)

Before letting it run on GitHub:

```bash
# 1. Clone your repo
git clone https://github.com/YOUR_USERNAME/linkedin-automation.git
cd linkedin-automation

# 2. Create .env file (DON'T commit this!)
cat > .env << EOF
CLAUDE_API_KEY=your_key_here
LINKEDIN_ACCESS_TOKEN=your_token_here
LINKEDIN_PERSON_ID=12345
OPENAI_API_KEY=your_key_here
DOMAIN_NAME=My Brand
DOMAIN_NICHE=web design
ENABLE_IMAGE_GENERATION=true
ENABLE_LINKEDIN_POSTING=false
TEST_MODE=true
EOF

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the script
python linkedin_automation.py

# 5. Check output
ls linkedin_posts/
cat linkedin_automation.log
```

---

## 📅 Step 7: Set Daily Schedule

The workflow file has:
```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9:00 AM UTC
```

### Change the time (cron format):
```
'0 9 * * *'      → 9:00 AM UTC every day
'0 8 * * *'      → 8:00 AM UTC every day
'0 9 * * 1-5'    → 9:00 AM UTC Monday-Friday only
'0 9,17 * * *'   → 9:00 AM AND 5:00 PM UTC every day
```

**Convert to your timezone:**
- UTC to EST: Subtract 5 hours
- UTC to PST: Subtract 8 hours
- UTC to CET: Subtract 1 hour

---

## ✅ Step 8: Enable Posting (After Testing)

Once everything works:

1. Go to GitHub repo settings → Variables
2. Change `ENABLE_LINKEDIN_POSTING` to `true`
3. Change `TEST_MODE` to `false`
4. Next scheduled run will post to LinkedIn!

---

## 🔄 Manual Testing

You can manually trigger the workflow:

1. Go to: **Actions** tab in your GitHub repo
2. Select: **LinkedIn Daily Automation**
3. Click: **Run workflow**
4. Check logs in **Show all jobs**

---

## 📊 Monitor Your Automation

### Check logs:
```
GitHub → Actions → Latest run → Artifacts
```

### View generated posts:
```
GitHub → linkedin_posts/ folder
```

### See what was posted:
```
linkedin_posts/post_20250906_090000.json
```

### Disable temporarily:
```
1. Go to Actions tab
2. Click three dots on workflow
3. Click "Disable workflow"
4. Re-enable when ready
```

---

## 🛠️ Troubleshooting

### ❌ "Secrets not found" error
- Make sure you added them in GitHub Settings → Secrets
- Make sure the secret names EXACTLY match the code

### ❌ "LinkedIn posting failed"
- Check `ENABLE_LINKEDIN_POSTING` is false initially
- Verify your LinkedIn access token is valid
- Ensure LinkedIn API permissions are granted

### ❌ "Claude API rate limit"
- Claude has rate limits for free tier
- If hitting limits, add small delay between runs
- Consider paid Claude API tier for production

### ❌ "Image generation not working"
- Verify OPENAI_API_KEY is added
- Check your OpenAI account has billing enabled
- Each image costs ~$0.04

### ✅ "It works but posts look weird"
- Edit SKILL.md to change tone/style
- Run manually first to test changes
- The Skill completely controls post quality

---

## 🎨 Customizing Posts

### 1. Edit the Skill File
```
Edit: SKILL.md → Instructions section
Change:
- Content pillars (topics)
- Brand voice
- Hashtag strategy
- Post structure
```

### 2. Add Your Topics
In `linkedin_automation.py`, modify the `topics` list:
```python
self.topics = [
    "your topic 1",
    "your topic 2",
    "your topic 3",
]
```

### 3. Change Image Style
Edit the image prompt template in `PostGenerator.generate_post()`

---

## 🚨 Important Notes

### Rate Limits & Costs
- **Claude API**: ~$0.003 per post (pennies)
- **DALL-E**: ~$0.04 per image
- **LinkedIn API**: FREE
- **GitHub Actions**: 2,000 minutes/month FREE

**Monthly cost estimate**: $0.60-$1.50 for daily automation

### LinkedIn API Restrictions
- Only company pages or your profile
- No connection automation
- Professional content only
- Must follow LinkedIn terms

### Best Practices
1. Test in TEST_MODE first
2. Monitor logs for errors
3. Rotate content topics to avoid repetition
4. Keep posts between 500-1300 characters
5. Post during peak engagement hours

---

## 📞 Quick Reference

### Disable/Enable Automation
```bash
GitHub → Actions → LinkedIn Daily Automation → ... → Disable/Enable
```

### View Logs
```bash
GitHub → Actions → Latest run → Show all jobs → Build logs
```

### Manual Run
```bash
GitHub → Actions → LinkedIn Daily Automation → Run workflow
```

### Edit Schedule
```bash
Edit: .github/workflows/linkedin-automation.yml
Change: cron: '0 9 * * *'
```

---

## 🎉 Success Checklist

- [ ] All 4 API keys collected
- [ ] GitHub repo created
- [ ] Secrets added to GitHub
- [ ] Variables added to GitHub
- [ ] Workflow file in `.github/workflows/`
- [ ] Local test passed (optional)
- [ ] TEST_MODE enabled
- [ ] First scheduled run succeeds
- [ ] Post appears in `linkedin_posts/`
- [ ] ENABLE_LINKEDIN_POSTING changed to true
- [ ] Real post appears on LinkedIn!

---

## 💡 Next Steps

1. **Customize the Skill** - Edit SKILL.md for your voice
2. **Add more topics** - LinkedIn automation.py line ~35
3. **Adjust schedule** - More posts per week? Change cron
4. **Monitor performance** - Track engagement on LinkedIn
5. **Iterate** - What posts get most comments? Refine based on that

---

**You're now running AI-powered LinkedIn automation 24/7! 🚀**
