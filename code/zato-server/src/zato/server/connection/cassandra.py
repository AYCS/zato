# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import getLogger

# Cassandra
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import ConstantReconnectionPolicy
from cassandra.query import dict_factory

# Zato
from zato.server.connection import BaseConnPoolStore, BasePoolAPI

# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################

msg_to_stdlib = {
    'tls_ca_certs': 'ca_certs',
    'tls_client_cert': 'certfile',
    'tls_client_priv_key': 'keyfile',
    }

# ################################################################################################################################

class CassandraAPI(BasePoolAPI):
    """ API through which connections to Cassandra can be obtained.
    """

# ################################################################################################################################

class CassandraConnStore(BaseConnPoolStore):
    """ Stores connections to Cassandra.
    """
    conn_name = 'Cassandra'

# ################################################################################################################################

    def create_session(self, name, config, config_no_sensitive):
        auth_provider = PlainTextAuthProvider(config.username, config.password) if config.username else None

        tls_options = {}
        for msg_name, stdlib_name in msg_to_stdlib.items():
            if config.get(msg_name):
                tls_options[stdlib_name] = config[msg_name]

        cluster = Cluster(
            config.contact_points.splitlines(), int(config.port), cql_version=config.cql_version,
            protocol_version=int(config.proto_version), executor_threads=int(config.exec_size),
            auth_provider=auth_provider, ssl_options=tls_options)

        session = cluster.connect()
        session.row_factory = dict_factory
        session.set_keyspace(config.default_keyspace)

        return session

# ################################################################################################################################

    def delete_session(self, name):
        """ Deletes a connection session. Must be called with self.lock held.
        """
        self.sessions[name].conn.shutdown()

# ################################################################################################################################