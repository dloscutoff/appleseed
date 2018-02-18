
;; Convenience functions for standard system actions

(load utilities)
(load objects)
(load stdio)

(def exit!
  (lambda ((exit-code 0))
    (new Action (name "exit!") (exit-code exit-code))))

(def die!
  (lambda (message)
    (do
      (print! message)
      (exit! 1))))
