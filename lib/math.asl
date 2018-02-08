
(load utilities)
(load metafunctions)
(load lists)

(def abs
  (lambda (num)
    (if (negative? num)
      (neg num)
      num)))

(def -
  (lambda args
    (if args
      (if (tail args)
        (_foldl sub (tail args) (head args))
        (neg (head args)))
      0)))

(def +
  (lambda args (foldl-default add args 0)))

(def sum
  (lambda (ls) (foldl-default add ls 0)))

(def *
  (lambda args (foldl-default mul args 1)))

(def product
  (lambda (ls) (foldl-default mul ls 1)))

(def /
  (lambda args
    (if args
      (if (tail args)
        (_foldl div (tail args) (head args))
        (div 1 (head args)))
      1)))

(def divides?
  (lambda (divisor multiple)
    (if (mod multiple divisor) 0 1)))

(def even?
  (lambda (num)
    (if (mod num 2) 0 1)))

(def odd?
  (lambda (num) (mod num 2)))

; When given a negative exponent, pow returns 0, except with special cases for bases 1, -1, or 0
; When the exponent is 0, pow returns 1, even when the base is 0
(def pow
  (lambda (base exponent)
    (if (negative? exponent)
      (if base
        (if (equal? (abs base) 1)
          (pow base (neg exponent))
          0)
        nil)
      (product (repeat-val base exponent)))))

(def _gcd-nonnegative
  (lambda (num1 num2)
    (if num2
      (_gcd-nonnegative num2 (mod num1 num2))
      num1)))

(def gcd
  (lambda (num1 num2)
    (if (negative? num1)
      (gcd (neg num1) num2)
      (if (negative? num2)
        (_gcd-nonnegative num1 (neg num2))
        (_gcd-nonnegative num1 num2)))))

(def _to-base
  (lambda (base num accum)
    (if (positive? num)
      (_to-base base
        (div num base)
        (cons (mod num base) accum))
      accum)))

(def to-base
  (lambda (base num)
    (if (positive? base)
      (if (equal? base 1)
        (repeat-val 1 num)
        (_to-base base num nil))
      nil)))

(def from-base
  (lambda (base digits (accum 0))
    (if digits
      (from-base base
        (tail digits)
        (add (head digits) (mul accum base)))
      accum)))

(def bigger
  (lambda (value1 value2)
    (if (less? value1 value2)
      value2
      value1)))

(def max
  (lambda (ls) (foldl bigger ls)))

(def smaller
  (lambda (value1 value2)
    (if (less? value1 value2)
      value1
      value2)))

(def min
  (lambda (ls) (foldl smaller ls)))

(def factorial
  (lambda (num) (product (1to num))))

(def _prime?
  (lambda (num factor)
    (if (less? factor num)
      (if (divides? factor num)
        0
        (_prime? num (inc factor)))
      1)))

(def prime?
  (lambda (num)
    (if (equal? num (neg 1))
      1
      (if (less? num 2)
        0
        (_prime? num 2)))))

(def _prime-factors
  (lambda (num test-factor accum)
    (if (greater? test-factor num)
      accum
      (if (divides? test-factor num)
        (_prime-factors (div num test-factor) test-factor (cons test-factor accum))
        (_prime-factors num (inc test-factor) accum)))))

; Definition for 0 and negative numbers is chosen such that (product (prime-factors n)) equals n
(def prime-factors
  (lambda (num)
    (if num
      (if (negative? num)
        (_prime-factors (neg num) 2 (list (neg 1)))
        (_prime-factors num 2 nil))
      (q (0)))))
