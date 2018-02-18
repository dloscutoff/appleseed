
;; Convenience functions for standard system actions

(load utilities)
(load objects)
(load stdio)

(def exit!
  (lambda ((code 0))
    (new Action (name "exit!") (code code))))

(def die!
  (lambda (message)
    (do
      (print! message)
      (exit! 1))))
