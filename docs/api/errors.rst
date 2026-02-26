Errors
======

All SDK errors inherit from :class:`~etoropy.EToroError`:

.. code-block:: text

   EToroError
     +-- EToroApiError           # HTTP 4xx/5xx
     |     +-- EToroRateLimitError   # HTTP 429
     +-- EToroAuthError          # HTTP 401/403 or WS auth failure
     +-- EToroValidationError    # Invalid input
     +-- EToroWebSocketError     # WS connection/protocol errors

EToroError
----------

.. autoclass:: etoropy.EToroError
   :members:
   :show-inheritance:

EToroApiError
-------------

.. autoclass:: etoropy.EToroApiError
   :members:
   :show-inheritance:

EToroRateLimitError
-------------------

.. autoclass:: etoropy.EToroRateLimitError
   :members:
   :show-inheritance:

EToroAuthError
--------------

.. autoclass:: etoropy.EToroAuthError
   :members:
   :show-inheritance:

EToroValidationError
--------------------

.. autoclass:: etoropy.EToroValidationError
   :members:
   :show-inheritance:

EToroWebSocketError
-------------------

.. autoclass:: etoropy.EToroWebSocketError
   :members:
   :show-inheritance:
