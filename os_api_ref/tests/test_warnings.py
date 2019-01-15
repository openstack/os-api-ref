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


class TestWarnings(base.TestCase):
    """Test basic rendering.

    This can be used to test that basic rendering works for these
    examples, so if someone breaks something we know.
    """

    @with_app(buildername='html', srcdir=base.example_dir('warnings'),
              copy_srcdir_to_tmpdir=True)
    def setUp(self, app, status, warning):
        super(TestWarnings, self).setUp()
        self.app = app
        self.app.build()
        self.status = status.getvalue()
        self.warning = warning.getvalue()
        self.html = (app.outdir / 'index.html').read_text(encoding='utf-8')
        self.soup = BeautifulSoup(self.html, 'html.parser')
        self.content = str(self.soup)

    def test_out_of_order(self):
        """Do we get an out of order naming warning."""
        self.assertIn(
            ("WARNING: Parameters out of order ``name2`` "
             "should be after ``name``"),
            self.warning)

    def test_missing_lookup_name(self):
        """Warning when missing a lookup key in parameter file."""
        self.assertIn(
            ("WARNING: No field definition for ``lookup_key_name`` found in "),
            self.warning)

    def test_missing_field(self):
        """Warning when missing type field in parameter file."""
        self.assertIn(
            ("WARNING: Failure on key: name, values: " +
             "OrderedDict([('description'," +
             " 'name_1 is missing type field.\\n'), ('in', 'body')," +
             " ('required', True)]). " +
             "'NoneType' object has no attribute 'split'"),
            self.warning)

    def test_invalid_parameter_definition(self):
        """Warning when parameter definition is invalid."""
        self.assertIn(
            ("WARNING: Invalid parameter definition ``invalid_name``. " +
             "Expected format: ``name: reference``. "),
            self.warning)

    def test_empty_parameter_file(self):
        """Warning when parameter file exists but is empty."""
        self.assertIn(
            ("WARNING: Parameters file is empty"),
            self.warning)

    def test_no_parameters_set(self):
        """Error when parameters are not set in rest_parameters stanza."""
        self.assertIn(
            ("No parameters defined\n\n.." +
             " rest_parameters:: parameters.yaml"),
            self.warning)

    def test_parameter_file_not_exist(self):
        """Error when parameter file does not exist"""
        self.assertIn(
            ("No parameters defined\n\n.." +
             " rest_parameters:: no_parameters.yaml"),
            self.warning)

    def test_missing_path_parameter_in_stanza(self):
        """Warning when path param not found in rest_parameter stanza."""

        self.assertIn(
            ("WARNING: No path parameter ``b_id`` found in" +
             " rest_parameter stanza.\n"),
            self.warning)
