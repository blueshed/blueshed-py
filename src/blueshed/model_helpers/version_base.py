'''
Created on 19 Feb 2015

@author: peterb
'''
from sqlalchemy.types import Integer, DateTime
from sqlalchemy.schema import Column
import datetime
from blueshed.model_helpers.base import _Base_, Base
        


_Base_.version_id = Column(Integer, nullable=False)
_Base_.last_updated = Column(DateTime, 
                        default=datetime.datetime.now,
                        onupdate=datetime.datetime.now)

_Base_.__mapper_args__ = {
    "version_id_col": _Base_.version_id  # @UndefinedVariable
}
