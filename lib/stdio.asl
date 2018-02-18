
;; Convenience functions for standard I/O actions

(load utilities)
(load objects)

(def write!
  (lambda (val)
    (new Action (name "write!") (value val))))

(def error-write!
  (lambda (val)
    (new Action (name "error-write!") (value val))))

(def print!
  (lambda (val)
    (new Action (name "print!") (value val))))

(def ask-line!
  (lambda ((prompt ""))
    (new Action (name "ask-line!") (prompt prompt))))
