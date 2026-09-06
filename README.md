# LinkedIn Daily Automation with Claude + DALL-E

Automatically generate and post LinkedIn content every day using Claude AI, DALL-E images, and GitHub Actions (hosting).

**Status**: ✅ Production Ready | 💰 ~$1/month | ⚡ 100% Automated

---

## 🎯 What This Does

```
Every day at 9 AM UTC:
  1. Claude generates an engaging LinkedIn post
  2. DALL-E creates a relevant image
  3. LinkedIn API posts your content
  4. All stored in GitHub for tracking

No manual work needed!
```

---

## 📸 Example Output

```
🎯 POST COPY:
"I see founders choose domains in 5 minutes, then spend months regretting it.

Your domain isn't just a URL—it's your first impression:
🚀 .io signals tech/startup credibility
📱 .co is trendy but might confuse users
💼 .com still carries weight in B2B
🌍 Geographic domains build local authority
💪 New extensions can differentiate your brand

The right domain = 10-15% boost in early trust.

What domain extension do you regret? 👇

#DomainStrategy #WebDesign #Branding #Startups #DigitalMarketing"

📸 IMAGE PROMPT:
"Split-screen comparison of domain extensions with trust badges, modern minimalist design"

⏰ SUGGESTED TIME:
Tuesday 9:00 AM

💡 ENGAGEMENT:
"What's your domain regret?" - Sparks comment section
```

---

## 🏗️ How It Works

### Architecture

```
┌─ GitHub Actions (Hosting - FREE)
│  ├─ Scheduler: Runs daily at 9 AM UTC
│  ├─ Python Script: linkedin_automation.py
│  └─ Storage: linkedin_posts/ folder (in repo)
│
├─ Claude API (Post Generation)
│  ├─ Uses: Your Claude Skill instructions
│  ├─ Generates: Post copy + image prompts
│  └─ Cost: ~$0.003 per post
│
├─ OpenAI DALL-E (Image Generation)
│  ├─ Creates: 1024x1024 LinkedIn images
│  └─ Cost: ~$0.04 per image
│
└─ LinkedIn Official API (Posting)
   ├─ Posts: Directly to your profile/page
   └─ Cost: FREE
```

### File Structure

```
linkedin-automation/
├── .github/
│   └── workflows/
│       └── linkedin-automation.yml    ← GitHub scheduler
├── linkedin_automation.py              ← Main automation script
├── SKILL.md                            ← Claude skill (post instructions)
├── requirements.txt                    ← Python dependencies
├── linkedin_posts/                     ← Generated posts stored here
│   ├── post_20250906_090000.json      ← Post metadata
│   ├── linkedin_post_20250906_090000.png  ← Generated image
│   └── linkedin_automation.log         ← Execution logs
├── SETUP_GUIDE.md                      ← Detailed setup
├── QUICK_START.md                      ← 10-minute quick start
└── README.md                           ← This file
```

---

## 🚀 Quick Start (10 Minutes)

### 1. Get API Keys
```
✓ Claude API: https://console.anthropic.com/
✓ LinkedIn: https://www.linkedin.com/developers/apps
✓ OpenAI: https://platform.openai.com/
```

### 2. Create GitHub Repo
```bash
git clone https://github.com/YOUR_USERNAME/linkedin-automation
cd linkedin-automation
# Add the files from this package
git push
```

### 3. Add Secrets to GitHub
```
Settings → Secrets → Add:
- CLAUDE_API_KEY
- LINKEDIN_ACCESS_TOKEN
- LINKEDIN_PERSON_ID
- OPENAI_API_KEY
```

### 4. Add Variables to GitHub
```
Settings → Variables → Add:
- DOMAIN_NAME = "Your Brand"
- DOMAIN_NICHE = "your niche"
- ENABLE_IMAGE_GENERATION = "true"
- ENABLE_LINKEDIN_POSTING = "false"  ← START HERE (TEST MODE)
- TEST_MODE = "true"
```

### 5. Test It
```
GitHub → Actions → Run workflow manually
Check linkedin_posts/ folder for results
```

### 6. Enable Real Posting
```
Change ENABLE_LINKEDIN_POSTING to "true"
Change TEST_MODE to "false"
Next run will post to LinkedIn!
```

