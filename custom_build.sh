#!/bin/bash
set -e  # Exit immediately if a command exits with a non-zero status

# Echo the script steps for debugging
echo "===== CLOUDFLARE PAGES BUILD SCRIPT ====="
echo "Current directory: $(pwd)"
echo "Files in current directory:"
ls -la

# Create a debug file in the site output to verify the build process
echo "Debug: Build script was executed at $(date)" > build_debug.txt

# Check for Gemfile and handle it properly
if [ ! -f "Gemfile" ]; then
    echo "Gemfile not found in current directory."
    echo "Creating a new Gemfile with required dependencies..."
    
    # Create a new Gemfile with the necessary dependencies
    cat > Gemfile << 'EOF'
# Specify the source for Ruby gems
source "https://rubygems.org"

# Core Jekyll dependency
gem "jekyll", "~> 4.3.2"

# Required for Jekyll to run on Ruby 3+ (handles HTTP server functionality)
gem "webrick", "~> 1.8"

# Jekyll plugins for enhanced functionality
group :jekyll_plugins do
  # Generates RSS/Atom feed for blog posts
  gem "jekyll-feed"
  
  # Adds SEO meta tags for better search engine optimization
  gem "jekyll-seo-tag"
  
  # Generates a sitemap.xml for search engines
  gem "jekyll-sitemap"
end

# Add any additional dependencies your site needs
gem "kramdown-parser-gfm"  # GitHub Flavored Markdown support
EOF

    echo "Created new Gemfile"
    cat Gemfile
fi

# Ensure _config.yml has correct markdown processor
echo "Checking _config.yml for correct markdown processor..."
if [ -f "_config.yml" ]; then
    # Create backup
    cp _config.yml _config.yml.bak
    
    # Completely overwrite _config.yml with known good values
    echo "Creating new _config.yml with correct kramdown settings..."
    cat > _config.yml << 'EOF'
title: Awesome Endo and Adeno Resources
remote_theme: "jekyll/minima@1e8a445"
markdown: kramdown
kramdown:
  input: GFM
  syntax_highlighter: rouge
minima:
  skin: auto

# Site configuration
url: "" # Leave empty for local development
baseurl: "" # Leave empty for root domain

# Build settings
source: .
destination: _site
exclude: ['Gemfile', 'Gemfile.lock', 'node_modules', 'vendor/bundle', 'vendor/cache', 'vendor/gems', 'vendor/ruby']

# Enable GitHub Pages and Jekyll
github:
  pages:
    enabled: true
    build: true
EOF
    
    echo "Current _config.yml content:"
    cat _config.yml
else
    echo "Warning: _config.yml not found"
fi

# Print Ruby and Bundler versions
echo "Ruby version: $(ruby -v)"
echo "Gem version: $(gem -v)"

# Install bundler (Cloudflare may have bundler but we install it anyway)
echo "Installing bundler..."
gem install bundler

# Install dependencies
echo "Installing dependencies..."
bundle install

# Debug what Jekyll sees
echo "Files available to Jekyll:"
ls -la

# Build the Jekyll site
echo "Building Jekyll site..."
if [ -f ".jekyll-config" ]; then
  echo "Using special Jekyll configuration..."
  JEKYLL_OPTIONS="-V --trace --config _config.yml,.jekyll-config"
else
  JEKYLL_OPTIONS="-V --trace"
fi

# Add temporary debug info for README.md
echo "Checking README.md for potential issues..."
head -n 10 README.md

# Create a patched copy of README.md with frontmatter
echo "Creating README-patched.md with explicit kramdown frontmatter..."
cat > README-patched.md << 'EOF'
---
markdown: kramdown
---

EOF

# Append the original README content to the patched file
cat README.md >> README-patched.md

# Temporarily replace the original with the patched version
mv README-patched.md README.md.temp
mv README.md README.md.original
mv README.md.temp README.md

# Create a modified index.md that doesn't use includes
echo "Creating a modified index.md without include statements..."
if [ -f "index.md" ]; then
  cp index.md index.md.original
  
  # Create a new index.md that directly embeds README content
  cat > index.md << 'EOF'
---
layout: default
title: Awesome Endo and Adeno Resources
markdown: kramdown
---

EOF
  
  # Append README.md content directly to index.md rather than using include
  cat README.md >> index.md
  
  echo "Created new index.md that directly embeds README content"
  head -n 10 index.md
fi

# Create a _kramdown.yml file with explicit settings
echo "Creating _kramdown.yml with explicit settings..."
cat > _kramdown.yml << 'EOF'
auto_ids: true
input: GFM
syntax_highlighter: rouge
EOF

# Build with verbose option and explicit env vars
echo "Running Jekyll build with verbose output..."
JEKYLL_ENV=production JEKYLL_LOG_LEVEL=debug bundle exec jekyll build -V --trace --config _config.yml,_config.local.yml || {
  echo "Jekyll build failed, creating basic static HTML instead..."
  
  # Create _site directory if it doesn't exist
  mkdir -p _site
  
  # Create a simple index.html with README.md content
  echo "<!DOCTYPE html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\">
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
  <title>Awesome Endo and Adeno Resources</title>
  <style>
    body { 
      font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
      line-height: 1.6;
      color: #333;
      max-width: 900px;
      margin: 0 auto;
      padding: 20px;
    }
    a { color: #0366d6; text-decoration: none; }
    a:hover { text-decoration: underline; }
    h1, h2, h3, h4 { margin-top: 24px; margin-bottom: 16px; font-weight: 600; line-height: 1.25; }
    h1 { font-size: 2em; }
    h2 { font-size: 1.5em; padding-bottom: 0.3em; border-bottom: 1px solid #eaecef; }
    h3 { font-size: 1.25em; }
    ul, ol { padding-left: 2em; }
    li { margin-bottom: 0.25em; }
    code { font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace; background-color: rgba(27,31,35,0.05); padding: 0.2em 0.4em; border-radius: 3px; }
    pre { background-color: #f6f8fa; border-radius: 3px; padding: 16px; overflow: auto; }
    pre code { background-color: transparent; padding: 0; }
    blockquote { margin-left: 0; padding-left: 1em; color: #6a737d; border-left: 0.25em solid #dfe2e5; }
    hr { height: 0.25em; padding: 0; margin: 24px 0; background-color: #e1e4e8; border: 0; }
    table { border-collapse: collapse; width: 100%; overflow: auto; }
    table th, table td { padding: 6px 13px; border: 1px solid #dfe2e5; }
    table tr { background-color: #fff; border-top: 1px solid #c6cbd1; }
    table tr:nth-child(2n) { background-color: #f6f8fa; }
  </style>
</head>
<body>
  <h1>Awesome Endo and Adeno Resources</h1>
  <div id=\"content\">
" > _site/index.html

  # Convert README.md to HTML and append to the index.html file
  if command -v pandoc >/dev/null 2>&1; then
    echo "Using pandoc to convert README.md to HTML..."
    pandoc -f markdown -t html README.md >> _site/index.html
  else
    echo "Pandoc not available, using simple cat instead..."
    echo "<pre>" >> _site/index.html
    cat README.md >> _site/index.html
    echo "</pre>" >> _site/index.html
  fi

  # Close HTML tags
  echo "  </div>
</body>
</html>" >> _site/index.html

  echo "Created basic static HTML site"
  ls -la _site
}

# Create a simple file to verify build completed
echo "Build completed at $(date)" > _site/build_complete.txt
echo "Build output contents:"
ls -la _site

echo "===== BUILD PROCESS COMPLETE =====" 