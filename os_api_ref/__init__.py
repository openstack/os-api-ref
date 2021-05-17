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

from collections import OrderedDict
import hashlib
import os
import re

from docutils import nodes
from docutils.parsers import rst
from docutils.parsers.rst.directives.tables import Table
from docutils.statemachine import ViewList
import pbr.version
import six
from sphinx.util import logging
from sphinx.util.osutil import copyfile
import yaml

from os_api_ref.http_codes import http_code
from os_api_ref.http_codes import http_code_html
from os_api_ref.http_codes import HTTPResponseCodeDirective

__version__ = pbr.version.VersionInfo(
    'os_api_ref').version_string()

LOG = logging.getLogger(__name__)

"""This provides a sphinx extension able to create the HTML needed
for the api-ref website.

It contains 2 new stanzas.

  .. rest_method:: GET /foo/bar

Which is designed to be used as the first stanza in a new section to
state that section is about that REST method. During processing the
rest stanza will be reparented to be before the section in question,
and used as a show/hide selector for it's details.

  .. rest_parameters:: file.yaml

     - name1: name_in_file1
     - name2: name_in_file2
     - name3: name_in_file3

Which is designed to build structured tables for either response or
request parameters. The stanza takes a value which is a file to lookup
details about the parameters in question.

The contents of the stanza are a yaml list of key / value pairs. The
key is the name of the parameter to be shown in the table. The value
is the key in the file.yaml where all other metadata about the
parameter will be extracted. This allows for reusing parameter
definitions widely in API definitions, but still providing for control
in both naming and ordering of parameters at every declaration.

"""


def ordered_load(
        stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
    """Load yaml as an ordered dict

    This allows us to inspect the order of the file on disk to make
    sure it was correct by our rules.
    """
    class OrderedLoader(Loader):
        pass

    def construct_mapping(loader, node):
        loader.flatten_mapping(node)
        return object_pairs_hook(loader.construct_pairs(node))

    OrderedLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping)
    # for parameters.yaml we treat numbers (especially version
    # numbers) as strings. So that microversion specification of 2.20
    # and 2.2 don't get confused.
    OrderedLoader.add_constructor(
        u'tag:yaml.org,2002:float',
        yaml.constructor.SafeConstructor.construct_yaml_str)

    return yaml.load(stream, OrderedLoader)


