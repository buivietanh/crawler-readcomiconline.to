# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options 
import time
import re
import pymysql
import os
import unicodedata
import json
import easygui
import paramiko
import sys



hostname = 'xxxxxxxxxxx'

portRoot = xxxx
userRoot = 'xxxx'
passRoot = 'xxxx'

portDB = xxxx
userDB = 'xxxx'
passDB = 'xxxx'
db = 'xxxx'



transport = paramiko.Transport((hostname, portRoot))

print ("Connecting...")
transport.connect(username = userRoot, password = passRoot)

sftp = paramiko.SFTPClient.from_transport(transport)
print ("Connected.")



connection = pymysql.connect(host= hostname,
							 port= portDB,
                             user= userDB,
                             password= passDB,                             
                             db= db,
                             autocommit=True)



cursor = connection.cursor()
cwd = os.getcwd()
flag = True

def slugify(s):
	s = s.lower()
	for c in [' ', '-', '.', '/']:
		s = s.replace(c, '_')
	s = re.sub('\W', '', s)
	s = s.replace('_', ' ')
	s = re.sub('\s+', ' ', s)
	s = s.strip()
	s = s.replace(' ', '-')
	return s

def getSeries( titles):
	sql = """SELECT * FROM series WHERE title = '%s' """ %(titles)
	#sql = """SELECT ValA FROM `%s` WHERE Val2 = '%s' AND Val3 = '%s'""" % (Val1, Val2, Val3)
	result_count = cursor.execute(sql)
	result = cursor.fetchall()
	result = list(result)
	return result

def getLastestChapter( sid):

	sql = """ SELECT chapters.title, chapters.seq FROM latest_chapters LEFT JOIN chapters ON latest_chapters.cid = chapters.id WHERE latest_chapters.sid = %d """ %(sid)
	result_count = cursor.execute(sql)
	result = cursor.fetchall()
	result = list(result)
	return result

def addSeries( title, slug, aliases, status, released, notes, genres, authors):
	sid = addDetailsSeries( title, slug, aliases, status, released, notes)
	addLatestIssue( sid)
	addGenresSeries( sid, genres)
	addAuthorsSeries( sid, authors)
	return sid

def addDetailsSeries( title, slug, aliases, status, released, notes):
	sql = """ INSERT INTO series (title, slug, aliases, status, released, notes, gtime) VALUES ('%s', '%s', '%s', '%s', %d, %r, NOW())""" %(title, slug, aliases, status, released, notes)
	cursor.execute(sql)
	sid = cursor.lastrowid
	return sid

def addGenresSeries( sid, genres):
 	for genre in genres:
 		sql = """ INSERT INTO series_genres (sid, genre) VALUES (%d, '%s') """ %(sid, genre)
 		cursor.execute(sql)

def addAuthorsSeries( sid, authors):
 	for author in authors:
 		sql = """ INSERT INTO series_authors (sid, author) VALUES (%d, '%s') """ %(sid, author)
 		cursor.execute(sql)

def addLatestIssue( sid):
	sql = """INSERT INTO latest_chapters (sid, cid) VALUES (%d, NULL)""" %(sid)
	cursor.execute(sql)

def incrementIssueCount( sid, count = 1):
	sql = """UPDATE series SET chapters = chapters + %d WHERE id = %d """ %(count, sid)
	cursor.execute(sql)

def updateLatestIssue( sid, cid):
	sql = """UPDATE latest_chapters SET cid = %d WHERE sid = %d """ %(cid, sid)
	cursor.execute(sql)

def addIssue( sid, title, seq, sticky, pages, listpage):
	cid = addIssueDetails( sid, title, seq, sticky, pages, listpage)
	updateLatestIssue( sid, cid)
	incrementIssueCount( sid)

def addIssueDetails( sid, title, seq, sticky, pages, listpage):
	sql = """INSERT INTO chapters (sid, title, seq, sticky, pages, listpage, gtime) VALUES (%d, '%s', %d, %d, %d, '%s', NOW())""" %(sid, title, seq, sticky, pages, listpage)
	cursor.execute(sql)
	cid = cursor.lastrowid
	return cid


