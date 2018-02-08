
(load utilities)

(def length
  (lambda (ls (accum 0))
    (if ls
      (length (tail ls) (inc accum))
      accum)))

(def nth
  (lambda (ls index)
    (if (type? index Int)
      (if (negative? index)
        nil
        (if index
          (nth (tail ls) (dec index))
          (head ls)))
      nil)))

(def last
  (lambda (ls)
    (if ls
      (if (tail ls)
        (last (tail ls))
        (head ls))
      nil)))

(def reverse
  (lambda (ls (accum nil))
    (if ls
      (reverse (tail ls) (cons (head ls) accum))
      accum)))

(def _concat
  (lambda (lists accum)
    (if lists
      (_concat (tail lists) (reverse (reverse (head lists)) accum))
      accum)))
  
(def concat
  (lambda lists
    (_concat (reverse lists) nil)))

(def _flatten
  (lambda (ls accum)
    (if ls
      (if (type? (head ls) List)
        (_flatten (tail ls) (flatten (head ls) accum))
        (_flatten (tail ls) (cons (head ls) accum)))
      accum)))

(def flatten
  (lambda (val (accum nil))
    (if (type? val List)
      (_flatten (reverse val) accum)
      (cons val accum))))

(def _insert
  (lambda (val ls-front ls-back index)
    (if index
      (_insert
        val
        (cons (head ls-back) ls-front)
        (tail ls-back)
        (dec index))
      (reverse
        ls-front
        (cons val ls-back)))))

(def insert
  (lambda (val ls index)
    (if (type? index Int)
      (if (negative? index)
        nil
        (_insert val nil ls index))
      nil)))

(def insert-end
  (lambda (val ls)
    (reverse (cons val (reverse ls)))))

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
  (lambda (item ls (index 0) (accum nil))
    (if ls
      (if (equal? (head ls) item)
        (all-indices item (tail ls) (inc index) (cons index accum))
        (all-indices item (tail ls) (inc index) accum))
      (reverse accum))))

(def quote-each
  (lambda (ls (accum nil))
    (if ls
      (quote-each
        (tail ls)
        (cons (quote (head ls)) accum))
      (reverse accum))))

(def inclusive-range
  (lambda (lower upper (accum nil))
    (if
      (both (type? lower Int) (type? upper Int))
      (if (less? upper lower)
        accum
        (inclusive-range lower (dec upper) (cons upper accum)))
      (less? upper lower))))

(def reverse-inclusive-range
  (lambda (upper lower (accum nil))
    (if
      (both (type? lower Int) (type? upper Int))
      (if (less? upper lower)
        accum
        (reverse-inclusive-range upper (inc lower) (cons lower accum)))
      (less? upper lower))))

(def 0to
  (lambda (num) (inclusive-range 0 num)))

(def 1to
  (lambda (num) (inclusive-range 1 num)))

(def to0
  (lambda (num) (reverse-inclusive-range num 0)))

(def to1
  (lambda (num) (reverse-inclusive-range num 1)))

(def range
  (lambda (first (second nil))
    (if (nil? second)
      (inclusive-range 0 (dec first))
      (inclusive-range first (dec second)))))

(def repeat-val
  (lambda (val count (accum nil))
    (if (positive? count)
      (repeat-val val (dec count) (cons val accum))
      accum)))

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
