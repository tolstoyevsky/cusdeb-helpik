#!/usr/bin/env python3
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

"""Mock server for simulating MediaWiki API. """

import os
from argparse import ArgumentParser

from aiohttp import web


class Handler(web.View):
    """Class-based view for handling requests to the /api.php endpoint. """

    def __init__(self, request):
        super().__init__(request)

        self._base_dir = os.path.dirname(os.path.abspath(__file__))
        self._existing_pages = ('Hello_page/en', 'Hello_page/ru', )

    async def get(self):
        """Hanles the GET requests to the /api.php endpoint. """

        try:
            page_name = self.request.query['page']
        except KeyError:
            return web.json_response(self._handle_invalid_title())

        if page_name in self._existing_pages:
            return web.json_response(self._get_page_from_disk(page_name))

        return web.json_response(self._handle_missing_title())

    def _get_page_from_disk(self, page_name):
        file_name = f"{page_name.lower().replace('/', '.')}.html"
        path = os.path.join(self._base_dir, file_name)

        with open(path, 'r') as infile:
            text = infile.read()

        return {
            'parse': {
                'title': page_name.replace('_', ' '),
                'pageid': 1,
                'text': text,
            }
        }

    @staticmethod
    def _handle_missing_title():
        return {
            'error': {
                'code': 'missingtitle',
                'info': "The page you specified doesn't exist.",
                # Skip the docref field since it's not so important.
            }
        }

    @staticmethod
    def _handle_invalid_title():
        return {
            'error': {
                'code': 'invalidtitle',
                'info': 'Bad title "".',
                # Skip the docref field since it's not so important.
            }
        }


async def create_app():
    """Creates an Application instance. """

    app = web.Application()
    app.router.add_get('/api.php', Handler)
    return app


def main():
    """The main entry point. """

    parser = ArgumentParser(description='usage: %prog [options] arguments')
    parser.add_argument('-p', '--port', dest='port', type=int, default=8080,
                        help='the port the server listens on')

    options = parser.parse_args()

    web.run_app(create_app(), port=options.port)


if __name__ == '__main__':
    main()
