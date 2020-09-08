# CusDeb Helpik

CusDeb Helpik is microservice intended primarily, but **not** exclusively, for gathering synopses from [CusDeb Wiki](http://wiki.cusdeb.com) to display them on the [client](https://github.com/tolstoyevsky/cusdeb-web-client).

Helpik interacts directly with the [MediaWiki API](https://mediawiki.org/wiki/API:Main_page) and, therefore, it can be used with any wiki based on MediaWiki.

## Installation

```
$ git clone https://github.com/tolstoyevsky/cusdeb-helpik.git
$ virtualenv -ppython3 cusdeb-helpik-env
$ source cusdeb-helpik-env/bin/activate
(cusdeb-helpik-env) $ cd cusdeb-helpik
(cusdeb-helpik-env) $ python3 setup.py install
(cusdeb-helpik-env) $ python3 bin/server.py
```

### How to run tests

```
(cusdeb-helpik-env) $ python3 -m pytest test/run_tests.py
```

## API

* **URI:** `/helpik_api/get_synopsis/`
* **Method:** `GET`
* **Params**
  * `pageName=[string]`
  * `language=[string]`
  * `section=[string]`

  `pageName` is the name of the target page.

  `language` is the language of the target page. If the page in the specified language doesn't exist, Helpik fallbacks to English. If the fallback doesn't work the microservice returns a 404 status code (see below).

  `section` allows, if passed, the client to fetch the synopsis of the specified section on the target page instead of the synopsis of the page itself.
* **Success Response**
  * **Code:** 200
    * **Content:** `{"text": "<text>", "url": "<url>"}`, where
      * `<text>` is the synopsis of either the target page or the specified section on the target page;
      * `<url>` is the URL of the target page.
* **Error Responses**
  * **Code:** 404
    * **Content:** None
    * **Reason:** either the target page or the specified section on the target page doesn't exist.
  * **Code:** 503
    * **Content:** None
    * **Reason:** the MediaWiki API is unavailable when invoking the `/helpik_api/get_synopsis/` endpoint.

## Authors

See [AUTHORS](AUTHORS.md).

## Licensing

CusDeb Helpik is available under the [Apache License, Version 2.0](LICENSE).

