#!/usr/bin/env python3
"""
Script to filter broken links, excluding bot-blocking sites.
"""

def filter_broken_links():
    """Filter out bot-blocking sites and focus on genuinely broken links."""
    
    # All broken links from the previous scan
    all_broken_links = [
        ("https://www.fertstert.org/article/S0015-0282(25", "HTTP 403", "truncated URL"),
        ("https://www.perplexity.ai/", "HTTP 403", "bot blocking"),
        ("https://awesome.re\">", "Connection Error", "malformed with trailing quote"),
        ("https://www.reddit.com/r/adenomyosis/", "HTTP 403", "Reddit bot blocking"),
        ("https://www.endometriosis.org.hk/", "Connection Error", "site down"),
        ("https://www.endogenomics.com/endo-genomics-a-new-era-of-endometriosis-research", "HTTP 404", "page not found"),
        ("https://www.noendo.fr/#/", "HTTP 500", "server error"),
        ("https://www.reddit.com/r/Endometriosis/", "HTTP 403", "Reddit bot blocking"),
        ("https://www.sciencedirect.com/science/article/pii/S0301211521001234", "HTTP 400", "bad request"),
        ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7891234/", "HTTP 405", "method not allowed"),
        ("https://qvin.com/", "HTTP 403", "bot blocking"),
        ("https://www.frontiersin.org/articles/10.3389/fendo.2021.789456/full", "HTTP 404", "page not found"),
        ("https://endometriosisaustralia.org/", "Connection Error", "site down"),
        ("https://awesome.re/badge.svg\"", "HTTP 404", "trailing quote typo"),
        ("https://bii.dk/bio-studio-projects/cure-me/", "HTTP 404", "page not found"),
        ("https://www.science.org/doi/10.1126/scitranslmed.adk8230", "HTTP 403", "bot blocking"),
        ("https://www.tandfonline.com/doi/full/10.1080/13625187.2021.1901234", "HTTP 403", "bot blocking"),
        ("https://www.reddit.com/r/Endo/comments/1jc2yxl/endo_study_that_compensates_100", "HTTP 403", "Reddit bot blocking"),
        ("https://pmc.ncbi.nlm.nih.gov/articles/PMC8348135/", "HTTP 405", "method not allowed"),
        ("https://journals.biologists.com/dmm/article/17/10/dmm050566/362466/RNA-sequencing-reveals-molecular-mechanisms-of", "HTTP 403", "bot blocking"),
        ("https://endofibroid.com.sg/", "HTTP 520", "server error"),
        ("https://www.speakendo.com/", "HTTP 404", "page not found"),
        ("https://www.mdpi.com/2227-9059/12/4/888", "HTTP 403", "bot blocking"),
        ("https://endomarch.org/", "Connection Error", "site down"),
        ("https://www.jultrasoundmed.org/content/40/3/567", "Connection Error", "site down"),
        ("https://www.endometriosisph.org/", "Connection Error", "site down"),
        ("https://jamanetwork.com/journals/jama/article-abstract/2821194", "HTTP 403", "bot blocking"),
        ("https://www.endometriosisindia.com/", "Connection Error", "site down"),
        ("https://www.reddit.com/r/Endo/", "HTTP 403", "Reddit bot blocking"),
    ]
    
    # Sites that are known to block bots (HTTP 403)
    bot_blocking_sites = [
        "reddit.com",
        "perplexity.ai", 
        "qvin.com",
        "science.org",
        "tandfonline.com",
        "journals.biologists.com",
        "mdpi.com",
        "jamanetwork.com"
    ]
    
    # Filter out bot-blocking sites
    genuinely_broken_links = []
    bot_blocked_links = []
    
    for url, error, description in all_broken_links:
        is_bot_blocked = any(site in url for site in bot_blocking_sites)
        
        if is_bot_blocked:
            bot_blocked_links.append((url, error, description))
        else:
            genuinely_broken_links.append((url, error, description))
    
    return genuinely_broken_links, bot_blocked_links

def main():
    print("🔍 Filtering Broken Links (Excluding Bot-Blocking Sites)")
    print("=" * 70)
    
    genuinely_broken, bot_blocked = filter_broken_links()
    
    print(f"\n📊 SUMMARY")
    print(f"Total broken links: {len(genuinely_broken) + len(bot_blocked)}")
    print(f"Genuinely broken links: {len(genuinely_broken)}")
    print(f"Bot-blocked links: {len(bot_blocked)}")
    
    print(f"\n🚨 GENUINELY BROKEN LINKS ({len(genuinely_broken)}):")
    print("-" * 50)
    
    for i, (url, error, description) in enumerate(genuinely_broken, 1):
        print(f"{i:2d}. {url}")
        print(f"    Error: {error}")
        print(f"    Issue: {description}")
        print()
    
    print(f"\n🤖 BOT-BLOCKED LINKS ({len(bot_blocked)}) - Excluded from broken count:")
    print("-" * 50)
    
    for i, (url, error, description) in enumerate(bot_blocked, 1):
        print(f"{i:2d}. {url}")
        print(f"    Error: {error}")
        print(f"    Note: {description}")
        print()
    
    print(f"\n💡 RECOMMENDATIONS:")
    print("-" * 30)
    print("• Bot-blocked sites may work in a browser")
    print("• Focus on fixing genuinely broken links first")
    print("• Check truncated URLs and malformed links")
    print("• Verify sites that are completely down")

if __name__ == "__main__":
    main() 