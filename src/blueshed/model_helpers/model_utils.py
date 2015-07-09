'''
Connect, create_all, drop_all and date overlaps - all useful
and used in every system

Created on 3 Mar 2015

@author: peterb
'''
from sqlalchemy.engine import reflection, create_engine
from sqlalchemy.sql.schema import MetaData, ForeignKeyConstraint, Table
from sqlalchemy.sql.ddl import DropConstraint, DropTable
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.sql.expression import and_, or_
from blueshed.model_helpers.sqla_views import DropView


_SESSION_EXTENSIONS_ = []
_SESSION_KWARGS_ = {"autoflush":False}
_pool_recycle_ = 3600


def overlaps(cls, from_date, to_date):
    return or_(and_(cls.from_date <= to_date, #starts
                    cls.from_date >= from_date),
               and_(cls.to_date <= to_date, #ends
                    cls.to_date >= from_date),
               and_(cls.from_date <= from_date, #spans
                    cls.to_date >= to_date))
    

def connect(db_url,echo=False, pool_recycle=None):
    
    params = dict(echo=echo)
    if 'mysql' in db_url:
        params['encoding']='utf-8'
        params['pool_recycle']= pool_recycle if pool_recycle else _pool_recycle_
        params['isolation_level']='READ COMMITTED'
        
    engine = create_engine(db_url, **params)
    Session = sessionmaker(bind=engine, 
                           extension=_SESSION_EXTENSIONS_, 
                           **_SESSION_KWARGS_)

    return engine,Session
    
    
def create_all(Base, engine):
    Base.metadata.create_all(engine)
    

def drop_all(session):

    inspector = reflection.Inspector.from_engine(session.bind)
    
    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in 
    # a transaction.
    
    metadata = MetaData()
    
    tbs = []
    all_fks = []
    
    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((),(),name=fk['name'])
                )
        t = Table(table_name,metadata,*fks)
        tbs.append(t)
        all_fks.extend(fks)
    
    for fkc in all_fks:
        session.execute(DropConstraint(fkc))
        
    for view_name in inspector.get_view_names():
        session.execute(DropView(view_name))
    
    for table in tbs:
        session.execute(DropTable(table))
    
    session.commit()
