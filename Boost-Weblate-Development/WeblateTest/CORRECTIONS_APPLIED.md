# Corrections Applied to Weblate Guides

**Date:** October 10, 2025  
**Reference:** [Official Weblate Documentation - Installing on Debian and Ubuntu](https://docs.weblate.org/en/latest/admin/install/venv-debian.html)

---

## Overview

All three guide files have been corrected to match the official Weblate documentation exactly. The official documentation is the authoritative source, and all guides now follow its structure and instructions precisely.

---

## Major Corrections Applied

### 1. System Packages Installation

**Changed from:** Single combined apt install command  
**Changed to:** Separated into distinct installation steps as per official docs

#### Build Dependencies
```bash
sudo apt install -y \
  libxml2-dev libxslt-dev libfreetype6-dev libjpeg-dev libz-dev libyaml-dev \
  libffi-dev libcairo-dev gir1.2-pango-1.0 gir1.2-rsvg-2.0 libgirepository-2.0-dev \
  libacl1-dev liblz4-dev libzstd-dev libxxhash-dev libssl-dev libpq-dev libjpeg-dev build-essential \
  python3-gdbm python3-dev git
```

**Note:** Uses `libgirepository-2.0-dev` with a hint that older distributions use `libgirepository1.0-dev`.

#### Optional Dependencies (LDAP/SAML)
```bash
sudo apt install -y \
  libldap2-dev libldap-common libsasl2-dev \
  libxmlsec1-dev
```

#### Production Server Components
**Key addition:** These are installed SEPARATELY, as shown in official docs:
```bash
# Web server option 1: NGINX and uWSGI
sudo apt install -y nginx uwsgi uwsgi-plugin-python3

# Web server option 2: Apache with mod_wsgi
sudo apt install -y apache2 libapache2-mod-wsgi-py3

# Caching backend: Redis
sudo apt install -y redis-server

# Database server: PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# SMTP server
sudo apt install -y exim4

# Gettext for the msgmerge add-on
sudo apt install -y gettext
```

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Step 1
- `COMMON_ERRORS_GUIDE.md` - Error 2

---

### 2. Settings File Location

**Changed from:** Copying settings to local `weblate/settings.py` directory  
**Changed to:** Copying settings within the installed package (as per official docs)

#### Official Method
```bash
# Copy settings template within the installed package
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
cp ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings_example.py \
   ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings.py

# Edit the settings file
nano ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings.py
```

**Note:** The official documentation explicitly shows copying TO the installed package location, NOT creating a separate local `weblate/` directory.

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Step 5
- `COMMON_ERRORS_GUIDE.md` - Error 1

---

### 3. Celery Startup Command

**Changed from:** Multiple options including manual commands  
**Changed to:** Official recommended method using the example script

#### Official Method
```bash
source ~/weblate-env/bin/activate
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery start
```

**Note from official docs:** "This is not necessary for development purposes, but strongly recommended for production."

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Step 7
- `COMMON_ERRORS_GUIDE.md` - Error 15

---

### 4. Data Directory Paths

**Changed from:** Hardcoded paths like `~/Documents/weblate/data/`  
**Changed to:** Generic paths matching official docs (`~/weblate-data/` or user-configured DATA_DIR)

**Examples:**
- SSH keys: `~/weblate-data/ssh/id_ed25519.pub`
- Repositories: `~/weblate-data/vcs/PROJECT_SLUG/COMPONENT_SLUG/`
- Cache: `~/weblate-data/cache/`

**Note:** Official docs use `DATA_DIR` setting which can be configured by the user.

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Multiple sections
- `COMMON_ERRORS_GUIDE.md` - Multiple errors
- `USER_GUIDE.md` - VCS operations section

---

### 5. Working Directory References

**Changed from:** Commands requiring `cd ~/Documents/weblate`  
**Changed to:** Direct commands with virtualenv activation (matching official docs)

#### Before
```bash
cd ~/Documents/weblate
source weblate-env/bin/activate
weblate migrate
```

#### After (Official Style)
```bash
source ~/weblate-env/bin/activate
weblate migrate
```

**Note:** Official documentation assumes virtualenv is activated, with a reminder note: "The virtualenv must be activated when running weblate commands."

**Affected files:**
- All three guides - multiple commands

---

### 6. Database Default Fixes

**Changed from:** Presented as required steps  
**Changed to:** Presented as troubleshooting fixes (official migrations should handle this)

#### Updated Language
```bash
# Fix database defaults (only if you encounter IntegrityError)
# weblate dbshell <<< "ALTER TABLE trans_component ALTER COLUMN hide_glossary_matches SET DEFAULT false;"
# weblate dbshell <<< "ALTER TABLE addons_addonactivitylog ALTER COLUMN pending SET DEFAULT false;"
```

**Note added:** "The official documentation doesn't mention database default fixes as they should be included in migrations. If you encounter IntegrityError issues, see the Common Errors Guide."

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Removed from main steps
- `COMMON_ERRORS_GUIDE.md` - Error 5 & 6 (with clarification note)

---

### 7. GitHub Credentials Configuration

**Changed from:** Missing `scheme` parameter  
**Changed to:** Complete configuration matching official Weblate code

#### Correct Format
```python
GITHUB_CREDENTIALS = {
    "api.github.com": {
        "username": "your-github-username",
        "token": "ghp_YOUR_TOKEN_HERE",
        "scheme": "https",
    }
}
```

**Affected files:**
- `COMMON_ERRORS_GUIDE.md` - Error 15
- References in other guides

---

### 8. Post-Installation Steps

**Changed from:** Generic instructions  
**Changed to:** Match official documentation steps exactly

#### Official Post-Installation Checklist
1. ✅ Access Weblate on http://localhost:8000
2. ✅ Sign in with admin credentials
3. ✅ Stop test server with Ctrl+C
4. ✅ **Review potential issues** at `/manage/performance/` URL or run `weblate check --deploy`

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Step 8

---

### 9. Common Paths Table

**Updated to reflect official documentation structure:**

| Item | Path |
|------|------|
| **Virtual env** | `~/weblate-env/` |
| **Settings file** | `~/weblate-env/lib/python3.X/site-packages/weblate/settings.py` |
| **Celery script** | `~/weblate-env/lib/python3.X/site-packages/weblate/examples/celery` |
| **Data directory** | `~/weblate-data/` (or as configured in DATA_DIR) |
| **Repositories** | `~/weblate-data/vcs/` |

**Affected files:**
- `QUICK_SETUP_GUIDE.md` - Common Paths section

---

### 10. Command References

All command examples now:
- ✅ Use `source ~/weblate-env/bin/activate` (not relative paths)
- ✅ Reference installed package paths for scripts
- ✅ Use official Celery script commands
- ✅ Match official documentation style

**Affected files:**
- All three guides - all command examples

---

## Files Corrected

1. **QUICK_SETUP_GUIDE.md** - Complete rewrite to match official documentation structure
2. **COMMON_ERRORS_GUIDE.md** - All commands and paths updated to official standards
3. **USER_GUIDE.md** - Paths and commands corrected (no major structural changes needed)

---

## Verification Against Official Documentation

✅ **Package installation** - Matches official docs exactly  
✅ **Settings location** - Matches official docs exactly  
✅ **Celery startup** - Matches official docs exactly  
✅ **Data paths** - Uses generic paths like official docs  
✅ **Command style** - Matches official docs format  
✅ **Post-installation** - Includes all official recommendations  

---

## Key Takeaways

1. **Always use official documentation paths** - Not project-specific hardcoded paths
2. **Settings file location matters** - Official method is within installed package
3. **Production components are separate** - nginx, uwsgi, redis, postgresql installed separately
4. **Database fixes are troubleshooting** - Not required steps in official docs
5. **Use official Celery script** - `~/weblate-env/lib/.../weblate/examples/celery start`

---

## References

- **Official Documentation:** https://docs.weblate.org/en/latest/admin/install/venv-debian.html
- **Hardware Requirements:** https://docs.weblate.org/en/latest/admin/install/venv-debian.html#hardware-requirements
- **Configuration:** https://docs.weblate.org/en/latest/admin/install/venv-debian.html#configuring-weblate
- **After Installation:** https://docs.weblate.org/en/latest/admin/install/venv-debian.html#after-installation

---

**Correction completed:** All guides now accurately reflect the official Weblate documentation.
