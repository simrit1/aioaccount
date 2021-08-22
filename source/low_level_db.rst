Low level database
==================
.. note::
    Not recommended to be used in production.

    Currently only the 'user' table exists, providing any other
    table name will result in a error.

.. note::
    SqlWrapper & MongoWrapper are syntactically identical
    and are initialized into 'AccountHandler._db_wrapper'

SQL
^^^
.. autoclass:: aioaccount.SqlWrapper()
    :members:
    :undoc-members:

Mongo
^^^^^
.. autoclass:: aioaccount.MongoWrapper()
    :members:
    :undoc-members:
