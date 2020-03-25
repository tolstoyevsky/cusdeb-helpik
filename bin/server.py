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

"""Server-side of Helpik. """

import logging

import aiohttp
import bs4
from aiohttp import web
from aiohttp.web_request import Request

from bin import config
from bin import exceptions

logging.basicConfig(filename=config.LOG_PATH, level=logging.INFO)
LOGGER = logging.getLogger(__name__)


class Handler(web.View):
    """Class-based handler of the requests for wiki synopses. """

    def __init__(self, request: Request):
        super().__init__(request)

        self._params = {
            'action': 'parse',
            'prop': 'text',
            'page': '',
            'origin': '*',
            'format': 'json',
            'formatversion': 2
        }
        self._synopsis = ''
        self._client_language = config.DEFAULT_LANGUAGE

    async def get(self):
        """Returns content of a page by a page name. """

        synopsis = {}

        if 'pageName' in self.request.query:
            self._params['page'] = self.request.query['pageName']

        if 'language' in self.request.query:
            self._client_language = self.request.query['language']

        await self._get_synopsis()

        synopsis['text'] = self._strip()
        synopsis['url'] = config.MEDIAWIKI_API_URL.replace(
            f'{config.MEDIAWIKI_API_URL.split("/")[-1]}', '') + self._params['page']
        LOGGER.info('Response to the client`s request')

        if synopsis['text'] == 'None':
            return web.StreamResponse(status=404)

        return web.json_response(synopsis)

    async def _get_synopsis(self):
        """Parses the content of the wiki page. """

        self._params['page'] = f"{self._params['page']}/{self._client_language}"
        content = await self._request_mediawiki_api()

        try:
            if content == '':
                raise exceptions.CouldNotConnectToMediaWiki
        except exceptions.CouldNotConnectToMediaWiki:
            self._synopsis = ''

        try:
            if 'error' in content:
                raise exceptions.NotFoundRequestLanguage
        except exceptions.NotFoundRequestLanguage:
            LOGGER.warning('Not found request language for wiki page (%s)', self._client_language)
            self._params['page'] = self._params['page'].replace(f'/{self._client_language}', '/en')
            content = await self._request_mediawiki_api()

        try:
            self._synopsis = content
            self._synopsis = self._synopsis['parse']['text']
        except (AttributeError, TypeError, KeyError):
            self._synopsis = ''
            LOGGER.error('MediaWiki does not return page text')
        return self._synopsis

    async def _request_mediawiki_api(self):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=f'{config.MEDIAWIKI_API_URL}',
                                       params=self._params) as resp:
                    content = await resp.json()
                await session.close()
        except aiohttp.client_exceptions.ClientConnectorError:
            content = ''
            LOGGER.error('Could not connect to MediaWiki')

        return content

    def _strip(self):
        """Fetches synopsis and strips HTML tags out of the this. """

        text = bs4.BeautifulSoup(self._synopsis, 'lxml')
        try:
            text = text.p
        except AttributeError:
            text = ''
            LOGGER.error('Not found any content on requests page')

        return str(text)


async def main():
    """The main entry point. """

    app = web.Application()
    app.router.add_get('/helpik_api/get_synopsis/', Handler)
    return app


if __name__ == '__main__':
    web.run_app(main(), host=config.HOST, port=config.PORT)
