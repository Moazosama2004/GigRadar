from app.engine.match_engine import MatchEngine

engine = MatchEngine()

print(f"Profile skills: {engine.skills[:5]}")
print(f"Profile title:  {engine.title}")
print()

results = engine.score_all(progress_callback=print)

print(f"\nTop 5 matched gigs:")
for gig in results[:5]:
    print(f"  [{gig['match_score']:>3}/100] {gig['title'][:60]}")
    print(f"         {gig['source']} | {gig['budget']} | {gig['posted_at']}")
    print(f"         {gig['url']}")
    print()
