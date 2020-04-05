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

"""Emulation mediawiki. """

from aiohttp import web

from helpik import config


async def get_response(request):
    """Get response on any request. """

    if 'test' not in request.query_string:
        return web.json_response({})
    return web.json_response({
        "parse":
            {"text": "<p>To hell and back.</p><h2>article 1</h2><p>I don't fear Hell;"
                     " Hell fears me.</p><h3>article 2</h3><p>I go like the devil.</p>"}
    })


async def main():
    """The main entry point. """

    app = web.Application()
    app.router.add_get('/api.php', get_response)
    return app


if __name__ == '__main__':
    web.run_app(main(), host='127.0.0.1', port=config.EMULATED_MEDIAWIKI_PORT)
