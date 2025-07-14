#!/usr/bin/env python3
"""
Script to check for broken links in the Awesome Endo and Adeno Resources repository.
"""

import re
import requests
import urllib.parse
from urllib.parse import urlparse
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import sys

def extract_links_from_markdown(file_path):
    """Extract all URLs from markdown file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find all URLs in markdown links and plain text
    url_pattern = r'https?://[^\s\)]+'
    urls = re.findall(url_pattern, content)
    
    # Clean up URLs (remove trailing punctuation and brackets)
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation that might be part of the text, not the URL
        url = url.rstrip('.,;:!?')
        url = url.rstrip(')')
        url = url.rstrip(']')
        cleaned_urls.append(url)
    
    return list(set(cleaned_urls))  # Remove duplicates

def check_link(url, timeout=10):
    """Check if a link is accessible."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, timeout=timeout, headers=headers, allow_redirects=True)
        
        # Consider 2xx and 3xx status codes as successful
        if 200 <= response.status_code < 400:
            return url, True, response.status_code, None
        else:
            return url, False, response.status_code, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        return url, False, None, "Timeout"
    except requests.exceptions.ConnectionError:
        return url, False, None, "Connection Error"
    except requests.exceptions.TooManyRedirects:
        return url, False, None, "Too Many Redirects"
    except requests.exceptions.RequestException as e:
        return url, False, None, str(e)
    except Exception as e:
        return url, False, None, f"Unexpected error: {str(e)}"

def main():
    print("🔍 Checking links in Awesome Endo and Adeno Resources...")
    print("=" * 60)
    
    # Extract links from README.md
    links = extract_links_from_markdown('README.md')
    
    print(f"Found {len(links)} unique links to check")
    print()
    
    broken_links = []
    working_links = []
    
    # Check links with threading for better performance
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_link, url): url for url in links}
        
        for future in as_completed(future_to_url):
            url, is_working, status_code, error = future.result()
            
            if is_working:
                working_links.append((url, status_code))
                print(f"✅ {url} (Status: {status_code})")
            else:
                broken_links.append((url, error))
                print(f"❌ {url} - {error}")
            
            # Small delay to be respectful to servers
            time.sleep(0.1)
    
    print()
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    print(f"Total links checked: {len(links)}")
    print(f"Working links: {len(working_links)}")
    print(f"Broken links: {len(broken_links)}")
    
    if broken_links:
        print()
        print("🚨 BROKEN LINKS FOUND:")
        print("-" * 40)
        for url, error in broken_links:
            print(f"• {url}")
            print(f"  Error: {error}")
            print()
    else:
        print()
        print("🎉 All links are working!")
    
    return len(broken_links)

if __name__ == "__main__":
    try:
        broken_count = main()
        sys.exit(broken_count)
    except KeyboardInterrupt:
        print("\n\n⚠️  Link checking interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1) 