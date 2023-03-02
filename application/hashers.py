
import hashlib
from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare

from django.utils.translation import ugettext_noop as _


class PlainTextPassword(BasePasswordHasher):
    """
    Plain Text 

    """
    # Only "unsalted_md5" can be used as Plain Text algo
    algorithm = "unsalted_md5" 
  
    def encode(self, password):
        return password
    
    def encode(self, password, salt):
        assert password is not None
        hash = password
        return '%s' % (hash)
    
    def verify(self, password, encoded):
        return password == encoded
    def safe_summary(self, encoded):
         return {
            _('algorithm'): "PlainText",
        }