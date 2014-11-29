# -*- coding:utf-8 -*-

''' Sina Weibo SDK powered by requests (http://docs.python-requests.org/en/latest/)
This is perfectly for weibo-application (not crawler).
If you are intereted in crawling weibo data, you may like this instead:
    https://github.com/ghostrong/weibo-crawler
Author: Xiaosong Rong
Email: rongxiaosong@gmail.com
'''

import sys
import json
import urllib
import urllib2
import time
from datetime import datetime, timedelta
import requests


class APIError(StandardError):
    ''' raise APIError if got failed message.
    '''
    def __init__(self, error_code, error, request):
        self.error_code = error_code
        self.error = error
        self.request = request
        StandardError.__init__(self, error)

    def __str__(self):
        return 'APIError: %s, %s, request: %s' % (self.error_code, self.error, self.request)


_HTTP_GET = 'GET'
_HTTP_POST = 'POST'
_HTTP_UPLOAD = 'UPLOAD'


def _http_call(url, method, access_token='', proxies=[], **kw):
    params = {}
    data = []
    files = []
    headers = {'Authorization': 'OAuth2 %s' % access_token}

    if method == _HTTP_GET:
        params = kw
    elif method == _HTTP_POST:
        data = kw
    elif method == _HTTP_UPLOAD: # **update a status with a picture
        files = {'pic': kw['pic']}
        kw.pop('pic', 0)
        data = kw
        method = _HTTP_POST # **UPLOAD is not a valid http method, so POST instead

    r = requests.request(method, url, headers=headers, params=params, data=kw,
                            files=files, proxies=proxies)
    try:
        data = r.json()
    except Exception, e:
        raise APIError(r.status_code, str(e), url)
    if isinstance(data,dict) and data.has_key('error_code'): # **api error
        raise APIError(data['error_code'], data.get('error', ''), data.get('request', ''))
    return data


def _encode_params(**kw):
    args = []
    for k, v in kw.iteritems():
        qv = v.encode('utf8') if isinstance(v,unicode) else str(v)
        #quote is essential here; when using requests it's not necessary
        args.append('%s=%s' % (k, urllib.quote(qv)))
    return '&'.join(args)

# only for GET method
# requests cannot support https proxy well, so this is written by urllib2
def _call_with_proxy(url, access_token, proxies, **kw):
    headers = {'Authorization': 'OAuth2 %s' % access_token}
    proxy_handler = urllib2.ProxyHandler(proxies)
    opener = urllib2.build_opener(
        urllib2.HTTPHandler(),
        urllib2.HTTPSHandler(),
        proxy_handler,
        )
    params = _encode_params(**kw)
    http_url = '%s?%s' % (url, params)
    req = urllib2.Request(http_url, headers=headers)
    r = opener.open(req)

    try:
        data = json.loads(r.read())
    except Exception, e:
        raise APIError(r.getcode(), str(e), url)
    if isinstance(data,dict) and data.has_key('error_code'): # **api error
        raise APIError(data['error_code'], data.get('error', ''), data.get('request', ''))
    return data


class APIClient(object):
    # **following params need to be set
    # **config.py is recommanded
    APP_KEY= ''
    APP_SECRET = ''
    REDIRECT_URL = ''

    def __init__(self, domain='api.weibo.com', version='2'):
        self.auth_url = 'https://%s/oauth2/' % domain
        self.api_url = 'https://%s/%s/' % (domain, version)
        self.TOKEN_FILE = ''
        self.access_token = ''
        # self.config_from_object()

    def config_from_object(self):
        import config
        self.APP_KEY = config.APP_KEY
        self.APP_SECRET = config.APP_SECRET
        self.REDIRECT_URL = config.REDIRECT_URL
        self.TOKEN_FILE = config.TOKEN_FILE
        self.access_token = config.ACCESS_TOKEN
        if not self.access_token:
            try:
                self.set_token_from_json()
                print 'Init: set token from %s' % self.TOKEN_FILE
            except Exception, e:
                print 'Request new token...'
                self.request_token()

    def set_access_token(self, access_token):
        self.access_token = access_token

    def set_token_from_json(self):
        fp = open(self.TOKEN_FILE)
        token = json.loads(fp.read())
        fp.close()
        self.set_access_token(token['access_token'])

    def request_token(self): # **need some manual work: acquire the code from redirect url
        para_tuple = ['action=submit',
            'response_type=code',
            'redirect_uri='+self.REDIRECT_URL,
            'client_id='+self.APP_KEY ,
            ]
        params = '&'.join(para_tuple)
        manual_url = self.auth_url + '%s?%s' % ('authorize',params)
        print u'Open the following url to any browser: \n'
        print manual_url
        # code, acquired from the redirect url
        code = raw_input('\nInput the code:  # copy and paste your code here\n')
        r = _http_call(self.auth_url+'access_token',
                _HTTP_POST,
                client_id=self.APP_KEY,
                client_secret=self.APP_SECRET,
                redirect_uri=self.REDIRECT_URL,
                code=code,
                grant_type='authorization_code',
                )

        #r = {'access_token':u'', 'expires_in':'int', 'remind_in':u'', 'uid':u''}
        request_date = datetime.now()
        deadline = request_date + timedelta( seconds=r.get('expires_in',0) )
        r['request_date'] = request_date.strftime("%Y-%m-%d %H:%M:%S")
        r['deadline'] = deadline.strftime("%Y-%m-%d %H:%M:%S")
        file = open(self.TOKEN_FILE,'w')
        file.write(json.dumps(r))
        file.close()
        print 'New access_token is in "%s"' % self.TOKEN_FILE
        self.set_access_token( r['access_token'] )
        return

    def call(self, api_method, **kw):
        return self.get(api_method, **kw)

    def get(self, api_method, **kw):
        url = '%s%s.json' % (self.api_url, api_method)
        return _http_call(url, _HTTP_GET, self.access_token, **kw)

    def post(self, api_method, **kw):
        url = '%s%s.json' % (self.api_url, api_method)
        return _http_call(url, _HTTP_POST, self.access_token, **kw)

    def upload(self, api_method, **kw): # **update a status with a picture
        url = '%s%s.json' % (self.api_url, api_method)
        return _http_call(url, _HTTP_UPLOAD, self.access_token, **kw)

    def call_with_proxy(self, api_method, proxies={}, **kw):  #only for http method "GET"
        url = '%s%s.json' % (self.api_url, api_method)
        return _call_with_proxy(url, self.access_token, proxies=proxies, **kw)