**👉 See QUICK_START.md for detailed walkthrough**

---

## 🎛️ Configuration

### Environment Variables

| Variable | Values | Purpose |
|---|---|---|
| `CLAUDE_API_KEY` | Your API key | Authentication for Claude |
| `LINKEDIN_ACCESS_TOKEN` | Your token | LinkedIn API auth |
| `LINKEDIN_PERSON_ID` | Numeric ID | Your LinkedIn profile ID |
| `OPENAI_API_KEY` | Your API key | DALL-E image generation |
| `DOMAIN_NAME` | String | Your brand name |
| `DOMAIN_NICHE` | String | Your specialty (e.g., "web design") |
| `ENABLE_IMAGE_GENERATION` | true/false | Generate images? |
| `ENABLE_LINKEDIN_POSTING` | true/false | Post to LinkedIn? |
| `TEST_MODE` | true/false | Test mode (no real posts) |

### Schedule

Edit `.github/workflows/linkedin-automation.yml`:

```yaml
schedule:
  - cron: '0 9 * * *'  # 9:00 AM UTC daily
```

**Cron examples:**
- `'0 8 * * *'` → 8 AM UTC
- `'0 17 * * *'` → 5 PM UTC
- `'0 9 * * 1-5'` → Mon-Fri only
- `'0 9,17 * * *'` → 9 AM AND 5 PM

---

## 🎨 Customizing Posts

### Edit the Claude Skill

The `SKILL.md` file controls how posts are generated. Edit it to change:

**Post Topics:**
```markdown
## Examples
### Post about [your topic]
Input: "[topic]"
Output: [example post]
```

**Brand Voice:**
```markdown
## Brand Voice Guidelines
- Tone: [your tone]
- Language: [your style]
- Perspective: [your angle]
```

**Hashtags:**
```markdown
## Hashtag Strategy
- Industry: [tags]
- Niche: [tags]
- Trending: [tags]
```

**Image Style:**
```markdown
## Image Prompt Template
Always use: [your style description]
Color palette: [your colors]
```

### Add More Topics

Edit `linkedin_automation.py`:

```python
self.topics = [
    "why domain extensions matter",
    "domain security best practices",
    "how to audit your domain portfolio",
    "your topic here",
]
```

---

## 📊 Monitoring

### View Logs
```
GitHub → Actions → Latest run → Logs
```

### Check Generated Posts
```
GitHub → linkedin_posts/ folder
```

### View Post Metadata
```
linkedin_posts/post_20250906_090000.json
```

### Check Automation Status
```
GitHub → Actions → LinkedIn Daily Automation
(Shows green for success, red for errors)
```

---

## 🔧 Troubleshooting

### ❌ Workflow fails with "Secret not found"
- Go to Settings → Secrets
- Verify all 4 secrets are added
- Check spelling matches exactly

### ❌ LinkedIn posting fails
- Keep `ENABLE_LINKEDIN_POSTING = false` initially
- Verify your access token is valid
- Check LinkedIn account has API permissions
- Ensure using official LinkedIn API (not scrapers)

### ❌ Images not generating
- Verify `OPENAI_API_KEY` is added to secrets
- Check OpenAI account has billing enabled
- Each image costs ~$0.04

### ❌ Claude API rate limited
- Free tier has limits
- Consider $10/month Claude Pro
- Or add delay between multiple runs

### ✅ Posts look low quality
- Edit SKILL.md instructions
- Run manually first to test changes
- Quality is 100% controlled by the Skill

---

## 💰 Costs

**Per Month (assuming 1 post/day):**

| Service | Usage | Cost |
|---|---|---|
| Claude API | 30 posts @ $0.003 | $0.09 |
| DALL-E | 30 images @ $0.04 | $1.20 |
| LinkedIn API | Unlimited | FREE |
| GitHub Actions | 2,000 min/mo free | FREE |
| **Total** | | **~$1.30/month** |

---

## 🛡️ Safety & Compliance

### LinkedIn Policy Compliance
- ✅ Uses official LinkedIn API
- ✅ Posts professional content only
- ✅ No connection automation
- ✅ No spam or manipulation
- ✅ Transparent engagement

### Best Practices
1. Test in TEST_MODE first
2. Review first few posts manually
3. Monitor LinkedIn analytics
4. Adjust based on engagement
5. Keep content authentic

---

## 📁 What Gets Stored?

In your GitHub repository:

```
linkedin_posts/
├── post_20250906_090000.json      ← Post metadata (visible in GitHub)
├── linkedin_post_20250906_090000.png   ← Image (visible in GitHub)
└── linkedin_automation.log         ← Logs (visible in GitHub)
```

**Privacy note**: Make your GitHub repo PRIVATE if you want posts private before publishing.

---

## 🔄 Workflow Overview

```
GITHUB ACTIONS SCHEDULE (9 AM UTC)
         ↓
LINKEDIN AUTOMATION RUNS
         ↓
    Claude generates post
         ↓
    DALL-E creates image
         ↓
    LinkedIn API posts
         ↓
    Results saved to github
         ↓
NOTIFICATION (optional Slack)
```

---

## ⚡ Performance

- **Post generation**: 10-15 seconds
- **Image generation**: 20-30 seconds
- **LinkedIn posting**: 3-5 seconds
- **Total time**: ~1 minute per day
- **GitHub Action limit**: 2,000 min/month (enough for 67 posts/day!)

---

## 🎓 How Claude Skills Work (Explanation)

A Claude Skill is like giving Claude a "manual" to follow:

```
Without Skill:
  User → "Generate a post" → Generic result

With Skill:
  User → "Generate a post" → Claude reads SKILL.md → 
  Follows your specific rules → Perfect branded result
```

**Why Skills?**
- Reusable: Load automatically when relevant
- Consistent: Same instructions every time
- Maintainable: Edit once, affects all uses
- Lightweight: Only loaded when needed (~50-100 tokens)

**Scopes:**
- **Global** (~/.claude/skills/): Personal use only
- **Project** (.claude/skills/): Shared with team via Git

---

## 🚀 Advanced Customization

### Multiple Topics Per Day
```python
# In linkedin_automation.py
posts_per_day = 3  # Generate 3 posts
```

### Different Posting Times
Edit cron:
```yaml
schedule:
  - cron: '0 9 * * *'   # 9 AM
  - cron: '0 17 * * *'  # 5 PM
```

### Slack Notifications
Uncomment in workflow file, add Slack webhook

### Database Storage
Replace GitHub storage with PostgreSQL, MongoDB, etc.

---

## 📚 Learning Resources

1. **QUICK_START.md** - 10-minute setup
2. **SETUP_GUIDE.md** - Detailed walkthrough
3. **SKILL.md** - Post generation rules
4. **linkedin_automation.py** - Source code
5. GitHub Actions docs: https://docs.github.com/actions

---

## 🤝 Contributing & Support

**Questions?**
1. Check logs in GitHub Actions
2. Review SETUP_GUIDE.md
3. Test in TEST_MODE first

**Want to improve?**
1. Fork this repo
2. Make changes
3. Test locally
4. Submit PR

---

## 📄 License

MIT License - Use freely, modify, share

---

## ✨ Features Checklist

- ✅ Daily automated posts
- ✅ AI-generated content (Claude)
- ✅ AI-generated images (DALL-E)
- ✅ Direct LinkedIn posting
- ✅ Content management
- ✅ Logging & monitoring
- ✅ GitHub-hosted (free)
- ✅ Customizable Skill
- ✅ TEST_MODE for safe testing
- ✅ ~$1/month cost

---

## 🎉 Ready to Start?

1. **Quick start**: Read QUICK_START.md (10 min)
2. **Detailed setup**: Read SETUP_GUIDE.md (30 min)
3. **Customize**: Edit SKILL.md for your brand
4. **Deploy**: Push to GitHub, watch it work!

**Your LinkedIn automation awaits! 🚀**

---

## 📞 Files Reference

| File | Purpose |
|---|---|
| `linkedin_automation.py` | Main automation script |
| `SKILL.md` | Claude skill (post instructions) |
| `.github/workflows/linkedin-automation.yml` | GitHub scheduler |
| `requirements.txt` | Python dependencies |
| `QUICK_START.md` | 10-minute setup |
| `SETUP_GUIDE.md` | Detailed walkthrough |
| `README.md` | This file |

---

**Made with ❤️ for automating your LinkedIn presence**
