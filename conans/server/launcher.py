#!/usr/bin/python
import os
import sys

from conans import REVISIONS
from conans.paths import conan_expand_user
from conans.server import SERVER_CAPABILITIES
from conans.server.conf import get_server_store

from conans.server.crypto.jwt.jwt_credentials_manager import JWTCredentialsManager
from conans.server.migrate import migrate_and_get_server_config
from conans.server.plugin_loader import load_authentication_plugin, load_authorization_plugin
from conans.server.rest.server import ConanServer

from conans.server.service.authorize import BasicAuthorizer, BasicAuthenticator


class ServerLauncher(object):
    def __init__(self, force_migration=False, server_dir=None):
        if sys.version_info.major == 2:
            raise Exception("The conan_server needs Python>=3 for running")
        self.force_migration = force_migration
        if server_dir:
            user_folder = server_folder = server_dir
        else:
            user_folder = conan_expand_user("~")
            server_folder = os.path.join(user_folder, '.conan_server')

        server_config = migrate_and_get_server_config(
            user_folder, self.force_migration, server_dir is not None
        )
        if custom_authn := server_config.custom_authenticator:
            authenticator = load_authentication_plugin(server_folder, custom_authn)
        else:
            authenticator = BasicAuthenticator(dict(server_config.users))

        if custom_authz := server_config.custom_authorizer:
            authorizer = load_authorization_plugin(server_folder, custom_authz)
        else:
            authorizer = BasicAuthorizer(server_config.read_permissions,
                                         server_config.write_permissions)

        credentials_manager = JWTCredentialsManager(server_config.jwt_secret,
                                                    server_config.jwt_expire_time)

        server_store = get_server_store(server_config.disk_storage_path, server_config.public_url)

        server_capabilities = SERVER_CAPABILITIES
        server_capabilities.append(REVISIONS)

        self.server = ConanServer(server_config.port, credentials_manager,
                                  authorizer, authenticator, server_store,
                                  server_capabilities)
        if not self.force_migration:
            print("***********************")
            print(f"Using config: {server_config.config_filename}")
            print(f"Storage: {server_config.disk_storage_path}")
            print(f"Public URL: {server_config.public_url}")
            print(f"PORT: {server_config.port}")
            print("***********************")

    def launch(self):
        if not self.force_migration:
            self.server.run(host="0.0.0.0")
