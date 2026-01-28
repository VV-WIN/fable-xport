# Quick Troubleshooting Guide

## Common Issues and Solutions

### 1. "Failed to fetch books" or 403 Error

**Problem:** Your authentication credentials are incorrect or expired.

**Solution:**
1. Go to Fable.co in your browser
2. Press F12 to open Developer Tools
3. Go to Network tab and refresh the page
4. Find a request to `api.fable.co`
5. Get a fresh User ID and Auth Token
6. Delete the `.env` file in the project folder
7. Run the tool again and enter the new credentials

**Important:** The Auth Token should NOT include "JWT " at the beginning - just copy the long string after it.

---

### 2. "No books found"

**Problem:** The tool can't find any books in your library.

**Solution:**
- Make sure you're using the correct Fable account
- Verify you have books in your Fable.co library
- Check that your User ID matches your logged-in account

---

### 3. Export is missing data (ratings, reviews, etc.)

**Problem:** Some books don't have all fields populated.

**This is normal!** Here's why:
- **Ratings details** (characters, plot, writing, setting) only show if you rated those specific aspects
- **Reviews** only show for books you've reviewed
- **Reading dates** only show for books you've started/finished
- **Genres/moods** only show if Fable has that data

**Not a bug** - the export includes all available data for each book.

---

### 4. Export takes a long time

**Problem:** Export seems slow or frozen.

**This is normal for large libraries:**
- 100 books: ~15 seconds
- 500 books: ~1 minute
- 1000 books: ~2 minutes

The tool shows progress for each list, so you know it's working.

**If it truly freezes:**
1. Close the tool (Ctrl+C)
2. Check your internet connection
3. Try exporting one list at a time (answer "yes" to separate files)

---

### 5. "NoneType object has no attribute 'get'" Error

**Problem:** Some books have unexpected data structure.

**Solution:** 
This should be fixed in the latest version. If you still see it:
1. Note which list is causing the error
2. The export will continue and complete other lists
3. The problematic list may have partial data
4. Try exporting again - sometimes this is a temporary API issue

---

### 6. Files won't open or have encoding issues

**Problem:** CSV/JSON/Markdown files look corrupted or have strange characters.

**Solution:**
- **CSV:** Open with Excel or Google Sheets, not Notepad
- **JSON:** Use a JSON viewer or text editor like VS Code
- **Markdown:** Use a Markdown viewer or text editor

If you see weird characters:
- The files use UTF-8 encoding
- In Excel: Use "Data" → "Get External Data" → "From Text" and select UTF-8 encoding
- In Google Sheets: Files should open correctly automatically

---

### 7. Missing "Finished" books or incomplete Finished list

**Problem:** Your Finished list has 456 books but export only shows 69.

**Possible causes:**
1. **API pagination issue** - Try exporting again
2. **Some books don't have complete data** - Tool skips books with invalid structure
3. **Fable API returned incomplete response** - This can happen with very large lists

**Solutions:**
- Export multiple times and compare - sometimes different attempts get different results
- Try exporting as "one combined file" instead of separate lists
- Report the issue to Fable support if the problem persists

---

### 8. Windows Defender or antivirus blocks the tool

**Problem:** Security software flags `run.bat` or downloads.

**This is a false positive.** The tool is safe - it only downloads from Fable.co.

**Solution:**
1. Add an exception for the fable-xport folder in your antivirus
2. Or right-click `run.bat` → "Run as administrator"
3. Windows may ask "Do you want to allow this app?" → Click Yes

---

### 9. "Python not found" or installation issues

**Problem:** Tool can't install Python or dependencies.

**The tool uses `uv` to auto-install Python.** This should just work!

**If it doesn't:**
1. Download Python manually from python.org (version 3.7 or newer)
2. During installation, check "Add Python to PATH"
3. Run the tool again

---

### 10. Export succeeded but files are empty

**Problem:** Files are created but contain no books.

**Check:**
1. Do you actually have books in that list on Fable.co?
2. Did you see "✓ Exported X books" for that list?
3. Try opening with a different program (Excel vs Google Sheets)

**If files truly empty:**
- Check the terminal output for any error messages
- Try exporting a different list to see if the issue is list-specific
- Your token may have expired - get a fresh one

---

## Getting More Help

**Before reporting issues:**
1. ✅ Verify your User ID is correct (it's a long UUID)
2. ✅ Verify your Auth Token doesn't include "JWT " at the start
3. ✅ Try getting fresh credentials from Fable.co
4. ✅ Try exporting again - sometimes it's a temporary API issue

**Still stuck?**
- Check that you're running the latest version
- Try exporting a smaller list first (e.g., "Did Not Finish" with 1 book)
- Look for error messages in the terminal output

---

## Tips for Best Results

✅ **Run exports during off-peak hours** - Early morning or late evening  
✅ **Have a stable internet connection** - WiFi preferred over mobile data  
✅ **Don't close the browser with Fable.co** - Keeps your session active  
✅ **Export regularly** - Weekly or monthly backups prevent data loss  
✅ **Keep the `.env` file** - You won't need to re-enter credentials next time  

---

**Remember:** Some data variations are normal. Not every book will have every field, and that's okay! The tool exports everything Fable has available for each book.
