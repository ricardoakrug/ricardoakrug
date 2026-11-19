"""Write the latest posts from the English blog feed into README.md.

The script replaces the text between the BLOG-POSTS markers.
It writes the file only when the list changes.
"""

import sys
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path

FEED_URL = "https://ricardokrug.com.br/en/feed.xml"
README = Path(__file__).resolve().parent.parent / "README.md"
START = "<!-- BLOG-POSTS:START -->"
END = "<!-- BLOG-POSTS:END -->"
MAX_POSTS = 5


def fetch_posts():
    request = urllib.request.Request(FEED_URL, headers={"User-Agent": "profile-readme-updater"})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    posts = []
    for item in root.iter("item"):
        title = item.findtext("title", "").strip()
        link = item.findtext("link", "").strip()
        date = parsedate_to_datetime(item.findtext("pubDate"))
        posts.append((date, title, link))
    posts.sort(reverse=True)
    return posts[:MAX_POSTS]


def render(posts):
    lines = [f"- [{title}]({link}) · {date:%b %-d, %Y}" for date, title, link in posts]
    return "\n".join(lines)


def main():
    posts = fetch_posts()
    if not posts:
        # Stop with an error when the feed is empty. Do not delete the current list.
        sys.exit("The feed has no posts.")
    text = README.read_text()
    head, rest = text.split(START, 1)
    _, tail = rest.split(END, 1)
    new_text = f"{head}{START}\n{render(posts)}\n{END}{tail}"
    if new_text != text:
        README.write_text(new_text)
        print("README.md updated.")
    else:
        print("No change.")


if __name__ == "__main__":
    main()
