# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import re

import pytest

pytestmark = pytest.mark.nondestructive

URL_LINK = '<a class="url" href="{0}/" target="_blank">URL</a>'
SCREENSHOT_LINK = '<a class="image" href="#" target="_blank">Screenshot</a>'
SCREENSHOT_REGEX = '<div class="image"><a href="#"><img src="data:image/png;base64,.*"/></a></div>'  # noqa
LOGS_REGEX = '<a class="text" href="data:text/plain;charset=utf-8;base64,.*" target="_blank">.* Log</a>'  # noqa
HTML_REGEX = '<a class="text" href="data:text/plain;charset=utf-8;base64,.*" target="_blank">HTML</a>'  # noqa


def run(testdir, *args):
    testdir.makepyfile("""
        import pytest
        @pytest.mark.nondestructive
        def test_fail(webtext):
            assert False
    """)
    path = testdir.tmpdir.join('report.html')
    result = testdir.runpytestqa('--html', path, *args)
    with open(str(path)) as f:
        html = f.read()
    return result, html


@pytest.mark.parametrize('when', ['always', 'failure', 'never'])
def test_capture_debug_env(testdir, base_url, monkeypatch, when):
    monkeypatch.setenv('SELENIUM_CAPTURE_DEBUG', when)
    testdir.makepyfile("""
        import pytest
        @pytest.mark.nondestructive
        def test_capture_debug(webtext):
            assert {0}
    """.format('True' if 'always' else 'False'))
    result, html = run(testdir)
    if when in ['always', 'failure']:
        assert URL_LINK.format(base_url) in html
        assert SCREENSHOT_LINK in html
        assert re.search(SCREENSHOT_REGEX, html) is not None
        assert re.search(LOGS_REGEX, html) is not None
        assert re.search(HTML_REGEX, html) is not None
    else:
        assert URL_LINK.format(base_url) not in html
        assert SCREENSHOT_LINK not in html
        assert re.search(SCREENSHOT_REGEX, html) is None
        assert re.search(LOGS_REGEX, html) is None
        assert re.search(HTML_REGEX, html) is None


@pytest.mark.parametrize('when', ['always', 'failure', 'never'])
def test_capture_debug_config(testdir, base_url, when):
    testdir.makefile('.ini', pytest="""
        [pytest]
        selenium_capture_debug={0}
    """.format(when))
    testdir.makepyfile("""
        import pytest
        @pytest.mark.nondestructive
        def test_capture_debug(webtext):
            assert {0}
    """.format('True' if 'always' else 'False'))
    result, html = run(testdir)
    if when in ['always', 'failure']:
        assert URL_LINK.format(base_url) in html
        assert SCREENSHOT_LINK in html
        assert re.search(SCREENSHOT_REGEX, html) is not None
        assert re.search(LOGS_REGEX, html) is not None
        assert re.search(HTML_REGEX, html) is not None
    else:
        assert URL_LINK.format(base_url) not in html
        assert SCREENSHOT_LINK not in html
        assert re.search(SCREENSHOT_REGEX, html) is None
        assert re.search(LOGS_REGEX, html) is None
        assert re.search(HTML_REGEX, html) is None


@pytest.mark.parametrize('exclude', ['url', 'screenshot', 'html', 'logs'])
def test_exclude_debug_env(testdir, base_url, monkeypatch, exclude):
    monkeypatch.setenv('SELENIUM_EXCLUDE_DEBUG', exclude)
    result, html = run(testdir)
    assert result.ret

    if exclude == 'url':
        assert URL_LINK.format(base_url) not in html
    else:
        assert URL_LINK.format(base_url) in html

    if exclude == 'screenshot':
        assert SCREENSHOT_LINK not in html
        assert re.search(SCREENSHOT_REGEX, html) is None
    else:
        assert SCREENSHOT_LINK in html
        assert re.search(SCREENSHOT_REGEX, html) is not None

    if exclude == 'logs':
        assert re.search(LOGS_REGEX, html) is None
    else:
        assert re.search(LOGS_REGEX, html) is not None

    if exclude == 'html':
        assert re.search(HTML_REGEX, html) is None
    else:
        assert re.search(HTML_REGEX, html) is not None


@pytest.mark.parametrize('exclude', ['url', 'screenshot', 'html', 'logs'])
def test_exclude_debug_config(testdir, base_url, monkeypatch, exclude):
    testdir.makefile('.ini', pytest="""
        [pytest]
        selenium_exclude_debug={0}
    """.format(exclude))
    result, html = run(testdir)
    assert result.ret

    if exclude == 'url':
        assert URL_LINK.format(base_url) not in html
    else:
        assert URL_LINK.format(base_url) in html

    if exclude == 'screenshot':
        assert SCREENSHOT_LINK not in html
        assert re.search(SCREENSHOT_REGEX, html) is None
    else:
        assert SCREENSHOT_LINK in html
        assert re.search(SCREENSHOT_REGEX, html) is not None

    if exclude == 'logs':
        assert re.search(LOGS_REGEX, html) is None
    else:
        assert re.search(LOGS_REGEX, html) is not None

    if exclude == 'html':
        assert re.search(HTML_REGEX, html) is None
    else:
        assert re.search(HTML_REGEX, html) is not None
