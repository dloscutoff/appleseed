
;; Convenience functions for standard I/O actions

(load utilities)
(load objects)

(def print!
  (lambda (val)
    (new Action (name "print!") (value val))))

(def print-error!
  (lambda (val)
    (new Action (name "print-error!") (value val))))

(def write!
  (lambda (val)
    (new Action (name "write!") (value val))))

(def write-error!
  (lambda (val)
    (new Action (name "write-error!") (value val))))

(def ask-line!
  (lambda ((prompt ""))
    (new Action (name "ask-line!") (prompt prompt))))
