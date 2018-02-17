
(load utilities)
(load metafunctions)
(load lists)

; Returns the absolute value of its argument
(def abs
  (lambda (num)
    (if (negative? num)
      (neg num)
      num)))

; Returns the sign of its argument
(def sgn
  (lambda (num)
    (if (negative? num)
      -1
      (if (zero? num) 0 1))))

; Variadic subtraction function:
; - With no arguments, returns 0
; - With one argument, negates the argument
; - With more than one argument, subtracts all subsequent arguments from
;   the first
(def -
  (lambda args
    (if args
      (if (tail args)
        (foldl sub args)
        (neg (head args)))
      0)))

; Variadic addition function:
; - With no arguments, returns 0
; - With one or more arguments, adds all arguments together
(def +
  (lambda args (foldl add args 0)))

; Takes the sum of a list
; Different from + in that sum takes a single argument, a list, whereas
; + takes multiple arguments
(def sum
  (lambda (ls) (foldl add ls 0)))

; Variadic multiplication function:
; - With no arguments, returns 1
; - With one or more arguments, multiplies all arguments together
(def *
  (lambda args (foldl mul args 1)))

; Takes the product of a list
; Different from * in that product takes a single argument, a list, whereas
; * takes multiple arguments
(def product
  (lambda (ls) (foldl mul ls 1)))

; Variadic division function:
; - With no arguments, returns 1
; - With one argument, divides 1 by the argument (not very useful in integer
;   math, but perhaps more useful when user-defined types come into play)
; - With more than one argument, divides the first argument by all subsequent
;   arguments
(def /
  (lambda args
    (if args
      (if (tail args)
        (foldl div args)
        (div 1 (head args)))
      1)))

; Tests whether <divisor> divides <multiple> evenly
(def divides?
  (lambda (divisor multiple) (zero? (mod multiple divisor))))

; Tests whether <num> is even
(def even?
  (lambda (num) (zero? (mod num 2))))

; Tests whether <num> is odd
(def odd?
  (lambda (num) (mod num 2)))

; Returns the square of <num>
(def square
  (lambda (num) (mul num num)))

; Integer exponential: <base> to the power of <exponent>
; When <exponent> is 0, pow returns 1, even if <base> is 0
; When <exponent> is negative, pow returns 0, except in special cases:
; - With <base> of 1 or -1, the negative sign doesn't make a difference
; - With <base> of 0, it's division by zero
(def pow
  (lambda (base exponent)
    (if (negative? exponent)
      (if base
        (if (equal? (abs base) 1)
          (pow base (neg exponent))
          0)
        (div 1 0))
      (product (repeat-val base exponent)))))

(def gcd
  (lambda (num1 num2)
    (if (negative? num1)
      (gcd (neg num1) num2)
      (if (negative? num2)
        (_gcd-nonnegative num1 (neg num2))
        (_gcd-nonnegative num1 num2)))))

(def _gcd-nonnegative
  (lambda (num1 num2)
    (if num2
      (_gcd-nonnegative num2 (mod num1 num2))
      num1)))

(def to-base
  (lambda (base num)
    (if (positive? base)
      (if (equal? base 1)
        (repeat-val 1 num)
        (_to-base base num))
      nil)))

(def _to-base
  (lambda (base num (accum nil))
    (if (positive? num)
      (_to-base base
        (div num base)
        (cons (mod num base) accum))
      accum)))

(def from-base
  (lambda (base digits (accum 0))
    (if digits
      (from-base base
        (tail digits)
        (add (head digits) (mul accum base)))
      accum)))

(def bigger
  (lambda (value1 value2)
    (if (less? value1 value2) value2 value1)))

(def max
  (lambda (ls)
    (if ls (_max (tail ls) (head ls)) nil)))

(def _max
  (lambda (ls largest)
    (if ls
      (if (greater? (head ls) largest)
        (_max (tail ls) (head ls))
        (_max (tail ls) largest))
      largest)))

(def smaller
  (lambda (value1 value2)
    (if (less? value1 value2) value1 value2)))

(def min
  (lambda (ls)
    (if ls (_min (tail ls) (head ls)) nil)))

(def _min
  (lambda (ls smallest)
    (if ls
      (if (less? (head ls) smallest)
        (_min (tail ls) (head ls))
        (_min (tail ls) smallest))
      smallest)))

(def <ordered?
  (lambda (ls)
    (if (tail ls)
      (both (less? (head ls) (htail ls)) (<ordered? (tail ls)))
      1)))

(def <
  (lambda args (<ordered? args)))

(def <=ordered?
  (lambda (ls)
    (if (tail ls)
      (both (not (greater? (head ls) (htail ls))) (<=ordered? (tail ls)))
      1)))

(def <=
  (lambda args (<=ordered? args)))

(def >ordered?
  (lambda (ls)
    (if (tail ls)
      (both (greater? (head ls) (htail ls)) (>ordered? (tail ls)))
      1)))

(def >
  (lambda args (>ordered? args)))

(def >=ordered?
  (lambda (ls)
    (if (tail ls)
      (both (not (less? (head ls) (htail ls))) (>=ordered? (tail ls)))
      1)))

(def >=
  (lambda args (>=ordered? args)))

(def factorial
  (lambda (num) (product (1to num))))

; Tests whether <num> is prime
; -1 is considered prime, because its only divisors are 1 and itself
; 0, 1, and all other negative numbers are non-prime
(def prime?
  (lambda (num)
    (if (equal? num -1)
      1
      (if (less? num 2)
        0
        (_prime? num 2)))))

(def _prime?
  (lambda (num factor)
    (if (less? factor num)
      (if (divides? factor num)
        0
        (_prime? num (inc factor)))
      1)))

; Called without arguments, returns an infinite list of the prime numbers
; using the Sieve of Eratosthenes
(def primes
  (lambda ((sieve (count-up 2)))
    ; Include the first number in the sieve
    (cons (head sieve)
      ; Include larger numbers from the sieve...
      (primes
        ; ...keeping only those not evenly divisible by the first (i.e. that
        ; are nonzero modulo the first number)
        (filter (partial mod ? (head sieve)) (tail sieve))))))

; Given an integer, returns a list of its prime factors
; Some special cases: 1 returns empty list; 0 returns list containing 0;
; negative numbers return -1 plus the prime factors of their absolute value
; This definition for 0 and negative numbers is chosen so that
; (product (prime-factors n)) always equals n
(def prime-factors
  (lambda (num)
    (if num
      (if (negative? num)
        (cons -1 (_prime-factors (neg num) 2))
        (_prime-factors num 2))
      (q (0)))))

(def _prime-factors
  (lambda (num test-factor)
    (if (greater? test-factor num)
      nil
      (if (divides? test-factor num)
        (cons test-factor
          (_prime-factors (div num test-factor) test-factor))
        (_prime-factors num (inc test-factor))))))
