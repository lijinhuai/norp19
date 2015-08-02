 # -*- coding: UTF-8 -*- 
import sys    
import requests
from bs4 import BeautifulSoup
import re
import time
import sqlite3
import smtplib  
from email.mime.text import MIMEText
from download import startDown

headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
           'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
           'Host':'www.91porn.com'}

def log(info):
	t=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	line = t+" | "+info+"\n"
	open("log.txt","a").write(line)	
	

def getUrl(entryUrl):
	videoUrl=[]
	try:
		headers = {'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.130 Safari/537.36',
           'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
           'Host':'www.91porn.com'}
		r = requests.get(entryUrl,headers=headers)
		soup = BeautifulSoup(r.text)
		for item in soup.find_all("a"):
			temp = item.get("href")
			if "viewkey" in temp:
				videoUrl.append(temp) 
				#print temp

		return list(set(videoUrl))
	except:
		log("something wrong with the entryUrl, check the network")
		return


def getDownloadUrl(videoUrl):
	#check if has downloaded	
	m = re.search("viewkey=(\S*)&page",videoUrl)
	if m:
		viewkey = m.group(1)
	else:
		return

	viewkeyList = getViewkeyFromDb()
	if viewkey in viewkeyList:
		print "found this"
		return
	#get the video info	
	videoInfo = {"viewkey":viewkey,"title":"", "Runtime":"" ,"Views":"","Comments":"","Favorites":"","Point":"",
	"Added":"","From":"","Description":"","DownUrl":""}	

	r = requests.get(videoUrl,headers=headers)
	soup = BeautifulSoup(r.text)
	try:
		video_id_url = soup.find(id='91').get("src")
	except:
		log("Can't find share url (network, wathchLimit, netchange)")
		return
	#print video_id_url
	m = re.search("video_id=(\S*)&",video_id_url)
	if m:
		#print m.group(1)
		video_id = m.group(1)
	else:
		return
	#open(video_id+".html","w").write(r.content)
	requestAPI = "http://91.bestchic.com/getfile_jw.php?VID="
	r = requests.get(requestAPI+video_id,headers={'Host':'91.bestchic.com'})
	downUrl = r.text.split("&")[0].split("=")[1]
	#print "url is :" + downUrl
	videoInfo["DownUrl"] = downUrl
	
	#===================
	#collect detail here
	try:
		title = soup.find(id="viewvideo-title").string.strip()
		#print "titile is:"+title
		videoInfo["title"] = title
	except:
		pass
	
	try:
		for item in soup.find(attrs={"class":"boxPart"}).find_all("span"):
			key = item.string.strip(":").strip()
			value = item.next_sibling.strip()
			if key == "时长":
				videoInfo["Runtime"] = value
			if key == "查看":
				videoInfo["Views"] = value
			if key == "留言":
				videoInfo["Comments"] = value
			if key == "收藏":
				videoInfo["Favorites"] = value
			if key == "积分":
				videoInfo["Point"] = value

	except:
		pass
	tempList = soup.find("div",attrs={"class":"startratebox2"}).findAllNext("span",attrs={"class":"info"})
	Added = tempList[1].findNext("span",attrs={"class":"title"}).string.strip()
	From = tempList[2].findNext("a").get("href")+"#"
	Description = soup.find("meta",{"name":"description"}).get("content")
	videoInfo["Added"] = Added
	videoInfo["From"] = From
	videoInfo["Description"] = Description
	print "==================================================================="
	return videoInfo


def saveToDb(videoInfo):
	conn = sqlite3.connect("91.db")
	cur = conn.cursor()
	stat = "insert into video values (?,?,?,?,?,?,?,?,?,?,?)"

	data = (videoInfo["viewkey"],videoInfo["title"],videoInfo["Runtime"],videoInfo["Views"],videoInfo["Comments"],
		videoInfo["Favorites"],videoInfo["Point"],videoInfo["Added"],videoInfo["From"],videoInfo["Description"],
		videoInfo["DownUrl"])
	cur.execute(stat,data)
	conn.commit()
	conn.close()


	

def getViewkeyFromDb():
	conn = sqlite3.connect("91.db")
	cur = conn.cursor()
	stat = "select viewkey from video"
	cur.execute(stat)
	data = cur.fetchall()
	conn.close()
	return [item[0] for item in data]




def getComments():
	pass

def saveVideoInfo():
	pass



def sendMail():
	mail_user = "903218171@qq.com"
	mail_pass = "mabin150750"
	sender = "903218171@qq.com"
	receivers = ["main@iie.ac.cn"] 
	message = "这事一封测试邮件,邮件服务器拒绝发送邮件，判断为发送垃圾邮件。建议您检查邮件内容，是否包含一些比较敏感的内容。 "
	try: 
		smtpObj = smtplib.SMTP_SSL("smtp.163.com",465) 
		smtpObj.set_debuglevel(1) 
		state = smtpObj.login(mail_user,mail_pass)  
		if state[0] == 235:
			smtpObj.sendmail(sender, receivers, message)  
			smtpObj.quit()  
			print "success"
		else:
			print "error" 
	except Exception, e:
		print str(e)
		return False



if __name__ == '__main__':
	reload(sys)  
	sys.setdefaultencoding('utf8')
	
	#entryUrl = "http://www.sina.com"
	entryUrl = "http://www.91porn.com/v.php?category=rf&viewtype=basic"
	

	while True:
		try:
			videoUrlList = getUrl(entryUrl)
			if videoUrlList:
				for video in videoUrlList:
					print "======" + video
					videoinfo = getDownloadUrl(video)
					if videoinfo:
						saveToDb(videoinfo)
						outputname = videoinfo["title"]+".mp4"
						url = videoinfo["DownUrl"]
						try:
							startDown( url, outputname, blocks=5) 
						except:
							log("download "+outputname+"error!")
							pass
					else:
						pass
		except:
			pass

		time.sleep(12*60*60)
	
 
			
	
	
	

		
