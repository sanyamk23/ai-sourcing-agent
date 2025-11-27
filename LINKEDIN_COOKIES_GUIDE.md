# 🍪 LinkedIn Cookies Setup Guide

## Problem
Every time you scrape LinkedIn, you have to login again. This is slow and LinkedIn may block you.

## Solution
Use your Chrome profile with saved LinkedIn cookies. Login once, scrape forever!

## Setup (One-Time)

### Option 1: Use Your Main Chrome Profile (Recommended)

```bash
python setup_linkedin_cookies.py
```

Then:
1. Select option `1` (Use main Chrome profile)
2. Select your Chrome profile (usually "Default")
3. Chrome will open
4. Login to LinkedIn if not already logged in
5. Press Enter in terminal
6. Done! ✅

### Option 2: Create Separate Profile for Scraping

```bash
python setup_linkedin_cookies.py
```

Then:
1. Select option `2` (Create separate profile)
2. Chrome will open with new profile
3. Login to LinkedIn
4. Press Enter in terminal
5. Done! ✅

## How It Works

### Before (Without Cookies)
```
Every scrape:
1. Open Chrome
2. Go to LinkedIn
3. Enter username
4. Enter password
5. Solve CAPTCHA (maybe)
6. Finally scrape
Time: 30-60 seconds
```

### After (With Cookies)
```
Every scrape:
1. Open Chrome with saved profile
2. Already logged in! ✅
3. Scrape immediately
Time: 5 seconds
```

## Usage in Code

### Automatic (Recommended)
The scraper will automatically use saved cookies if available:

```python
# In config.yaml, set:
linkedin:
  use_profile: true  # Use saved cookies
  headless: false    # Must be false to use profile
```

### Manual
```python
from src.browser_profile_manager import BrowserProfileManager

# Create driver with saved profile
driver = BrowserProfileManager.create_custom_profile_driver(
    "./chrome_profile_linkedin",
    headless=False
)

# Now use driver - already logged in!
driver.get("https://www.linkedin.com/feed")
# You're logged in! No need to enter credentials
```

## Where Are Cookies Stored?

### Option 1 (Main Chrome Profile)
- **macOS**: `~/Library/Application Support/Google/Chrome/Default`
- **Windows**: `C:\Users\YourName\AppData\Local\Google\Chrome\User Data\Default`
- **Linux**: `~/.config/google-chrome/Default`

### Option 2 (Separate Profile)
- `./chrome_profile_linkedin/` (in your project directory)

## Benefits

1. ✅ **No repeated logins** - Login once, use forever
2. ✅ **Faster scraping** - Skip login step (saves 30+ seconds)
3. ✅ **Avoid CAPTCHAs** - LinkedIn trusts your saved session
4. ✅ **Less suspicious** - Looks like normal browsing
5. ✅ **Multiple profiles** - Use different LinkedIn accounts

## Troubleshooting

### "Chrome profile not found"
- Make sure Chrome is installed
- Try Option 2 (separate profile)

### "Still asking for login"
- Run setup again: `python setup_linkedin_cookies.py`
- Make sure you pressed Enter AFTER logging in
- Check that `headless: false` in config

### "Profile is locked"
- Close all Chrome windows
- Run setup again

### "Cookies expired"
- LinkedIn sessions expire after ~30 days
- Just run setup again to refresh

## Advanced: Multiple LinkedIn Accounts

```python
# Account 1
driver1 = BrowserProfileManager.create_custom_profile_driver(
    "./chrome_profile_account1"
)

# Account 2
driver2 = BrowserProfileManager.create_custom_profile_driver(
    "./chrome_profile_account2"
)
```

## Security Notes

- ✅ Cookies are stored locally on your machine
- ✅ Not uploaded anywhere
- ✅ Same security as Chrome browser
- ⚠️  Don't share `chrome_profile_linkedin/` folder
- ⚠️  Add to `.gitignore` (already done)

## Update .gitignore

Already added:
```
chrome_profile_linkedin/
chrome_profile*/
```

## Example Workflow

### First Time Setup
```bash
# 1. Setup cookies
python setup_linkedin_cookies.py

# 2. Login to LinkedIn in the browser that opens

# 3. Press Enter

# 4. Done!
```

### Every Time After
```bash
# Just run your scraper
python run_api.py

# Or create a job in UI
# Scraper automatically uses saved cookies
# No login needed! ✅
```

## Comparison

| Feature | Without Cookies | With Cookies |
|---------|----------------|--------------|
| Login time | 30-60 seconds | 0 seconds |
| CAPTCHA risk | High | Low |
| Suspicious | Yes | No |
| Setup time | Every time | Once |
| Maintenance | None | Refresh every 30 days |

## FAQ

**Q: Do I need to keep Chrome open?**
A: No, the scraper opens its own Chrome instance.

**Q: Will this affect my regular Chrome browsing?**
A: No, if you use Option 2 (separate profile).

**Q: Can I use this for other sites?**
A: Yes! Works for any site with login.

**Q: Is this against LinkedIn's terms?**
A: Using your own account for personal use is fine. Don't scrape excessively.

**Q: How often do I need to refresh cookies?**
A: About once a month, or when LinkedIn logs you out.

---

**Ready to setup?** Run: `python setup_linkedin_cookies.py`
