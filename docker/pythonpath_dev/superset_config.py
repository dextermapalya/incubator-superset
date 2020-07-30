# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

#
# This file is included in the final Docker image and SHOULD be overridden when
# deploying the image to prod. Settings configured here are intended for use in local
# development environments. Also note that superset_config_docker.py is imported
# as a final step as a means to override "defaults" configured here
#

import logging
import os
from superset.config import *

from cachelib.file import FileSystemCache
from cachelib.redis import RedisCache
#from werkzeug.contrib.cache import RedisCache
from celery.schedules import crontab

logger = logging.getLogger()


def get_env_variable(var_name, default=None):
    """Get the environment variable or raise exception."""
    try:
        return os.environ[var_name]
    except KeyError:
        if default is not None:
            return default
        else:
            error_msg = "The environment variable {} was missing, abort...".format(
                var_name
            )
            raise EnvironmentError(error_msg)


DATABASE_DIALECT = get_env_variable("DATABASE_DIALECT")
DATABASE_USER = get_env_variable("DATABASE_USER")
DATABASE_PASSWORD = get_env_variable("DATABASE_PASSWORD")
DATABASE_HOST = get_env_variable("DATABASE_HOST")
DATABASE_PORT = get_env_variable("DATABASE_PORT")
DATABASE_DB = get_env_variable("DATABASE_DB")

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = "%s://%s:%s@%s:%s/%s" % (
    DATABASE_DIALECT,
    DATABASE_USER,
    DATABASE_PASSWORD,
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_DB,
)

REDIS_HOST = get_env_variable("REDIS_HOST")
REDIS_PORT = get_env_variable("REDIS_PORT")
REDIS_CELERY_DB = get_env_variable("REDIS_CELERY_DB", 0)
REDIS_RESULTS_DB = get_env_variable("REDIS_CELERY_DB", 1)


#RESULTS_BACKEND = FileSystemCache("/app/superset_home/sqllab")
RESULTS_BACKEND = RedisCache(host=REDIS_HOST, port=REDIS_PORT, key_prefix='superset_results')


#CACHE CONFIG
CACHE_CONFIG = {
'CACHE_TYPE': 'redis',
'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24, # 1 day default (in secs)
'CACHE_KEY_PREFIX': 'superset_results',
'CACHE_REDIS_URL': 'redis://superset_cache:6379/0',
}

TABLE_NAMES_CACHE_CONFIG = {
'CACHE_TYPE': 'redis',
'CACHE_DEFAULT_TIMEOUT': 60 * 60 * 24, # 1 day default (in secs)
'CACHE_KEY_PREFIX': 'superset_results',
'CACHE_REDIS_URL': 'redis://superset_cache:6379/0',
}

class CeleryConfig(object):
    BROKER_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_CELERY_DB}"
    CELERY_IMPORTS = ("superset.sql_lab", "superset.tasks",)
    CELERY_RESULT_BACKEND = f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_RESULTS_DB}"
    CELERY_ANNOTATIONS = {"tasks.add": {"rate_limit": "10/s"},
            'email_reports.send': {
                'rate_limit': '1/s',
                'time_limit': 5,
                'soft_time_limit': 7,
                'ignore_result': True,
            },
    
    }
    CELERYBEAT_SCHEDULE = {
        'email_reports.schedule_hourly': {
            'task': 'email_reports.schedule_hourly',
            'schedule': crontab(minute=1, hour='*'),
        },
    }
    CELERY_TASK_PROTOCOL = 1


CELERY_CONFIG = CeleryConfig
SQLLAB_CTAS_NO_LIMIT = True
ENABLE_SCHEDULED_EMAIL_REPORTS = True
EMAIL_NOTIFICATIONS = True

SMTP_HOST = "smtp.gmail.com"
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = "dexter.m@apalya.com"
SMTP_PORT = 25
SMTP_PASSWORD = "abcd1234" #os.environ.get("SMTP_PASSWORD")
SMTP_MAIL_FROM = "dexter.m@apalya.com"
#
# Optionally import superset_config_docker.py (which will have been included on
# the PYTHONPATH) in order to allow for local settings to be overridden
#
try:
    from superset_config_docker import *  # noqa
    import superset_config_docker

    logger.info(
        f"Loaded your Docker configuration at " f"[{superset_config_docker.__file__}]"
    )
except ImportError:
    logger.info("Using default Docker config...")
