
(load utilities)
(load lists)

(def quote-each
  (lambda (ls)
    (if ls
      (cons (quote (head ls)) (quote-each (tail ls)))
      nil)))

(def eval-each
  (macro (&ls)
    (if &ls
      (cons (eval (head &ls)) (eval-each (tail &ls)))
      nil)))

(def apply
  (macro (&func &arglist)
    (eval
      (cons (q &func) (quote-each &arglist)))))

(def map
  (lambda (func ls)
    (if ls
      (cons (func (head ls)) (map func (tail ls)))
      nil)))

(def filter
  (lambda (func ls)
    (if ls
      (if (func (head ls))
        (cons (head ls) (filter func (tail ls)))
        (filter func (tail ls)))
      nil)))

(def filter-not
  (lambda (func ls)
    (if ls
      (if (func (head ls))
        (filter-not func (tail ls))
        (cons (head ls) (filter-not func (tail ls))))
      nil)))

(def take-while
  (lambda (func ls)
    (if (both ls (func (head ls)))
      (cons (head ls) (take-while func (tail ls)))
      nil)))

(def drop-while
  (lambda (func ls)
    (if (both ls (func (head ls)))
      (drop-while func (tail ls))
      ls)))

(def foldl
  (lambda (func ls (default nil))
    (if ls
      (_foldl func (tail ls) (head ls))
      default)))

(def _foldl
  (lambda (func ls accum)
    (if ls
      (_foldl func
        (tail ls)
        (func accum (head ls)))
      accum)))

; TODO: figure out what to do with chain-last
;(def _chain-last
;  (macro args
;    (if (tail args)
;      (list (q (arg)) (head args))
;      (eval
;        (cons
;          (q _chain-last)
;          (cons
;            (insert-end (head args) (htail args))
;            (ttail args)))))))

;(def chain-last
;  (macro args
;    (eval
;      (cons
;        (q _chain-last)
;        (cons
;          (insert-end (q arg) (head args))
;          (tail args))))))

; Takes a function and some number of arguments, where the arguments can
; be either actual values or the placeholder ?
; Let the number of ?s be N; then the return value is an N-argument function
; that puts its arguments in place of the ?s and calls the original function
; For example, (partial mod ? 10) returns a one-argument function that
; computes its argument modulo 10--equivalent to (lambda (n) (mod n 10))
(def partial
  (macro &fn-and-params
    (list
      (map _#name   ; Construct parameter list
        (range
          (count-occurrences (q ?) (tail &fn-and-params))))
      (cons         ; Construct function body
        (head &fn-and-params)
        (_partial (tail &fn-and-params) 0)))))

(def _partial
  (macro (&params &param-index)
    (if &params
      (if (equal? (head &params) (q ?))
        (cons
          (_#name &param-index)
          (_partial (tail &params) (inc &param-index)))
        (cons
          (quote (eval (head &params)))
          (_partial (tail &params) &param-index)))
      nil)))

; Helper for creating partial functions
; Turns a number like 4 into a name #4
(def _#name
  (lambda (num)
    (str
      (cons 35
        (chars (str num))))))

; Example of how to use partial: add-n returns a single-argument function
; that adds a number to its argument; for example, (add-n 1) does the same
; thing as inc
(def add-n
  (lambda (num)
    (partial add ? num)))

; Takes a function and some number of arguments; returns a new variadic
; function that calls the original function with the specified arguments
; followed by the new function's arguments
; For example, (variadic-partial + 1) returns a function that adds 1 together
; with all its arguments--equivalent to (lambda args (+ 1 (sum args)))
; For partial application, partial (above) is normally recommended as being
; more flexible and easier to understand, but if the partial application
; result needs to be variadic, use variadic-partial
(def variadic-partial
  (macro &func-and-args
      (list
        (q _varargs)
        (list
          (q apply)
          (quote (eval (head &func-and-args)))
          (list
            (q concat)
            (quote (eval-each (tail &func-and-args)))
            (q _varargs))))))

; Composes functions together; for example, (compose f g h) returns a new
; function that passes its argument to h, the result to g, and that result
; to f--equivalent to (lambda (val) (f (g (h val))))
(def compose
  (macro &functions
    (list
      (q (_argument))
      (_compose &functions))))

(def _compose
  (macro (&functions)
    (if &functions
      (list
        (quote (eval (head &functions)))
        (_compose (tail &functions)))
      (q _argument))))
