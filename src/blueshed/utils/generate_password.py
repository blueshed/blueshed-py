'''
Password generation of four commonly used words from a word list
seperated by hyphens.

Created on Apr 7, 2013

@author: peterb
'''
from pkg_resources import resource_filename  # @UnresolvedImport
import itertools
import random
from blueshed.utils.email_password import EmailPassword


class GeneratePasswordMixin(object):
    
    def __init__(self):
        self._wordlist_ = None
        
        
    @property
    def wordlist(self):
        if self._wordlist_ is None:
            nbits = 11
            filename = resource_filename("blueshed.utils","wordlist.txt")
            self._wordlist_ = [line.split()[1] for line in itertools.islice(open(filename), 2**nbits)]
        return self._wordlist_
    
    
    def generate_password(self, nwords=4):
        choice = random.SystemRandom().choice
        return '-'.join(choice(self.wordlist) for i in range(nwords))
    
        
    def _email_password_(self, tmpl_path, email, password, **kwargs):
        email = EmailPassword(tmpl_path, email, password=password, **kwargs)
        email.send()