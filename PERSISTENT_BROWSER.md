# 🌐 Persistent Browser Session Feature

## Overview

The LinkedIn scraper now maintains a **persistent browser session** that stays open between job searches, eliminating the need to log in repeatedly.

## Key Changes

### Before
- ❌ New browser window for each search
- ❌ Login to LinkedIn every time
- ❌ Solve CAPTCHA repeatedly
- ❌ Slower searches (30-60 seconds login time)
- ❌ Browser closes after each search

### After
- ✅ Single browser window reused
- ✅ Login once, use forever
- ✅ Solve CAPTCHA once (if needed)
- ✅ Faster subsequent searches (skip login)
- ✅ Browser stays open, new tabs for each search

## How It Works

1. **First Search**
   - Opens Chrome browser
   - Logs into LinkedIn with credentials from `.env`
   - Performs search
   - Browser stays open

2. **Subsequent Searches**
   - Reuses existing browser session
   - Opens new tab with search URL
   - No login required
   - Much faster!

3. **Browser Management**
   - Browser stays open until:
     - You manually close it
     - You run `python close_browser.py`
     - You stop the API server

## Usage

### Normal Operation
Just use the API or Web UI as usual. The browser will:
- Open automatically on first LinkedIn search
- Stay open for future searches
- Open new tabs for each search

### Manual Browser Control

**Close the browser:**
```bash
python close_browser.py
```

**Check browser status:**
- If browser is open, you'll see it in your taskbar/dock
- New searches will open new tabs in the existing window

## Benefits

### Speed
- **First search**: ~45-60 seconds (includes login)
- **Subsequent searches**: ~15-30 seconds (no login)
- **Time saved**: ~30-45 seconds per search after the first

### Reliability
- Fewer CAPTCHA challenges
- More stable session
- Better success rate

### User Experience
- Monitor searches in real-time
- See what the scraper is doing
- Manually intervene if needed (solve CAPTCHA, etc.)

## Technical Details

### Implementation
- Class-level shared driver instance (`LinkedInScraper._shared_driver`)
- Login state tracking (`LinkedInScraper._is_logged_in`)
- Browser detach option enabled (stays open after script ends)
- New tab creation using JavaScript `window.open()`

### Code Changes
```python
# Persistent driver
_shared_driver = None
_is_logged_in = False

def _get_or_create_driver(self):
    if LinkedInScraper._shared_driver is None:
        # Create new browser with detach option
        options.add_experimental_option("detach", True)
        LinkedInScraper._shared_driver = uc.Chrome(options=options)
    return LinkedInScraper._shared_driver
```

## Troubleshooting

### Browser won't close
```bash
python close_browser.py
```

### Browser stuck or frozen
1. Close manually from taskbar
2. Run `python close_browser.py`
3. Restart API server

### Login fails
1. Check credentials in `.env`
2. Solve CAPTCHA in browser window
3. Browser will remember login for future searches

### Too many tabs open
- Tabs accumulate with each search
- Close tabs manually or restart browser
- Run `python close_browser.py` to start fresh

## Best Practices

1. **Let it run**: Don't close the browser manually during searches
2. **Monitor first search**: Watch the login process to solve any CAPTCHAs
3. **Clean up periodically**: Close browser between sessions with `close_browser.py`
4. **Minimize window**: Browser can run minimized in background

## Future Enhancements

Potential improvements:
- [ ] Auto-close old tabs after search completes
- [ ] Session timeout and auto-refresh
- [ ] Multiple browser profiles for different accounts
- [ ] Headless mode with persistent session
- [ ] Browser health checks and auto-restart

## Notes

- Browser uses `undetected-chromedriver` to avoid detection
- Session cookies are maintained automatically
- Works on macOS, Linux, and Windows
- Requires Chrome browser installed
