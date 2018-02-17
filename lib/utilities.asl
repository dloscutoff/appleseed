
(def nil ())
(def Int "Int")
(def List "List")
(def String "String")
(def Object "Object")
(def Builtin "Builtin")
(def Event "Event")
(def Action "Action")

(def list (q (args args)))

(def macro
  (q
    (0 (&params &expr)
      (q (0 &params &expr)))))

(def lambda
  (macro (&params &expr)
    (q (&params &expr))))

(def quote
  (macro (&expr)
    (list (q q) &expr)))

(def neg (macro (&num) (sub 0 &num)))
(def dec (macro (&num) (sub &num 1)))
(def inc (macro (&num) (add 1 &num)))

(def nil? (macro (&val) (equal? &val nil)))
(def zero? (macro (&val) (equal? &val 0)))
(def greater? (macro (&num1 &num2) (less? &num2 &num1)))
(def positive? (macro (&num) (less? 0 &num)))
(def negative? (macro (&num) (less? &num 0)))

(def type?
  (macro (&val &some-type) (equal? (type &val) &some-type)))

(def htail (macro (&ls) (head (tail &ls))))
(def ttail (macro (&ls) (tail (tail &ls))))

(def not (macro (&val) (if &val 0 1)))

(def both
  (macro (&expr1 &expr2)
    (if &expr1 &expr2 &expr1)))

(def either
  (macro (&expr1 &expr2)
    (if &expr1 &expr1 &expr2)))

(def neither
  (macro (&expr1 &expr2)
    (if &expr1 0 (not &expr2))))

(def and
  (macro &exprs
    (if &exprs
      (if (tail &exprs)
        (if (eval (head &exprs))
          (eval
            (cons
              (q and)
              (tail &exprs)))
          (eval (head &exprs)))
        (eval (head &exprs)))
      1)))

(def or
  (macro &exprs
    (if (tail &exprs)
      (if (eval (head &exprs))
        (eval (head &exprs))
        (eval
          (cons
            (q or)
            (tail &exprs))))
      (eval (head &exprs)))))

(def if-not
  (macro (&test &expr1 &expr2)
    (if &test &expr2 &expr1)))
