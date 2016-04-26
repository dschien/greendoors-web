import logging
from rest_framework import exceptions

from greendoors import settings


__author__ = 'schien'

logger = logging.getLogger(__name__)


class LoggingMixin(object):
    """
    Provides full logging of requests and responses
    """

    def finalize_response(self, request, response, *args, **kwargs):
        # do the logging
        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            logger.debug("[{0}] Response data: {1}".format(self.__class__.__name__, self.cap(str(response.data), 300)))
        return super(LoggingMixin, self).finalize_response(request, response, *args, **kwargs)

    def cap(self, s, l):
        return s if len(s) <= l else s[0:l - 3] + '...'

    def initial(self, request, *args, **kwargs):

        # do the logging

        if hasattr(settings, 'DEBUG') and settings.DEBUG:
            try:
                data = request.DATA
                logger.debug("[{0}] Request data: {1}".format(self.__class__.__name__, data))
            except exceptions.ParseError:
                data = '[Invalid data in request]'
                logger.debug("[{0}] {1}".format(self.__class__.__name__, data))
        try:
            super(LoggingMixin, self).initial(request, *args, **kwargs)
        except Exception as er:
            logger.debug("[{0}] Error during request processing: {1}".format(self.__class__.__name__, er))
            raise


class RequestLoggingMixin(LoggingMixin):
    """
    Only logs the request but not the response.
    """

    def initial(self, request, *args, **kwargs):
        super(LoggingMixin, self).initial(request, *args, **kwargs)