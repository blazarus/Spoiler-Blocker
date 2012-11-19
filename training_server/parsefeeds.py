import feedparser
import pdb

url = "http://sports.yahoo.com/nba/rss.xml"

feed = feedparser.parse(url)
pdb.set_trace()
print feed