"""
Facebook user authentication middleware django module.

@author: Roy McElmurry (roy.miv@gmail.com)
"""

import json
import urllib
import urllib2
import logging
from django import http
from projectnomnom import settings, models

class FacebookMiddleware(object):
    """
    Ensures that the user is logged in with Facebook on every page request. If the user is not
    logged in it will perform the OAuth procedure with FaceBook and redirect the user to the
    original page when finished.
    """
    def fb_api_call(self, path, domain=u'graph', params=None, access_token=None):
        """
        Make a FaceBook API call
        
        Params:
            path: The path of the remote api call.
            domain: The domain for the api call.
            params: Query string arguments to provide with the api call.
            access_token: The FaceBook access_token associated with the user's session.
        Return: Whatever data the api call returns as a string. 
        """
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
        """
        Directs the client to the FaceBook authorization page where the client authorizes this app
        for data access.
        
        Params:
            return_url: The URL that FaceBook should redirect the client to upon authorization
                completion.
        """
        fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                        "?client_id=%s&redirect_uri=%s" %
                        (settings.FACEBOOK['APP_ID'],  return_url))
    
        if len(settings.FACEBOOK['PERMISSIONS']):
            fb_login_uri += "&scope=%s" % ",".join(settings.FACEBOOK['PERMISSIONS'])

        return http.HttpResponseRedirect(fb_login_uri)

    def get_fb_access_token(self, code, return_url):
        """
        Acquires the FaceBook api access token using the authorization code for this app.
        
        Params:
            code: The FaceBook app authorization code for this user.
            return_url: The URL that FaceBook should redirect the client to with the api access
                token.
        Return: The api access token and its expire time.
        """
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
        """
        Processes the webserver request and verifies that the FaceBook authorization code is present
        among the request arguments. If it is then we retrieve the api access token and proceed to
        the originally requested URL. If the authorization code is not present or has expired we
        will first redirect the user to the FaceBook app authorization page.
        
        Params:
            request: The web request object to be processed.
        """
        if request.REQUEST.get('code', None):
            try:
                token, expiration = self.get_fb_access_token(request.REQUEST.get('code'),
                                                             request.build_absolute_uri(request.path))
                data = json.loads(self.fb_api_call('me', access_token=token))
                request.user = models.FacebookUser(name=data['first_name']+data['last_name'],
                                                   uid=data['id'], token=token, expiration=expiration)
            except:
                return self.get_fb_code(request.build_absolute_uri(request.path))
        else:
            return self.get_fb_code(request.build_absolute_uri(request.path))

        