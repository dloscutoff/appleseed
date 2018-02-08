
(load utilities)
(load lists)
(load metafunctions)
(load math)

(def main-diagonal
  (lambda (matrix (accum nil))
    (if
      (both matrix (head matrix))
      (main-diagonal
        (map tail (tail matrix))
        (cons (head (head matrix)) accum))
      (reverse accum))))

(def matrix-trace
  (lambda (matrix)
    (sum (main-diagonal matrix))))

(def transpose
  (lambda (matrix (accum nil))
    (if (both matrix (all matrix))
      (transpose
        (map tail matrix)
        (cons (map head matrix) accum))
      (reverse accum))))

(def zip
  (lambda args (transpose args)))

(def _each-head-or-default
  (lambda (matrix default accum)
    (if matrix
      (if (head matrix)
        (_each-head-or-default
          (tail matrix)
          default
          (cons (head (head matrix)) accum))
        (_each-head-or-default
          (tail matrix)
          default
          (cons default accum)))
      (reverse accum))))

(def transpose-default
  (lambda (matrix default (accum nil))
    (if (both matrix (any matrix))
      (transpose-default
        (map tail matrix)
        default
        (cons (_each-head-or-default matrix default nil) accum))
      (reverse accum))))

(def _zip-with
  (lambda (func lists accum)
    (if lists
      (_zip-with func
        (tail lists)
        (cons (apply func (head lists)) accum))
      (reverse accum))))

; Takes a function and any number of lists and applies the function to corresponding elements of the lists
(def zip-with
  (lambda func-and-lists
    (_zip-with
      (head func-and-lists)
      (transpose (tail func-and-lists))
      nil)))
