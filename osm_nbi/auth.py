# -*- coding: utf-8 -*-

# Copyright 2018 Whitestack, LLC
# Copyright 2018 Telefonica S.A.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: esousa@whitestack.com or alfonso.tiernosepulveda@telefonica.com
##


"""
Authenticator is responsible for authenticating the users,
create the tokens unscoped and scoped, retrieve the role
list inside the projects that they are inserted
"""

__author__ = "Eduardo Sousa <esousa@whitestack.com>; Alfonso Tierno <alfonso.tiernosepulveda@telefonica.com>"
__date__ = "$27-jul-2018 23:59:59$"

import cherrypy
import logging
import yaml
from base64 import standard_b64decode
from copy import deepcopy
# from functools import reduce
from hashlib import sha256
from http import HTTPStatus
from random import choice as random_choice
from time import time
from os import path
from base_topic import BaseTopic    # To allow project names in project_id

from authconn import AuthException
from authconn_keystone import AuthconnKeystone
from osm_common import dbmongo
from osm_common import dbmemory
from osm_common.dbbase import DbException


class Authenticator:
    """
    This class should hold all the mechanisms for User Authentication and
    Authorization. Initially it should support Openstack Keystone as a
    backend through a plugin model where more backends can be added and a
    RBAC model to manage permissions on operations.
    This class must be threading safe
    """

    periodin_db_pruning = 60 * 30  # for the internal backend only. every 30 minutes expired tokens will be pruned

    def __init__(self):
        """
        Authenticator initializer. Setup the initial state of the object,
        while it waits for the config dictionary and database initialization.
        """
        self.backend = None
        self.config = None
        self.db = None
        self.tokens_cache = dict()
        self.next_db_prune_time = 0  # time when next cleaning of expired tokens must be done
        self.resources_to_operations_file = None
        self.roles_to_operations_file = None
        self.resources_to_operations_mapping = {}
        self.operation_to_allowed_roles = {}
        self.logger = logging.getLogger("nbi.authenticator")

    def start(self, config):
        """
        Method to configure the Authenticator object. This method should be called
        after object creation. It is responsible by initializing the selected backend,
        as well as the initialization of the database connection.

        :param config: dictionary containing the relevant parameters for this object.
        """
        self.config = config

        try:
            if not self.db:
                if config["database"]["driver"] == "mongo":
                    self.db = dbmongo.DbMongo()
                    self.db.db_connect(config["database"])
                elif config["database"]["driver"] == "memory":
                    self.db = dbmemory.DbMemory()
                    self.db.db_connect(config["database"])
                else:
                    raise AuthException("Invalid configuration param '{}' at '[database]':'driver'"
                                        .format(config["database"]["driver"]))
            if not self.backend:
                if config["authentication"]["backend"] == "keystone":
                    self.backend = AuthconnKeystone(self.config["authentication"])
                elif config["authentication"]["backend"] == "internal":
                    self._internal_tokens_prune()
                else:
                    raise AuthException("Unknown authentication backend: {}"
                                        .format(config["authentication"]["backend"]))
            if not self.resources_to_operations_file:
                if "resources_to_operations" in config["rbac"]:
                    self.resources_to_operations_file = config["rbac"]["resources_to_operations"]
                else:
                    possible_paths = (
                        __file__[:__file__.rfind("auth.py")] + "resources_to_operations.yml",
                        "./resources_to_operations.yml"
                    )
                    for config_file in possible_paths:
                        if path.isfile(config_file):
                            self.resources_to_operations_file = config_file
                            break
                    if not self.resources_to_operations_file:
                        raise AuthException("Invalid permission configuration: resources_to_operations file missing")
            if not self.roles_to_operations_file:
                if "roles_to_operations" in config["rbac"]:
                    self.roles_to_operations_file = config["rbac"]["roles_to_operations"]
                else:
                    possible_paths = (
                        __file__[:__file__.rfind("auth.py")] + "roles_to_operations.yml",
                        "./roles_to_operations.yml"
                    )
                    for config_file in possible_paths:
                        if path.isfile(config_file):
                            self.roles_to_operations_file = config_file
                            break
                    if not self.roles_to_operations_file:
                        raise AuthException("Invalid permission configuration: roles_to_operations file missing")
        except Exception as e:
            raise AuthException(str(e))

    def stop(self):
        try:
            if self.db:
                self.db.db_disconnect()
        except DbException as e:
            raise AuthException(str(e), http_code=e.http_code)

    def init_db(self, target_version='1.0'):
        """
        Check if the database has been initialized, with at least one user. If not, create the required tables
        and insert the predefined mappings between roles and permissions.

        :param target_version: schema version that should be present in the database.
        :return: None if OK, exception if error or version is different.
        """
        # Always reads operation to resource mapping from file (this is static, no need to store it in MongoDB)
        # Operations encoding: "<METHOD> <URL>"
        # Note: it is faster to rewrite the value than to check if it is already there or not
        if self.config["authentication"]["backend"] == "internal":
            return

        operations = []
        with open(self.resources_to_operations_file, "r") as stream:
            resources_to_operations_yaml = yaml.load(stream)

        for resource, operation in resources_to_operations_yaml["resources_to_operations"].items():
            if operation not in operations:
                operations.append(operation)
            self.resources_to_operations_mapping[resource] = operation

        records = self.db.get_list("roles_operations")

        # Loading permissions to MongoDB. If there are permissions already in MongoDB, do nothing.
        if len(records) == 0:
            with open(self.roles_to_operations_file, "r") as stream:
                roles_to_operations_yaml = yaml.load(stream)

            roles = []
            for role_with_operations in roles_to_operations_yaml["roles_to_operations"]:
                # Verifying if role already exists. If it does, send warning to log and ignore it.
                if role_with_operations["role"] not in roles:
                    roles.append(role_with_operations["role"])
                else:
                    self.logger.warning("Duplicated role with name: {0}. Role definition is ignored."
                                        .format(role_with_operations["role"]))
                    continue

                role_ops = {}
                root = None

                if not role_with_operations["operations"]:
                    continue

                for operation, is_allowed in role_with_operations["operations"].items():
                    if not isinstance(is_allowed, bool):
                        continue

                    if operation == ":":
                        root = is_allowed
                        continue

                    if len(operation) != 1 and operation[-1] == ":":
                        self.logger.warning("Invalid operation {0} terminated in ':'. "
                                            "Operation will be discarded"
                                            .format(operation))
                        continue

                    if operation not in role_ops.keys():
                        role_ops[operation] = is_allowed
                    else:
                        self.logger.info("In role {0}, the operation {1} with the value {2} was discarded due to "
                                         "repetition.".format(role_with_operations["role"], operation, is_allowed))

                if not root:
                    root = False
                    self.logger.info("Root for role {0} not defined. Default value 'False' applied."
                                     .format(role_with_operations["role"]))

                now = time()
                operation_to_roles_item = {
                    "_admin": {
                        "created": now,
                        "modified": now,
                    },
                    "name": role_with_operations["role"],
                    "root": root
                }

                for operation, value in role_ops.items():
                    operation_to_roles_item[operation] = value

                if self.config["authentication"]["backend"] != "internal" and \
                        role_with_operations["role"] != "anonymous":
                    keystone_id = [role for role in self.backend.get_role_list() 
                                   if role["name"] == role_with_operations["role"]]
                    if keystone_id:
                        keystone_id = keystone_id[0]
                    else:
                        keystone_id = self.backend.create_role(role_with_operations["role"])
                    operation_to_roles_item["_id"] = keystone_id["_id"]

                self.db.create("roles_operations", operation_to_roles_item)

        permissions = {oper: [] for oper in operations}
        records = self.db.get_list("roles_operations")

        ignore_fields = ["_id", "_admin", "name", "root"]
        for record in records:
            record_permissions = {oper: record["root"] for oper in operations}
            operations_joined = [(oper, value) for oper, value in record.items() if oper not in ignore_fields]
            operations_joined.sort(key=lambda x: x[0].count(":"))

            for oper in operations_joined:
                match = list(filter(lambda x: x.find(oper[0]) == 0, record_permissions.keys()))

                for m in match:
                    record_permissions[m] = oper[1]

            allowed_operations = [k for k, v in record_permissions.items() if v is True]

            for allowed_op in allowed_operations:
                permissions[allowed_op].append(record["name"])

        for oper, role_list in permissions.items():
            self.operation_to_allowed_roles[oper] = role_list

        if self.config["authentication"]["backend"] != "internal":
            self.backend.assign_role_to_user("admin", "admin", "system_admin")

    def authorize(self):
        token = None
        user_passwd64 = None
        try:
            # 1. Get token Authorization bearer
            auth = cherrypy.request.headers.get("Authorization")
            if auth:
                auth_list = auth.split(" ")
                if auth_list[0].lower() == "bearer":
                    token = auth_list[-1]
                elif auth_list[0].lower() == "basic":
                    user_passwd64 = auth_list[-1]
            if not token:
                if cherrypy.session.get("Authorization"):
                    # 2. Try using session before request a new token. If not, basic authentication will generate
                    token = cherrypy.session.get("Authorization")
                    if token == "logout":
                        token = None  # force Unauthorized response to insert user password again
                elif user_passwd64 and cherrypy.request.config.get("auth.allow_basic_authentication"):
                    # 3. Get new token from user password
                    user = None
                    passwd = None
                    try:
                        user_passwd = standard_b64decode(user_passwd64).decode()
                        user, _, passwd = user_passwd.partition(":")
                    except Exception:
                        pass
                    outdata = self.new_token(None, {"username": user, "password": passwd})
                    token = outdata["id"]
                    cherrypy.session['Authorization'] = token
            if self.config["authentication"]["backend"] == "internal":
                return self._internal_authorize(token)
            else:
                if not token:
                    raise AuthException("Needed a token or Authorization http header",
                                        http_code=HTTPStatus.UNAUTHORIZED)
                try:
                    self.backend.validate_token(token)
                    self.check_permissions(self.tokens_cache[token], cherrypy.request.path_info,
                                           cherrypy.request.method)
                    # TODO: check if this can be avoided. Backend may provide enough information
                    return deepcopy(self.tokens_cache[token])
                except AuthException:
                    self.del_token(token)
                    raise
        except AuthException as e:
            if cherrypy.session.get('Authorization'):
                del cherrypy.session['Authorization']
            cherrypy.response.headers["WWW-Authenticate"] = 'Bearer realm="{}"'.format(e)
            raise AuthException(str(e))

    def new_token(self, session, indata, remote):
        if self.config["authentication"]["backend"] == "internal":
            return self._internal_new_token(session, indata, remote)
        else:
            current_token = None
            if session:
                current_token = session.get("token")
            token_info = self.backend.authenticate(
                user=indata.get("username"),
                password=indata.get("username"),
                token=current_token,
                project=indata.get("project_id")
            )

            # if indata.get("username"):
            #     token, projects = self.backend.authenticate_with_user_password(
            #         indata.get("username"), indata.get("password"))
            # elif session:
            #     token, projects = self.backend.authenticate_with_token(
            #         session.get("id"), indata.get("project_id"))
            # else:
            #     raise AuthException("Provide credentials: username/password or Authorization Bearer token",
            #                         http_code=HTTPStatus.UNAUTHORIZED)
            #
            # if indata.get("project_id"):
            #     project_id = indata.get("project_id")
            #     if project_id not in projects:
            #         raise AuthException("Project {} not allowed for this user".format(project_id),
            #                             http_code=HTTPStatus.UNAUTHORIZED)
            # else:
            #     project_id = projects[0]
            #
            # if not session:
            #     token, projects = self.backend.authenticate_with_token(token, project_id)
            #
            # if project_id == "admin":
            #     session_admin = True
            # else:
            #     session_admin = reduce(lambda x, y: x or (True if y == "admin" else False),
            #                            projects, False)

            now = time()
            new_session = {
                "_id": token_info["_id"],
                "id": token_info["_id"],
                "issued_at": now,
                "expires": token_info.get("expires", now + 3600),
                "project_id": token_info["project_id"],
                "username": token_info.get("username") or session.get("username"),
                "remote_port": remote.port,
                "admin": True if token_info.get("project_name") == "admin" else False   # TODO put admin in RBAC
            }

            if remote.name:
                new_session["remote_host"] = remote.name
            elif remote.ip:
                new_session["remote_host"] = remote.ip

            # TODO: check if this can be avoided. Backend may provide enough information
            self.tokens_cache[token_info["_id"]] = new_session

            return deepcopy(new_session)

    def get_token_list(self, session):
        if self.config["authentication"]["backend"] == "internal":
            return self._internal_get_token_list(session)
        else:
            # TODO: check if this can be avoided. Backend may provide enough information
            return [deepcopy(token) for token in self.tokens_cache.values()
                    if token["username"] == session["username"]]

    def get_token(self, session, token):
        if self.config["authentication"]["backend"] == "internal":
            return self._internal_get_token(session, token)
        else:
            # TODO: check if this can be avoided. Backend may provide enough information
            token_value = self.tokens_cache.get(token)
            if not token_value:
                raise AuthException("token not found", http_code=HTTPStatus.NOT_FOUND)
            if token_value["username"] != session["username"] and not session["admin"]:
                raise AuthException("needed admin privileges", http_code=HTTPStatus.UNAUTHORIZED)
            return token_value

    def del_token(self, token):
        if self.config["authentication"]["backend"] == "internal":
            return self._internal_del_token(token)
        else:
            try:
                self.backend.revoke_token(token)
                del self.tokens_cache[token]
                return "token '{}' deleted".format(token)
            except KeyError:
                raise AuthException("Token '{}' not found".format(token), http_code=HTTPStatus.NOT_FOUND)

    def check_permissions(self, session, url, method):
        self.logger.info("Session: {}".format(session))
        self.logger.info("URL: {}".format(url))
        self.logger.info("Method: {}".format(method))

        key, parameters = self._normalize_url(url, method)

        # TODO: Check if parameters might be useful for the decision

        operation = self.resources_to_operations_mapping[key]
        roles_required = self.operation_to_allowed_roles[operation]
        roles_allowed = self.backend.get_user_role_list(session["id"])

        if "anonymous" in roles_required:
            return

        for role in roles_allowed:
            if role in roles_required:
                return

        raise AuthException("Access denied: lack of permissions.")

    def get_user_list(self):
        return self.backend.get_user_list()

    def _normalize_url(self, url, method):
        # Removing query strings
        normalized_url = url if '?' not in url else url[:url.find("?")]
        normalized_url_splitted = normalized_url.split("/")
        parameters = {}

        filtered_keys = [key for key in self.resources_to_operations_mapping.keys()
                         if method in key.split()[0]]

        for idx, path_part in enumerate(normalized_url_splitted):
            tmp_keys = []
            for tmp_key in filtered_keys:
                splitted = tmp_key.split()[1].split("/")
                if idx >= len(splitted):
                    continue
                elif "<" in splitted[idx] and ">" in splitted[idx]:
                    if splitted[idx] == "<artifactPath>":
                        tmp_keys.append(tmp_key)
                        continue
                    elif idx == len(normalized_url_splitted) - 1 and \
                            len(normalized_url_splitted) != len(splitted):
                        continue
                    else:
                        tmp_keys.append(tmp_key)
                elif splitted[idx] == path_part:
                    if idx == len(normalized_url_splitted) - 1 and \
                            len(normalized_url_splitted) != len(splitted):
                        continue
                    else:
                        tmp_keys.append(tmp_key)
            filtered_keys = tmp_keys
            if len(filtered_keys) == 1 and \
                    filtered_keys[0].split("/")[-1] == "<artifactPath>":
                break

        if len(filtered_keys) == 0:
            raise AuthException("Cannot make an authorization decision. URL not found. URL: {0}".format(url))
        elif len(filtered_keys) > 1:
            raise AuthException("Cannot make an authorization decision. Multiple URLs found. URL: {0}".format(url))

        filtered_key = filtered_keys[0]

        for idx, path_part in enumerate(filtered_key.split()[1].split("/")):
            if "<" in path_part and ">" in path_part:
                if path_part == "<artifactPath>":
                    parameters[path_part[1:-1]] = "/".join(normalized_url_splitted[idx:])
                else:
                    parameters[path_part[1:-1]] = normalized_url_splitted[idx]

        return filtered_key, parameters

    def _internal_authorize(self, token_id):
        try:
            if not token_id:
                raise AuthException("Needed a token or Authorization http header", http_code=HTTPStatus.UNAUTHORIZED)
            # try to get from cache first
            now = time()
            session = self.tokens_cache.get(token_id)
            if session and session["expires"] < now:
                # delete token. MUST be done with care, as another thread maybe already delete it. Do not use del
                self.tokens_cache.pop(token_id, None)
                session = None
            if session:
                return session

            # get from database if not in cache
            session = self.db.get_one("tokens", {"_id": token_id})
            if session["expires"] < now:
                raise AuthException("Expired Token or Authorization http header", http_code=HTTPStatus.UNAUTHORIZED)
            self.tokens_cache[token_id] = session
            return session
        except DbException as e:
            if e.http_code == HTTPStatus.NOT_FOUND:
                raise AuthException("Invalid Token or Authorization http header", http_code=HTTPStatus.UNAUTHORIZED)
            else:
                raise

        except AuthException:
            if self.config["global"].get("test.user_not_authorized"):
                return {"id": "fake-token-id-for-test",
                        "project_id": self.config["global"].get("test.project_not_authorized", "admin"),
                        "username": self.config["global"]["test.user_not_authorized"], "admin": True}
            else:
                raise

    def _internal_new_token(self, session, indata, remote):
        now = time()
        user_content = None

        # Try using username/password
        if indata.get("username"):
            user_rows = self.db.get_list("users", {"username": indata.get("username")})
            if user_rows:
                user_content = user_rows[0]
                salt = user_content["_admin"]["salt"]
                shadow_password = sha256(indata.get("password", "").encode('utf-8') + salt.encode('utf-8')).hexdigest()
                if shadow_password != user_content["password"]:
                    user_content = None
            if not user_content:
                raise AuthException("Invalid username/password", http_code=HTTPStatus.UNAUTHORIZED)
        elif session:
            user_rows = self.db.get_list("users", {"username": session["username"]})
            if user_rows:
                user_content = user_rows[0]
            else:
                raise AuthException("Invalid token", http_code=HTTPStatus.UNAUTHORIZED)
        else:
            raise AuthException("Provide credentials: username/password or Authorization Bearer token",
                                http_code=HTTPStatus.UNAUTHORIZED)

        token_id = ''.join(random_choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                           for _ in range(0, 32))
        project_id = indata.get("project_id")
        if project_id:
            if project_id != "admin":
                # To allow project names in project_id
                proj = self.db.get_one("projects", {BaseTopic.id_field("projects", project_id): project_id})
                if proj["_id"] not in user_content["projects"] and proj["name"] not in user_content["projects"]:
                    raise AuthException("project {} not allowed for this user"
                                        .format(project_id), http_code=HTTPStatus.UNAUTHORIZED)
        else:
            project_id = user_content["projects"][0]
        if project_id == "admin":
            session_admin = True
        else:
            # To allow project names in project_id
            project = self.db.get_one("projects", {BaseTopic.id_field("projects", project_id): project_id})
            session_admin = project.get("admin", False)
        new_session = {"issued_at": now, "expires": now + 3600,
                       "_id": token_id, "id": token_id, "project_id": project_id, "username": user_content["username"],
                       "remote_port": remote.port, "admin": session_admin}
        if remote.name:
            new_session["remote_host"] = remote.name
        elif remote.ip:
            new_session["remote_host"] = remote.ip

        self.tokens_cache[token_id] = new_session
        self.db.create("tokens", new_session)
        # check if database must be prune
        self._internal_tokens_prune(now)
        return deepcopy(new_session)

    def _internal_get_token_list(self, session):
        now = time()
        token_list = self.db.get_list("tokens", {"username": session["username"], "expires.gt": now})
        return token_list

    def _internal_get_token(self, session, token_id):
        token_value = self.db.get_one("tokens", {"_id": token_id}, fail_on_empty=False)
        if not token_value:
            raise AuthException("token not found", http_code=HTTPStatus.NOT_FOUND)
        if token_value["username"] != session["username"] and not session["admin"]:
            raise AuthException("needed admin privileges", http_code=HTTPStatus.UNAUTHORIZED)
        return token_value

    def _internal_del_token(self, token_id):
        try:
            self.tokens_cache.pop(token_id, None)
            self.db.del_one("tokens", {"_id": token_id})
            return "token '{}' deleted".format(token_id)
        except DbException as e:
            if e.http_code == HTTPStatus.NOT_FOUND:
                raise AuthException("Token '{}' not found".format(token_id), http_code=HTTPStatus.NOT_FOUND)
            else:
                raise

    def _internal_tokens_prune(self, now=None):
        now = now or time()
        if not self.next_db_prune_time or self.next_db_prune_time >= now:
            self.db.del_list("tokens", {"expires.lt": now})
            self.next_db_prune_time = self.periodin_db_pruning + now
            self.tokens_cache.clear()  # force to reload tokens from database