def anoBrowser(url):
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = (
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
	)
	service_args = [
    # '--proxy=149.215.113.110:70',
    ]

	#driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
	#driver = webdriver.PhantomJS(service_args=['--load-images=no'])  #Dont load images
	chrome_options = Options()  
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--incognito")
	chrome_driver = cwd +"\\chromedriver.exe"
	driver = webdriver.Chrome(executable_path=chrome_driver,   chrome_options=chrome_options)

	driver.set_window_size(200,260)
	driver.get(url)

	time.sleep(15)
	#WebDriverWait(driver, 10).until(
	    #EC.presence_of_element_located((By.ID, "containerRoot"))
	#)
	return driver

def anoBrowserRe(url):
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap["phantomjs.page.settings.userAgent"] = (
		"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
	)

	service_args = [
    # '--proxy=149.215.113.110:70',
    # '--proxy-type=http',
    ]
    
	#driver = webdriver.PhantomJS(desired_capabilities=dcap, service_args=service_args)
	#driver = webdriver.PhantomJS(service_args=['--load-images=no'])  #Dont load images
	chrome_options = Options()  
	chrome_options.add_argument("--headless")
	chrome_options.add_argument("--incognito")
	chrome_driver = cwd +"\\chromedriver.exe"
	driver = webdriver.Chrome(executable_path=chrome_driver,   chrome_options=chrome_options)

	driver.set_window_size(100,100)
	driver.get(url)

	time.sleep(15)
	#WebDriverWait(driver, 10).until(
	    #EC.presence_of_element_located((By.ID, "containerRoot"))
	#)
	details = {}
	doc = driver.page_source
	details['driver'] = driver
	details['doc'] = doc

	return details


def getComics(url):
	driver = anoBrowser(url)
	listLink = []
	for a in driver.find_elements_by_xpath('//div//table[@class="listing"]//tbody//tr//td[1]//a'):
	    listLink.append(a.get_attribute('href'))
	driver.quit()
	return listLink

def getIssues(url):
	driverRe = anoBrowserRe(url)
	details = {}
	left,sep,right = driverRe['doc'].partition('lstImages.push("')	
	abc,xyz,asd = right.partition('var currImage = 0;')
	abc = abc.replace('lstImages.push("','')
	abc = abc.replace('\n        \n        ','')
	abc = abc.replace('s1600','s0')
	abc = abc.replace('");',',')
	abc = abc.split(',')
	driverRe['driver'].quit()
	details['issues'] = abc
	return details

def st(a):
	d = {}
	for k, v in a.items():
		key = int(k.split('=')[-1])
		d[key] = list((k, v))
	sorted_d = sorted(d.items()	)
	return sorted_d	

