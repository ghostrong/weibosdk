#coding=utf8


from apiclient import APIClient


class WeiboExp(APIClient):

    def __init__(self):
        super(WeiboExp, self).__init__()

    def get_user_by_id(self, uid):
        r = self.call('users/show', uid=uid)
        return r

    def get_user_by_name(self, name):
        r = self.call('users/show', screen_name=name)
        return r

    def update_status(self, status):
        # status is unicode
        r = self.post('statuses/update', status=status)
        return r

    def update_status_with_pic(self, status, path):
        # status is unicode
        pic = open(path, 'rb')
        r = self.upload('statuses/upload', status=status, pic=pic)
        return r

    def test_proxy(self, name):
        # proxies = {'https':'http://user:password@host:port'}
        from config import proxies
        r = self.call_with_proxy('users/show', proxies, screen_name=name)
        print r['screen_name']


if __name__ == '__main__':
    api = WeiboExp()
    api.set_access_token('xxxx')
    import time
    r = api.get_user_by_id(1990786715)
    # r = api.update_status( u'测试我的post ----- %s' % time.ctime() )
    # r = api.update_status_with_pic(u'皮卡丘-pikaqiu -- %s'.encode('utf8') % time.ctime(), 't.jpg')
    print r
