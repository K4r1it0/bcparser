import sys
from urllib.parse import urlparse
import dns.resolver as resolv
import needle

hosts=set()
def get_domain(sub):
    roottld = ""
    for tld in sub.split(".")[::-1]:
        roottld = "%s.%s" % (tld, roottld)        
        try:
        	return roottld[:-1], resolv.query(roottld)
        except:
        	pass
    return None, None

def get_hostname(url):
	if url.startswith("http"):
	    parsed_uri = urlparse(url)
	    return '{uri.netloc}'.format(uri=parsed_uri).split("/")[0]
	elif "*." in url:
		return url.replace("*.","").split("/")[0]
	else:
		return url.split("/")[0]
		


with open(sys.argv[1]) as file:
	urls = [line.split(" ")[0].strip() for line in file]
	for url in urls:
		host = get_hostname(url)
		if host:
		   hosts.add(host)


for i in needle.GroupWorkers(target=get_domain, arguments=[[host] for host in hosts], concurrent=50, kernel='threadpoolexecutor'):
	tld,dns=i._return
	if tld:
		print(tld)