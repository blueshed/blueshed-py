'''
This is used by Audit to keep track of versions.
Perhaps version_base is better?

Created on Nov 28, 2012

@author: peterb
'''
import datetime
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer, DateTime
from blueshed.model_helpers.base import Base


class Versioned(object):
    
    _version_ = Column(Integer, default=0)
    _version_by_ = Column(Integer)
    _version_on_ = Column(DateTime, default=datetime.datetime.now)

    
    def _to_pairs(self, ignore=None, for_update=True):
        result = Base._to_pairs(self, ignore)
        if for_update is True:
            result['_version'] = self._version_
            result['_version_by'] = self._version_by_
            result['_version_on'] = self._version_on_
        return result
    
    def _from_pairs(self, pairs):
        if self._version_ != 0 and pairs.get('_version') != self._version_:
            raise Exception('Version mismatch')
        Base._from_pairs(self, pairs)
    
