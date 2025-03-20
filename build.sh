#!/bin/bash
set -e

echo "===== CUSTOM JEKYLL BUILD SCRIPT ====="

# Create a temporary _config_override.yml to ensure proper kramdown settings
cat > _config_override.yml << EOF
# Override kramdown settings
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge
EOF

echo "Created _config_override.yml with proper kramdown settings"

# Create a temporary modified version of index.md that doesn't use include
echo "Creating modified index.md..."
cp index.md index.md.bak

# Fetch README content
README_CONTENT=$(cat README.md)

# Create a new index.md with explicit kramdown front matter and README content embedded
cat > index.md << EOF
---
layout: default
title: Awesome Endo and Adeno Resources
---

# Awesome Endo and Adeno Resources

$README_CONTENT
EOF

echo "Modified index.md to directly include README content"

# Install dependencies
echo "Installing dependencies..."
gem install bundler -v 2.4.19
bundle install

# Build Jekyll site with our override config
echo "Building Jekyll site with override config..."
JEKYLL_ENV=production bundle exec jekyll build --config _config.yml,_config_override.yml

# Restore original index.md
echo "Restoring original index.md..."
mv index.md.bak index.md

# Remove temporary config
rm _config_override.yml

echo "===== BUILD COMPLETE =====" 