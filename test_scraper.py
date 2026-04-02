from app.engine.scraper_manager import ScraperManager

manager = ScraperManager()
print("Keywords:", manager.keywords)
print("Scrapers loaded:", [s.source for s in manager.scrapers])

gigs = manager.run(progress_callback=print)
print(f"\nTotal gigs: {len(gigs)}")
if gigs:
    print("\nFirst gig:")
    for k, v in gigs[0].items():
        print(f"  {k}: {v}")
