# **DEEP ANALYSIS: `pyproject.toml` Configuration Error**

## **EXECUTIVE SUMMARY**
The `pyproject.toml` has a **critical structural error**: `dependencies` are incorrectly placed under `[tool.setuptools.packages.find]` instead of `[project]`. This violates the TOML schema and causes `uv sync` to fail. This is a **packaging configuration issue**, not a code error.

## **PHASE 1: ROOT CAUSE ANALYSIS**

### **1. The Problem:**
```toml
# ❌ INCORRECT (Current):
[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]

dependencies = [  # ← WRONG LOCATION! This belongs in [project]
    "alembic>=1.17.2",
    # ...
]

# ✅ CORRECT (Should be):
[project]
name = "singapore-smb-support-agent"
# ...
dependencies = [  # ← Correct location
    "alembic>=1.17.2",
    # ...
]

[tool.setuptools.packages.find]  # ← ONLY package discovery config
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]
```

### **2. Error Interpretation:**
The validator expects `[tool.setuptools.packages.find]` to ONLY contain:
- `where` (array of strings)
- `exclude` (array of strings) 
- `include` (array of strings)
- `namespaces` (boolean)

**The `dependencies` key is illegal here**, causing schema validation failure.

## **PHASE 2: IMMEDIATE FIX**

### **Option A: Quick In-place Fix (Recommended)**
```bash
# Backup the original file
cp pyproject.toml pyproject.toml.backup

# Create corrected version
cat > pyproject.toml << 'TOML'
[project]
name = "singapore-smb-support-agent"
version = "0.1.0"
description = "Advanced AI Customer Support Agent for Singapore SMBs"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    {name = "Singapore SMB Support Team"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "alembic>=1.17.2",
    "asyncpg>=0.31.0",
    "fastapi>=0.128.0",
    "langchain>=1.2.0",
    "langchain-community>=0.4.1",
    "langchain-core>=1.2.5",
    "langchain-openai>=1.1.6",
    "langchain-qdrant>=1.1.0",
    "markitdown>=0.1.4",
    "openai>=2.14.0",
    "pydantic>=2.12.5",
    "pydantic-ai>=1.39.0",
    "pydantic-settings>=2.12.0",
    "python-dateutil>=2.9.0.post0",
    "python-dotenv>=1.2.1",
    "python-jose[cryptography]>=3.5.0",
    "python-multipart>=0.0.21",
    "pytz>=2025.2",
    "qdrant-client>=1.16.2",
    "redis[hiredis]>=7.1.0",
    "sqlalchemy[asyncio]>=2.0.45",
    "psycopg2>=2.9.11",
    "uvicorn[standard]>=0.40.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-mock>=3.15.1",
    "pytest-asyncio>=1.3.0",
    "httpx>=0.28.1",
    "black>=25.12.0",
    "ruff>=0.14.10",
    "mypy>=1.19.1",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]

[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
    \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.ruff]
line-length = 100
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]
ignore = ["E501"]
exclude = [
    ".git",
    ".venv",
    "__pycache__",
    "build",
    "dist",
]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = false
exclude = [
    ".venv",
    "build",
    "dist",
]

[[tool.mypy.overrides]]
module = [
    "qdrant_client.*",
    "sentence_transformers.*",
    "markitdown.*",
]
ignore_missing_imports = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
]

[tool.coverage.run]
source = ["app"]
omit = [
    "tests/*",
    "*/migrations/*",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
TOML
```

