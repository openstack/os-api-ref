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
    def setUp(self, app, status, warning):
        super(TestBasicExample, self).setUp()
        self.app = app
        self.status = status
        self.warning = warning
        self.app.build()
        self.html = (app.outdir / 'index.html').read_text()
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.content = str(self.soup)

    def test_expand_all(self):
        """Do we get an expand all button like we expect."""
        content = str(self.soup.find(id='expand-all'))
        example_button = ('<button class="btn btn-info btn-sm btn-expand-all" '
                          'data-toggle="collapse" id="expand-all">'
                          'Show All</button>')
        self.assertEqual(
            example_button,
            content)

    def test_rest_method(self):
        """Do we get a REST method call block"""

        # TODO(sdague): it probably would make sense to do this as a
        # whole template instead of parts.
        content = str(self.soup.find_all(class_='operation-grp'))
        self.assertIn(
            '<span class="glyphicon glyphicon-link"></span>',
            str(content))
        self.assertIn(
            '<span class="label label-GET">GET</span>',
            str(content))
        self.assertIn(
            '<div class="row col-md-12">/servers</div>',
            str(content))
        self.assertIn(
            ('<button class="btn btn-info btn-sm btn-detail" '
             'data-target="#list-servers-detail" data-toggle="collapse" '
             'id="list-servers-detail-btn">detail</button>'),
            str(content))

    def test_parameters(self):
        """Do we get some parameters table"""

        table = """<table border="1" class="docutils">
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
</tbody>
</table>"""

        self.assertIn(table, self.content)

    def test_rest_response(self):

        success_table = """table border="1" class="docutils">
<colgroup>
<col width="30%"/>
<col width="70%"/>
</colgroup>
<thead valign="bottom">
<tr class="row-odd"><th class="head">Code</th>
<th class="head">Reason</th>
</tr>
</thead>
<tbody valign="top">
<tr class="row-even"><td><code>200 - OK</code></td>
<td>Request was successful.</td>
</tr>
<tr class="row-odd"><td><code>100 - Continue</code></td>
<td>An unusual code for an API</td>
</tr>
<tr class="row-even"><td><code>201 - Created</code></td>
<td>Resource was created and is ready to use.</td>
</tr>
</tbody>
</table>
"""

        error_table = """<table border="1" class="docutils">
<colgroup>
<col width="30%"/>
<col width="70%"/>
</colgroup>
<thead valign="bottom">
<tr class="row-odd"><th class="head">Code</th>
<th class="head">Reason</th>
</tr>
</thead>
<tbody valign="top">
<tr class="row-even"><td><code>405 - Method Not Allowed</code></td>
<td>Method is not valid for this endpoint.</td>
</tr>
<tr class="row-odd"><td><code>403 - Forbidden</code></td>
<td>Policy does not allow current user to do this operation.</td>
</tr>
<tr class="row-even"><td><code>401 - Unauthorized</code></td>
<td>User must authenticate before making a request</td>
</tr>
<tr class="row-odd"><td><code>400 - Bad Request</code></td>
<td>Some content in the request was invalid</td>
</tr>
<tr class="row-even"><td><code>500 - Internal Server Error</code></td>
<td>Something went wrong inside the service.</td>
</tr>
<tr class="row-odd"><td><code>409 - Conflict</code></td>
<td>There is already a zone with this name.</td>
</tr>
</tbody>
</table>
"""
        self.assertIn(success_table, self.content)
        self.assertIn(error_table, self.content)
