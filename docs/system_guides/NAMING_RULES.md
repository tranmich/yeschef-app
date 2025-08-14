# IMMEDIATE NAMING CONVENTION RULES
# Follow these rules to prevent conflicts in the future

## ✅ SAFE NAMING PATTERNS:

### Backend Files:
- Main server: hungie_server.py (not app.py)
- API endpoints: {feature}_api.py (recipe_api.py, search_api.py)
- Services: {feature}_service.py
- Models: {feature}_model.py

### Frontend Files:
- Components: {Feature}Component.js (RecipeComponent.js)
- Pages: {Feature}Page.js (SearchPage.js)
- Services: {feature}Service.js

### Scripts & Tools:
- Parsers: parse_{source}.py (parse_bonappetit.py)
- Analysis: analyze_{feature}.py
- Database: db_{action}.py (db_migrate.py, db_backup.py)
- Tests: test_{component}.py
- Utils: {purpose}_util.py (string_util.py, date_util.py)

## ❌ AVOID THESE PATTERNS:

### Never Use:
- app.* (conflicts with app/ directory)
- server.* (too generic, conflicts likely)
- main.* (ambiguous scope)
- test.* (conflicts with test/ directory)
- Generic names: debug.py, check.py, temp.py
- Version numbers: parser2.py, app_v2.py

### Problem Patterns:
- {name}_backup.py (creates clutter)
- {name}_old.py (creates confusion)
- {name}_copy.py (import conflicts)
- {name}_final.py (never actually final)

## 🔧 CURRENT WORKING FILES:
- Backend: minimal_server.py ✅ (working, don't change)
- Frontend: frontend/ directory ✅ (working, don't change)
- Database: hungie.db ✅ (working, don't change)

## 📋 IMMEDIATE ACTIONS:
1. Keep current working setup as-is
2. For new files, follow naming rules above
3. Before creating any file, check if name exists:
   - ls {filename}* 
   - Check both .py and directory with same name
4. Use prefixes to avoid conflicts:
   - hungie_{purpose}.py
   - recipe_{action}.py
   - api_{endpoint}.py

## 🚫 DO NOT:
- Run large reorganization scripts (they freeze terminals)
- Rename working files (app.py, minimal_server.py, backend_server.py)
- Create files with generic names
- Add version numbers or backup suffixes