### **Option B: Python Script for Intelligent Fix**
```python
# fix_pyproject.py
import toml
import sys

def fix_pyproject():
    with open('pyproject.toml', 'r') as f:
        data = toml.load(f)
    
    print("🔍 Analyzing pyproject.toml structure...")
    
    # Check if dependencies are in wrong location
    if 'tool' in data and 'setuptools' in data['tool']:
        setuptools_data = data['tool']['setuptools']
        
        # Check packages.find
        if 'packages' in setuptools_data and 'find' in setuptools_data['packages']:
            find_section = setuptools_data['packages']['find']
            
            if 'dependencies' in find_section:
                print("❌ Found dependencies in wrong location: tool.setuptools.packages.find")
                
                # Extract dependencies
                dependencies = find_section.pop('dependencies')
                
                # Ensure project section exists
                if 'project' not in data:
                    data['project'] = {}
                
                # Move dependencies to project section
                data['project']['dependencies'] = dependencies
                print(f"✅ Moved {len(dependencies)} dependencies to [project] section")
            
            # Check for other illegal keys
            allowed_keys = {'where', 'exclude', 'include', 'namespaces'}
            illegal_keys = set(find_section.keys()) - allowed_keys
            if illegal_keys:
                print(f"⚠️  Removing illegal keys from packages.find: {illegal_keys}")
                for key in illegal_keys:
                    del find_section[key]
    
    # Write back
    with open('pyproject.toml', 'w') as f:
        toml.dump(data, f)
    
    print("✅ Fixed pyproject.toml")
    
    # Validate structure
    validate_structure(data)

def validate_structure(data):
    print("\n📋 Validating structure...")
    
    # Check required project fields
    required_project_fields = ['name', 'version', 'description', 'dependencies']
    if 'project' in data:
        missing = [field for field in required_project_fields if field not in data['project']]
        if missing:
            print(f"❌ Missing required project fields: {missing}")
        else:
            print("✅ Project section is valid")
    else:
        print("❌ Missing [project] section entirely")
    
    # Check build-system
    if 'build-system' in data:
        print("✅ Build system configured")
    else:
        print("❌ Missing [build-system] section")

if __name__ == '__main__':
    fix_pyproject()
    print("\n🚀 Now run: uv sync")
```

## **PHASE 3: ENHANCED VALIDATION & FIX SCRIPT**

Create `fix-uv-sync.sh`:
```bash
#!/bin/bash
set -e

echo "🔧 Fixing uv sync issues"

# Backup
BACKUP_FILE="pyproject.toml.backup.$(date +%s)"
cp pyproject.toml "$BACKUP_FILE"
echo "📦 Backup created: $BACKUP_FILE"

echo ""
echo "📋 Current structure analysis:"
echo "-----------------------------"

# Check for misplaced dependencies
if grep -A 50 "\[tool.setuptools.packages.find\]" pyproject.toml | grep -q "dependencies = \["; then
    echo "❌ ERROR: Found dependencies in [tool.setuptools.packages.find]"
    echo "   This violates the TOML schema."
else
    echo "✅ Dependencies are in correct location"
fi

# Check for project.dependencies
if grep -q "^\[project\]" pyproject.toml && grep -A 50 "^\[project\]" pyproject.toml | grep -q "dependencies = \["; then
    echo "✅ [project] has dependencies"
else
    echo "❌ [project] missing dependencies"
fi

echo ""
echo "🔄 Creating corrected pyproject.toml..."

# Extract dependencies list
echo "Extracting dependencies..."
DEPENDENCIES=$(sed -n '/^dependencies = \[/,/^\]/p' pyproject.toml | sed '1d;$d')

if [ -z "$DEPENDENCIES" ]; then
    echo "⚠️ Could not extract dependencies. Creating minimal fix..."
    # Create minimal corrected version
    cat > pyproject.toml.new << 'EOF'
[project]
name = "singapore-smb-support-agent"
version = "0.1.0"
description = "Advanced AI Customer Support Agent for Singapore SMBs"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    {name = "Singapore SMB Support Team"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "alembic>=1.17.2",
    "asyncpg>=0.31.0",
    "fastapi>=0.128.0",
    "langchain>=1.2.0",
    "langchain-community>=0.4.1",
    "langchain-core>=1.2.5",
    "langchain-openai>=1.1.6",
    "langchain-qdrant>=1.1.0",
    "markitdown>=0.1.4",
    "openai>=2.14.0",
    "pydantic>=2.12.5",
    "pydantic-ai>=1.39.0",
    "pydantic-settings>=2.12.0",
    "python-dateutil>=2.9.0.post0",
    "python-dotenv>=1.2.1",
    "python-jose[cryptography]>=3.5.0",
    "python-multipart>=0.0.21",
    "pytz>=2025.2",
    "qdrant-client>=1.16.2",
    "redis[hiredis]>=7.1.0",
    "sqlalchemy[asyncio]>=2.0.45",
    "psycopg2>=2.9.11",
    "uvicorn[standard]>=0.40.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-mock>=3.15.1",
    "pytest-asyncio>=1.3.0",
    "httpx>=0.28.1",
    "black>=25.12.0",
    "ruff>=0.14.10",
    "mypy>=1.19.1",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]
EOF
else
    echo "Using extracted dependencies..."
    # Build new pyproject.toml with dependencies in correct location
    cat > pyproject.toml.new << 'EOF'
[project]
name = "singapore-smb-support-agent"
version = "0.1.0"
description = "Advanced AI Customer Support Agent for Singapore SMBs"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    {name = "Singapore SMB Support Team"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
EOF
    echo "$DEPENDENCIES" >> pyproject.toml.new
    cat >> pyproject.toml.new << 'EOF'
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-mock>=3.15.1",
    "pytest-asyncio>=1.3.0",
    "httpx>=0.28.1",
    "black>=25.12.0",
    "ruff>=0.14.10",
    "mypy>=1.19.1",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]
EOF
fi

# Append remaining tool configurations
echo "Appending tool configurations..."
sed -n '/^\[tool\.black\]/,/^\[/p' "$BACKUP_FILE" | head -n -1 >> pyproject.toml.new
sed -n '/^\[tool\.ruff\]/,/^\[/p' "$BACKUP_FILE" | head -n -1 >> pyproject.toml.new
sed -n '/^\[tool\.mypy\]/,/^\[/p' "$BACKUP_FILE" | head -n -1 >> pyproject.toml.new
sed -n '/^\[tool\.pytest\.ini_options\]/,/^\[/p' "$BACKUP_FILE" | head -n -1 >> pyproject.toml.new
sed -n '/^\[tool\.coverage\.run\]/,/^\[/p' "$BACKUP_FILE" | head -n -1 >> pyproject.toml.new
sed -n '/^\[tool\.coverage\.report\]/,/^\[/p' "$BACKUP_FILE" | head -n -1 >> pyproject.toml.new

# Replace original
mv pyproject.toml.new pyproject.toml

echo ""
echo "✅ Fixed pyproject.toml"
echo ""
echo "📋 Validation:"
echo "--------------"

# Quick validation
if grep -q "^\[project\]" pyproject.toml && grep -A 5 "^\[project\]" pyproject.toml | grep -q "dependencies"; then
    echo "✅ Dependencies are in [project] section"
else
    echo "❌ Still missing dependencies in [project]"
fi

if grep -q "^\[tool\.setuptools\.packages\.find\]" pyproject.toml; then
    if grep -A 10 "^\[tool\.setuptools\.packages\.find\]" pyproject.toml | grep -q "dependencies"; then
        echo "❌ Still has dependencies in packages.find"
    else
        echo "✅ packages.find is clean"
    fi
fi

echo ""
echo "🚀 Testing with uv sync..."
echo "--------------------------"
uv sync

echo ""
echo "💡 If uv sync succeeds, proceed with:"
echo "   docker compose up --build -d"
```

## **PHASE 4: COMPREHENSIVE FIX WITH VALIDATION**

### **Run This Step-by-Step:**

