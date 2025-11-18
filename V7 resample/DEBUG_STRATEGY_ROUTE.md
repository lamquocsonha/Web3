# Debug Strategy Route Issue

## Problem
Clicking "Strategy" in the navigation menu shows Manual Trading page instead of Strategy page.

## Root Cause Analysis

The Flask routes are correctly configured:
- ✅ `app.py` line 39-43: `/strategy` route exists
- ✅ `templates/strategy.html` exists and is valid
- ✅ `base.html` line 19: Navigation link is correct `<a href="/strategy">`

**Most likely causes:**
1. **Flask server needs restart** after code changes
2. **Browser cache** serving old page
3. **Wrong server** is running (old version)

## How to Fix

### Step 1: Test if Route Works

I've created a **RED TEST PAGE** to verify the route works.

1. **Start Flask server:**
   ```bash
   cd "/home/user/Web3/V7 resample"
   ./start_server.sh
   ```

2. **Open in browser:**
   ```
   http://localhost:5000/strategy
   ```

3. **Expected result:**
   - ✅ **RED page** with yellow border saying "STRATEGY PAGE WORKING"
   - ❌ **Manual Trading page** = route not working or cache issue

### Step 2: If You See RED Page

The route works! The issue is browser cache.

**Fix:**
1. Open the app in browser
2. Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac) to hard reload
3. Or clear browser cache for localhost

Then restore the real Strategy page:

```bash
# Edit app.py line 42-43:
# FROM:
    return render_template('strategy-test.html')
    # return render_template('strategy.html')

# TO:
    return render_template('strategy.html')
```

### Step 3: If You See Manual Trading Page

The route is not working.

**Possible fixes:**

1. **Kill old Flask processes:**
   ```bash
   pkill -f "python.*app.py"
   pkill -f flask
   ```

2. **Restart Flask server:**
   ```bash
   ./start_server.sh
   ```

3. **Check Flask is running correctly:**
   ```bash
   curl http://localhost:5000/strategy
   # Should return HTML with "STRATEGY PAGE WORKING"
   ```

### Step 4: Final Verification

Once you see the RED test page working:

1. Edit `app.py` to restore real Strategy page
2. Restart Flask server
3. Hard reload browser (`Ctrl+Shift+R`)
4. Click "Strategy" in nav → Should show Strategy Builder page

## Files Created for Testing

- `templates/strategy-test.html` - Red test page
- `start_server.sh` - Easy server startup script
- `test_routes.py` - Automated route testing (requires Flask)
- `DEBUG_STRATEGY_ROUTE.md` - This file

## Quick Commands

```bash
# Start server
./start_server.sh

# Test route via curl
curl http://localhost:5000/strategy

# Kill Flask
pkill -f "python.*app.py"
```

## After Testing

Once confirmed working, you can:
1. Delete test files:
   - `templates/strategy-test.html`
   - `test_routes.py`
   - `DEBUG_STRATEGY_ROUTE.md`

2. Restore `app.py`:
   ```python
   @app.route('/strategy')
   def strategy():
       return render_template('strategy.html')
   ```

3. Commit and push changes
