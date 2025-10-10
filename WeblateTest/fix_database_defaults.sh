#!/bin/bash
# Fix missing database-level defaults in Weblate database
# These columns have Python defaults in models but missing database defaults

cd /home/wefwe2ffw2/Documents/weblate
source weblate-env/bin/activate

echo "Fixing database default values..."

# Fix 1: trans_component.hide_glossary_matches
echo "1. Setting default for trans_component.hide_glossary_matches..."
weblate dbshell <<< "ALTER TABLE trans_component ALTER COLUMN hide_glossary_matches SET DEFAULT false;"

# Fix 2: addons_addonactivitylog.pending
echo "2. Setting default for addons_addonactivitylog.pending..."
weblate dbshell <<< "ALTER TABLE addons_addonactivitylog ALTER COLUMN pending SET DEFAULT false;"

echo ""
echo "✅ All database defaults fixed!"
echo ""
echo "Verification:"
weblate dbshell <<< "
SELECT 
    table_name, 
    column_name, 
    column_default, 
    is_nullable 
FROM information_schema.columns 
WHERE (table_name = 'trans_component' AND column_name = 'hide_glossary_matches')
   OR (table_name = 'addons_addonactivitylog' AND column_name = 'pending')
ORDER BY table_name, column_name;
"

echo ""
echo "Done! You can now use Weblate without IntegrityErrors."

