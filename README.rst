os-api-ref
==========

Sphinx Extensions to support API reference sites in OpenStack

This project is a collection of sphinx stanzas that assist in building
an API Reference site for an OpenStack project in RST. RST is great
for unstructured English, but displaying semi structured (and
repetitive) data in tables is not it's strength. This provides tooling
to insert semi-structured data describing request and response
parameters, and turn those into nice tables.

The project also includes a set of styling (and javascript) that is
expected to layer on top of an ``oslosphinx`` theme base. This
provides a nice set of collapsing sections for REST methods and
javascript controls to expand / collapse all sections.

Features
--------

* 2 new sphinx stanzas ``rest_method`` and ``rest_parameters`` which
  support putting semi-structured data into the RST files.

TODO
----

A list, in no particular order, of things we should do in this
project. If you would like to contribute to any of these please show
up in ``#openstack-dev`` on keystone and ask for ``sdague`` to
discuss.

* Enhance documentation with examples and best practices
* Testing for the code
* ``max_microversion`` parameter support - so that we automatically
  tag parameters that have been removed
* microversion selector, so that you can get a version of the api-ref
  that hides all microversion elements beyond your selected version
  (this one is going to be a bit of complex javascript)
* make this compatible with openstackdocstheme (which is equal parts
  work here and with the openstack docs theme).

Potential ideas
~~~~~~~~~~~~~~~

These aren't even quite todos, but just ideas about things that might
be useful.

* ``.. litteralinclude`` is good for API samples files to be included,
  but should we have more markup that includes the full ``REST /URL``
  as well


Sphinx stanzas
--------------

TODO: document the details of the stanzas


* Free software: Apache license
.. * Documentation: http://docs.openstack.org/developer/os-api-ref
* Source: http://git.openstack.org/cgit/openstack/os-api-ref
