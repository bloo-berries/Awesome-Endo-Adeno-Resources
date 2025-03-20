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
bundle exec jekyll build

# Create a simple file to verify build completed
echo "Build completed at $(date)" > _site/build_complete.txt
echo "Build output contents:"
ls -la _site

echo "===== BUILD PROCESS COMPLETE =====" 