.. rest_expand_all::

I am text, hear me roar!

==============
 List Servers
==============

.. rest_method:: GET /servers

.. rest_parameters:: parameters.yaml

   - name: name

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
   - 409: duplcate_zone