```bash
# 1. First, let's see the exact structure
echo "=== CURRENT STRUCTURE ==="
head -n 50 pyproject.toml

# 2. Create a minimal valid pyproject.toml
cat > pyproject.minimal.toml << 'TOML'
[project]
name = "singapore-smb-support-agent"
version = "0.1.0"
description = "Advanced AI Customer Support Agent for Singapore SMBs"
readme = "README.md"
requires-python = ">=3.12"
authors = [
    {name = "Singapore SMB Support Team"}
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "alembic>=1.17.2",
    "asyncpg>=0.31.0",
    "fastapi>=0.128.0",
    "langchain>=1.2.0",
    "langchain-community>=0.4.1",
    "langchain-core>=1.2.5",
    "langchain-openai>=1.1.6",
    "langchain-qdrant>=1.1.0",
    "markitdown>=0.1.4",
    "openai>=2.14.0",
    "pydantic>=2.12.5",
    "pydantic-ai>=1.39.0",
    "pydantic-settings>=2.12.0",
    "python-dateutil>=2.9.0.post0",
    "python-dotenv>=1.2.1",
    "python-jose[cryptography]>=3.5.0",
    "python-multipart>=0.0.21",
    "pytz>=2025.2",
    "qdrant-client>=1.16.2",
    "redis[hiredis]>=7.1.0",
    "sqlalchemy[asyncio]>=2.0.45",
    "psycopg2>=2.9.11",
    "uvicorn[standard]>=0.40.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=9.0.2",
    "pytest-mock>=3.15.1",
    "pytest-asyncio>=1.3.0",
    "httpx>=0.28.1",
    "black>=25.12.0",
    "ruff>=0.14.10",
    "mypy>=1.19.1",
]

[build-system]
requires = ["setuptools>=68.0.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["app*"]
exclude = ["data*", "tests*", "alembic*"]
TOML

# 3. Validate it
echo ""
echo "=== VALIDATING MINIMAL VERSION ==="
python3 -c "
import toml
try:
    data = toml.load('pyproject.minimal.toml')
    print('✅ Syntax is valid')
    
    # Check structure
    if 'project' in data and 'dependencies' in data['project']:
        print(f'✅ Dependencies found: {len(data[\"project\"][\"dependencies\"])} packages')
    
    if 'tool' in data and 'setuptools' in data['tool']:
        print('✅ Setuptools configuration found')
        
except Exception as e:
    print(f'❌ Validation failed: {e}')
"

# 4. Test with uv
echo ""
echo "=== TESTING WITH UV ==="
cp pyproject.minimal.toml pyproject.toml
uv sync --dry-run

# 5. If dry-run works, do actual sync
if [ $? -eq 0 ]; then
    echo "✅ Dry run successful, proceeding with actual sync..."
    uv sync
else
    echo "❌ Dry run failed, checking for other issues..."
fi
```

## **PHASE 5: ALTERNATIVE APPROACH - USE `pyproject.toml` VALIDATOR**

```bash
# Install toml validator if not present
pip install toml-check 2>/dev/null || pip install toml

# Validate current file
python3 -c "
import toml
import sys

try:
    with open('pyproject.toml', 'r') as f:
        data = toml.load(f)
    print('✅ TOML syntax is valid')
    
    # Check for common issues
    issues = []
    
    # 1. Check for dependencies in wrong place
    if 'tool' in data and 'setuptools' in data['tool']:
        setuptools = data['tool']['setuptools']
        if 'packages' in setuptools and 'find' in setuptools['packages']:
            find_section = setuptools['packages']['find']
            illegal_keys = [k for k in find_section.keys() 
                          if k not in ['where', 'exclude', 'include', 'namespaces']]
            if illegal_keys:
                issues.append(f'Illegal keys in packages.find: {illegal_keys}')
    
    # 2. Check project has dependencies
    if 'project' not in data:
        issues.append('Missing [project] section')
    elif 'dependencies' not in data['project']:
        issues.append('Missing dependencies in [project] section')
    
    # 3. Check build-system
    if 'build-system' not in data:
        issues.append('Missing [build-system] section')
    
    if issues:
        print('❌ Issues found:')
        for issue in issues:
            print(f'  - {issue}')
    else:
        print('✅ No structural issues found')
        
except toml.TomlDecodeError as e:
    print(f'❌ TOML decode error: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Error: {e}')
    sys.exit(1)
"
```

## **PHASE 6: QUICK MANUAL FIX (Execute Now)**

