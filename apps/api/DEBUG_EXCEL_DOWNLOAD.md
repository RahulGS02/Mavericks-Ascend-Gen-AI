# 🔍 Debug Guide - Excel Download 500 Error

## ❌ **Current Issue**

Excel download endpoint returns **500 Internal Server Error**

```
❌ Download failed with status code: 500
```

---

## 🧪 **Diagnostic Steps**

### **Step 1: Test Excel Generation Separately**

First, verify Excel generation works independently:

```powershell
python test_excel_only.py
```

**Expected Output:**
```
✅ ALL EXCEL TESTS PASSED!
💡 Excel generation is working correctly!
```

**If this fails:** Excel generator has a bug
**If this passes:** Issue is in the API endpoint

---

### **Step 2: Check Server Logs**

The server should be showing detailed error logs. Look at the terminal where you ran:
```powershell
uvicorn app.main:app --reload
```

**Look for lines containing:**
- `ERROR` or `Exception`
- `Excel generation failed`
- `Traceback`

**Copy the full error stack trace** - this will tell us exactly what's failing.

---

### **Step 3: Run E2E Test with Verbose Output**

I've updated the test to show more details:

```powershell
python test_e2e_nl_query.py
```

Now when Excel download fails, it will show:
```
❌ Download failed with status code: 500
❌ Response content: {actual error message}
```

---

## 🔍 **Possible Causes & Solutions**

### **Cause 1: Import Error**

**Error in logs might show:**
```
ImportError: pandas and openpyxl are required
```

**Solution:**
```powershell
pip install pandas openpyxl --upgrade
```

---

### **Cause 2: Memory Issue with Large Data**

If you're trying to export 25 rows with many columns, the buffer might be too large.

**Solution:** Limit the query results
```python
# In test_e2e_nl_query.py, change max_rows
"max_rows": 10  # Instead of 50
```

---

### **Cause 3: Column Serialization Error**

Some column types (like JSONB arrays) might not serialize to Excel properly.

**Check logs for:**
```
TypeError: Object of type X is not JSON serializable
```

**Temporary Solution:** Test with a simpler query first
```python
TEST_QUERIES = [
    {
        "name": "Simple Test",
        "query": "Show me the top 5 mavericks by name",  # Simpler query
        "max_rows": 5
    }
]
```

---

### **Cause 4: StreamingResponse Issue**

The buffer might not be compatible with StreamingResponse.

**Solution Already Applied:**
```python
# In nl_query.py line 248
excel_buffer.seek(0)  # Already added
```

But FastAPI might need the buffer wrapped differently.

**Alternative Fix:** Try this in `nl_query.py` around line 255:

```python
# Instead of:
return StreamingResponse(
    excel_buffer,
    ...
)

# Try:
return StreamingResponse(
    iter([excel_buffer.getvalue()]),  # Wrap in iterator
    ...
)
```

---

### **Cause 5: Database Transaction Issue**

The database session might be closed before Excel generation completes.

**Check:** If server logs show:
```
sqlalchemy.exc.ResourceClosedError
```

**Solution:** The query execution should complete before Excel generation starts (it already does, but verify in logs)

---

## 🛠️ **Debugging Process**

### **A. Check What the Test Shows:**

Run the updated test:
```powershell
python test_e2e_nl_query.py
```

Look at the error response content that now gets printed.

---

### **B. Check Server Terminal:**

Look at the server logs for the exact error. You should see something like:

```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  ...
  [THE ACTUAL ERROR]
```

---

### **C. Test Excel Generation Alone:**

```powershell
python test_excel_only.py
```

If this works, the issue is NOT in excel_generator.py

---

### **D. Test Direct API Call:**

Try calling the endpoint directly with curl:

```powershell
# First get token
$token = "your_token_here"

# Then download
curl -X POST "http://localhost:8000/api/v1/nl-query/search/download" `
  -H "Authorization: Bearer $token" `
  -H "Content-Type: application/json" `
  -d '{"query":"Show me top 3 mavericks","max_rows":3}' `
  --output test.xlsx
```

Check if test.xlsx is created and valid.

---

## 📋 **Action Plan**

**Do these in order:**

1. **Run test_excel_only.py**
   - If fails: Excel generator has bug
   - If passes: Continue

2. **Check server terminal logs**
   - Copy the full error stack trace
   - Look for the root cause

3. **Run updated test_e2e_nl_query.py**
   - Note the error response content
   - Share with me

4. **Try simpler query**
   - Use "Show me top 3 mavericks" with max_rows=3
   - See if small data works

5. **Check browser/Postman**
   - Try downloading via Swagger UI at http://localhost:8000/docs
   - See if browser shows more details

---

## 📝 **Information Needed**

To fix this, I need to see:

1. **Server logs** - The full error stack trace from the uvicorn terminal
2. **Test output** - Run `python test_excel_only.py` and share output
3. **Error response** - The actual error message from the API (now shown in test)

---

## 🔧 **Quick Fixes to Try**

### **Fix 1: Alternative StreamingResponse**

Edit `nl_query.py` line 270-277:

```python
# Change from:
return StreamingResponse(
    excel_buffer,
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f"attachment; filename={filename}"}
)

# To:
from fastapi.responses import Response

return Response(
    content=excel_buffer.getvalue(),
    media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    headers={"Content-Disposition": f"attachment; filename={filename}"}
)
```

---

### **Fix 2: Add Error Handling**

The enhanced logging I added should help identify the issue. Check server logs for:

```
INFO:     Generating Excel with X rows
INFO:     Excel buffer size: X bytes
INFO:     Excel buffer ready for streaming
```

Or error messages like:
```
ERROR:    Excel generation failed: [actual error]
```

---

## 🎯 **Next Steps**

1. **Run diagnostic test:** `python test_excel_only.py`
2. **Check server logs** in the uvicorn terminal
3. **Share the error details** so I can provide the exact fix

**The server logs will tell us exactly what's failing!** 🔍
