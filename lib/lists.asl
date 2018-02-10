
(load utilities)

(def length
  (lambda (ls (accum 0))
    (if ls
      (length (tail ls) (inc accum))
      accum)))

(def nth
  (lambda (index ls)
    (if (both (type? index Int) (not (negative? index)))
      (if index
        (nth (dec index) (tail ls))
        (head ls))
      nil)))

(def last
  (lambda (ls)
    (if ls
      (if (tail ls)
        (last (tail ls))
        (head ls))
      nil)))

(def take
  (lambda (count ls)
    (if (both ls (positive? count))
      (cons (head ls)
        (take (dec count) (tail ls)))
      nil)))

(def drop
  (lambda (count ls)
    (if (both ls (positive? count))
      (drop (dec count) (tail ls))
      ls)))

(def reverse
  (lambda (ls (accum nil))
    (if ls
      (reverse (tail ls) (cons (head ls) accum))
      accum)))

(def concat
  (lambda lists
    (if lists
      (if (tail lists)
        (_concat (head lists) (tail lists))
        (head lists))
      nil)))

(def _concat
  (lambda (ls lists)
    (if ls
      (cons (head ls) (_concat (tail ls) lists))
      (if (tail lists)
        (_concat (head lists) (tail lists))
        (head lists)))))

(def flatten
  (lambda (val)
    (if (type? val List)
      (if val
        ; <val> is a nonempty list
        (_flatten (flatten (head val)) (tail val))
        ; <val> is nil
        nil)
      ; <val> is not a list--make it into a single-item list
      (cons val nil))))

(def _flatten
  (lambda (ls rest)
    (if ls
      ; <ls> is a nonempty, already flattened list
      (cons (head ls) (_flatten (tail ls) rest))
      ; <ls> is nil
      (if rest
        ; <rest> is a nonempty, still to-be-flattened list
        (_flatten (flatten (head rest)) (tail rest))
        ; <rest> is nil, and we're done
        nil))))

(def insert
  (lambda (val ls index)
    (if (both (type? index Int) (not (negative? index)))
      (if index
        (cons (head ls) (insert val (tail ls) (dec index)))
        (cons val ls))
      nil)))

(def insert-end
  (lambda (val ls)
    (if ls
      (cons (head ls) (insert-end val (tail ls)))
      (cons val nil))))

(def contains?
  (lambda (ls item)
    (if ls
      (if (equal? (head ls) item)
        1
        (contains? (tail ls) item))
      0)))

(def count-occurrences
  (lambda (item ls (count 0))
    (if ls
      (if (equal? (head ls) item)
        (count-occurrences item (tail ls) (inc count))
        (count-occurrences item (tail ls) count))
      count)))

(def first-index
  (lambda (item ls (index 0))
    (if ls
      (if (equal? (head ls) item)
        index
        (first-index item (tail ls) (inc index)))
      nil)))

(def last-index
  (lambda (item ls (index 0) (current-last-index nil))
    (if ls
      (if (equal? (head ls) item)
        (last-index item (tail ls) (inc index) index)
        (last-index item (tail ls) (inc index) current-last-index))
      current-last-index)))

(def all-indices
  (lambda (item ls (index 0))
    (if ls
      (if (equal? (head ls) item)
        (cons index (all-indices item (tail ls) (inc index)))
        (all-indices item (tail ls) (inc index)))
      nil)))

(def count-up
  (lambda (lower (upper nil))
    (if (nil? upper)
      ; Infinite range from <lower> on up
      (cons lower (count-up (inc lower) nil))
      ; Traditional range from <lower> to <upper>
      (if (both (type? lower Int) (type? upper Int))
        (if (less? upper lower)
          nil
          (cons lower (count-up (inc lower) upper)))
        nil))))

(def count-down
  (lambda (upper (lower nil))
    (if (nil? lower)
      ; Infinite range from <upper> on down
      (cons upper (count-down (dec upper) nil))
      ; Traditional range from <upper> down to <lower>
      (if (both (type? lower Int) (type? upper Int))
        (if (less? upper lower)
          nil
          (cons upper (count-down (dec upper) lower)))
        nil))))

(def 0to
  (lambda ((num nil)) (count-up 0 num)))

(def 1to
  (lambda ((num nil)) (count-up 1 num)))

(def to0
  (lambda (num) (count-down num 0)))

(def to1
  (lambda (num) (count-down num 1)))

; With two arguments, generates a list of integers starting at <first> and ending just before <second>
; With one argument, generates a list of integers starting at 0 and ending just before <first>
(def range
  (lambda (first (second nil))
    (if (nil? second)
      (count-up 0 (dec first))
      (count-up first (dec second)))))

; With two arguments, generates a list of <count> <val>s
; With one argument, generates an infinite list of <val>s
(def repeat-val
  (lambda (val (count nil))
    (if (nil? count)
      (cons val (repeat-val val nil))
      (if (both (type? count Int) (positive? count))
        (cons val (repeat-val val (dec count)))
        nil))))

(def all
  (lambda (ls)
    (if ls
      (if (head ls)
        (all (tail ls))
        0)
      1)))

(def any
  (lambda (ls)
    (if ls
      (if (head ls)
        1
        (any (tail ls)))
      0)))
