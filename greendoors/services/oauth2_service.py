import ConfigParser
import json
import logging
import os
import urllib
from greendoors import settings

__author__ = 'schien'

GOOGLE_ACCOUNTS_BASE_URL = 'https://accounts.google.com'

logger = logging.getLogger(__name__)


class OAuthService(object):
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read(os.path.join(settings.PROJECT_ROOT, 'mailconf'))
        self.email = self.config.get('GMAIL', 'username')
        self.refresh_token = self.config.get('GMAIL', 'refresh_token')
        self.client_id = self.config.get('GMAIL', 'client_id')
        self.client_secret = self.config.get('GMAIL', 'client_secret')


    def AccountsUrl(self, command):
        """Generates the Google Accounts URL.

        Args:
          command: The command to execute.

        Returns:
          A URL for the given command.
        """
        return '%s/%s' % (GOOGLE_ACCOUNTS_BASE_URL, command)

    def refresh_oauth_token(self):
        logger.info('refreshing oauth token')

        params = {}
        params['client_id'] = self.client_id
        params['client_secret'] = self.client_secret
        params['refresh_token'] = self.refresh_token
        params['grant_type'] = 'refresh_token'
        request_url = self.AccountsUrl('o/oauth2/token')

        response = urllib.urlopen(request_url, urllib.urlencode(params)).read()
        obj = json.loads(response)
        if 'access_token' in obj:
            logger.info('Got new token, expires in {0}'.format(obj['expires_in']))
            return obj['access_token']
        logger.error('Could not get new access token. Response: {0}'.format(response))
        raise Exception('Could not get new access token. Response: {0}'.format(response))

    def get_access_token_expiry(self, access_token):
        host = 'https://www.googleapis.com/'
        path = 'oauth2/v1/tokeninfo'
        params = {}
        params['access_token'] = access_token
        response = urllib.urlopen(host + path, urllib.urlencode(params)).read()

        return json.loads(response)['expires_in']

    def get_access_token(self):
        # todo check if expired
        return self.refresh_oauth_token()


