
class CheckHeaders(object):

	def __init__(self, cache, results, log):
		self.cache = cache
		self.results = results
		self.log = log
		self.headers = set()
		self.category = "Server Info"

	def split_server_line(self, line):
		if "(" in line:
			os = line[line.find('(')+1:line.find(')')]
			sh = line[:line.find('(')-1] + line[line.find(')')+1: ]
			return os, sh
		else:
			return False, line

	def add_header(self, response):
		for header in response.headers:

			# extract the headers and values. 
			headers = [(hdr, value) for hdr, value, url in self.headers]

			# if the header and value is not in the header set, add them along with the url.
			# only the first header,value,url set should be added. 
			if not (header, response.headers[header]) in headers:
				self.headers.add( (header, response.headers[header], response.url))

	def run(self):
		# get all the headers seen during the scan
		for response in self.cache.get_responses():
			self.add_header(response)

		# examine all the headers found
		for hdr,val,url in self.headers:
			
			# "server" can be used to identify the web server and operating system 
			if hdr == 'Server':

				# extract the OS if present: (Apache/2.2 (Ubuntu) PHP/5.3.1 )
				# os = Ubuntu
				# line = Apache/2.2 PHP/5.3.1
				os, line = self.split_server_line(val)
				
				out = []
				for part in line.split(" "):
					try:
						pkg,version = part.split('/')
						
						# add the results to the log and the results
						self.log.add( {url: {pkg: [version]} } )
						self.results.add(self.category, pkg, {'version': version, 'count':1}, False)
					except Exception as e:
						continue

			# "X-Powered-By" can be used to identify the PHP version (and potentially the OS)
			elif hdr == 'X-Powered-By':
				# 2014-07-27: the length of val.split('/') is not always 2 (e.g.: X-Powered-By: ASP.NET)
				vals = val.split('/')
				if len(vals) == 2:
					pkg,version = val.split('/')
					count = 1
				else:
					pkg,version,count = val,'',0.1

				self.log.add( {url: {pkg: [version]} } )
				self.results.add(self.category, pkg, {'version': version, 'count':count}, False)

			elif hdr == 'X-AspNet-Version':
				pkg = "ASP.NET"
				version = val

				self.log.add( {url: {pkg: [version]} } )
				self.results.add(self.category, pkg, {'version': version, 'count':1}, False)				

			elif hdr == 'Set-Cookie':
				if 'ASP.NET_SessionId' in val:
					pkg = "ASP.NET"
					version = ''
					
					self.log.add( {url: {pkg: [version]} } )
					self.results.add(self.category, pkg, {'version': version, 'count':0.1}, False)	




