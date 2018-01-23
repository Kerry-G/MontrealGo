'''
montrealReddit is a package for Montreal Bot
'''
import praw
import re
import random
from config import reddit
montreal = reddit.subreddit('montreal')

def isURL(s):
	return not ('.com' in s or '.jpg' in s or '.net' in s or '.ca' in s or '.org' in s or '.io' in s or '.it' in s)

def isImage(s):
	return '.jpg' in s

def getData(flair, time='day',image=False):
	data = []
	data_listing = montreal.top(time)

	for report in data_listing:
		if report.link_flair_text != flair or isURL(report.url):
			continue
		if image and not isImage(report.url) :
			continue
		data_dict = dict()
		data_dict['url'] = report.url
		data_dict['author'] = report.author
		data_dict['title'] = report.title
		data.append(data_dict)

	return data

def getImage():
	x = getData(flair="Pictures", time="month", image=True)
	return x[random.randrange(0,len(x),1)]

def getNews():
	x = getData(flair="News", time="month")
	return x[random.randrange(0,len(x),1)]

def getHistorical():
	x = getData(flair="Historical", time="week")
	return x[random.randrange(0,len(x),1)]
	


