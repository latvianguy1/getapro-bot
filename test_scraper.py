"""
Test script to verify the scraper works without sending notifications
"""

from scraper import GetaProScraper
import json


def main():
    print("=" * 60)
    print("🔍 GetaPro Scraper Test")
    print("=" * 60)
    
    scraper = GetaProScraper()
    
    # Test scraping all jobs (no filter)
    print("\n📋 Testing: Scraping ALL jobs (first page)...")
    jobs = scraper.scrape_jobs()
    
    if jobs:
        print(f"\n✅ Found {len(jobs)} jobs!\n")
        print("-" * 60)
        
        for i, job in enumerate(jobs[:5], 1):  # Show first 5
            print(f"\n📌 Job #{i}:")
            print(f"   Title: {job['title']}")
            print(f"   Category: {job['category']}")
            print(f"   Subcategory: {job.get('subcategory', 'N/A')}")
            print(f"   Price: {job.get('price', 'N/A')}")
            print(f"   Location: {job.get('location', 'N/A')}")
            print(f"   Time: {job.get('time_posted', 'N/A')}")
            print(f"   Description: {job['description'][:100]}...")
        
        if len(jobs) > 5:
            print(f"\n... and {len(jobs) - 5} more jobs")
    else:
        print("\n⚠️ No jobs found. The HTML structure might have changed.")
        print("Let's try a different parsing approach...")
    
    # Test specific category
    print("\n" + "=" * 60)
    print("📋 Testing: IT pakalpojumi category...")
    
    it_jobs = scraper.scrape_jobs("it-pakalpojumi")
    
    if it_jobs:
        print(f"✅ Found {len(it_jobs)} IT jobs!")
        for job in it_jobs[:3]:
            print(f"   - {job['title']} ({job.get('location', 'N/A')})")
    else:
        print("⚠️ No IT jobs found")
    
    # Show available categories
    print("\n" + "=" * 60)
    print("📁 Available categories:")
    print("-" * 60)
    
    for slug, info in scraper.CATEGORIES.items():
        print(f"  • {slug}: {info['name']}")


if __name__ == "__main__":
    main()

