import requests
from bs4 import BeautifulSoup
import urllib3
import re
import json
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

username=""
password=""
followable = set()
offset=25
sess=None



def login():
	req = requests.session()
	res = req.get("https://bugcrowd.com/user/sign_in")
	csrf = 	BeautifulSoup(res.text,'html.parser').find_all('meta')[4]['content']
	data = {"utf8":"%E2%9C%93","authenticity_token":csrf,"user[redirect_to]":"","user[email]":username,"user[password]":password,"commit":"Log+in"}
	req.post('https://bugcrowd.com/user/sign_in',data=data, verify=False,allow_redirects=True)
	return req

def pending(op=None):
	###if no argument pathed pending() will return true if thair is a new pending program
    ###if called with pending("list") will list pending program urls 
    ###if called with pending("accept") will join all pending program
	res = sess.get('https://bugcrowd.com/programs.json',verify=False)
	json = res.json()
	length = int(json['meta']['quickFilterCounts']['pending-invite'])
	pending = (length/offset)
	for i in range(pending + 1):
		pendingJson = sess.get('https://bugcrowd.com/programs.json?hidden[]=false&pending_invite[]=true&sort[]=invited-desc&sort[]=promoted-desc&offset[]={}'.format(i*25)).json()
		for i in range(len(pendingJson['programs'])):
			if pendingJson['programs'][i]['invited_status'] == 'invited' and not pendingJson['programs'][i]['can_submit_report?']:
				if op == "accept":
					path = pendingJson['programs'][i]['summary_path']
					token = pendingJson['programs'][i]['accept_invitation_path']
					res = sess.get("https://bugcrowd.com{}".format(path))
					csrf = BeautifulSoup(res.text,'html.parser').find_all('meta')[5]['content']
					res = sess.post("https://bugcrowd.com{}".format(token),data={"authenticity_token":csrf,"commit":"Accept+Invite","utf8":"%E2%9C%93"},verify=False)
					if res.status_code == 200:
						print("New Pending Invite Accepted")				
				if op == "list":
					print("Program Url: https://bugcrowd.com{}".format(pendingJson['programs'][i]['summary_path']))
				if op == None:
					if length > 0:
						return True
					else:
						return False

def joinable(op=None):
    ###if no argument pathed joinable() will return true if thair joinable program
    ###if called with joinable("list") will list joinable program urls 
    ###if called with joinable("accept") will join all joinable program

    count=0
    res = sess.get('https://bugcrowd.com/programs.json')
    json = res.json()
    length= int(json['meta']['quickFilterCounts']['joinable'])
    joinable = (length/offset)
    for i in range(joinable + 1):
            joinableJson = sess.get('https://bugcrowd.com/programs.json?joinable[]=true&hidden[]=false&sort[]=invited-desc&sort[]=promoted-desc&offset[]={}'.format(i*25),verify=False).json()
            for i in range(len(joinableJson['programs'])):
                requirements = joinableJson['programs'][i].get('outstanding_requirements_count',0)
                isjoinable = joinableJson['programs'][i].get('badge_type',False)
                if isjoinable and requirements == 0:
                    count +=1
                    if op == "accept":
                        path = joinableJson['programs'][i]['program_url']
                        token = joinableJson['programs'][i]['code']
                        res = sess.get("https://bugcrowd.com{}".format(path))
                        csrf = BeautifulSoup(res.text,'html.parser').find_all('meta')[5]['content']
                     	res = sess.post("https://bugcrowd.com/programs/{}/program_applications".format(token),data={"authenticity_token":csrf,"_method":"post"},verify=False)
                    	if res.status_code == 200:
                    		print("New Joinable Program Joined")
                    if op == "list":
                    	print("Program Url: https://bugcrowd.com{}".format(joinableJson['programs'][i]['program_url']))
                    if op == None:
	                	if count > 0:
	                		return True
	                	else:
	                		return False


def getallprograms(op):
	###Return set() of all paid programs and log all followable programa to followable set() 
	programs=set()
	count=0
	res = sess.get('https://bugcrowd.com/programs.json',verify=False)
	json = res.json()
	if op == "p": ##paid accepted invites only
		url = "https://bugcrowd.com/programs.json?accepted_invite[]=true&hidden[]=false&sort[]=invited-desc&sort[]=promoted-desc&points_only[]=false&offset[]={}"
		length = int(json['meta']['quickFilterCounts']['accepted-invite'])
	if op == "a": ##all paid programs
		url = "https://bugcrowd.com/programs.json?points_only[]=false&hidden[]=false&sort[]=invited-desc&sort[]=promoted-desc&offset[]={}"
		length = int(json['meta']['quickFilterCounts']['reward'])
	allprograms = (length/offset)
	for i in range(allprograms + 1):
		alljson = sess.get(url.format(i*25),verify=False).json()
		for i in range(len(alljson['programs'])):
			try:
				if not "teasers" in alljson['programs'][i]['program_url']:
					programs.add(alljson['programs'][i]['program_url'].replace('/',''))
					#if alljson['programs'][i]['following?'] == False:
					#	followable.add(alljson['programs'][i]['program_url'].replace('/',''))
			except:
				pass
	return programs



def getscope(program_url):
	###get all passed program scopes
	print("Scope for {}".format(program_url))
	url = re.compile('((http|https)\:\/\/)?[a-zA-Z0-9*\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*')
	result = set()
	res = sess.get("https://bugcrowd.com/{}".format(program_url))
	try :
		data = BeautifulSoup(res.text,'html.parser').find('div',{"data-react-class":"ResearcherTargetGroups"})['data-react-props']
		josndata = json.loads(data)
		for i in range(len(josndata['groups'][0]['targets'])):
			result.add(josndata['groups'][0]['targets'][i]['name'])
		f = open("./result/{}.txt".format(program_url),"a")
		for i in result:
			if url.match(i):
				i = i.replace("/*","")
				f.write(i.encode('utf8')+"\n")
		f.close()
		print("Saved to ./result/{}.txt".format(program_url,program_url)) 
	except:
		pass
#def follow(program_url):
#	response = sess.post('https://bugcrowd.com/{}/program_subscribers.json'.format(program_url),data={'utf8': '\u2713'},proxies={"https":"127.0.0.1:8080"},verify=False)

#def main():
#	global sess
#	sess = login()
#	if pending():
#		pending(True)
#	if joinable():
#		joinable(True)
#	programs = getallprograms()
#	for i in followable:
#		follow(i)
#	for p in programs:
#		getscopee(p)
#main()
sess = login()
programs = getallprograms("p")
for name in programs:
	getscope(name)
