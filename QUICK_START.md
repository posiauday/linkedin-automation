# Quick Start: LinkedIn Automation in 10 Minutes

## ⚡ The Absolute Minimum You Need

1. **GitHub Account** (free)
2. **4 API Keys**
3. **10 minutes to set it up**

---

## 🎯 5-Step Setup

### Step 1️⃣ Get API Keys (5 min)

```
A. Claude API Key
   → Go to: https://console.anthropic.com/
   → Copy API key

B. LinkedIn Access Token
   → Go to: https://www.linkedin.com/developers/apps
   → Create app, get token & person ID

C. OpenAI API Key
   → Go to: https://platform.openai.com/
   → Copy API key
```

### Step 2️⃣ Create GitHub Repo (2 min)

```bash
# Create new repo on GitHub
# Name it: "linkedin-automation"
# Keep it private

# Clone it
git clone https://github.com/YOUR_USERNAME/linkedin-automation.git
cd linkedin-automation

# Copy these files from setup guide into it:
# - linkedin_automation.py
# - SKILL.md
# - requirements.txt
# - Create: .github/workflows/linkedin-automation.yml

git add .
git commit -m "Initial setup"
git push
```

### Step 3️⃣ Add Secrets to GitHub (2 min)

```
Go to: https://github.com/YOUR_USERNAME/linkedin-automation/settings/secrets/actions

Add these SECRETS:
✓ CLAUDE_API_KEY = [your claude key]
✓ LINKEDIN_ACCESS_TOKEN = [your linkedin token]
✓ LINKEDIN_PERSON_ID = [your linkedin ID number]
✓ OPENAI_API_KEY = [your openai key]
```

### Step 4️⃣ Add Variables to GitHub (1 min)

```
Go to: https://github.com/YOUR_USERNAME/linkedin-automation/settings/variables/actions

Add these VARIABLES:
✓ DOMAIN_NAME = "Your Brand"
✓ DOMAIN_NICHE = "web design"
✓ ENABLE_IMAGE_GENERATION = "true"
✓ ENABLE_LINKEDIN_POSTING = "false"  ← START HERE (TEST MODE)
✓ TEST_MODE = "true"
```

### Step 5️⃣ Trigger First Run (manual)

```
1. Go to: Actions tab in your GitHub repo
2. Click: "LinkedIn Daily Automation"
3. Click: "Run workflow"
4. Wait ~2 minutes
5. Check: linkedin_posts/ folder for results
```

---

## ✅ How to Know It Worked

✓ Green checkmark next to workflow run in Actions tab
✓ `linkedin_posts/` folder has new files
✓ `linkedin_automation.log` shows success messages
✓ JSON file contains your post

---

## 🔄 Enable Real Posting

Once you verified it works:

```
1. GitHub → Settings → Variables
2. Change: ENABLE_LINKEDIN_POSTING → "true"
3. Change: TEST_MODE → "false"
4. Next scheduled run posts to LinkedIn!
```

---

## ⏰ Automate Daily

The workflow automatically runs at:
```
9:00 AM UTC every day
```

To change:
```
Edit: .github/workflows/linkedin-automation.yml
Line: cron: '0 9 * * *'

Examples:
'0 8 * * *'    → 8 AM UTC
'0 17 * * *'   → 5 PM UTC
'0 9 * * 1-5'  → 9 AM Mon-Fri only
```

---

## 📊 Monitor Your Automation

Every day:
1. Post auto-generates
2. Image auto-creates
3. Post goes live to LinkedIn
4. Results saved in `linkedin_posts/`

Check anytime:
```
GitHub → Actions → Click latest run → View logs
```

---

## 🎨 Customize Your Posts

Edit `SKILL.md` to change:
- Post topics
- Brand voice
- Hashtags
- Post structure
- Image style

---

## 💰 Cost Breakdown

**Per day:**
- Claude: $0.003 (3/100 of a cent)
- DALL-E: $0.04 (4 cents)
- LinkedIn: FREE
- GitHub: FREE

**Per month (30 posts):**
- Total: ~$1.20 + tax
- That's a coffee worth of automation!

---

## 🚨 What If Something Breaks?

**Check these first:**

1. **Secrets missing?**
   - GitHub → Settings → Secrets
   - Make sure all 4 are there

2. **API rate limited?**
   - Claude has free tier limits
   - Consider $10/month paid tier

3. **LinkedIn posting won't work?**
   - Keep `ENABLE_LINKEDIN_POSTING = false` first
   - Test in TEST_MODE
   - Verify token is valid

4. **Images not generating?**
   - Check OPENAI_API_KEY added
   - Check OpenAI account has billing
   - Each image costs $0.04

---

## 🎉 You're Done!

Your LinkedIn automation is now running 24/7.

**Next (optional):**
- Customize SKILL.md for your brand
- Add more topics to topics list
- Adjust posting frequency
- Monitor engagement, iterate

**Questions?**
- Check logs in Actions tab
- Error messages usually explain what went wrong
- Read SETUP_GUIDE.md for details

---

## 📝 One-Liner Reference

```bash
# View workflow status
Open: https://github.com/YOUR_USERNAME/linkedin-automation/actions

# View generated posts
Open: https://github.com/YOUR_USERNAME/linkedin-automation/tree/main/linkedin_posts

# Change schedule (cron format)
Edit: .github/workflows/linkedin-automation.yml

# Change post topics
Edit: linkedin_automation.py (line ~35)

# Change post style
Edit: SKILL.md (Instructions section)
```

---

**That's it! Your LinkedIn automation is live. 🚀**
