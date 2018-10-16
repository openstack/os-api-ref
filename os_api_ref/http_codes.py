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

from docutils import nodes
from docutils.parsers.rst.directives.tables import Table
from docutils.statemachine import ViewList
from six.moves.http_client import responses
from sphinx.util import logging
import yaml

LOG = logging.getLogger(__name__)

# cache for file -> yaml so we only do the load and check of a yaml
# file once during a sphinx processing run.
HTTP_YAML_CACHE = {}


class HTTPResponseCodeDirective(Table):

    headers = ["Code", "Reason"]

    status_types = ("success", "error")

    # This is for HTTP response codes that OpenStack may use that are not part
    # the httplib response dict.
    CODES = {
        429: "Too Many Requests",
    }

    required_arguments = 2

    def __init__(self, *args, **kwargs):
        self.CODES.update(responses)
        super(HTTPResponseCodeDirective, self).__init__(*args, **kwargs)

    def _load_status_file(self, fpath):
        global HTTP_YAML_CACHE
        if fpath in HTTP_YAML_CACHE:
            return HTTP_YAML_CACHE[fpath]

        # LOG.info("Fpath: %s" % fpath)
        try:
            with open(fpath, 'r') as stream:
                lookup = yaml.safe_load(stream)
        except IOError:
            LOG.warning(
                "Parameters file %s not found" % fpath,
                (self.env.docname, None))
            return
        except yaml.YAMLError as exc:
            LOG.warning(exc)
            raise

        HTTP_YAML_CACHE[fpath] = lookup
        return lookup

    def run(self):
        self.env = self.state.document.settings.env

        # Make sure we have some content, which should be yaml that
        # defines some parameters.
        if not self.content:
            error = self.state_machine.reporter.error(
                'No parameters defined',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        if not len(self.arguments) >= 2:
            error = self.state_machine.reporter.error(
                '%s' % self.arguments,
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        _, status_defs_file = self.env.relfn2path(self.arguments.pop())
        status_type = self.arguments.pop()

        self.status_defs = self._load_status_file(status_defs_file)

        # LOG.info("%s" % str(self.status_defs))

        if status_type not in self.status_types:
            error = self.state_machine.reporter.error(
                'Type %s is not one of %s' % (status_type, self.status_types),
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        self.yaml = self._load_codes()

        self.max_cols = len(self.headers)
        # TODO(sdague): it would be good to dynamically set column
        # widths (or basically make the colwidth thing go away
        # entirely)
        self.options['widths'] = [30, 70]
        self.col_widths = self.get_column_widths(self.max_cols)
        if isinstance(self.col_widths, tuple):
            # In docutils 0.13.1, get_column_widths returns a (widths,
            # colwidths) tuple, where widths is a string (i.e. 'auto').
            # See https://sourceforge.net/p/docutils/patches/120/.
            self.col_widths = self.col_widths[1]
        # Actually convert the yaml
        title, messages = self.make_title()
        # LOG.info("Title %s, messages %s" % (title, messages))
        table_node = self.build_table()
        self.add_name(table_node)

        title_block = nodes.title(
            text=status_type.capitalize())

        section = nodes.section(ids=title_block)
        section += title_block
        section += table_node

        return [section] + messages

    def _load_codes(self):
        content = "\n".join(self.content)
        parsed = yaml.safe_load(content)

        new_content = list()

        for item in parsed:
            if isinstance(item, int):
                new_content.append((item, self.status_defs[item]['default']))
            else:
                try:
                    for code, reason in item.items():
                        new_content.append(
                            (code, self.status_defs[code][reason])
                        )
                except KeyError:
                    LOG.warning(
                        "Could not find %s for code %s" % (reason, code))
                    new_content.append(
                        (code, self.status_defs[code]['default']))

        return new_content

    def build_table(self):
        table = nodes.table()
        tgroup = nodes.tgroup(cols=len(self.headers))
        table += tgroup

        # TODO(sdague): it would be really nice to figure out how not
        # to have this stanza, it kind of messes up all of the table
        # formatting because it doesn't let tables just be the right
        # size.
        tgroup.extend(
            nodes.colspec(colwidth=col_width, colname='c' + str(idx))
            for idx, col_width in enumerate(self.col_widths)
        )

        thead = nodes.thead()
        tgroup += thead

        row_node = nodes.row()
        thead += row_node
        row_node.extend(nodes.entry(h, nodes.paragraph(text=h))
                        for h in self.headers)

        tbody = nodes.tbody()
        tgroup += tbody

        rows, groups = self.collect_rows()
        tbody.extend(rows)
        table.extend(groups)

        return table

    def add_col(self, node):
        entry = nodes.entry()
        entry.append(node)
        return entry

    def add_desc_col(self, value):
        entry = nodes.entry()
        result = ViewList(value.split('\n'))
        self.state.nested_parse(result, 0, entry)
        return entry

    def collect_rows(self):
        rows = []
        groups = []
        try:
            # LOG.info("Parsed content is: %s" % self.yaml)
            for code, desc in self.yaml:

                h_code = http_code()
                h_code['code'] = code
                h_code['title'] = self.CODES.get(code, 'Unknown')

                trow = nodes.row()
                trow += self.add_col(h_code)
                trow += self.add_desc_col(desc)
                rows.append(trow)
        except AttributeError as exc:
            # if 'key' in locals():
            LOG.warning("Failure on key: %s, values: %s. %s" %
                        (code, desc, exc))
            # else:
            #     rows.append(self.show_no_yaml_error())
        return rows, groups


def http_code_html(self, node):
    tmpl = "<code>%(code)s - %(title)s</code>"
    self.body.append(tmpl % node)
    raise nodes.SkipNode


class http_code(nodes.Part, nodes.Element):
    """Node for http_code stanza

    Because we need to insert very specific HTML at the final stage of
    processing, the http_code stanza needs a custom node type. This
    lets us accumulate the relevant data into this node, during
    parsing, but not turn it into known sphinx types (lists, tables,
    sections).

    Then, during the final build phase we transform directly to the
    html that we want.

    NOTE: this means we error trying to build latex or man pages for
    these stanza types right now. This is all fixable if we add an
    output formatter for this node type, but it's not yet a
    priority. Contributions welcomed.
    """
    pass
