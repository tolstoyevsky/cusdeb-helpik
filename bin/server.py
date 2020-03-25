# Copyright (C) 2020 Dmitry Ivanko. All Rights Reserved.
# Copyright (C) 2020 Vladislav Yarovoy. All Rights Reserved.
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

"""Server-side of the Helpik microservice. """

import logging
from urllib.parse import urljoin

from aiohttp import ClientSession, web
from aiohttp.client_exceptions import ClientConnectorError
from bs4 import BeautifulSoup

from helpik import config, exceptions

logging.basicConfig(filename=config.LOG_PATH, level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class Handler(web.View):
    """Class-based requests handler to the Helpik microservice. """

    def __init__(self, request):
        super().__init__(request)

        self._params = {
            'action': 'parse',
            'prop': 'text',
            'page': '',  # will be specified later
            'origin': '*',
            'format': 'json',
            'formatversion': 2,
        }

        self._language = config.DEFAULT_LANGUAGE
        self._raw_contents = self._section = ''
        self._resp = {}

    async def get(self):
        """Handles GET requests to the microservice. """

        if 'pageName' in self.request.query:
            self._params['page'] = self.request.query['pageName']

        if 'language' in self.request.query:
            self._language = self.request.query['language']

        if 'section' in self.request.query:
            self._section = self.request.query['section']

        try:
            await self._get_raw_contents()
        except exceptions.CouldNotConnectToMediaWikiAPI:
            return web.StreamResponse(status=503)
        except exceptions.PageDoesNotExist:
            return web.StreamResponse(status=404)

        try:
            return web.json_response({
                'text': self._get_synopsis(),
                'url': urljoin(config.MEDIAWIKI_API_URL, '/' + self._params['page']),
            })
        except exceptions.ThereIsNoSynopsis:
            return web.StreamResponse(status=404)

    def _check_if_page_exists(self):
        if 'error' in self._resp and self._resp['error']['code'] == 'missingtitle':
            return False

        return True

    async def _get_raw_contents(self):
        self._params['page'] = f"{self._params['page']}/{self._language}"

        await self._request_mediawiki_api()

        if not self._check_if_page_exists():
            LOGGER.info('Fallback to English because the requested page does not exist in the '
                        'specified language (%s)', self._language)

            self._params['page'] = f"{self._params['page'][:-len(self._language)]}en"
            await self._request_mediawiki_api()

        if not self._check_if_page_exists():
            raise exceptions.PageDoesNotExist

        self._raw_contents = self._resp['parse']['text']

    def _get_synopsis(self):
        if self._section:
            soup = BeautifulSoup(self._raw_contents, 'lxml')
            for header in soup('h2'):
                if header.find('span', id=self._section.replace('_', ' ')):
                    self._raw_contents = str(header.find_next_sibling())
                    break
            else:
                raise exceptions.ThereIsNoSynopsis

        soup = BeautifulSoup(self._raw_contents, 'lxml')
        try:
            return str(soup.p)
        except AttributeError as exc:
            LOGGER.info("Could not find a synopsis on the page '%s'", self._params['page'])
            raise exceptions.ThereIsNoSynopsis from exc

    async def _request_mediawiki_api(self):
        try:
            async with ClientSession() as session:
                async with session.get(url=config.MEDIAWIKI_API_URL, params=self._params) as resp:
                    self._resp = await resp.json()
        except ClientConnectorError as exc:
            LOGGER.error('Could not connect to %s: %s', config.MEDIAWIKI_API_URL, exc)
            raise exceptions.CouldNotConnectToMediaWikiAPI


async def main():
    """The main entry point. """

    app = web.Application()
    app.router.add_get('/helpik_api/get_synopsis/', Handler)
    return app


if __name__ == '__main__':
    web.run_app(main(), host=config.HOST, port=config.PORT)
