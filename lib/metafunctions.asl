
(load utilities)
(load lists)

(def apply
  (macro (&func-or-macro &arglist)
    (eval
      (cons (q &func-or-macro) (quote-each &arglist)))))

(def map
  (lambda (func ls (accum nil))
    (if ls
      (map func
        (tail ls)
        (cons (func (head ls)) accum))
      (reverse accum))))

(def filter
  (lambda (func ls (accum nil))
    (if ls
      (filter func
        (tail ls)
        (if (func (head ls))
          (cons (head ls) accum)
          accum))
      (reverse accum))))

(def take-while
  (lambda (func ls (accum nil))
    (if
      (if ls (func (head ls)) nil)
      (take-while func
        (tail ls)
        (cons (head ls) accum))
      (reverse accum))))

(def _foldl
  (lambda (func ls accum)
    (if ls
      (_foldl func
        (tail ls)
        (func accum (head ls)))
      accum)))

(def foldl-default
  (lambda (func ls default)
    (if ls
      (_foldl func (tail ls) (head ls))
      default)))

(def foldl
  (lambda (func ls) (foldl-default func ls nil)))

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

; Turns a number like 4 into a name #4
(def _#name
  (lambda (num)
    (str
      (cons 35
        (chars (str num))))))

(def _partial
  (macro (&params &param-index)
    (if &params
      (if (equal? (head &params) (q ?))
        (cons
          (_#name &param-index)
          (apply _partial
            (list (tail &params) (inc &param-index))))
        (cons
          (quote (eval (head &params)))
          (apply _partial
            (list (tail &params) &param-index))))
      nil)))

(def partial
  (macro &fn-and-params
    (list
      (map _#name   ; Construct parameter list
        (range
          (count-occurrences (q ?) (tail &fn-and-params))))
      (cons         ; Construct function body
        (head &fn-and-params)
        (_partial (tail &fn-and-params) 0)))))

; Example of a partial function: add-n returns a single-argument function that adds a number to its argument
(def add-n
  (lambda (num)
    (partial add ? num)))

(def _compose
  (macro (&functions)
    (if &functions
      (list
        (head &functions)
        (_compose (tail &functions)))
      (q _argument))))

(def compose
  (macro &functions
    (eval
      (list
        (q lambda)
        (q (_argument))
        (_compose &functions))))
