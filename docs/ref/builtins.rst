
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

   * Argument: :c:type:`List`
   * Returns: :c:type:`String`
   * Errors if: argument contains any elements that are not :c:type:`Int` or :c:type:`Bool`

   Given a list of character codes, returns a string consisting of those characters.

.. data:: chars

   * Argument: :c:type:`String`
   * Returns: :c:type:`List`

   Given a string, returns a list of its character codes (nonnegative :c:type:`Int`\ s).

.. data:: repr

   * Argument: any type
   * Returns: :c:type:`String`

   Returns a string representing the argument:

   * :c:type:`Int`: ``(repr 42)`` → ``"42"``
   * :c:type:`Bool`: ``(repr true)`` → ``"true"``
   * :c:type:`List`: ``(repr (list 1 2 ()))`` → ``"(1 2 ())"``
   * :c:type:`String`: ``(repr "xyz")`` → ``"xyz"``; ``(repr "xyz abc")`` → ``"`xyz abc`"``
   * :c:type:`Object`: ``(repr (object (type "Complex") (re 5) (im 2)))`` → ``"{(type Complex) (im 2) (re 5)}"``
   * :c:type:`Builtin`: ``(repr add)`` → ``"<builtin function add>"``; ``(repr def)`` → ``"<builtin macro def>"``


Booleans and conditionals
-------------------------

.. data:: bool

   * Argument: any type
   * Returns: :c:type:`Bool`

   Returns ``false`` if the argument is ``0``, ``false``, ``()``, ``""``, or ``{}``. Otherwise, returns ``true``.

.. data:: if

   * Macro
   * First argument: any type
   * Second argument: any type
   * Third argument: any type
   * Returns: any type

   Evaluates the first argument (the **condition**). If it is logically true (i.e. passing it to :data:`bool` would return ``true``), evaluates and returns the second argument (the **true branch**). Otherwise, evaluates and returns the third argument (the **false branch**). The branch that is not chosen is never evaluated.

.. data:: less?

   * First argument: any type
   * Second argument: any type
   * Returns: :c:type:`Bool`
   * Errors if: the two arguments' types are not comparable (see below)

   Returns ``true`` if the first argument is strictly less than the second. Types that can be compared:

   * :c:type:`Int` or :c:type:`Bool` can be compared against :c:type:`Int` or :c:type:`Bool` (with ``false`` treated as ``0`` and ``true`` as ``1``)
   * :c:type:`String` can be compared against :c:type:`String` (using lexicographic ordering)
   * :c:type:`List` can be compared against :c:type:`List`:
      * :js:data:`nil` is less than any list but itself
      * For non-empty lists, the heads are compared first
      * If the heads are not comparable, the lists are not comparable (an error)
      * If the heads are equal, the tails are compared, continuing until the elements are inequal or one or both lists become :js:data:`nil`

.. data:: equal?

   * First argument: any type
   * Second argument: any type
   * Returns: :c:type:`Bool`

   Returns ``true`` if both arguments are of the same type and contain the same data.

.. note::

   Infinite lists can *sometimes* be compared with :data:`equal?`. As soon as two elements are different, the result is ``false``, of course, but a result of ``true`` can also be returned if both lists result from identical calls to the same function. For example, ``(equal? (tail (0to)) (1to))`` returns ``true``: ``(1to)`` calls ``(count-up 1 nil)``, while ``(0to)`` calls ``(count-up 0 nil)``, which in turn is ``(cons 0 (count-up 1 nil))``. Thus, both ``(tail (0to))`` and ``(1to)`` end up as deferred calls to ``count-up`` with arguments ``1`` and ``nil``, and therefore compare as equal.

   However, two infinite lists that are generated in different ways *cannot* be compared this way, and (if they actually are equal) will result in an infinite loop. For example, ``(repeat-val 1)`` and ``(zip-with sub (1to) (0to))`` both happen to return infinite lists of ones, but they are generated by calls to completely different functions, and so Appleseed has no way of knowing that they are equal except to check every value.

   (The same reasoning holds for :data:`less?`, except that it returns ``false`` when the lists are equal.)

   In summary, while it does work in certain cases, it is not recommended to compare two infinite lists because of the risk of infinite loops.


Objects
-------

.. data:: object

   * Macro
   * Takes zero or more arguments
   * Each argument: two-item :c:type:`List`
   * Returns: :c:type:`Object`

   Creates a new :c:type:`Object`. Each argument is a name-value pair for a :js:data:`property` of the object. The name is not evaluated, while the value is; thus, a bare name token should be used for the name, while an expression can be used for the value: ``(object (x (mul 6 7)))``

.. data:: has-property?

   * Macro
   * First argument: :c:type:`Object`
   * Second argument: :c:type:`String`
   * Returns: :c:type:`Bool`

   Returns ``true`` if the first argument has the property named by the second argument. The second argument is not evaluated; thus, a bare name token should be used: ``(has-property? (object (x (mul 6 7))) y)`` → ``false``

.. data:: get-property

   * Macro
   * First argument: :c:type:`Object`
   * Second argument: :c:type:`String`
   * *(Optional)* Third argument: any type
   * Returns: any type
   * Errors if: the object does not have that property and no default is provided

   Looks up the property named by the second argument in the first argument and returns its value. If the object does not have the specified property but the optional third argument is supplied, returns the third argument; if no third argument is given, a missing property results in an error. The second argument is not evaluated, but the other two are.

.. data:: copy

   * Macro
   * Takes one or more arguments
   * First argument: any type
   * Each remaining argument: two-item :c:type:`List`
   * Returns: :c:type:`Object`
   * Warns if: more than one argument is given but the first argument is not an :c:type:`Object`

   Returns a copy of the first argument. If the first argument is an :c:type:`Object`, name-value pairs may be given as additional arguments, using the same syntax as in :data:`object`; these properties are set in the new object, overwriting any properties of the same names from the original.


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

