
(load utilities)
(load lists)
(load metafunctions)

; Takes an integer character code, returns a string containing the
; associated character
(def chr
  (macro (&charcode)
    (str (cons &charcode nil))))

; Takes a string, returns the character code of the first character
(def asc
  (macro (&string)
    (head (chars &string))))

(def newline (chr 10))

(def strlen
  (lambda (string)
    (length (chars string))))

(def strcat
  (lambda strings
    (str
      (apply concat (map chars strings)))))

; This function can also be used on lists
(def starts-with?
  (lambda (prefix string)
    (if (type? prefix String)
      (starts-with? (chars prefix) string)
      (if (type? string String)
        (starts-with? prefix (chars string))
        (if prefix
          (if string
            (if (equal? (head prefix) (head string))
              (starts-with? (tail prefix) (tail string))
              0)
            0)
          1)))))

(def join
  (lambda (strings sep)
    (foldl (partial strcat ? sep ?) strings "")))

; Takes a string and parses an integer from the beginning of it
; Ignores leading spaces; single minus sign can occur just before
; the digits; otherwise, if the string doesn't start with a number,
; returns 0
(def parse-int
  (lambda (string)
    (_parse-int (chars string))))

; The helper function _parse-int takes a list of character codes
; Optional arguments:
; - <accum>: accumulator for the integer being parsed
; - <digits-only>: false if we're still accepting leading spaces or
;   minus sign, true if the parsing now requires digits
(def _parse-int
  (lambda (charcodes (digits-only 0) (accum 0))
    ; If the list of charcodes has run out, return <accum>
    (if charcodes
      ; If the first charcode is a digit, shift the value in <accum> up
      ; by a decimal place, add the digit value of the charcode, and
      ; recurse with the rest of the charcodes, requiring digits only
      (if (<= 48 (head charcodes) 57)
        (_parse-int
          (tail charcodes)
          1
          (add (mul accum 10) (sub (head charcodes) 48)))
        ; Else, if the charcode isn't a digit and we require digits
        ; only, stop parsing and return <accum>
        (if digits-only
          accum
          ; Else, if the charcode is a space, skip it
          (if (equal? (head charcodes) (asc " "))
            (_parse-int (tail charcodes))
            ; Else, if the charcode is a minus sign, parse an integer
            ; (digits only) and return its negation
            (if (equal? (head charcodes) (asc "-"))
              (neg (_parse-int (tail charcodes) 1))
              ; Else, this isn't a valid character; stop parsing and
              ; return <accum>
              accum))))
      accum)))
