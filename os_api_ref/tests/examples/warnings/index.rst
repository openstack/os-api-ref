.. rest_expand_all::

I am text, hear me roar!

==============
 List Servers
==============

.. rest_method:: GET /servers

.. rest_parameters:: parameters.yaml

   - name: name
   - name: lookup_key_name
   - name: name_1
   - invalid_name


No Parameters Specified
-----------------------

.. rest_parameters:: parameters.yaml



Empty File and Parameters Specified
-----------------------------------

.. rest_parameters:: empty_parameters_file.yaml

   - name: name

Nonexistent Parameter File
--------------------------

.. rest_parameters:: no_parameters.yaml


Check missing path parameters in stanza
---------------------------------------

.. rest_method:: GET /server/{server_id}/{new_id}/{new_id2}

.. rest_parameters:: parameters.yaml

   - server_id: server_id

Check another missing path parameters in stanza
-----------------------------------------------

.. rest_method:: GET /server/{b_id}/{c_id2}/{server_id}

.. rest_parameters:: parameters.yaml

   - server_id: server_id
