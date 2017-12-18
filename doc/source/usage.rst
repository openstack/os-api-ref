Usage
=====

``os-api-ref`` is designed to be used inside of a sphinx tree that is
devoted solely to the documentation of the API.

Modify your ``source/conf.py`` file to include ``os_api_ref`` in the
list of sphinx extensions. This extension assumes you are also using
``openstackdocstheme`` for some of the styling, and may not fully work if you
are not.

.. code-block:: python

   # Add any Sphinx extension module names here, as strings. They can be
   # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.

   extensions = [
       'os_api_ref',
   ]


Stanzas
=======

rest_method
-----------

The ``rest_method`` stanza is a way to declare that a section is about
a particular REST method. It takes the form of:

.. code-block:: rst

   .. rest_method:: <METHODNAME> <url>

``METHODNAME`` should be one of the commonly used REST methods or HTTP verbs.
This stanza should be the first element in a ``section`` that has some
descriptive title about the method. An example from the Nova
documentation is:

.. code-block:: rst

   List Servers
   ============

   .. rest_method:: GET /v2.1/{tenant_id}/servers

   Lists IDs, names, and links for all servers.


   Servers contain a status attribute that indicates the current server
   state. You can filter on the server status when you complete a list
   servers request. The server status is returned in the response
   body. The possible server status values are:

   ...

This is going to do a slightly unexpected transform where the
``rest_method`` is pivoted up and into the section title to produce an
HTML line of the form: <METHOD> <URL> <SECTIONTITLE> <SHOW/HIDE
BUTTON>.

The entire contents of the ``List Servers`` section will then be
hidden by default, with a button to open it on demand.

rest_parameters
---------------

The ``rest_parameters`` stanza is a solution to the problem of tables
in ``rst``.

A REST API that uses JSON has a large number of structured parameters
that include type, location (i.e. is this in the query, the header,
the path, the body), whether or not this parameter is required, as well as
the desire to provide a long description about each parameter. And, assuming
some consistent modeling, that parameter will show up in multiple calls. A
``server_id`` used in the path is always going to have the same
meaning.

It is natural to want to display this data in a tabular way to show
all these dimensions. However, tables in ``rst`` are quite cumbersome, and
repeating the same data over and over again is error prone.

The ``rest_parameters`` stanza solves this by having the inline markup
be a yaml list of ``name: value`` pairs. ``name`` is the name of the
parameter. ``value`` is the key to lookup the rest of the details for
this parameter in a parameters file.  In each method,
there should be one ``rest_parameters`` stanza for the request, and
another ``rest_parameters`` stanza for the response.

.. code-block:: rst

   .. rest_parameters:: parameters.yaml

      - tenant_id: tenant_id
      - changes-since: changes-since
      - image: image_query
      - flavor: flavor_query
      - name: server_name_query
      - status: server_status_query
      - host: host_query
      - limit: limit
      - marker: marker

And corresponding entries in ``parameters.yaml``:

.. code-block:: yaml

   tenant_id:
     description: |
       The UUID of the tenant in a multi-tenancy cloud.
     in: path
     required: true
     type: string
   ...
   changes-since:
     description: |
       Filters the response by a date and time when the image last changed status.
       Use this query parameter to check for changes since a previous request rather
       than re-downloading and re-parsing the full status at each polling interval.
       If data has changed, the call returns only the items changed since the ``changes-since``
       time. If data has not changed since the ``changes-since`` time, the call returns an
       empty list.\nTo enable you to keep track of changes, this filter also displays images
       that were deleted if the ``changes-since`` value specifies a date in the last 30 days.
       Items deleted more than 30 days ago might be returned, but it is not guaranteed.
       The date and time stamp format is `ISO 8601 <https://en.wikipedia.org/wiki/ISO_8601>`_:

       ::

          CCYY-MM-DDThh:mm:ss±hh:mm

       The ``±hh:mm`` value, if included, returns the time zone as an offset from UTC.
       For example, ``2015-08-27T09:49:58-05:00``.
       If you omit the time zone, the UTC time zone is assumed.
     in: query
     required: false
     type: string
   server_status_query:
     description: |
       Filters the response by a server status, as a string. For example, ``ACTIVE``.
     in: query
     required: false
     type: string

Every ``rest_parameters`` stanza specifies the lookup file it will
use. This gives you the freedom to decide how you would like to split
up your parameters, ranging from a single global file, to a dedicated
file for every stanza, or anywhere in between.

