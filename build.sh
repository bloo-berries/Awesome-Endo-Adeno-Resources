#!/bin/bash
set -e

# Debug - Show current directory and files
echo "Current directory: $(pwd)"
echo "Listing files in current directory:"
ls -la

# Check if Gemfile exists
if [ -f "Gemfile" ]; then
  echo "Found Gemfile"
else
  echo "Gemfile not found, checking case sensitivity issue..."
  # List any gemfile regardless of case
  find . -maxdepth 1 -name "[gG]emfile" -type f
  
  # If lowercase gemfile exists, create a proper Gemfile
  if [ -f "gemfile" ]; then
    echo "Found lowercase gemfile, copying to Gemfile..."
    cp gemfile Gemfile
  else
    echo "No gemfile found in any case variation."
    exit 1
  fi
fi

# Install dependencies and build
echo "Installing bundler..."
gem install bundler

echo "Installing dependencies..."
bundle install

echo "Building Jekyll site..."
bundle exec jekyll build 