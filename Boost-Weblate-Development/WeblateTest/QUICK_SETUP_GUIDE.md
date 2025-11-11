# Weblate Quick Setup Guide

**A streamlined guide for setting up Weblate from scratch**

---

## Overview

This guide walks you through a typical Weblate installation on Ubuntu/Debian in approximately 30-60 minutes.

---

## Prerequisites Checklist

Before starting, ensure you have:

- [ ] Ubuntu 20.04+ or Debian 11+
- [ ] 4 GB RAM minimum
- [ ] 10 GB free disk space
- [ ] Sudo/root access
- [ ] Internet connection

---

## Step 1: Install System Dependencies

### Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### Install Build Dependencies
```bash
sudo apt install -y \
  libxml2-dev libxslt-dev libfreetype6-dev libjpeg-dev libz-dev libyaml-dev \
  libffi-dev libcairo-dev gir1.2-pango-1.0 gir1.2-rsvg-2.0 libgirepository-2.0-dev \
  libacl1-dev liblz4-dev libzstd-dev libxxhash-dev libssl-dev libpq-dev libjpeg-dev build-essential \
  python3-gdbm python3-dev git
```

**Hint:** Older distributions do not have `libgirepository-2.0-dev`, use `libgirepository1.0-dev` instead.

### Install Optional Dependencies (for LDAP/SAML support)
```bash
sudo apt install -y \
  libldap2-dev libldap-common libsasl2-dev \
  libxmlsec1-dev
```

### Install Production Server Components

```bash
# Web server option 1: NGINX and uWSGI
sudo apt install -y nginx uwsgi uwsgi-plugin-python3

# Web server option 2: Apache with mod_wsgi
# sudo apt install -y apache2 libapache2-mod-wsgi-py3

# Caching backend: Redis
sudo apt install -y redis-server

# Database server: PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# SMTP server
sudo apt install -y exim4

# Gettext for the msgmerge add-on
sudo apt install -y gettext
```

**Note:** You can run these components on dedicated servers for larger installations.

**Time:** 5-10 minutes

---

## Step 2: Setup PostgreSQL Database

### Create Database and User
```bash
sudo -u postgres psql << EOF
CREATE DATABASE weblate;
CREATE USER weblate WITH PASSWORD 'weblate';
ALTER ROLE weblate SET client_encoding TO 'utf8';
ALTER ROLE weblate SET default_transaction_isolation TO 'read committed';
ALTER ROLE weblate SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE weblate TO weblate;
\q
EOF
```

### Test Connection
```bash
psql -U weblate -h 127.0.0.1 -d weblate -W
# Enter password: weblate
# If successful, type: \q
```

✅ **Success indicator:** You can connect without errors

**Time:** 2 minutes

---

## Step 3: Verify Redis

```bash
sudo systemctl status redis-server
sudo systemctl enable redis-server

# Test Redis
redis-cli ping
# Should return: PONG
```

✅ **Success indicator:** Redis responds with "PONG"

**Time:** 1 minute

---

## Step 4: Setup Python Environment

### Install uv Package Manager
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.cargo/env
```

### Create Virtual Environment
```bash
cd ~
mkdir -p Documents/weblate
cd Documents/weblate

uv venv weblate-env
source weblate-env/bin/activate
```

### Install Weblate
```bash
uv pip install "weblate[all]"
```

✅ **Success indicator:** Installation completes without errors

**Time:** 10-15 minutes

---

## Step 5: Configure Weblate

### Generate Secret Key
```bash
weblate-generate-secret-key
```

**Save this key!** You'll need it in the next step.

### Copy and Edit Settings

**Important:** Copy settings file to the **installed package location**, not to a local directory.

```bash
# Find your Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

# Copy settings template within the installed package
cp ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings_example.py \
   ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings.py
```

**Note:** The virtualenv must be activated when running weblate commands.

### Edit Configuration
```bash
# Find your Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

# Edit the settings file
nano ~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/settings.py
```

**Minimal required changes:**

```python
# 1. Secret Key (CRITICAL!)
SECRET_KEY = "paste-your-generated-secret-key-here"

# 2. Site Configuration
SITE_DOMAIN = "localhost:8000"
ENABLE_HTTPS = False
SITE_URL = "http://localhost:8000"

# 3. Database credentials
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "weblate",
        "USER": "weblate",
        "PASSWORD": "weblate",
        "HOST": "127.0.0.1",
        "PORT": "",
    }
}

# 4. Data Directory (adjust path as needed)
DATA_DIR = "/home/YOUR_USERNAME/weblate-data"
CACHE_DIR = f"{DATA_DIR}/cache"

# 5. Redis Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
    }
}

# 6. Celery
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = CELERY_BROKER_URL
```

**Save and exit:** `Ctrl+O`, `Enter`, `Ctrl+X`

### Create Data Directory
```bash
mkdir -p ~/weblate-data/cache
```

**Time:** 5 minutes

---

## Step 6: Initialize Database

**Note:** Ensure the virtualenv is activated before running weblate commands.

### Run Migrations
```bash
source ~/weblate-env/bin/activate
weblate migrate
```

✅ **Success indicator:** All migrations apply successfully

**Note:** The official documentation doesn't mention database default fixes as they should be included in migrations. If you encounter IntegrityError issues, see the Common Errors Guide.

### Create Admin User
```bash
weblate createadmin
```

**Save the generated password!**

### Collect Static Files
```bash
weblate collectstatic --noinput
weblate compress
```

**Time:** 5-10 minutes

---

## Step 7: Start Services

### Start Celery Workers

```bash
source ~/weblate-env/bin/activate

