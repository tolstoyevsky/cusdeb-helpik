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

"""Test server.py. """

import json
import unittest

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from bin.server import main
from helpik import config


class TestCase(AioHTTPTestCase):
    """Test case. """

    async def get_application(self):
        config.MEDIAWIKI_API_URL = f'http://127.0.0.1:{config.EMULATED_MEDIAWIKI_PORT}/api.php'
        return await main()

    @unittest_run_loop
    async def test_client_request(self):
        """This test checks method _strip and work server.py with correct params. """

        resp = await self.client.request("GET",
                                         "/helpik_api/get_synopsis/?pageName=test&language=en")
        text = await resp.text()
        self.assertEqual('<p>To hell and back.</p>', json.loads(text)['text'])
        assert 'test/en' in json.loads(text)['url']

    @unittest_run_loop
    async def test_client_request_with_different_language(self):
        """This test checks method _get_synopsis and work server.py without language in params
        and language in which there is no translation. """

        resp = await self.client.request("GET", "/helpik_api/get_synopsis/?pageName=test")
        text = await resp.text()
        self.assertEqual('<p>To hell and back.</p>', json.loads(text)['text'])

        resp = await self.client.request("GET", "/helpik_api/get_synopsis/?pageName=test&"
                                                "language=ru")
        text = await resp.text()
        self.assertEqual('<p>To hell and back.</p>', json.loads(text)['text'])

    @unittest_run_loop
    async def test_client_request_no_params(self):
        """This test checks method get and work server.py without params. """

        resp = await self.client.request("GET", "/helpik_api/get_synopsis/")
        status = resp.status
        self.assertEqual(404, status)

    @unittest_run_loop
    async def test_client_request_with_different_section(self):
        """This test checks method _strip and work server.py with different level section. """

        resp = await self.client.request("GET", "/helpik_api/get_synopsis/?pageName=test&"
                                                "language=en&section=article_1")
        text = await resp.text()
        self.assertEqual("<p>I don't fear Hell; Hell fears me.</p>", json.loads(text)['text'])

        resp = await self.client.request("GET", "/helpik_api/get_synopsis/?pageName=test&"
                                                "language=en&section=article_2")
        text = await resp.text()
        self.assertEqual("<p>I go like the devil.</p>", json.loads(text)['text'])


if __name__ == '__main__':
    unittest.main()
