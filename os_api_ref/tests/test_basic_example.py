# -*- coding: utf-8 -*-

# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""
test_os_api_ref
----------------------------------

Tests for `os_api_ref` module.
"""

from bs4 import BeautifulSoup
from sphinx_testing import with_app

from os_api_ref.tests import base


class TestBasicExample(base.TestCase):
    """Test basic rendering.

    This can be used to test that basic rendering works for these
    examples, so if someone breaks something we know.
    """

    @with_app(buildername='html', srcdir=base.example_dir('basic'),
              copy_srcdir_to_tmpdir=True)
    def test_sphinx_build(self, app, status, warning):
        app.build()
        html = (app.outdir / 'index.html').read_text()
        soup = BeautifulSoup(html, 'html.parser')
        content = str(soup.find(id='expand-all'))
        example_button = ('<button class="btn btn-info btn-sm btn-expand-all" '
                          'data-toggle="collapse" id="expand-all">'
                          'Show All</button>')
        self.assertEqual(
            example_button,
            content)
