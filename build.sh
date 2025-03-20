#!/bin/bash
set -e

# Debug - Show current directory and files
echo "Current directory: $(pwd)"
echo "Listing files in current directory:"
ls -la

# Ensure we're in the correct directory
if [ ! -f "Gemfile" ]; then
    echo "Error: Gemfile not found in current directory"
    echo "Current directory contents:"
    ls -la
    exit 1
fi

# Install bundler if not already installed
if ! command -v bundler &> /dev/null; then
    echo "Installing bundler..."
    gem install bundler
fi

# Install dependencies
echo "Installing dependencies..."
bundle install

# Build the site
echo "Building Jekyll site..."
bundle exec jekyll build

# Verify build output
if [ ! -d "_site" ]; then
    echo "Error: Build failed - _site directory not created"
    exit 1
fi

echo "Build completed successfully!" 