# Weblate Common Errors and Solutions

**Comprehensive troubleshooting guide for typical setup issues**

---

## Table of Contents

1. [Installation Errors](#installation-errors)
2. [Database Errors](#database-errors)
3. [Service Startup Errors](#service-startup-errors)
4. [Component Creation Errors](#component-creation-errors)
5. [Git/VCS Errors](#gitvcs-errors)
6. [Translation Errors](#translation-errors)
7. [Performance Issues](#performance-issues)

---

## Installation Errors

### Error 1: "ModuleNotFoundError: No module named 'weblate.settings'"

**When it occurs:** Starting Celery or Django server

**Error message:**
```
ModuleNotFoundError: No module named 'weblate.settings'
```

**Cause:** Missing `settings.py` file in your project

**Solution:**
```bash
# Copy settings to the installed package location
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut-d'.' -f1,2)
cp ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings_example.py \
   ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings.py

# Edit the settings file
nano ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings.py
```

**Important:** The official docs recommend copying settings within the installed package, not creating a local directory.

**Verification:**
```bash
ls -l weblate/settings.py
# Should show the file exists
```

---

### Error 2: Package Installation Fails

**When it occurs:** Running `uv pip install "weblate[all]"`

**Error message:**
```
error: failed to build wheel for ...
```

**Cause:** Missing system development packages

**Solution:**
```bash
# Install build dependencies
sudo apt install -y \
  libxml2-dev libxslt-dev libfreetype6-dev libjpeg-dev libz-dev libyaml-dev \
  libffi-dev libcairo-dev gir1.2-pango-1.0 gir1.2-rsvg-2.0 libgirepository-2.0-dev \
  libacl1-dev liblz4-dev libzstd-dev libxxhash-dev libssl-dev libpq-dev libjpeg-dev build-essential \
  python3-gdbm python3-dev git

# Note: Older distributions use libgirepository1.0-dev instead

# Optional dependencies for LDAP/SAML
sudo apt install -y \
  libldap2-dev libldap-common libsasl2-dev \
  libxmlsec1-dev

# Production server components (separate installations)
sudo apt install -y nginx uwsgi uwsgi-plugin-python3
sudo apt install -y redis-server
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y exim4
sudo apt install -y gettext

# Then retry installation
source ~/weblate-env/bin/activate
uv pip install "weblate[all]"
```

---

### Error 3: "command not found: uv"

**When it occurs:** After installing uv

**Solution:**
```bash
# Reload shell environment
source $HOME/.cargo/env

# Or add to ~/.bashrc permanently
echo 'source $HOME/.cargo/env' >> ~/.bashrc
source ~/.bashrc
```

---

## Database Errors

### Error 4: "FATAL: password authentication failed for user 'weblate'"

**When it occurs:** Django trying to connect to PostgreSQL

**Cause:** Database password mismatch

**Solution:**
```bash
# Reset PostgreSQL password
sudo -u postgres psql << EOF
ALTER USER weblate WITH PASSWORD 'weblate';
\q
EOF

# Update settings.py to match
nano weblate/settings.py
# Set: DATABASES['default']['PASSWORD'] = 'weblate'
```

**Verification:**
```bash
psql -U weblate -h 127.0.0.1 -d weblate -W
# Enter password: weblate
# Should connect successfully
```

---

### Error 5: "IntegrityError: null value in column 'hide_glossary_matches'"

**When it occurs:** Creating a new component

**Error message:**
```
django.db.utils.IntegrityError: null value in column "hide_glossary_matches" 
of relation "trans_component" violates not-null constraint
```

**Cause:** Migration created column without database-level default

**Solution:**
```bash
source ~/weblate-env/bin/activate

# Fix the database default
weblate dbshell <<< "ALTER TABLE trans_component ALTER COLUMN hide_glossary_matches SET DEFAULT false;"
```

**Note:** The official migrations should handle this, but if you encounter this error, this fix resolves it.

**Verification:**
```bash
weblate dbshell << EOF
SELECT column_name, column_default, is_nullable 
FROM information_schema.columns 
WHERE table_name = 'trans_component' 
AND column_name = 'hide_glossary_matches';
\q
EOF
```

Expected output:
```
 column_name          | column_default | is_nullable 
----------------------+----------------+-------------
 hide_glossary_matches | false          | NO
```

---

### Error 6: "IntegrityError: null value in column 'pending'"

**When it occurs:** Committing translations or using addons

**Error message:**
```
django.db.utils.IntegrityError: null value in column "pending" 
of relation "addons_addonactivitylog" violates not-null constraint
```

**Cause:** Same as Error 5 - missing database default

**Solution:**
```bash
source ~/weblate-env/bin/activate

weblate dbshell <<< "ALTER TABLE addons_addonactivitylog ALTER COLUMN pending SET DEFAULT false;"
```

**Note:** The official migrations should handle this, but if you encounter this error, this fix resolves it.

---

### Error 7: "relation 'trans_component' does not exist"

**When it occurs:** First startup or after database reset

**Cause:** Database migrations not applied

**Solution:**
```bash
source ~/weblate-env/bin/activate

# Run all migrations
weblate migrate

# Create admin user if needed
weblate createadmin
```

---

## Service Startup Errors

### Error 8: Celery Won't Start

**When it occurs:** Starting Celery workers

**Error message:**
```
ERROR: Cannot connect to redis://localhost:6379
```

**Cause:** Redis not running

**Solution:**
```bash
# Check Redis status
sudo systemctl status redis-server

# Start Redis if stopped
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test connection
redis-cli ping
# Should return: PONG

# If Redis is running but connection fails, check firewall
sudo ufw status
```

---

### Error 9: Port 8000 Already in Use

**When it occurs:** Starting Django server

**Error message:**
```
Error: That port is already in use.
```

**Solution:**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill <PID>

# Or use different port
weblate runserver 0.0.0.0:8001
```

---

### Error 10: "Permissions denied" on Data Directory

**When it occurs:** Weblate trying to write files

**Solution:**
```bash
cd ~/Documents/weblate

# Fix ownership
chown -R $USER:$USER data/

# Fix permissions
chmod -R 755 data/
```

---

## Component Creation Errors

### Error 11: Component Shows "0 Strings"

**When it occurs:** After creating component

**Cause:** Multiple possible causes

**Solution 1: Migrations not applied**
```bash
source ~/weblate-env/bin/activate

# Apply all migrations
weblate migrate

# Fix database defaults if needed (see Error 5 & 6)
weblate dbshell <<< "ALTER TABLE trans_component ALTER COLUMN hide_glossary_matches SET DEFAULT false;"
weblate dbshell <<< "ALTER TABLE addons_addonactivitylog ALTER COLUMN pending SET DEFAULT false;"

# Force reload translations
weblate loadpo --all
```

**Solution 2: Wrong file mask**
Check your file mask matches actual files:
```bash
# Find your data directory (check settings.py for DATA_DIR)
# List files in cloned repository
ls -laR ~/weblate-data/vcs/PROJECT_SLUG/COMPONENT_SLUG/

# Update component with correct file mask via web UI
```

**Solution 3: Missing monolingual base file**
For monolingual formats (Android, JSON, etc.), ensure:
- Base language file exists
- Path is correct relative to repository root
- File format matches

---

### Error 12: "Repository could not be cloned"

**When it occurs:** Creating component with Git repository

**Possible causes and solutions:**

**Private repository without authentication:**
```python
# Use SSH URL with deploy key
repo = "git@github.com:username/repo.git"

# Or HTTPS with token
repo = "https://username:TOKEN@github.com/username/repo.git"
```

**Invalid repository URL:**
```bash
# Test manually
git ls-remote https://github.com/username/repo.git
```

**SSH key not configured:**
```bash
# Find your data directory (check settings.py for DATA_DIR)
# Add Weblate SSH key to GitHub
cat ~/weblate-data/ssh/id_ed25519.pub
# Copy and add to GitHub → Settings → Deploy keys
```

---

### Error 13: "Could not parse base file"

**When it occurs:** Component with monolingual format

**Cause:** Invalid or corrupted base language file

**Solution:**
```bash
# Find your data directory (check settings.py for DATA_DIR)
# Verify file is valid
cd ~/weblate-data/vcs/PROJECT_SLUG/COMPONENT_SLUG/

# For JSON
python3 -m json.tool path/to/base.json

# For XML
xmllint --noout path/to/strings.xml

# Check encoding
file -i path/to/file
```

---

## Git/VCS Errors

### Error 14: "Could not push: Permission denied (publickey)"

**When it occurs:** Pushing translations to repository

**Cause:** SSH key not added to GitHub or lacks write permission

**Solution:**

1. **Get Weblate SSH public key:**
```bash
# Find your data directory (check settings.py for DATA_DIR)
cat ~/weblate-data/ssh/id_ed25519.pub
```

2. **Add to GitHub:**
   - Go to repository → Settings → Deploy keys
   - Click "Add deploy key"
   - Paste key
   - ✅ **Check "Allow write access"**

3. **Test SSH connection:**
```bash
ssh -T git@github.com
```

---

### Error 15: "Could not create pull request 401: Bad credentials"

**When it occurs:** VCS type is "github" and trying to create PR

**Cause:** Invalid or expired GitHub API token

**Solution:**

1. **Generate new GitHub token:**
   - Go to: https://github.com/settings/tokens/new
   - Select scope: ✅ `repo`
   - Generate and copy token

2. **Update settings.py:**
```python
GITHUB_CREDENTIALS = {
    "api.github.com": {
        "username": "your-github-username",
        "token": "ghp_YOUR_NEW_TOKEN_HERE",
        "scheme": "https",
    }
}
```

3. **Restart Weblate:**
```bash
pkill -f "weblate runserver"
pkill -f "celery.*weblate"

# Restart services
source ~/weblate-env/bin/activate
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery start
weblate runserver
```

---

### Error 16: "Could not read Username for 'https://github.com': terminal prompts disabled"

**When it occurs:** Pushing with HTTPS URL without credentials

**Cause:** Using HTTPS URL format without embedded authentication

**Solution - Use SSH instead:**
```python
# Change component URLs from HTTPS to SSH
# From: https://github.com/username/repo.git
# To:   git@github.com:username/repo.git
```

**Via Django shell:**
```bash
weblate shell << EOF
from weblate.trans.models import Component
c = Component.objects.get(project__slug='myproject', slug='mycomponent')
c.repo = "git@github.com:username/repo.git"
c.push = "git@github.com:username/repo.git"
c.save(update_fields=['repo', 'push'])
EOF
```

---

## Translation Errors

### Error 17: "You cannot save this translation"

**When it occurs:** Trying to save translation

**Cause:** User lacks permission

**Solution:**
```bash
# Grant user translation permission
# Via web UI: Settings → Users → [Username] → Teams → Add to Translators
```

---

### Error 18: "Translation is locked"

**When it occurs:** Trying to translate

**Cause:** Component or project is locked

**Solution:**
```bash
# Unlock via web UI: Component → Manage → Repository → Unlock

# Or via shell:
weblate shell << EOF
from weblate.trans.models import Component
c = Component.objects.get(project__slug='myproject', slug='mycomponent')
c.do_lock(None, lock=False)
EOF
```

---

### Error 19: Automatic Translation Not Working

**When it occurs:** Using auto-translate feature

**Possible causes:**

**1. No translation memory:**
```bash
# Import existing translations
weblate shell << EOF
from weblate.trans.models import Component
c = Component.objects.get(project__slug='myproject', slug='mycomponent')
c.commit_pending("import", None)
EOF
```

**2. Celery not running:**
```bash
ps aux | grep celery | grep -v grep
# If no output, start Celery
```

---

## Performance Issues

### Error 20: Slow Translation Loading

**Cause:** Database queries not optimized

**Solution:**
```bash
# Run database optimization
weblate shell << EOF
from django.core.management import call_command
call_command('optimize_index')
EOF

# Restart services
pkill -f "weblate runserver"
pkill -f "celery.*weblate"
# Then start again
```

---

### Error 21: High Memory Usage

**Cause:** Too many Celery workers

**Solution:**
Edit Celery configuration to limit workers:

```bash
# Start with specific worker count
celery -A weblate.utils worker -B --loglevel=info --concurrency=2
```

---

## Diagnostic Commands

### General Health Check
```bash
source ~/weblate-env/bin/activate

# System check
weblate check --deploy

# Database check
weblate dbshell <<< "\dt"

# Redis check
redis-cli ping
```

### Service Status
```bash
# Check running processes
ps aux | grep -E "(celery|runserver)" | grep -v grep

# Check ports
lsof -i :8000  # Django
lsof -i :6379  # Redis
lsof -i :5432  # PostgreSQL
```

### Log Analysis
```bash
# Django development server logs (if running in background with nohup)
tail -f server.log

# Celery logs (if using example script)
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
tail -f ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log
```

---

## Emergency Fixes

### Complete Reset (Development Only!)

**WARNING:** This deletes all data!

```bash
# Stop services
pkill -f "weblate runserver"
pkill -f "celery.*weblate"

# Drop and recreate database
sudo -u postgres psql << EOF
DROP DATABASE weblate;
CREATE DATABASE weblate;
GRANT ALL PRIVILEGES ON DATABASE weblate TO weblate;
\q
EOF

# Clear data directory (adjust path to match your DATA_DIR setting)
rm -rf ~/weblate-data/*

# Rerun migrations
source ~/weblate-env/bin/activate
weblate migrate

# Fix database defaults if needed
weblate dbshell <<< "ALTER TABLE trans_component ALTER COLUMN hide_glossary_matches SET DEFAULT false;"
weblate dbshell <<< "ALTER TABLE addons_addonactivitylog ALTER COLUMN pending SET DEFAULT false;"

# Create admin
weblate createadmin

# Start services
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery start
weblate runserver
```

---

## Preventive Measures

### Always Run After Installation
```bash
source ~/weblate-env/bin/activate

# 1. Apply migrations
weblate migrate

# 2. Fix database defaults (only if you encounter IntegrityError)
# weblate dbshell <<< "ALTER TABLE trans_component ALTER COLUMN hide_glossary_matches SET DEFAULT false;"
# weblate dbshell <<< "ALTER TABLE addons_addonactivitylog ALTER COLUMN pending SET DEFAULT false;"

# 3. Verify services
systemctl status postgresql redis-server
ps aux | grep -E "(celery|runserver)"
```

### Regular Maintenance
```bash
source ~/weblate-env/bin/activate

# Weekly cleanup
weblate cleanuptrans

# Monthly backup
pg_dump -U weblate weblate > backup-$(date +%Y%m%d).sql
# Adjust path to match your DATA_DIR setting
tar -czf data-backup-$(date +%Y%m%d).tar.gz ~/weblate-data/
```

---

## Getting Further Help

If errors persist:

1. **Check logs carefully:**
   ```bash
   tail -100 server.log
   tail -100 weblate-celery.log
   ```

2. **Run full diagnostic:**
   ```bash
   weblate check --deploy
   ```

3. **Search documentation:**
   - https://docs.weblate.org/
   - https://github.com/WeblateOrg/weblate/issues

4. **Ask community:**
   - https://github.com/WeblateOrg/weblate/discussions

---

**Last Updated:** October 10, 2025  
**Weblate Version:** 5.13.3  
**Covers:** Installation, Database, Services, Git, Translation errors

