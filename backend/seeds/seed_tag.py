#!/usr/bin/env python3
"""
Seed script for tags.
Run once after migration: python scripts/seed_tags.py
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import SessionLocal
from app.models.tag import Tag

TAGS = [
    {
        "name": "Feel-Good Movie",
        "description": "Leaves you with a smile and a lighter mood."
    },
    {
        "name": "Heartwarming",
        "description": "Soft, kind, and emotionally comforting."
    },
    {
        "name": "Heartbreaking",
        "description": "Hits right in the feelings, possibly with tears."
    },
    {
        "name": "Hilarious",
        "description": "Actually made you laugh, not just smile politely."
    },
    {
        "name": "Terrifying",
        "description": "The kind of scary that stays with you after."
    },
    {
        "name": "Fun Jump Scares",
        "description": "Cheap maybe, but honestly pretty-scary fun."
    },
    {
        "name": "Meh",
        "description": "Not terrible, not great, just… pretty okay."
    },
    {
        "name": "All That for What?",
        "description": "Big setup, confusing payoff, questionable life choices."
    },
    {
        "name": "Epic",
        "description": "Big scale, big emotions, big “wow” moments."
    },
    {
        "name": "Cozy Watch",
        "description": "Feels like a blanket, snacks, and no stress."
    },
    {
        "name": "Unsettling",
        "description": "Something feels wrong, and that's the point."
    },
    {
        "name": "Bittersweet",
        "description": "Beautiful, but with a little emotional damage."
    },
    {
        "name": "Mind-Blowing",
        "description": "Twists, ideas, or visuals that broke your brain a bit."
    },
    {
        "name": "Hidden Gem",
        "description": "Better than expected and deserves more attention."
    },
    {
        "name": "Cult Classic",
        "description": "Weird, iconic, and loved by the right people."
    },
    {
        "name": "Must-See",
        "description": "Feels like everyone should watch it at least once."
    },
    {
        "name": "Nostalgia Hit",
        "description": "Brings back memories in the best possible way."
    },
    {
        "name": "Hasn't Aged Well",
        "description": "Some parts are harder to defend today."
    },
    {
        "name": "Rewatchable",
        "description": "Easy to come back to again and again."
    },
    {
        "name": "Masterpiece",
        "description": "Everything just works. No notes."
    },
    {
        "name": "I Can Die Now",
        "description": "So satisfying it feels like a life goal completed."
    },
    {
        "name": "Guilty Pleasure",
        "description": "You know it's flawed, but you love it anyway."
    },
    {
        "name": "So Stupid It's Good",
        "description": "Dumb in exactly the right way."
    },
    {
        "name": "Perfect for a Date",
        "description": "Good vibes, easy to share, not too risky."
    },
    {
        "name": "Crowd Pleaser",
        "description": "The kind of movie most people can enjoy."
    },
    {
        "name": "Family Friendly",
        "description": "Safe and enjoyable for a mixed-age audience."
    },
    {
        "name": "Conversation Starter",
        "description": "Makes you want to talk about it right after."
    },
    {
        "name": "Late-Night Watch",
        "description": "Hits better when the world is quiet."
    },
    {
        "name": "Underrated",
        "description": "Deserves way more love than it gets."
    },
    {
        "name": "Overrated",
        "description": "The hype may have done too much."
    },
    {
        "name": "Perfect Cast",
        "description": "Everyone feels exactly right in their role."
    },
    {
        "name": "Amazing Script",
        "description": "Great dialogue, clever structure, or strong writing."
    },
    {
        "name": "Visual Feast",
        "description": "So beautiful you could pause almost anywhere."
    },
    {
        "name": "Great Soundtrack",
        "description": "The music does a lot of heavy lifting."
    },
    {
        "name": "Comfort Movie",
        "description": "A personal safe place disguised as a film."
    },
    {
        "name": "Emotional Damage",
        "description": "You're fine. Totally fine. Definitely not crying."
    },
    {
        "name": "What Did I Just Watch?",
        "description": "Strange, confusing, but hard to forget."
    },
    {
        "name": "Slow Burn",
        "description": "Takes its time, but the payoff is worth it."
    },
    {
        "name": "Too Long",
        "description": "Good moments, but your bladder disagrees."
    },
    {
        "name": "Surprisingly Good",
        "description": "Expectations were low. The movie said “watch me.”"
    },
    {
        "name": "Pure Chaos",
        "description": "Messy, loud, wild, and somehow entertaining."
    },
    {
        "name": "Badass",
        "description": "Cool moments, cool characters, cool energy."
    },
    {
        "name": "Smart and Clever",
        "description": "Makes you feel like the writers were three steps ahead."
    },
    {
        "name": "Beautifully Weird",
        "description": "Odd, original, and proud of it."
    },
    {
        "name": "Instant Classic",
        "description": "Feels like it will still matter years from now."
    },
    {
        "name": "Not for Me",
        "description": "You get why it exists, but it didn't click."
    },
    {
        "name": "Great Villain",
        "description": "The antagonist steals the show."
    },
    {
        "name": "Strong Ending",
        "description": "The final moments really land."
    },
    {
        "name": "Weak Ending",
        "description": "Whatever the ride, the landing was rough."
    },
    {
        "name": "Vibe Over Plot",
        "description": "The story may be thin, but the mood is everything."
    }
        
]

def seed():
    db = SessionLocal()
    try:
        for tag_data in TAGS:
            if not db.query(Tag).filter_by(name=tag_data["name"]).first():
                db.add(Tag(**tag_data))
        db.commit()
        print(f"{len(TAGS)} tags seeded.")
    finally:
        db.close()

if __name__ == "__main__":
    seed()
