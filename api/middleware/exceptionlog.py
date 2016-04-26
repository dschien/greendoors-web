'''
Created on Jan 2, 2013

@author: schien
'''
class ExceptionLoggingMiddleware(object):
    def process_exception(self, request, exception):
        import traceback
        print traceback.format_exc()