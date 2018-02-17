
(load utilities)
(load metafunctions)

; Given a type and 0 or more properties, constructs an object.
; E.g. (new Foo (x 1) (y 3)) => (object (type (q Foo)) (x 1) (y 3))
(def new
  (macro &type-and-properties
    (if (type? (head &type-and-properties) String)
      (eval
        (cons (q object)
          (cons
            (list (q type) (quote (head &type-and-properties)))
            (tail &type-and-properties))))
      nil)))

; Given an object, returns its type property if set, else Object
; Given anything else, returns its base type
(def object-type
  (lambda (obj)
    (if (type? obj Object)
      (get-property obj type Object)
      (type obj))))

; Given an object and a type, returns truthy if the object's type property
; matches the given type, falsey otherwise
(def object-type?
  (lambda (obj some-type)
    (and
      (type? obj Object)
      (has-property obj type)
      (equal? (get-property obj type) some-type))))
