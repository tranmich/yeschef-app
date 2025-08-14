# 🐛 Debugging Directory

## 📋 Purpose:
TEMPORARY debugging files only! All files here should be deleted after debugging session.

## ✅ Allowed Files:
- `temp_debug_YYYYMMDD_{purpose}.py` - Temporary debugging scripts
- `debug_session_YYYYMMDD.md` - Notes from debugging session
- `issue_reproduction_YYYYMMDD.py` - Scripts to reproduce issues

## 🗑️ Cleanup Rules:
- **DELETE files after each debugging session**
- **Extract useful code** to proper locations before deleting
- **Document solutions** in `docs/debugging/` if valuable

## ❌ DO NOT:
- Leave files here permanently
- Create generic names like `debug.py` or `test.py`
- Put production code here

## 🔄 After Every Session:
1. Review files in this directory
2. Extract/move useful code to proper locations
3. Delete all temporary files
4. Document solutions if applicable
