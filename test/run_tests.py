# Copyright (C) 2020 Evgeny Golyshev. All Rights Reserved.
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

"""Tests for the Helpik microservice. """

import asyncio
import os
import socket
from asyncio import create_subprocess_exec

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop, unused_port

from bin.server import main
from helpik import config


class HelpikTestCase(AioHTTPTestCase):
    """Testcase for the Helpik microservice. """

    def __init__(self, request):
        super().__init__(request)

        self._base_dir = os.path.dirname(os.path.abspath(__file__))
        self._port = self._proc = None

    async def setUpAsync(self):
        self._port = unused_port()
        config.MEDIAWIKI_API_URL = f'http://127.0.0.1:{self._port}/api.php'

        cmd = [f'{self._base_dir}/run_mock_mediawiki_api.py', '--port', str(self._port)]
        self._proc = await create_subprocess_exec(*cmd)

        # Wait until the server is ready.
        for _ in range(60):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                res = sock.connect_ex(('127.0.0.1', self._port))
                if res == 0:
                    break

            await asyncio.sleep(1)
        else:
            raise Exception('Could not run the mock server for simulating the MediaWiki API')

    async def tearDownAsync(self):
        self._proc.terminate()
        # TODO: figure out why 'await self._proc.wait()' freezes

    async def get_application(self):
        """Overrides the get_app method to return the application. """

        return await main()

    @unittest_run_loop
    async def test_requesting_page(self):
        """Tests if it's possible to request for the synopsys of the specified page. """

        path = '/helpik_api/?page=Hello_page'
        resp = await self.client.request('GET', path)
        assert resp.status == 200

        parsed = await resp.json()
        assert parsed['text'] == '<p>Friendly greeting page.</p>'

        resp = await self.client.request('GET', path + '&lang=ru')
        assert resp.status == 200

        parsed = await resp.json()
        assert parsed['text'] == '<p>Страница дружеского приветствия.</p>'

    @unittest_run_loop
    async def test_requesting_for_non_existent_page(self):
        """Tests if the microservice returns 404 in response to the request for
        a non-existent _page_.
        """

        path = '/helpik_api/?page=Hello_page2'
        resp = await self.client.request('GET', path)
        assert resp.status == 404

    @unittest_run_loop
    async def test_requesting_for_non_existent_section(self):
        """Tests if the microservice returns 404 in response to the request for
        a non-existent _section_.
        """

        path = '/helpik_api/?page=Hello_page&lang=en&sec=Description2'
        resp = await self.client.request('GET', path)
        assert resp.status == 404

    @unittest_run_loop
    async def test_requesting_for_section(self):
        """Tests if it's possible to request the synopsis of the specified section. """

        path = '/helpik_api/?page=Hello_page&lang=en&sec=Description'
        resp = await self.client.request('GET', path)
        assert resp.status == 200

        parsed = await resp.json()
        assert parsed['text'] == '<p>The page has been created for testing purposes.</p>'

    @unittest_run_loop
    async def test_requesting_for_another_section(self):
        """Tests if it's possible to request the synopsis of another section from the same page. """

        path = '/helpik_api/?page=Hello_page&lang={lang}&sec=Copyright'
        resp = await self.client.request('GET', path.format(lang='en'))
        assert resp.status == 200

        parsed = await resp.json()
        assert '<p>The text of the page is licensed to the public under' in parsed['text']

        resp = await self.client.request('GET', path.format(lang='ru'))
        assert resp.status == 200

        parsed = await resp.json()
        assert '<p>Текст этой страницы распространяется под' in parsed['text']

    @unittest_run_loop
    async def test_requesting_unavailable_mediawiki_api(self):
        """Tests the case when the MediaWiki API is unavailable. """

        self._port = unused_port()  # the port isn't occupied by any server
        config.MEDIAWIKI_API_URL = f'http://127.0.0.1:{self._port}/api.php'  # unavailable server

        path = '/helpik_api/?page=Hello_page'
        resp = await self.client.request('GET', path)
        assert resp.status == 503

    @unittest_run_loop
    async def test_fallback(self):
        """Tests if the microservice is capable to fallback to English if there is no page in the
        specified language.
        """

        lang = 'fr'  # try to request for the page in French which doesn't exist
        path = f'/helpik_api/?page=Hello_page&lang={lang}&sec=Copyright'
        resp = await self.client.request('GET', path)
        assert resp.status == 200

        parsed = await resp.json()
        assert '<p>The text of the page is licensed to the public under' in parsed['text']
