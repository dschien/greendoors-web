from provider.oauth2.models import AccessToken

__author__ = 'schien'


class OAuthTestCaseMixin(object):

    def setCredentialsForAnyUser(self):
        c = self.client
        accesstoken = AccessToken.objects.all()[0]
        token = accesstoken.token
        user = accesstoken.user
        self.assertTrue(len(user.favourites.all()) == 0)
        c.credentials(HTTP_AUTHORIZATION=('Bearer %s' % token))
        return user