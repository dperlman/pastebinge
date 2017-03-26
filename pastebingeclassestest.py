#! /usr/bin/env python
## bitdrip tests


from __future__ import print_function
#import httplib2
#from httplib2 import Http
#from urllib import urlencode
#from urllib.parse import urlencode
import requests
import io
import re
import sys
import codecs
#from collections import OrderedDict
import time


#from lxml import html
# or maybe try https://github.com/shazow/urllib3 seems to have more support
# and https://github.com/kennethreitz/requests


paste_expire_date = ['N', '10M', '1H', '1D', '1M']
paste_private = ['public', 'unlisted', 'private']
paste_format = []

# httplib2:
# request(self, uri, method="GET", body=None, headers=None, redirections=DEFAULT_MAX_REDIRECTS, connection_type=None)

# the token is found like this for pastebin:
# <input type="hidden" name="csrf_token_post" value="MTQ5MDExODI5MjZuWE9kdUp0eGRUdUV3MmFxOVNsQUFMVWRQMUdlWGpF">




# def pretty_print_POST(req):
#   """
#   At this point it is completely built and ready
#   to be fired; it is "prepared".
# 
#   However pay attention at the formatting used in 
#   this function because it is programmed to be pretty 
#   printed and may differ from the actual request.
#   """
#   print('{}\n{}\n{}\n\n{}'.format(
#     '-----------START-----------',
#     req.method + ' ' + req.url,
#     '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
#     req.body,
#   ))


# def grep1(fileobj, regex):
#   r = re.compile(regex)
#   for line in fileobj:
#     result = r.search(line)
#     if result:
#       return result
# 
# def grep1str(string, regex):
#   r = re.compile(regex)
#   for line in string.splitlines():
#     print('Line!')
#     result = r.search(line)
#     if result:
#       return line
#   
# def get_value(string):
#   r = re.compile(r'value="(.*)"')
#   result = r.search(string)
#   if result:
#     return result.groups()[0]

starturl="http://pastebin.com"
posturl="http://pastebin.com/post.php"
tokentext="csrf_token_post"
pastebin_token_re = r'name="csrf_token_post"\s*value="(.*)"[\s>]'



class PastebinPost(object):
  
  def __init__(self, starturl=None, posturl=None, tokenre=None, paste_format='1', paste_expire_date='1H', paste_private='0', paste_name='', paste_code='', submit_hidden='submit_hidden', csrf_token_post=None, delay=2):
    if starturl:
      self.starturl = starturl
    else:
      self.starturl = "http://pastebin.com"
    if posturl:
      self.posturl = posturl
    else:
      self.posturl = "http://pastebin.com/post.php"
    if tokenre:
      self.tokenre = tokenre
    else:
      self.tokenre = r'name="csrf_token_post"\s*value="(.*)"[\s>]'
    self.csrf_token_post = csrf_token_post
    self.delay = delay
    
    
    # For testing:
    if paste_code=='':
      paste_code = "This is some paste text\nthis is another line of paste text\n" 
    if paste_name == '':
      paste_name = "This is the title for the paste"
      
    
    self._files = {
      "csrf_token_post": (None,csrf_token_post),
      "submit_hidden": (None,submit_hidden),
      "paste_code": (None,paste_code),
      "paste_format": (None,paste_format),
      "paste_expire_date": (None,paste_expire_date),
      "paste_private": (None,paste_private),
      "paste_name": (None,paste_name)
    }
    self.newpasteurl = None

    
  @property
  def files(self):
    self._files["csrf_token_post"] = (None, self.csrf_token_post)
    # then maybe also substitute the text and title
    return self._files
  
  def _get_token(self, text):
    """use the tokenre to get the token out of the text
    tokenre should be a regular expression string with one groups
    that finds the token value that you want.
    """
    tre = re.compile(self.tokenre)
    r = tre.search(text)
    if r:
      self.csrf_token_post = r.groups()[0]
      return self.csrf_token_post
    
    
  def _connect(self, theurl, headers=None):
    """open a connection session"""
    self.session = requests.Session()
    srstart = self.session.get(theurl, headers=headers)
    return srstart

  def connect(self):
    """open the connection to the post url and get the token
    """
    sr = self._connect(self.starturl)
    csrf_token_post = self._get_token(sr.text)
    self.csrf_token_post = csrf_token_post
    return csrf_token_post
    # wow, so far that works
    
  def _post(self, theurl, files, headers=None):
    """post request
    """
    pr = self.session.post(theurl, files=files, headers=headers)
    return pr 
    
  def post(self):
    self.postresponse = self._post(self.posturl, self.files)
    self.newpasteurl = self.postresponse.url
    return self.newpasteurl
    
  @classmethod
  def newpaste(cls, paste_name='', paste_code='', paste_expire_date='1H'):
    """simple classmethod interface
    """
    p=cls(paste_name=paste_name, paste_code=paste_code, paste_expire_date=paste_expire_date)
    p.connect()
    time.sleep(p.delay)
    pasteurl = p.post()
    return pasteurl
  
    



# HTTP POST to http://dpaste.com/api/v2/
# Fields: content, syntax, title, poster, expiry_days
# Required field: content
# Syntax choices: Full list in JSON form
# Response contents
# 
# Response code on success will be HTTP 201 Created
# Location header will be the created item's URL
# Response body will also be the item's URL
# Expires header will be the item's expiry date

# curl -s -F "expiry_days=1" -F "content=blahblahblahblah" --trace-ascii /dev/stdout http://dpaste.com/api/v2/

