'''
Audit Listener works with audit to provide a log of
crud activity in the db

Created on May 15, 2012

@author: peterb
'''
import datetime
from sqlalchemy import event
from blueshed.model_helpers.audit import Audit
from blueshed.model_helpers.versioned import Versioned
from blueshed.utils import utils

"""Used with PyDispatch as signal to broadcast changes to model object"""
AUDIT_EVENT = "AUDIT_EVENT"


class AuditListener(object):
        
    def __init__(self, control):
        self.control = control
        self._audit_broadcast_ = []
        self.accl_key = None
        
        event.listen(self.control._Session, "before_flush", self._before_flush)
        event.listen(self.control._Session, "after_flush", self._after_flush)
        event.listen(self.control._Session, "after_rollback", self._after_rollback)
        event.listen(self.control._Session, "after_commit", self._after_commit)
                    
            
    def _before_flush(self, session, context, instances):
        for item in session.dirty:
            Audit.create_version(item, session, 'updated', self.accl_key)
            if isinstance(item, Versioned):
                item._version_ = (item._version_ or 0) + 1
                item._version_by_ = self.accl_key
                item._version_on_ = datetime.datetime.now()
        for item in session.new:
            if isinstance(item, Versioned):
                item._version_by_ = self.accl_key            
        for item in session.deleted:
            Audit.create_version(item, session, 'deleted', self.accl_key)

        
    def _after_flush(self, session, context):
        for item in session.new:
            if not isinstance(item, Audit):
                Audit.create_version(item, session, 'created', self.accl_key)
            else:
                self._audit_broadcast_.append(utils.dumps(item._serialize))

            
    def _after_rollback(self, session):
        self._audit_broadcast_ = []
        self._ticker_changes = []
        self._page_changes = []
        self._price_filter_change = False


    def _after_commit(self, session):
#         for message in self._audit_broadcast_:
#             self.control._broadcast(signal=AUDIT_EVENT,message=message)
        self._audit_broadcast_ = []
        
