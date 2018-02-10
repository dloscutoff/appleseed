
(load utilities)
(load lists)
(load metafunctions)
(load math)

(def main-diagonal
  (lambda (matrix)
    (if (both matrix (head matrix))
      (cons (head (head matrix))
        (main-diagonal (map tail (tail matrix))))
      nil)))

(def matrix-trace
  (lambda (matrix)
    (sum (main-diagonal matrix))))

(def transpose
  (lambda (matrix)
    (if (both matrix (all matrix))
      (cons (map head matrix)
        (transpose (map tail matrix)))
      nil)))

(def zip
  (lambda args (transpose args)))

(def transpose-default
  (lambda (matrix default)
    (if (both matrix (any matrix))
      (cons
        (map
          ; TODO: rewrite as just a lambda once we have closures
          (partial _head-or-default ? default)
          matrix)
        (transpose-default (map tail matrix) default))
      nil)))

(def _head-or-default
  (lambda (row default)
    (if row (head row) default)))

; Takes a function and any number of lists and applies the function to
; corresponding elements of the lists
(def zip-with
  (lambda func-and-lists
    (_zip-with
      (head func-and-lists)
      (transpose (tail func-and-lists)))))

(def _zip-with
  (lambda (func arglists)
    (if arglists
      (cons
        (apply func (head arglists))
        (_zip-with func (tail arglists)))
      nil)))
