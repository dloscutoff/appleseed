
Appleseed builtins
==================

These functions and macros are built in to the Appleseed interpreter. All of them, unlike library functions and macros, have type :data:`Builtin`.

Arithmetic
----------

.. data:: add

   Adds two numbers. Arguments must be :data:`Int` or :data:`Bool`; returns :data:`Int`.

.. data:: sub

   Subtracts two numbers. Arguments must be :data:`Int` or :data:`Bool`; returns :data:`Int`.

.. data:: mul

   Multiplies two numbers. Arguments must be :data:`Int` or :data:`Bool`; returns :data:`Int`.

.. data:: div

   Divides two numbers. Note that this is integer division, rounding down: ``(div 5 3)`` is ``1``; ``(div -5 3)`` is ``-2``. Arguments must be :data:`Int` or :data:`Bool`; returns :data:`Int`. Errors if the second argument is ``0`` (or ``false``).

.. data:: mod

   Takes two numbers; returns its first argument modulo its second. Follows the same rules as Python regarding negative arguments: the return value is constrained to be between the second argument (exclusive) and zero (inclusive). As a result, ``(add (mul (div a b) b) (mod a b))`` is always equal to ``a``. Arguments must be :data:`Int` or :data:`Bool`; returns :data:`Int`. Errors if the second argument is ``0`` (or ``false``).

Lists
-----

* cons
* head
* tail

Strings
-------

* str
* chars
* repr

Objects
-------

* object
* has-property
* get-property
* copy

Booleans and conditionals
-------------------------

* bool
* if
* less?
* equal?

Other
-----

* q
* eval
* type
* def
* load
* debug

REPL only
---------

* help
* restart
* quit