class DpastePost(object):
  
  def __init__(self, starturl=None, posturl=None, expiry_days='1', paste_name='', paste_code='', delay=2):
    if starturl:
      self.starturl = starturl
    else:
      self.starturl = "http://dpaste.com"
    if posturl:
      self.posturl = posturl
    else:
      self.posturl = "http://dpaste.com/api/v2/"
    self.expiry_days = expiry_days
    self.delay = delay
    
    
    # For testing:
    if paste_code=='':
      paste_code = "This is some paste text\nthis is another line of paste text\n" 
    if paste_name == '':
      paste_name = "This is the title for the paste"
      
    
    self._files = {
      "paste_code": (None,paste_code),
      "expiry_days": (None,expiry_days),
      "paste_name": (None,paste_name)
    }
    self._data = {
      "content": paste_code,
      "syntax": None,
      "title": paste_name,
      "poster": None,
      "expiry_days": self.expiry_days
    }
    
    self.newpasteurl = None
    self.session = None

  @property
  def files(self):
    # then maybe also substitute the text and title
    return self._files
  
  @property
  def data(self):
    # do whatever
    return self._data

  def _connect(self, theurl, headers=None):
    """open a connection session"""
    self.session = requests.Session()
    srstart = self.session.get(theurl, headers=headers)
    return srstart

  def connect(self):
    """open the connection to the post url and get the token
    """
    sr = self._connect(self.starturl)
    # wow, so far that works
    
  def _post(self, theurl, data, headers=None):
    """post request
    """
    pr = self.session.post(theurl, data=data, headers=headers)
    return pr 
    
  def post(self):
    self.postresponse = self._post(self.posturl, self.data)
    #print(self.postresponse.text)
    self.newpasteurl = self.postresponse.text.strip()
    return self.newpasteurl
    
  @classmethod
  def newpaste(cls, paste_name='', paste_code='', expiry_days='1'):
    """simple classmethod interface
    """
    p=cls(paste_name=paste_name, paste_code=paste_code, expiry_days=expiry_days)
    p.connect()
    time.sleep(p.delay)
    pasteurl = p.post()
    return pasteurl
  
    







# testurl = 'http://httpbin.org/post'
# # Note that the python requests module is weird and to post a multipart form that isn't
# # file upload you have to use this None tuple trick.
# files = {
#   "csrf_token_post": (None,"MTQ5MDA1OTY4N3pFMWNoQlJSd2FSblUxRzdUM1VWRTlLbFpMOGw1OU9P"),
#   "submit_hidden": (None,"submit_hidden"),
#   "paste_code": (None,"This is some paste text\nthis is another line of paste text\n"),
#   "paste_format": (None,"1"),
#   "paste_expire_date": (None,"1H"),
#   "paste_private": (None,"0"),
#   "paste_name": (None,"This is some sort of title")
# }
# 
# r = requests.Request('POST', testurl, files=files)
# r=r.prepare()
# print(dir(r))
# print(pretty_print_POST(r))
# 
# r = requests.post(testurl, files=files)
# t=r.text
# td = codecs.escape_decode(bytes(t, "utf-8"))[0].decode("utf-8")
# print(td)
# 
# print(dir(r.request))
# print(r.request.url)
# print(r.request.prepare_method)
# r.request.prepare()
# print(dir(r.request))
# 
# print(r.request.headers)
# print(r.request.method)
# print(r.request.path_url)
# sys.exit()
  
  

#pasteurl = PastebinPost.newpaste(paste_name='This is a title for a paste', paste_code='This is line one\nThis is line two\nThis is line 3\n', paste_expire_date='1H')
pasteurl = DpastePost.newpaste(paste_name='This is a title for a paste', paste_code='This is line one\nThis is line two\nThis is line 3\n')
print(pasteurl)
sys.exit()

p = PastebinPost()
csrf_token_post = p.connect()
print('csrf_token_post')
print(csrf_token_post)
pasteurl = p.post()
print(pasteurl)
sys.exit()



#posttexttemplate


# h = httplib2.Http(".cache")
# (resp_headers, content) = h.request(starturl, "GET")
# 
# #print(content)
# found = grep1str(content.decode(), tokentext)
# print(found)
# print(get_value(found))
# 
# sys.exit()
# 
# headers={
#   'Pragma':'no-cache', 
#   'Origin': 'http://pastebin.com', 
#   'Accept-Encoding': 'gzip, deflate', 
#   'Accept-Language': 'en-US,en;q=0.8', 
#   'Upgrade-Insecure-Requests': '1', 
#   'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36', 
#   'Content-Type': 'multipart/form-data; boundary=----WebKitFormBoundaryAIIWFMbaG1lrsHlz',
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8', 
#   'Cache-Control': 'no-cache',
#   'Referer': 'http://pastebin.com/',
#   'Cookie': '__cfduid=dc522e5a344d5023d7ba3234e150867f71490059207; PHPSESSID=82c6aq94jvgoo09hnk7g167mh2; __qca=P0-1469735327-1490059208269; views=5; _ga=GA1.2.1311632957.1490059208; _gat=1; __gads=ID=feee8ae249172f1b:T=1490059690:S=ALNI_Ma_q45W2HclfwsWIltuCUZRFZZK0g', 
#   'Connection': 'keep-alive' 
# }
# 
# 
# testdata1="""------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="csrf_token_post"
# 
# MTQ5MDA1OTY4N3pFMWNoQlJSd2FSblUxRzdUM1VWRTlLbFpMOGw1OU9P
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="submit_hidden"
# 
# submit_hidden
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="paste_code"
# 
# #! another new test file
# test
# 
# test
#  te
# sttest
# t
# st
# 
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="paste_format"
# 
# 1
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="paste_expire_date"
# 
# N
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="paste_private"
# 
# 0
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz
# Content-Disposition: form-data; name="paste_name"
# 
# A title goes here
# ------WebKitFormBoundaryAIIWFMbaG1lrsHlz--
# """