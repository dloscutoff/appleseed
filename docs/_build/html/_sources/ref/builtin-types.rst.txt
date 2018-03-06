
Built-in types
==============

Appleseed has six data types built in: :data:`Int`, :data:`Bool`, :data:`List`, :data:`String`, :data:`Object`, and :data:`Builtin`.

.. data:: Int

   Type for integers. Examples: ``0``, ``42``, ``-5``
   
.. data:: Bool

   Type for truth values ``true`` and ``false``.

.. data:: List

   Type for lists of zero or more elements. The empty list ``()`` is also called *nil*. All non-empty lists can be analyzed as some value (the *head*) *cons*'ed to a shorter list (the *tail*). List elements may be of any type, including other lists. Examples: ``()``, ``(1 2 3)``, ``(a (b c) (d (e f ())))``

.. data:: String

   Type for strings. Unquoted strings in code, such as ``add``, are interpreted as names and looked up in the local or global symbol tables. To get a literal string, quote the token like ``(q add)`` or surround it in double quotes like ``"add"``. Double-quoted strings support escape sequences ``\"``, ``\\``, and ``\n``.
   
.. data:: Object

   Type for objects, sets of name-value pairs. Example: ``(object (type Fraction) (numerator 3) (denominator 4))``

.. data:: Builtin

   Type for :doc:`built-in functions and macros <builtins>`.
   