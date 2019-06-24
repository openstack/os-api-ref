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
import sphinx
from sphinx_testing import with_app

from os_api_ref.tests import base


class TestMicroversions(base.TestCase):
    """Test basic rendering.

    This can be used to test that basic rendering works for these
    examples, so if someone breaks something we know.
    """

    @with_app(buildername='html', srcdir=base.example_dir('microversions'),
              copy_srcdir_to_tmpdir=True)
    def setUp(self, app, status, warning):
        super(TestMicroversions, self).setUp()
        self.app = app
        self.app.build()
        self.status = status.getvalue()
        self.warning = warning.getvalue()
        self.html = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.content = str(self.soup)

    def test_rest_method(self):
        """Test that min / max mv css class attributes are set"""
        content = self.soup.find_all(class_='rp_min_ver_2_17')
        self.assertRegexpMatches(
            str(content[0]),
            '^<div class="operation-grp rp_min_ver_2_17 rp_max_ver_2_19 ?"')
        content = self.soup.find_all(class_='rp_max_ver_2_19')
        self.assertRegexpMatches(
            str(content[0]),
            '^<div class="operation-grp rp_min_ver_2_17 rp_max_ver_2_19 ?"')

    def test_parameters_table(self):
        """Test that min / max mv css class attributes are set in params"""
        if sphinx.version_info >= (2, 0, 0):
            table = """<div class="api-detail collapse section" id="list-servers-detail">
<table class="docutils align-{}">
<colgroup>
<col style="width: 20%"/>
<col style="width: 10%"/>
<col style="width: 10%"/>
<col style="width: 60%"/>
</colgroup>
<thead>
<tr class="row-odd"><th class="head"><p>Name</p></th>
<th class="head"><p>In</p></th>
<th class="head"><p>Type</p></th>
<th class="head"><p>Description</p></th>
</tr>
</thead>
<tbody>
<tr class="row-even"><td><p>name</p></td>
<td><p>body</p></td>
<td><p>string</p></td>
<td><p>The name of things</p></td>
</tr>
<tr class="rp_min_ver_2_11 row-odd"><td><p>name2</p></td>
<td><p>body</p></td>
<td><p>string</p></td>
<td><p>The name of things</p>
<p><strong>New in version 2.11</strong></p>
</td>
</tr>
<tr class="rp_max_ver_2_20 row-even"><td><p>name3</p></td>
<td><p>body</p></td>
<td><p>string</p></td>
<td><p>The name of things</p>
<p><strong>Available until version 2.20</strong></p>
</td>
</tr>
</tbody>
</table>
</div>
""".format('center' if sphinx.version_info < (2, 1, 0) else 'default')  # noqa
        else:
            table = """<div class="api-detail collapse section" id="list-servers-detail">
<table border="1" class="docutils">
<colgroup>
<col width="20%"/>
<col width="10%"/>
<col width="10%"/>
<col width="60%"/>
</colgroup>
<thead valign="bottom">
<tr class="row-odd"><th class="head">Name</th>
<th class="head">In</th>
<th class="head">Type</th>
<th class="head">Description</th>
</tr>
</thead>
<tbody valign="top">
<tr class="row-even"><td>name</td>
<td>body</td>
<td>string</td>
<td>The name of things</td>
</tr>
<tr class="rp_min_ver_2_11 row-odd"><td>name2</td>
<td>body</td>
<td>string</td>
<td><p class="first">The name of things</p>
<p class="last"><strong>New in version 2.11</strong></p>
</td>
</tr>
<tr class="rp_max_ver_2_20 row-even"><td>name3</td>
<td>body</td>
<td>string</td>
<td><p class="first">The name of things</p>
<p class="last"><strong>Available until version 2.20</strong></p>
</td>
</tr>
</tbody>
</table>
</div>
"""  # noqa

        self.assertIn(table, self.content)

    def test_mv_selector(self):

        button_selectors = '<option selected="selected" value="">All</option><option value="2.1">2.1</option><option value="2.2">2.2</option><option value="2.3">2.3</option><option value="2.4">2.4</option><option value="2.5">2.5</option><option value="2.6">2.6</option><option value="2.7">2.7</option><option value="2.8">2.8</option><option value="2.9">2.9</option><option value="2.10">2.10</option><option value="2.11">2.11</option><option value="2.12">2.12</option><option value="2.13">2.13</option><option value="2.14">2.14</option><option value="2.15">2.15</option><option value="2.16">2.16</option><option value="2.17">2.17</option><option value="2.18">2.18</option><option value="2.19">2.19</option><option value="2.20">2.20</option><option value="2.21">2.21</option><option value="2.22">2.22</option><option value="2.23">2.23</option><option value="2.24">2.24</option><option value="2.25">2.25</option><option value="2.26">2.26</option><option value="2.27">2.27</option><option value="2.28">2.28</option><option value="2.29">2.29</option><option value="2.30">2.30</option>'  # noqa
        self.assertIn(button_selectors, self.content)

    def test_js_declares(self):
        self.assertIn("os_max_mv = 30;", self.content)
        self.assertIn("os_min_mv = 1;", self.content)