# Find Python version for correct path
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

# Start Celery using the example script (recommended)
~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery start
```

**Note:** This is not necessary for development purposes, but strongly recommended for production. See [Background tasks using Celery](https://docs.weblate.org/en/latest/admin/install.html#celery) for more info.

### Start Django Development Server

**For development/testing:**
```bash
weblate runserver 0.0.0.0:8000
```

**For background (production-like):**
```bash
nohup weblate runserver 0.0.0.0:8000 > server.log 2>&1 &
```

**Note:** For production, use uWSGI + NGINX instead of Django's development server.

✅ **Success indicator:** Check if services are running:

```bash
# Check Celery
ps aux | grep celery | grep -v grep

# Check Django
ps aux | grep runserver | grep -v grep

# Test web access
curl -I http://localhost:8000
```

**Time:** 2 minutes

---

## Step 8: Access Weblate

1. **Open browser:** http://localhost:8000
2. **Sign in** with admin credentials from Step 6
3. You can stop the test server with **Ctrl+C**
4. **Review potential issues** at `/manage/performance/` URL or run `weblate check --deploy`

---

## Step 9: Create Your First Project

### Via Web Interface:

1. Click **"Create new translation project"**
2. Fill in:
   - **Project name:** "My App"
   - **URL slug:** "myapp"
   - **Website:** https://example.com (optional)

3. Click **"Save"**

### Add Component:

1. Create a component which points to the VCS repository
2. Important fields:
   - **Component name:** "Android Strings"
   - **Source code repository:** `https://github.com/username/repo.git`
   - **File mask:** `app/src/main/res/values-*/strings.xml` (for finding translatable files)
   - **Monolingual base language file:** `app/src/main/res/values/strings.xml`

Weblate supports a wide range of formats. See [Localization file formats](https://docs.weblate.org/en/latest/formats.html) for more details.

3. Click **"Save"**

✅ **Success indicator:** Component shows strings count > 0

**Note:** This can be a lengthy process depending on the size of your VCS repository.

**Time:** 5 minutes

---

## Verification Checklist

After setup, verify everything works:

- [ ] **Database connection:** `weblate check`
- [ ] **Redis connection:** `redis-cli ping`
- [ ] **Celery running:** `ps aux | grep celery`
- [ ] **Django running:** `ps aux | grep runserver`
- [ ] **Web access:** http://localhost:8000 loads
- [ ] **Admin login:** Credentials work
- [ ] **Project created:** Shows in dashboard
- [ ] **Component created:** Shows strings

---

## Quick Commands Reference

### Start Weblate
```bash
source ~/weblate-env/bin/activate

# Find Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)

# Start Celery
~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery start

# Start Django development server
weblate runserver
```

### Stop Weblate
```bash
# Stop Django (Ctrl+C if running in foreground)
pkill -f "weblate runserver"

# Stop Celery
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
~/weblate-env/lib/python${PYTHON_VERSION}/site-packages/weblate/examples/celery stop
```

### Check Status
```bash
# Activate virtualenv
source ~/weblate-env/bin/activate

# Check services
ps aux | grep -E "(celery|runserver)" | grep -v grep

# System check
weblate check

# Production deployment check
weblate check --deploy
```

---

## Common Paths

| Item | Path |
|------|------|
| **Virtual env** | `~/weblate-env/` |
| **Settings file** | `~/weblate-env/lib/python3.X/site-packages/weblate/settings.py` |
| **Celery script** | `~/weblate-env/lib/python3.X/site-packages/weblate/examples/celery` |
| **Data directory** | `~/weblate-data/` (or as configured in DATA_DIR) |
| **Repositories** | `~/weblate-data/vcs/` |

---

## Next Steps

After successful setup:

1. **Configure GitHub integration** - See "Weblate GitHub Integration Guide"
2. **Set up automatic push** - Configure component push settings
3. **Add translators** - Invite users to projects
4. **Configure webhooks** - Enable automatic updates from repositories

---

## Production Deployment

For production use, you should:

1. **Change passwords:**
   - Database: `DATABASES['default']['PASSWORD']`
   - Admin user: `weblate createadmin --update`

2. **Enable HTTPS:**
   - Set `ENABLE_HTTPS = True`
   - Configure NGINX with SSL certificate

3. **Setup systemd services:**
   - Create service files for Celery and uWSGI
   - Enable automatic startup on boot

4. **Configure backups:**
   - Database: `pg_dump` scheduled with cron
   - Data directory: Regular backups

5. **Set up monitoring:**
   - Server uptime monitoring
   - Error logging (Sentry)
   - Performance monitoring

See **COMPLETE_SETUP_GUIDE.md** for detailed production deployment instructions.

---

## Getting Help

If you encounter issues:

1. **Check error guide:** See "Weblate Common Errors Guide"
2. **Review logs:** `tail -f server.log` and `weblate-celery.log`
3. **Run diagnostics:** `weblate check --deploy`
4. **Official docs:** https://docs.weblate.org/
5. **Community:** https://github.com/WeblateOrg/weblate/discussions

---

## Estimated Total Time

- **Basic installation:** 30-45 minutes
- **With first project:** 45-60 minutes
- **Production setup:** 2-3 hours

---

**Last Updated:** October 10, 2025  
**Weblate Version:** 5.13.3  
**Target OS:** Ubuntu 20.04+ / Debian 11+

