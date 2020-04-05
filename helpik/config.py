# Copyright (C) 2020 Dmitry Ivanko. All Rights Reserved.
# Copyright (C) 2020 Vladislav Yarovoy. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Module allowing configuration of the service via the environment variables. """

import os

DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'en')

EMULATED_MEDIAWIKI_PORT = os.getenv('EMULATED_MEDIAWIKI_PORT', '8006')

HOST = os.getenv('HOST', 'localhost')

LOG_PATH = os.getenv('LOG_PATH', 'cusdeb-helpik.log')

MEDIAWIKI_API_URL = os.getenv('MEDIAWIKI_API_URL', 'https://wiki.cusdeb.com/api.php')

PORT = os.getenv('PORT', '8005')
