#!/usr/bin/env python3
"""Guard the four What We Do cards against accidental image regressions."""
from pathlib import Path
from html.parser import HTMLParser

HTML = Path(__file__).resolve().parents[1].joinpath("index.html").read_text()
expected = [
  {
    "title": "Custom Kitchen Cabinetry",
    "url": "https://images.unsplash.com/photo-1600489000022-c2086d79f9d4?auto=format&fit=crop&w=900&q=80"
  },
  {
    "title": "Cabinet Door Replacements",
    "url": "https://images.unsplash.com/photo-1777027518628-e39374100fd4?auto=format&fit=crop&w=900&q=80"
  },
  {
    "title": "Laundry Cabinetry",
    "url": "https://images.unsplash.com/photo-1790926156246-67ec96893a21?auto=format&fit=crop&w=900&q=80"
  },
  {
    "title": "Built-in Wardrobes",
    "url": "https://images.unsplash.com/photo-1778731660303-1fa5ede75477?auto=format&fit=crop&w=900&q=80"
  }
]
class CardParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_cards=False
        self.depth=0
        self.cards=[]
        self.current=None
        self.in_h3=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=="div" and a.get("class")=="cards":
            self.in_cards=True
            self.depth=1
            return
        if self.in_cards:
            if tag=="div":self.depth+=1
            if tag=="article" and a.get("class")=="card":
                self.current={"title":"","url":""}
            if self.current is not None and tag=="img":
                self.current["url"]=a.get("src","")
            if self.current is not None and tag=="h3":self.in_h3=True
    def handle_data(self,data):
        if self.in_h3 and self.current is not None:self.current["title"]+=data
    def handle_endtag(self,tag):
        if self.in_h3 and tag=="h3":self.in_h3=False
        if self.in_cards:
            if tag=="article" and self.current is not None:
                self.cards.append(self.current)
                self.current=None
            if tag=="div":
                self.depth-=1
                if self.depth==0:self.in_cards=False

p=CardParser();p.feed(HTML)
assert p.cards==expected, f"Image mapping changed, review required: {p.cards}"
assert len(set(x["url"] for x in p.cards))==4, "Duplicate images found"
assert "formsubmit.co/vinkitchencab@gmail.com" in HTML
print("PASS: 4 exact service-specific photos, no duplicates; form destination present")