class rest_method(nodes.Part, nodes.Element):
    """Node for rest_method stanza

    Because we need to insert very specific HTML at the final stage of
    processing, the rest_method stanza needs a custom node type. This
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


class rest_expand_all(nodes.Part, nodes.Element):
    """A node placeholder for the expand all button.

    This is a node that we can insert into the doctree which on final
    render can be converted to the custom HTML we need for the expand
    all button. It is automatically inserted at the top of the page
    for API ref documents.
    """
    pass


class RestExpandAllDirective(rst.Directive):
    # This tells sphinx that the directive will need to generate
    # content during the final build phase.
    has_content = True

    def run(self):
        app = self.state.document.settings.env.app
        node = rest_expand_all()
        max_ver = app.config.os_api_ref_max_microversion
        min_ver = app.config.os_api_ref_min_microversion
        releases = app.config.os_api_ref_release_microversions
        node['major'] = None
        try:
            if max_ver.split('.')[0] == min_ver.split('.')[0]:
                node['max_ver'] = int(max_ver.split('.')[1])
                node['min_ver'] = int(min_ver.split('.')[1])
                node['major'] = int(max_ver.split('.')[0])
                node['releases'] = releases
        except ValueError:
            # TODO(sdague): warn that we're ignoring this all
            pass
        except IndexError:
            pass
        return [node]


class RestMethodDirective(rst.Directive):

    # this enables content in the directive
    has_content = True

    @staticmethod
    def find_param(content, name):
        for line in content:
            if ("%s: " % name) in line:
                _, value = line.split(': ')
                return value.rstrip().lstrip()
        return None

    def run(self):
        lineno = self.state_machine.abs_line_number()
        target = nodes.target()
        section = nodes.section(classes=["detail-control"])

        node = rest_method()

        # TODO(sdague): this is a super simplistic parser, should be
        # more robust.
        method, sep, url = self.content[0].partition(' ')
        node['min_version'] = self.find_param(self.content, 'min_version')
        node['max_version'] = self.find_param(self.content, 'max_version')

        node['method'] = method
        node['url'] = url

        # Extract the path parameters from the url
        env = self.state.document.settings.env
        env.path_params = []
        env.path_params = re.findall("{[a-zA-Z][a-zA-Z_0-9]*}", url)

        node['target'] = self.state.parent.attributes['ids'][0]
        node['css_classes'] = ""
        if node['min_version']:
            node['css_classes'] += "rp_min_ver_%s " % (
                str(node['min_version']).replace('.', '_'))
        if node['max_version']:
            node['css_classes'] += "rp_max_ver_%s " % (
                str(node['max_version']).replace('.', '_'))

        # We need to build a temporary target that we can replace
        # later in the processing to get the TOC to resolve correctly.
        # SHA-1 is used even if collisions are possible, because
        # they are still unlikely to occurr and it is way shorter
        # than stronger SHAs.
        node_hash = hashlib.sha1(str(node).encode('utf-8')).hexdigest()
        temp_target = "%s-%s-selector" % (node['target'], node_hash)
        target = nodes.target(ids=[temp_target])
        self.state.add_target(temp_target, '', target, lineno)
        section += node

        return [target, section]


# cache for file -> yaml so we only do the load and check of a yaml
# file once during a sphinx processing run.
YAML_CACHE = {}


class RestParametersDirective(Table):

    headers = ["Name", "In", "Type", "Description"]

    def _load_param_file(self, fpath):
        global YAML_CACHE
        if fpath in YAML_CACHE:
            return YAML_CACHE[fpath]

        lookup = {}
        try:
            with open(fpath, 'r') as stream:
                lookup = ordered_load(stream)
        except IOError:
            LOG.warning("Parameters file not found, %s", fpath,
                        location=(self.env.docname, None))
            return
        except yaml.YAMLError as exc:
            LOG.exception(exc_info=exc)
            raise

        if lookup:
            self._check_yaml_sorting(fpath, lookup)
        else:
            LOG.warning("Parameters file is empty, %s", fpath,
                        location=(self.env.docname, None))
            return

        YAML_CACHE[fpath] = lookup
        return lookup

    def _check_yaml_sorting(self, fpath, yaml_data):
        """check yaml sorting

        Assuming we got an ordered dict, we iterate through it
        basically doing a gnome sort test
        (https://en.wikipedia.org/wiki/Gnome_sort) and ensure the item
        we are looking at is > the last item we saw. This is done at
        the section level first, so we're grouped, then alphabetically
        by lower case name within a section. Every time there is a
        mismatch we raise an warn message.
        """
        sections = {"header": 1, "path": 2, "query": 3, "body": 4}

        last = None
        for key, value in yaml_data.items():
            if not isinstance(value, dict):
                raise Exception('Expected a dict for {0}; got {0}={1}).\n'
                                'You probably have indentation typo in your'
                                'YAML source'.format(key, value))

            # use of an invalid 'in' value
            if value['in'] not in sections:
                LOG.warning("``%s`` is not a valid value for 'in' (must be "
                            "one of: %s). (see ``%s``)",
                            value['in'],
                            ", ".join(sorted(sections.keys())),
                            key)
                continue

            if last is None:
                last = (key, value)
                continue
            # ensure that sections only go up
            current_section = value['in']
            last_section = last[1]['in']
            if sections[current_section] < sections[last_section]:
                LOG.warning("Section out of order. All parameters in section "
                            "``%s`` should be after section ``%s``. (see "
                            "``%s``)", last_section, current_section, last[0])
            if (sections[value['in']] == sections[last[1]['in']] and
                key.lower() < last[0].lower()):
                LOG.warning("Parameters out of order ``%s`` should be after "
                            "``%s``", last[0], key)
            last = (key, value)

    def yaml_from_file(self, fpath):
        """Collect Parameter stanzas from inline + file.

        This allows use to reference an external file for the actual
        parameter definitions.
        """

        lookup = self._load_param_file(fpath)
        if not lookup:
            return

        content = "\n".join(self.content)
        parsed = yaml.safe_load(content)
        new_content = list()
        for paramlist in parsed:
            if not isinstance(paramlist, dict):
                location = (self.state_machine.node.source,
                            self.state_machine.node.line)
                LOG.warning("Invalid parameter definition ``%s``. Expected "
                            "format: ``name: reference``. Skipping.",
                            paramlist, location=location)
                continue
            for name, ref in paramlist.items():
                if ref in lookup:
                    new_content.append((name, lookup[ref]))
                else:
                    # TODO(sdague): this provides a kind of confusing
                    # error message because app.warn isn't meant to be
                    # used this way, however it does provide a way to
                    # track down where the parameters list is that is
                    # wrong. So it's good enough for now.
                    location = (self.state_machine.node.source,
                                self.state_machine.node.line)
                    LOG.warning("No field definition for ``%s`` found in "
                                "``%s``. Skipping.", ref, fpath)

                # Check for path params in stanza
                for i, param in enumerate(self.env.path_params):
                    if (param.rstrip('}').lstrip('{')) == name:
                        del self.env.path_params[i]
                        break
                    else:
                        continue

        if len(self.env.path_params) != 0:
            # Warn that path parameters are not set in rest_parameter
            # stanza and will not appear in the generated table.
            for param in self.env.path_params:
                location = (self.state_machine.node.source,
                            self.state_machine.node.line)
                LOG.warning("No path parameter ``%s`` found in rest_parameter"
                            " stanza.\n", param.rstrip('}').lstrip('{'))

        self.yaml = new_content

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

        if not len(self.arguments) >= 1:
            error = self.state_machine.reporter.error(
                'No reference file defined',
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]

        # NOTE(sdague): it's important that we pop the arg otherwise
        # we end up putting the filename as the table caption.
        rel_fpath, fpath = self.env.relfn2path(self.arguments.pop())
        self.yaml_file = fpath
        self.yaml_from_file(self.yaml_file)

        self.max_cols = len(self.headers)
        # TODO(sdague): it would be good to dynamically set column
        # widths (or basically make the colwidth thing go away
        # entirely)
        self.options['widths'] = [20, 10, 10, 60]
        self.col_widths = self.get_column_widths(self.max_cols)
        if isinstance(self.col_widths, tuple):
            # In docutils 0.13.1, get_column_widths returns a (widths,
            # colwidths) tuple, where widths is a string (i.e. 'auto').
            # See https://sourceforge.net/p/docutils/patches/120/.
            self.col_widths = self.col_widths[1]
        # Actually convert the yaml
        title, messages = self.make_title()
        table_node = self.build_table()
        self.add_name(table_node)
        if title:
            table_node.insert(0, title)
        return [table_node] + messages

    def get_rows(self, table_data):
        rows = []
        groups = []
        trow = nodes.row()
        entry = nodes.entry()
        para = nodes.paragraph(text=six.u(table_data))
        entry += para
        trow += entry
        rows.append(trow)
        return rows, groups

        # Add a column for a field. In order to have the RST inside
    # these fields get rendered, we need to use the
    # ViewList. Note, ViewList expects a list of lines, so chunk
    # up our content as a list to make it happy.
    def add_col(self, value):
        entry = nodes.entry()
        result = ViewList(value.split('\n'))
        self.state.nested_parse(result, 0, entry)
        return entry

    def show_no_yaml_error(self):
        trow = nodes.row(classes=["no_yaml"])
        trow += self.add_col("No yaml found %s" % self.yaml_file)
        trow += self.add_col("")
        trow += self.add_col("")
        trow += self.add_col("")
        return trow

    def collect_rows(self):
        rows = []
        groups = []
        try:
            for key, values in self.yaml:
                min_version = values.get('min_version', '')
                max_version = values.get('max_version', '')
                desc = values.get('description', '')
                classes = []
                if min_version:
                    desc += ("\n\n**New in version %s**\n" % min_version)
                    min_ver_css_name = ("rp_min_ver_" +
                                        str(min_version).replace('.', '_'))
                    classes.append(min_ver_css_name)
                if max_version:
                    desc += ("\n\n**Available until version %s**\n" %
                             max_version)
                    max_ver_css_name = ("rp_max_ver_" +
                                        str(max_version).replace('.', '_'))
                    classes.append(max_ver_css_name)
                trow = nodes.row(classes=classes)
                name = key
                if values.get('required', False) is False:
                    name += " (Optional)"
                trow += self.add_col(name)
                trow += self.add_col(values.get('in'))
                trow += self.add_col(values.get('type'))
                trow += self.add_col(desc)
                rows.append(trow)
        except AttributeError as exc:
            if 'key' in locals():
                LOG.warning("Failure on key: %s, values: %s. %s",
                            key, values, exc)
            else:
                rows.append(self.show_no_yaml_error())
        return rows, groups

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


def rest_method_html(self, node):
    tmpl = """
<div class="operation-grp %(css_classes)s">
<div class="row">
    <div class="col-md-2">
    <div class="operation">
    <a name="%(target)s" class="operation-anchor" href="#%(target)s"
      onclick="window.location.hash = hash;"
      >
      <span class="glyphicon glyphicon-link"></span></a>
    <span class="label label-%(method)s">%(method)s</span>
    </div>
    </div>
    <div class="col-md-9">
    <div class="row">
        <div class="endpoint-container">
        <div class="row col-md-12">%(url)s</div>
        <div class="row col-md-12"><p class="url-subtitle">%(desc)s</p></div>
        </div>
    </div>
    </div>
    <div class="col-md-1">
    <button
       class="btn btn-info btn-sm btn-detail"
       data-target="#%(target)s-detail"
       data-toggle="collapse"
       id="%(target)s-detail-btn"
       >detail</button>
    </div>
</div>
</div>"""

    node['url'] = node['url'].replace(
        '{',
        '<span class="path_parameter">{')
    node['url'] = node['url'].replace(
        '}',
        '}</span>')

    self.body.append(tmpl % node)
    raise nodes.SkipNode


def rest_expand_all_html(self, node):
    tmpl = """
<div class="row">
%(extra_js)s
<div class="col-md-2 col-md-offset-9">
%(selector)s
</div>
<div class=col-md-1>
    <button id="expand-all"
       data-toggle="collapse"
       class="btn btn-info btn-sm btn-expand-all"
    >Show All</button>
</div>
</div>"""

    node.setdefault('selector', "")
    node.setdefault('extra_js', "")

    if node['major']:
        node['selector'], node['extra_js'] = create_mv_selector(node)

    self.body.append(tmpl % node)
    raise nodes.SkipNode


def create_mv_selector(node):

    mv_list = '<option value="" selected="selected">All</option>'

    for x in range(node['min_ver'], node['max_ver'] + 1):
        mv_list += build_mv_item(node['major'], x, node['releases'])

    selector_tmpl = """
<form class=form-inline">
<div class="form-group">
<label class="control-label">
Microversions
</label>
<select class="combobox form-control" id="mv_select">
    %(mv_list)s
</select>
</div>
</form>
"""

    js_tmpl = """
<script>
    os_max_mv = %(max)d;
    os_min_mv = %(min)d;
</script>
"""

    selector_content = {
        'mv_list': mv_list
    }

    js_content = {
        'min': node['min_ver'],
        'max': node['max_ver']
    }

    return selector_tmpl % selector_content, js_tmpl % js_content


def build_mv_item(major, micro, releases):
    version = "%d.%d" % (major, micro)
    if version in releases:
        return '<option value="%s">%s - %s</option>' % (
            version, version, releases[version].capitalize())
    else:
        return '<option value="%s">%s</option>' % (version, version)


def resolve_rest_references(app, doctree):
    for node in doctree.traverse():
        if isinstance(node, rest_method):
            rest_node = node
            rest_method_section = node.parent
            rest_section = rest_method_section.parent
            gp = rest_section.parent

            # Added required classes to the top section
            rest_section.attributes['classes'].append('api-detail')
            rest_section.attributes['classes'].append('collapse')

            # Pop the title off the collapsed section
            title = rest_section.children.pop(0)
            rest_node['desc'] = title.children[0]

            # In order to get the links in the sidebar to be right, we
            # have to do some id flipping here late in the game. The
            # rest_method_section has basically had a dummy id up
            # until this point just to keep it from colliding with
            # it's parent.
            rest_section.attributes['ids'][0] = (
                "%s-detail" % rest_section.attributes['ids'][0])
            rest_method_section.attributes['ids'][0] = rest_node['target']

            # Pop the overall section into it's grand parent,
            # right before where the current parent lives
            idx = gp.children.index(rest_section)
            rest_section.remove(rest_method_section)
            gp.insert(idx, rest_method_section)


def copy_assets(app, exception):
    assets = ('api-site.css', 'api-site.js', 'combobox.js')
    fonts = (
        'glyphicons-halflings-regular.ttf',
        'glyphicons-halflings-regular.woff'
    )
    builders = ('html', 'readthedocs', 'readthedocssinglehtmllocalmedia')
    if app.builder.name not in builders or exception:
        return
    LOG.info('Copying assets: %s', ', '.join(assets))
    LOG.info('Copying fonts: %s', ', '.join(fonts))
    for asset in assets:
        dest = os.path.join(app.builder.outdir, '_static', asset)
        source = os.path.abspath(os.path.dirname(__file__))
        copyfile(os.path.join(source, 'assets', asset), dest)
    for font in fonts:
        dest = os.path.join(app.builder.outdir, '_static/fonts', font)
        source = os.path.abspath(os.path.dirname(__file__))
        copyfile(os.path.join(source, 'assets', font), dest)


def add_assets(app):
    app.add_css_file('api-site.css')
    app.add_js_file('api-site.js')
    app.add_js_file('combobox.js')


def setup(app):
    # Add some config options around microversions
    app.add_config_value('os_api_ref_max_microversion', '', 'env')
    app.add_config_value('os_api_ref_min_microversion', '', 'env')
    app.add_config_value('os_api_ref_release_microversions', '', 'env')
    # TODO(sdague): if someone wants to support latex/pdf, or man page
    # generation using these stanzas, here is where you'd need to
    # specify content specific renderers.
    app.add_node(rest_method, html=(rest_method_html, None))
    app.add_node(rest_expand_all, html=(rest_expand_all_html, None))
    app.add_node(http_code, html=(http_code_html, None))

    # This specifies all our directives that we're adding
    app.add_directive('rest_parameters', RestParametersDirective)
    app.add_directive('rest_method', RestMethodDirective)
    app.add_directive('rest_expand_all', RestExpandAllDirective)
    app.add_directive('rest_status_code', HTTPResponseCodeDirective)

    # The doctree-read hook is used do the slightly crazy doc
    # transformation that we do to get the rest_method document
    # structure.
    app.connect('doctree-read', resolve_rest_references)

    # Add all the static assets to our build during the early stage of building
    app.connect('builder-inited', add_assets)

    # This copies all the assets (css, js, fonts) over to the build
    # _static directory during final build.
    app.connect('build-finished', copy_assets)

    return {'version': __version__}
