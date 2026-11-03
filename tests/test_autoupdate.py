import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'src'))

import autoupdate  # noqa: E402
import githubapi  # noqa: E402

VALID_INI = b'key=value\nother=thing\n'


def fake_response(content: bytes = VALID_INI, status_error: Exception | None = None) -> Mock:
    response = Mock(content=content)
    response.raise_for_status.side_effect = status_error
    return response


class DownloadTest(unittest.TestCase):
    def test_valid_file(self):
        with patch.object(autoupdate.requests, 'get', return_value=fake_response()):
            self.assertEqual(autoupdate.download('http://x'), VALID_INI)

    def test_empty_or_invalid_file_is_rejected(self):
        for content in (b'', b'   \n', b'<html>not an ini</html>'):
            with self.subTest(content=content), \
                    patch.object(autoupdate.requests, 'get', return_value=fake_response(content)):
                with self.assertRaises(requests.RequestException):
                    autoupdate.download('http://x')

    def test_http_error_is_propagated(self):
        error = requests.HTTPError('404')
        with patch.object(autoupdate.requests, 'get', return_value=fake_response(status_error=error)):
            with self.assertRaises(requests.RequestException):
                autoupdate.download('http://x')


class FetchRemoteFileTest(unittest.TestCase):
    def test_known_url_is_used_first(self):
        with patch.object(autoupdate, 'download', return_value=VALID_INI) as download, \
                patch.object(autoupdate, 'find_global_ini') as find:
            self.assertEqual(autoupdate.fetch_remote_file(), VALID_INI)
            download.assert_called_once_with(autoupdate.KNOWN_URL)
            find.assert_not_called()

    def test_falls_back_to_github_lookup(self):
        calls = []

        def fake_download(url):
            calls.append(url)
            if url == autoupdate.KNOWN_URL:
                raise requests.RequestException('broken')
            return VALID_INI

        with patch.object(autoupdate, 'download', side_effect=fake_download), \
                patch.object(autoupdate, 'find_global_ini', return_value='http://new') as find:
            self.assertEqual(autoupdate.fetch_remote_file(), VALID_INI)
            find.assert_called_once()
            self.assertEqual(calls, [autoupdate.KNOWN_URL, 'http://new'])

    def test_returns_none_when_everything_fails(self):
        with patch.object(autoupdate, 'download', side_effect=requests.RequestException('broken')), \
                patch.object(autoupdate, 'find_global_ini', return_value=None):
            self.assertIsNone(autoupdate.fetch_remote_file())


class SaveAndUpdateTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.game = Path(self.tmp.name)
        self.ini = self.game / 'data' / 'Localization' / 'english' / 'global.ini'

    def test_save_creates_directories_and_leaves_no_temp_file(self):
        self.assertTrue(autoupdate.save_file(self.ini, VALID_INI))
        self.assertEqual(self.ini.read_bytes(), VALID_INI)
        self.assertEqual(os.listdir(self.ini.parent), ['global.ini'])

    def test_failed_write_keeps_existing_file(self):
        autoupdate.save_file(self.ini, b'old=1')
        with patch.object(autoupdate.os, 'replace', side_effect=OSError('locked')):
            self.assertFalse(autoupdate.save_file(self.ini, VALID_INI))
        self.assertEqual(self.ini.read_bytes(), b'old=1')
        self.assertEqual(os.listdir(self.ini.parent), ['global.ini'])

    def test_update_flow(self):
        with patch.object(autoupdate, 'fetch_remote_file', return_value=VALID_INI):
            self.assertTrue(autoupdate.check_for_updates(self.game))
            self.assertEqual(self.ini.read_bytes(), VALID_INI)
            self.assertTrue(autoupdate.check_for_updates(self.game))
            self.ini.write_bytes(b'old=1')
            self.assertTrue(autoupdate.check_for_updates(self.game))
            self.assertEqual(self.ini.read_bytes(), VALID_INI)

    def test_failed_download_does_not_touch_local_file(self):
        autoupdate.save_file(self.ini, b'old=1')
        with patch.object(autoupdate, 'fetch_remote_file', return_value=None):
            self.assertFalse(autoupdate.check_for_updates(self.game))
        self.assertEqual(self.ini.read_bytes(), b'old=1')


class GithubLookupTest(unittest.TestCase):
    def lookup(self, payload):
        response = Mock()
        response.json.return_value = payload
        with patch.object(githubapi.requests, 'get', return_value=response) as get:
            return githubapi.find_global_ini('o', 'r', 'master', token='abc'), get

    def test_finds_file_in_tree(self):
        url, get = self.lookup({'tree': [
            {'type': 'tree', 'path': 'data'},
            {'type': 'blob', 'path': 'data/english/global.ini'},
        ]})
        self.assertEqual(url, 'https://raw.githubusercontent.com/o/r/refs/heads/master/data/english/global.ini')
        self.assertEqual(get.call_args.kwargs['headers'], {'Authorization': 'token abc'})

    def test_no_match_or_invalid_payload(self):
        self.assertIsNone(self.lookup({'tree': [{'type': 'blob', 'path': 'readme.md'}]})[0])
        self.assertIsNone(self.lookup({'unexpected': True})[0])


if __name__ == '__main__':
    unittest.main()
