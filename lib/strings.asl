
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
    (if (type? string String)
      (starts-with? (chars prefix) (chars string))
      (if prefix
        (if string
          (if (equal? (head prefix) (head string))
            (starts-with? (tail prefix) (tail string))
            0)
          0)
        1))))

(def join
  (lambda (strings sep)
    (foldl (partial strcat ? sep ?) strings "")))
