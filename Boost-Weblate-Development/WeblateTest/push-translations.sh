#!/bin/bash

# Manual Push Script for Weblate
# Push committed translations to GitHub

cd /home/wefwe2ffw2/Documents/weblate
source weblate-env/bin/activate

echo "🚀 Pushing translations to GitHub..."
echo ""

python3 manage.py shell << 'EOF'
from weblate.trans.models import Component

c = Component.objects.get(project__slug='project02', slug='component0201')

# Check if there's anything to push
if c.needs_commit():
    print("⚠️  There are uncommitted changes!")
    print("   Committing first...")
    c.commit_pending("manual push", None)
    print("✓ Changes committed")
    print()

# Now push
print("Pushing to GitHub...")
c.do_push(None)
print()
print("✓ Successfully pushed to GitHub!")
print("✓ Pull request created (if VCS type is 'github')")
EOF

echo ""
echo "Done!"

