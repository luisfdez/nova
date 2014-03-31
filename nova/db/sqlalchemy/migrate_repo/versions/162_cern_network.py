# This is a placeholder for Grizzly backports.
# Do not use this number for new Havana work.  New Havana work starts after
# all the placeholders.
#
# See https://blueprints.launchpad.net/nova/+spec/backportable-db-migrations
# http://lists.openstack.org/pipermail/openstack-dev/2013-March/006827.html



from sqlalchemy import Boolean, Column, DateTime, Integer
from sqlalchemy import MetaData, String, Table
from nova.openstack.common import log as logging

meta = MetaData()

cern_network = Table('cern_network', meta,
        Column('created_at', DateTime(timezone=False)),
        Column('updated_at', DateTime(timezone=False)),
        Column('deleted_at', DateTime(timezone=False)),
        Column('deleted', Boolean(create_constraint=True, name=None)),
        Column('id', Integer, primary_key=True),
        Column('netcluster', String(255)),
        Column('host', String(255)),
        )

# (fixed_ips)
column_mac = Column('mac',  String(255))
column_netcluster = Column('netcluster',  String(255))


def upgrade(migrate_engine):
    meta.bind = migrate_engine

    # create CERN tables
    for table in (cern_network, ):
        try:
            table.create()
        except Exception:
            pass

    # alter fixed_ips table
    table = Table('fixed_ips', meta, autoload=True)
    try:
        table.create_column(column_mac)
    except Exception:
        pass

    try:
        table.create_column(column_netcluster)
    except Exception:
        pass

def downgrade(migration_engine):
    pass

