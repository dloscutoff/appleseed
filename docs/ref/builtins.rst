
Appleseed builtins
==================

These functions and macros are built in to the Appleseed interpreter. All of them, unlike library functions and macros, have type :c:type:`Builtin`.


Arithmetic
----------

.. data:: add

   * First argument: :c:type:`Int` or :c:type:`Bool`
   * Second argument: :c:type:`Int` or :c:type:`Bool`
   * Returns: :c:type:`Int`

   Adds two numbers.

.. data:: sub

   * First argument: :c:type:`Int` or :c:type:`Bool`
   * Second argument: :c:type:`Int` or :c:type:`Bool`
   * Returns: :c:type:`Int`

   Subtracts two numbers.

.. data:: mul

   * First argument: :c:type:`Int` or :c:type:`Bool`
   * Second argument: :c:type:`Int` or :c:type:`Bool`
   * Returns: :c:type:`Int`

   Multiplies two numbers.

.. data:: div

   * First argument: :c:type:`Int` or :c:type:`Bool`
   * Second argument: :c:type:`Int` or :c:type:`Bool`
   * Returns: :c:type:`Int`
   * Errors if: second argument is ``0`` or ``false``
   
   Divides two numbers. Note that this is integer division, rounding down: ``(div 5 3)`` is ``1``; ``(div -5 3)`` is ``-2``.

.. data:: mod

   * First argument: :c:type:`Int` or :c:type:`Bool`
   * Second argument: :c:type:`Int` or :c:type:`Bool`
   * Returns: :c:type:`Int`
   * Errors if: second argument is ``0`` or ``false``

   Returns its first argument modulo its second. Follows the same rules as Python regarding negative arguments: the return value is constrained to be between the second argument (exclusive) and zero (inclusive). As a result, ``(add (mul (div a b) b) (mod a b))`` is always equal to ``a``.


Lists
-----

.. data:: cons

   * First argument: any type
   * Second argument: :c:type:`List`
   * Returns: :c:type:`List`
   
   Returns a new list with the first argument as the head and the second argument as the tail.

.. data:: head

   * Argument: :c:type:`List`
   * Returns: any type

   Returns the head (first element) of the argument, or :js:data:`nil` if the argument is an empty list.

.. data:: tail

   * Argument: :c:type:`List`
   * Returns: :c:type:`List`

   Returns a new list containing the tail (all but the first element) of the argument, or :js:data:`nil` if the argument is an empty list.


Strings
-------

.. data:: str

.. data:: chars

.. data:: repr


Objects
-------

.. data:: object

.. data:: has-property

.. data:: get-property

.. data:: copy


Booleans and conditionals
-------------------------

.. data:: bool

.. data:: if

.. data:: less?

.. data:: equal?


Other
-----

.. data:: q

.. data:: eval

.. data:: type

.. data:: def

.. data:: load

.. data:: debug


REPL only
---------

.. data:: help

.. data:: restart

.. data:: quit