parameters file format
----------------------

The parameters file is inspired by the OpenAPI (aka: Swagger)
specification.  The OpenAPI specification provides a property object
which categorizes the parameters by type and describes how the parameter is used.
The following fields exist for every entry:

in
  where this parameter exists. One of ``header``, ``path``,
  ``query``, ``body``.

description
  a free form description of the parameter. This can be
  multiline (if using the | or > tags in yaml), and supports ``rst``
  format syntax.

required
  whether this parameter is required or not. If ``required:
  false`` the parameter name will be rendered with an (Optional)
  keyword next to it

type
  the javascript/json type of the field. one of ``boolean``, ``int``,
  ``float``, ``string``, ``uuid``, ``array``, ``object``.

min_version
  the microversion that this parameter was introduced at. Will render
  a *new in $version* stanza in the html output.

max_version
  the last version that includes this parameter. Will render
  a *Available until $version* stanza in the html output.


rest_status_code
----------------

The ``rest_status_code`` stanza is how you can show what HTTP status codes your
API uses and what they indicate.

.. code-block:: rst

   .. rest_status_code:: <success|error> <location of http-status.yaml file>

This stanza should be the first element after the narrative section of the
method description.

An example from the Designate documentation is:

.. code-block:: rst
   :emphasize-lines: 11-25

   Create Zone
   ===========

   .. rest_method::  POST /v2/zones

   Create a zone

   Response codes
   --------------

   .. rest_status_code:: success status.yaml

      - 200
      - 100
      - 201


   .. rest_status_code:: error status.yaml

      - 405
      - 403
      - 401
      - 400
      - 500
      - 409: duplicate_zone

And corresponding entries in ``http-status.yaml``:

.. code-block:: yaml

    100:
      default: |
        An unusual code for an API
    200:
      default: |
        Request was successful.
    201:
      default: >
        Request has been fulfilled and new resource created. The ``Location`` header
        has the URL to the new item.
    400:
      default: |
        Some content in the request was invalid
      zone_data_error: |
        Some of the data for the zone in the request is unavailable to the service.
    401:
      default: |
        User must authenticate before making a request.
    403:
      default: |
         Policy does not allow current user to do this operation.
    405:
      default: |
        Method is not valid for this endpoint and resource.
    409:
     default: |
        This resource has an action in progress that would conflict with this request.
     duplicate_zone: |
        There is already a zone with this name.
    500:
      default: |
        Something went wrong with the service which prevents it from fulfilling the request.

This RST example creates two HTML tables of response codes, one for success and one for
errors.

status file format
------------------

This is a simple yaml file, with a single object of status codes and the
reasons that each would be used.

Each status code **must** have a default entry in the status yaml file. The default entry is used
in the ``rest_status_code`` stanza when a code is listed with no value or lookup key.

There may be situations where the reason for a code may be different across
endpoints, or a different message may be appropriate.

In this case, adding a entry at the same level as the ``default`` and
referencing that in the stanza like so:

.. code-block:: yaml

   - 409: duplicate_zone

This will override the default message with the newly defined one.

You can get a copy of a starter status file from the os-api-ref repository,
by downloading :download:`http-status.yaml <http-status.yaml>`.

rest_expand_all
---------------

The ``rest_expand_all`` stanza is used to place a control in the
document that will be a global Show / Hide for all sections. There are
times when this is extremely nice to have.


Including Sample Files
======================

To refer to a sample file in a ``rst`` file, use the
``rst`` directive, ``literalinclude``. Typically, the content sent
or received is of type JSON, so the language role is set to javascript.
The example immediately follows the parameter listing in the ``rst`` file.
An example of an included Nova response sample file:

.. code-block:: rst

   .. literalinclude:: ../../doc/api_samples/os-evacuate/server-evacuate-resp.json
      :language: javascript


Runtime Warnings
================

The extension tries to help when it can by pointing out that something isn't
matching up correctly. The following warnings are generated when
issues are found:

* parameters file is not found
* parameters file is not valid yaml, i.e.
  missing colon after the name
* a lookup value in the ``rst`` file is not found in the parameters file
* the parameters file is not sorted as outlined in the rules below

The sorting rules for parameters file is that first elements should be
sorted by ``in``, going from earliest to latest processed.

#. header
#. path
#. query
#. body

After that, the parameters should be sorted by name, lower case alpha
numerically.

The sort enforcement is because in large parameters files it helps
prevent unintended duplicates.
