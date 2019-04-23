========================
Team and repository tags
========================

.. image:: https://governance.openstack.org/tc/badges/os-api-ref.svg
    :target: https://governance.openstack.org/tc/reference/tags/index.html

.. Change things from this point on

os-api-ref
==========

Sphinx Extensions to support API reference sites in OpenStack

This project is a collection of sphinx stanzas that assist in building
an API Reference site for an OpenStack project in RST. RST is great
for unstructured English, but displaying semi structured (and
repetitive) data in tables is not its strength. This provides tooling
to insert semi-structured data describing request and response
parameters and status or error messages, and turn those into nice tables.

The project also includes a set of styling (and javascript) that is
expected to layer on top of a Sphinx theme base. This addition
provides a nice set of collapsing sections for REST methods and
javascript controls to expand / collapse all sections.

Features
--------

* Sphinx stanza ``rest_method`` describing the method and resource for a REST
  API call. Lets authors write simply and also gives readers a clean way to
  scan all methods then click a button to get more information about a method.
* Sphinx stanza ``rest_parameters`` used to insert semi-structured data into
  the RST files describing the parameters users can send with the request. The
  stanza points to a structured YAML file, ``parameters.yaml``.
* Sphinx stanza ``rest_status_code`` used to insert pointers to error or status
  codes returned by the service. Points to a structured YAML file,
  ``http_codes.yaml``.

TODO
----

A list, in no particular order, of things we should do in this
project. If you would like to contribute to any of these please show
up in ``#openstack-dev`` on IRC and ask for ``sdague`` or ``mugsie``
to discuss or send an email to the openstack-discuss@lists.openstack.org list
with [api] in the subject line.

* Enhance documentation with more examples and best practices
* Testing for the code
* ``max_microversion`` parameter support - so that we automatically
  tag parameters that have been removed
* Make a microversion selector, so that you can get a version of the api-ref
  that hides all microversion elements beyond your selected version
  (this one is going to be a bit of complex javascript), in progress.

Potential ideas
~~~~~~~~~~~~~~~

These aren't even quite todos, but just ideas about things that might
be useful.

* ``.. literalinclude`` is good for API samples files to be included,
  but should we have more markup that includes the full ``REST /URL``
  as well.


Sphinx stanzas
--------------

**rest_method**: Enter the REST method, such as GET, PUT, POST, DELETE,
followed by the resource (not including an endpoint) for the call. For
example::

    .. rest_method:: PUT /v2/images/{image_id}/file

**rest_parameters**: Enter a reference to a ``parameters.yaml`` file and
indicate which parameter you want to document. For example::

    .. rest_parameters:: images-parameters.yaml

       - Content-type: Content-Type-data
       - image_id: image_id-in-path

Where the ``images-parameters.yaml`` file contains pointers named
``Content-type`` and ``image_id`` and descriptions for each.

**rest_status_code**: Enter a reference to a ``http-status.yaml`` file and
indicate which errors or status codes you want to document. You can also add
a pointer to more precise descriptions for each code. For example::

    .. rest_status_code:: success http-codes.yaml

      - 204

    .. rest_status_code:: error http-codes.yaml

      - 400: informal
      - 401
      - 403
      - 404
      - 409
      - 410: image-data-410
      - 413: image-data-413
      - 415: image-data-415
      - 500: informal
      - 503: image-data-503


* Free software: Apache license
* Documentation: https://docs.openstack.org/os-api-ref/latest/
* Source: https://opendev.org/openstack/os-api-ref