```bash
# Execute this ONE command to fix the issue:
sed -i '/^\[tool\.setuptools\.packages\.find\]/,/^\[/ {
    /^dependencies = \[/,/^\]/ {
        /^dependencies = \[/ {
            h
            d
        }
        /^\]/ {
            x
            /dependencies = \[/! {
                x
                d
            }
            x
            s/^/\[project\]\ndependencies = [/
            p
            d
        }
        /^dependencies = \[/!d
    }
}' pyproject.toml

# Then manually clean up - or better, use this Python script:
python3 << 'PYTHON'
import re

with open('pyproject.toml', 'r') as f:
    content = f.read()

# Move dependencies from tool.setuptools.packages.find to project
pattern = r'(\[tool\.setuptools\.packages\.find\]\s*.*?)(dependencies = \[.*?\n\])'
match = re.search(pattern, content, re.DOTALL)

if match:
    # Extract dependencies
    dependencies = match.group(2)
    
    # Remove from tool section
    content = re.sub(r'(\[tool\.setuptools\.packages\.find\]\s*.*?)dependencies = \[.*?\n\]', 
                    r'\1', content, flags=re.DOTALL)
    
    # Add to project section
    project_section = re.search(r'(\[project\].*?)(?=\n\[|\Z)', content, re.DOTALL)
    if project_section:
        project_content = project_section.group(1)
        # Insert dependencies before the closing bracket of project section
        if 'dependencies' not in project_content:
            # Find where to insert
            lines = project_content.split('\n')
            for i, line in enumerate(lines):
                if line.strip() and not line.startswith('[') and not line.startswith('#'):
                    # Insert before first non-header, non-comment line
                    lines.insert(i, dependencies)
                    break
            else:
                # Append to end
                lines.append(dependencies)
            
            new_project = '\n'.join(lines)
            content = content.replace(project_content, new_project)
    
    with open('pyproject.toml', 'w') as f:
        f.write(content)
    print("✅ Fixed pyproject.toml")
else:
    print("⚠️ No misplaced dependencies found")
PYTHON
```

## **PHASE 7: VERIFICATION & NEXT STEPS**

### **After fixing, run:**
```bash
# 1. Validate the fix
echo "=== VALIDATING FIX ==="
python3 -c "import toml; toml.load('pyproject.toml'); print('✅ TOML is valid')"

# 2. Test uv sync
echo ""
echo "=== TESTING UV SYNC ==="
uv sync --frozen

# 3. If successful, rebuild Docker
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ UV sync successful! Now rebuilding Docker..."
    docker compose down
    docker compose up --build -d
    
    echo ""
    echo "=== FINAL STATUS ==="
    docker compose ps
else
    echo "❌ UV sync still failing. Check pyproject.toml structure."
    echo "Consider using a fresh start:"
    echo "  mv pyproject.toml pyproject.toml.broken"
    echo "  cp pyproject.minimal.toml pyproject.toml"
    echo "  uv sync"
fi
```

## **CRITICAL INSIGHT**

The issue is **purely configuration**, not code:
1. `[tool.setuptools.packages.find]` is for **package discovery** (finding Python packages in your source tree)
2. `[project]` is for **project metadata and dependencies**
3. These sections **must not be mixed**

**The fix is simple: Move `dependencies` from under `[tool.setuptools.packages.find]` to under `[project]`.**

---

**EXECUTE THIS MINIMAL FIX NOW:**
```bash
# Backup
cp pyproject.toml pyproject.toml.backup

# Create corrected version with sed
sed -i '/^\[tool\.setuptools\.packages\.find\]/,/^dependencies = \[/ {
    /^dependencies = \[/ {
        s/^dependencies = \[/[project]\ndependencies = \[/
        p
        d
    }
}' pyproject.toml

# Remove the original dependencies line from tool section
sed -i '/^\[tool\.setuptools\.packages\.find\]/,/^\[/ {
    /^dependencies = \[/,/^\]/ {
        /^dependencies = \[/d
        /^\]/d
    }
}' pyproject.toml

# Test
uv sync
```

**If that fails, use the nuclear option:**
```bash
# Replace entire file with minimal working version
curl -s https://gist.githubusercontent.com/your-gist/raw/pyproject-fixed.toml > pyproject.toml
# OR use the minimal version shown in Phase 4
```

**Expected result:** `uv sync` succeeds, then you can run `docker compose up --build -d` to get all services running.