def Comics(link):
	driver 	= anoBrowser(link)
	driverRe 	= anoBrowserRe(link)
	
	title 	= re.findall(r'<a class="bigChar" .*>(.*?)</a>', driverRe['doc'])
	title[0]	= title[0].replace('&nbsp;', ' ').replace('\'', '').replace('\"', '').replace('’', '\'').replace('&amp;', '&')
	
	otherName 	= re.findall(r'<span class="info">Other name:</span>.*<a .*>(.*)</a>', driverRe['doc'])
	publisher	= re.findall(r'<span class="info">Publisher:</span>.*<a .*>(.*)</a>', driverRe['doc'])
	authors 	= re.findall(r'<span class="info">Writer:</span>.*<a .*>(.*)</a>', driverRe['doc'])
	genres 		= re.findall(r'<a href=".*" class="dotUnder" title=".">(.*)</a>', driverRe['doc'])
	released = re.findall(r'<span class="info">Publication date:</span>.*(\d{4}).*', driverRe['doc'])

	
	if otherName == []:
		aliases = title[0] + ' ' + released[0]
	else:
		aliases = otherName[0]
	slug = slugify(title[0])
	

	status 	= re.findall(r'<span class="info">Status:</span>(.*)', driverRe['doc'])
	status[0] = status[0].replace('&nbsp;','')
	if status[0] == 'Ongoing':
		status  = 'ONG'
	else:
		status = 'CMP'

	summary = re.findall(r'<p style="text-align: justify;">(.*?)</p>', driverRe['doc'])

	if len(summary) == 0:
		summary.append('Na')
	summary[0] 	= summary[0].replace('&nbsp;', ' ').replace('\'', '').replace('\"', '').replace('’', '\'')

	#genres = []
	if(publisher[0] == 'DC Comics') or (publisher[0] == 'Marvel'):
		genres.append(publisher[0])
	# for genre in driver.find_elements_by_xpath('//div[@class="barContent"]/div/p/a[@title="."]'):
	# 	print('genre: ', genre.text)
	# 	genres.append(genre.text)
	
	
	
	if len(summary) == 0 :
		summary = 'N/A'
	else:
		summary = summary[0]

	
	released[0] = int(released[0])
	title[0]	= title[0].replace('&nbsp;', ' ').replace('\'', '').replace('\"', '').replace('’', '\'').replace('&amp;', '&')
	titleSeries = title[0]
	
	#titleSeries = unicodedata.normalize('NFKD', titleSeries)
	summary = unicodedata.normalize('NFKD', summary)
	print(titleSeries)
	print(slug)
	print(aliases)
	print(released[0])
	print(status)
	print(genres)
	print(summary)
	print(authors)
	Series = getSeries(titleSeries)
	if len(Series) == 0:
		print('add new series')
		sid = addSeries( titleSeries, slug, aliases, status, released[0], summary, genres, authors)
		numberIssue = 0
		image 	= driver.find_element_by_xpath('//*[@id="rightside"]/div[1]/div[2]/div/img').get_attribute("src")

		#Save image to local
		saveImage = anoBrowser(image)
		saveImage.save_screenshot('./images/series/' + str(sid) + '.jpg')
		saveImage.quit()

		#Upload image from local to host via SFTP
		localpath = cwd + '/images/series/' + str(sid) + '.jpg'

		largefile = '/home/domain.com/public_html/images/series/large/' + str(sid) + '.jpg'
		smallfile = '/home/domain.com/public_html/images/series/small/' + str(sid) + '.jpg'
		
		sftp.put(localpath, largefile)
		sftp.put(localpath, smallfile)

		#Remove image from local
		os.remove(localpath)

	else:
		print('check numbers of issue')
		sid = Series[0][0]
		numberIssue = Series[0][8]
		print(numberIssue)
	lastestChapter = getLastestChapter( sid)
	print(lastestChapter[0])
	if lastestChapter[0][1] is None:
		seq = 0
	else:
		seq = int(lastestChapter[0][1])

	linkIssue = driver.find_elements_by_xpath('//div//table[@class="listing"]//tbody//tr//td//a')

	a = {}
	for b in linkIssue:
		url = b.get_attribute('href')
		titleIssue = b.get_attribute("innerHTML")
		if titleIssue.find("Issue #") == -1:
			titleIssue = titleIssue.replace('&nbsp;', ' ').replace('\'', '').replace('\"', '').replace('’', '\'').replace('&amp;', '&').replace(titleSeries + ' ', '').strip()
		else:
			titleIssue = titleIssue.replace('&nbsp;', ' ').replace('\'', '').replace('\"', '').replace('’', '\'').replace('&amp;', '&').replace(titleSeries + ' Issue #', '').strip()
		titleIssue = titleIssue.replace(' ', '_')
		a[url] = titleIssue
	c = st(a)
	i = 0	
	for issue in c:
		if i < numberIssue:
			i += 1
			continue
		else:
			url = issue[1][0]
			titleIssue = issue[1][1]
			print(titleIssue)
			print(url+'?&readType=1')
			issues = getIssues(url+'?&readType=1')
			print(issues['issues'])
			if len(issues['issues']) < 2:
				with open('issue.txt', 'w') as file:
					file.write(url)
				flag = False
				easygui.msgbox("Url has blocked! Please pass captcha to continue", title="Error!")
				break
				# sys.exit()
				# continue
			listpage = issues['issues']
			listpage = json.dumps(listpage)
			pages = len(issues['issues']) - 1
			sticky = 1
			seq = seq + 1
			addIssue( sid, titleIssue, seq, sticky, pages, listpage)
	driverRe['driver'].quit()
	driver.quit()

if __name__ == '__main__':
	try:
		with connection.cursor() as cursor:
			pageNumber = input('Please enter the page number: ')
			for i in range(int(pageNumber),0,-1):
				if flag == False:
					break
				else:
					url = 'https://readcomiconline.to/ComicList/LatestUpdate?page=%d'%(i)
					print(url)
					getComic = getComics(url)
					for link in getComic:
						try:
							if flag == False:
								break
							else:
								Comics(link)
							
						except Exception as e:
							print(e)
						else:
							continue
	finally:
		connection.close()
		sftp.close()
		transport.close()
		print ("Closed connection.")

