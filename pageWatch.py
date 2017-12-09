import os
import time
import urllib2
import shutil
import signal
import sys
from bs4 import BeautifulSoup
from bs4.element import Comment

def exitGracefully(signal, frame):
		print('Program exited.')
		sys.exit(0)

def checkIfUpdated(url="http://example.com/", secondsInterval=5, filePrefix="example", compareText=False):

	hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
	   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
	   'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
	   'Accept-Encoding': 'none',
	   'Accept-Language': 'en-US,en;q=0.8',
	   'Connection': 'keep-alive'}
	req = urllib2.Request(url, headers=hdr)

	# file cleanup
	if (os.path.isfile(filePrefix + "_old.html")): 
		os.remove(filePrefix + "_old.html")
	if (os.path.isfile(filePrefix + "_new.html")): 
		os.remove(filePrefix + "_new.html")
	if (not os.path.isfile(filePrefix + "_saved.html")): # check if webpage has been scraped before
		saved_webpage = open(filePrefix + "_saved.html", "w+")
		saved_webpage.write(urllib2.urlopen(req).read())
		saved_webpage.close()

	while True:
		signal.signal(signal.SIGINT, exitGracefully)

		webpage = urllib2.urlopen(req)
		webpage_html = webpage.read();

		if (webpage.getcode() == 200):
			saved_webpage = open(filePrefix + "_saved.html", "r+")

			if (compareText): # compare the visible text of the pages
				webpageChanged = (text_from_html(saved_webpage.read()).encode('utf-8') != text_from_html(webpage_html).encode('utf-8'))
			else: # compare the raw html of the pages
				webpageChanged = (saved_webpage.read() != webpage_html)

			if (webpageChanged):
				print("Changes detected at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "!")
				print("Compare " + filePrefix + "_old.html and " + filePrefix + "_new.html to see differences.")
	
				shutil.copyfile(filePrefix + "_saved.html", filePrefix + "_old.html")
				new_webpage = open(filePrefix + "_new.html", "w")
				new_webpage.write(webpage_html)
				new_webpage.close()

				saved_webpage.seek(0)
				saved_webpage.write(webpage_html)
				saved_webpage.close()

				break
			else:
				print("No changes detected at " + time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + ".")

				saved_webpage.seek(0)
				saved_webpage.write(webpage_html)
				saved_webpage.close()
		else:
			print("Error, could not fetch webpage. Status code: " + str(webpage.getcode()) + ".")

		time.sleep(secondsInterval)

def tag_visible(element):
	if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
		return False
	if isinstance(element, Comment):
		return False
	return True

def text_from_html(body):
	soup = BeautifulSoup(body, 'html.parser')
	texts = soup.findAll(text=True)
	visible_texts = filter(tag_visible, texts)
	return u" ".join(t.strip() for t in visible_texts)

urlInput = str(raw_input("Url of webpage: "))
updateInput = int(raw_input("Wait time (seconds) between checks: "))
filePrefixInput = str(raw_input("File prefix (html files will be saved under prefix_saved.html): "))
compareTextString = str(raw_input("Compare raw html (y/n)? "))

if (compareTextString.lower() == "yes" or compareTextString.lower() == "y"):
	compareTextBoolean = True
else:
	print("Visible text will be parsed and compared instead.")
	compareTextBoolean = False

print("")

checkIfUpdated(urlInput, updateInput, filePrefixInput, compareTextBoolean)