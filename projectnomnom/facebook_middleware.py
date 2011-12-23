import json
import urllib
import urllib2
import logging
from django import http
from projectnomnom import settings, models

class FacebookMiddleware(object):
    def fb_api_call(self, path, domain=u'graph', params=None, access_token=None):
        """Make an API call"""
        if not params:
            params = {}
        params[u'method'] = u'GET'
        if access_token:
            params[u'access_token'] = access_token
    
        for k, v in params.iteritems():
            if hasattr(v, 'encode'):
                params[k] = v.encode('utf-8')
    
        url = u'https://' + domain + u'.facebook.com/' + path
        params_encoded = urllib.urlencode(params)
        if len(params_encoded):
            url += '?' + params_encoded
        logging.info('FB API call: %s' % url)
        return urllib2.urlopen(url).read()

    def get_fb_code(self, return_url):
        fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                        "?client_id=%s&redirect_uri=%s" %
                        (settings.FACEBOOK['APP_ID'],  return_url))
    
        if len(settings.FACEBOOK['PERMISSIONS']):
            fb_login_uri += "&scope=%s" % ",".join(settings.FACEBOOK['PERMISSIONS'])

        return http.HttpResponseRedirect(fb_login_uri)

    def get_fb_access_token(self, code, return_url):
        params = {'client_id': settings.FACEBOOK['APP_ID'],
                  'redirect_uri': return_url,
                  'client_secret': settings.FACEBOOK['APP_SECRET'],
                  'code': code}
    
        result = self.fb_api_call(path=u"/oauth/access_token", params=params)
        print result
        pairs = result.split("&", 1)
        result_dict = {}
        for pair in pairs:
            (key, value) = pair.split("=")
            result_dict[key] = value
        return (result_dict["access_token"], result_dict["expires"])

    def process_request(self, request):
        if not request.REQUEST.get('code', None):
            return self.get_fb_code(request.build_absolute_uri())
        else:
            token, expiration = self.get_fb_access_token(request.REQUEST.get('code'),
                                                         request.build_absolute_uri(request.path))
            data = json.loads(self.fb_api_call('me', access_token=token))
            request.user = models.FacebookUser(name=data['first_name']+data['last_name'],
                                               uid=data['id'], token=token, expiration=expiration)

        