# Specify the source for Ruby gems
source "https://rubygems.org"

# Core Jekyll dependency
gem "jekyll", "~> 4.3.2"

# Required for Jekyll to run on Ruby 3+ (handles HTTP server functionality)
gem "webrick", "~> 1.8"

# GitHub Pages compatibility
gem "github-pages", group: :jekyll_plugins

# Jekyll plugins for enhanced functionality
group :jekyll_plugins do
  # Generates RSS/Atom feed for blog posts
  gem "jekyll-feed"
  
  # Adds SEO meta tags for better search engine optimization
  gem "jekyll-seo-tag"
  
  # Generates a sitemap.xml for search engines
  gem "jekyll-sitemap"
end
