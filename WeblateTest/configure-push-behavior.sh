#!/bin/bash

# Script to configure Weblate push behavior
# Choose how and when translations are committed and pushed

cd /home/wefwe2ffw2/Documents/weblate
source weblate-env/bin/activate

echo "Weblate Push Configuration"
echo "====================================="
echo ""
echo "Choose push behavior:"
echo ""
echo "1) Manual push only (disable auto-push)"
echo "   - Translations are committed automatically"
echo "   - You manually push when ready"
echo ""
echo "2) Auto-push on commit (current setting)"
echo "   - Translations are committed automatically"
echo "   - Pushes immediately after commit"
echo ""
echo "3) Commit immediately + Auto-push"
echo "   - Commits right after each translation"
echo "   - Pushes immediately"
echo ""
echo "4) Custom configuration"
echo ""

read -p "Enter your choice (1-4): " choice

case $choice in
  1)
    echo "Setting: Manual push only..."
    python3 manage.py shell -c "
from weblate.trans.models import Component
c = Component.objects.get(project__slug='project02', slug='component0201')
c.push_on_commit = False
c.commit_pending_age = 24
c.save(update_fields=['push_on_commit', 'commit_pending_age'])
print('✓ Auto-push disabled')
print('  - Commits: Every 24 hours')
print('  - Push: Manual only')
"
    ;;
  2)
    echo "Setting: Auto-push on commit..."
    python3 manage.py shell -c "
from weblate.trans.models import Component
c = Component.objects.get(project__slug='project02', slug='component0201')
c.push_on_commit = True
c.commit_pending_age = 24
c.save(update_fields=['push_on_commit', 'commit_pending_age'])
print('✓ Auto-push enabled')
print('  - Commits: Every 24 hours')
print('  - Push: Automatic after commit')
"
    ;;
  3)
    echo "Setting: Immediate commit + Auto-push..."
    python3 manage.py shell -c "
from weblate.trans.models import Component
c = Component.objects.get(project__slug='project02', slug='component0201')
c.push_on_commit = True
c.commit_pending_age = 0
c.save(update_fields=['push_on_commit', 'commit_pending_age'])
print('✓ Immediate commit and push enabled')
print('  - Commits: Immediately after translation')
print('  - Push: Automatic after commit')
"
    ;;
  4)
    read -p "Commit pending age (hours, 0=immediate): " hours
    read -p "Enable auto-push? (yes/no): " autopush
    
    if [[ "$autopush" == "yes" ]]; then
      push_value="True"
    else
      push_value="False"
    fi
    
    python3 manage.py shell -c "
from weblate.trans.models import Component
c = Component.objects.get(project__slug='project02', slug='component0201')
c.push_on_commit = $push_value
c.commit_pending_age = $hours
c.save(update_fields=['push_on_commit', 'commit_pending_age'])
print('✓ Custom configuration saved')
print(f'  - Commits: Every {$hours} hours')
print(f'  - Push: {\"Automatic\" if $push_value else \"Manual\"}')
"
    ;;
  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo "Configuration updated!"
echo ""
echo "To manually commit: Go to component → Repository maintenance → Commit"
echo "To manually push: Go to component → Repository maintenance → Push"

