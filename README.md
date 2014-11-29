weibosdk
========

Weibo client SDK for sina weibo API v2, powered by requests.

https://github.com/ghostrong/weibosdk

Rely on requests
----------------

[requests](http://docs.python-requests.org/en/latest/)

```
$ pip install requests
```
or
```
$ easy_install requests
```

Quickly Start
-------------

```
$ git clone https://github.com/ghostrong/weibosdk
```

edit config.py
```
APP_KEY = 'your app_key'
APP_SECRET = 'your app_secret'
REDIRECT_URL = 'redirect_url same as the url you commit to weibo.com'
TOKEN_FILE = 'filename where you want to save your token in'
ACCESS_TOKEN = 'your access_token'  # if not set, apiclient.APIClient.request_token is called.
```

get weibo user's profile:
```
>>> from apiclient import APIClient
>>> api = APIClient()
>>> api.config_from_object()
Request new token...
Open the following url to any brower:

https://api.weibo.com/oauth2/authorize?action=submit&response_type=code&redirect_uri=...

Input the code:
xxxxxxxxxxxxx

>>> user = api.call('users/show', uid=1990786715)
>>> if user: print user['screen_name']
XXX
```

Tips
----

Request new token will take some manual work:

  Open the url in any browser, after your authorization, you will see the redirect url like this:

    http://somedomain/?code=xxxxxx

  Copy the code "xxxxxx" and input it.

  It's done! and new token will be save in TOKEN_FILE that you edited in config.py.

  You don't need to do this work every. In fact, you'll never do this unless your last token is expired.

  More details, see [examply.py](https://github.com/ghostrong/weibosdk/blob/master/example.py)

  Sina weibo api docs: http://open.weibo.com/wiki/API%E6%96%87%E6%A1%A3_V2

  I will commit the multi-thread version in gevent soon.
