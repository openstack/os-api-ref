Usage
========

``os-api-ref`` is designed to be used inside of a sphinx tree that is
devoted solely to the documentation of the API.

Modify your ``source/conf.py`` file to include ``os_api_ref`` in the
list of sphinx extensions. This extension assumes you are also using
``oslosphinx`` for some of the styling, and may not fully work if you
are not.

.. code-block:: python

   # Add any Sphinx extension module names here, as strings. They can be
   # extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.

   extensions = [
       'os_api_ref',
       'oslosphinx',
   ]


Stanzas
=======

rest_method
-----------

The ``rest_method`` stanza is a way to declare that a section is about
a particular REST method. It takes the form of:

.. code-block:: rst

   .. rest_method:: <METHODNAME> <url>

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
