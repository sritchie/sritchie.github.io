---
title: "Cascalog Testing 2.0"
date: 2012-01-23T00:24:00.000Z
slug: cascalog-testing-2-0
tags:
  - code
  - cascalog
  - clojure
categories:
  - programming
---

A few months ago I announced [Midje-Cascalog](http://sritchie.github.com/2011/09/30/testing-cascalog-with-midje.html), my layer of Midje testing macros over the Cascalog MapReduce DSL. These allow you to write tests for your Cascalog jobs in a style that mimics Cascalog's own query execution syntax. In this post I discuss midje-cascalog's 0.4.0 release, which brings tighter Midje integration and a number of new ways to write tests. I'll start with a refresher on the old syntax before debuting the new. If you're eager, add the following to your project.clj:

```
[midje-cascalog "0.4.0"]
```

## Midje-Cascalog Refresher<a id="sec-1-1" name="sec-1-1"></a>

Take the following Cascalog query:

```
(use 'cascalog.api)

(let [src [["word"]]]
  (?<- (stdout)
       [?out-word]
       (src ?word)
       (str ?word " up!" :> ?out-word)))
```

Executing this code at the repl prints a single tuple with the string `word up!` to standard out.

How would you go about testing that this is true? With midje-cascalog, you would swap out the `?&lt;-` form for its testing equivalent: `fact?&lt;-`. Here's the same Cascalog test alongside a typical Midje test:

```
(let [src [["word"]]]
  (fact?<- [["word up!"]]
           [?out-word]
           (src ?word)
           (str ?word " up!" :> ?out-word)))

(fact "+ should add two numbers."
  (+ 2 2) => 4)
```

I find that `fact?&lt;-` and `fact?-` macros can be a bit confusing when you start mixing Cascalog and Midje tests, as they break the Midje pattern of `&lt;thing-to-test&gt; =&gt; &lt;expected-thing&gt;`. The syntax updates fix all of this with a set of checker functions that mimic Midje's excellent [set of collection checkers](https://github.com/marick/Midje/wiki/Checkers-for-collections-and-strings).

## The &quot;produces&quot; checker<a id="sec-1-2" name="sec-1-2"></a>

Midje-cascalog 0.4.0 introduces the `produces` function, mirroring Midje's `just`. Let's define a source of tuples and a query to test.

```
(use 'cascalog.api)
(require '[cascalog.ops :as c])

(def src
  [[1 2] [1 3]
   [3 4] [3 6]
   [5 2] [5 9]])

;; adds the values in each input tuple, sorts the output and returns
;; 2-tuples of the first number and the sum. [1 2] becomes [1 3], for
;; example.
(def query
  (<- [?x ?sum]
      (src ?x ?y)
      (:sort ?x)
      (c/sum ?y :> ?sum)))
```

You can think of a query as a set of tuples waiting to be generated (through query execution). With Midje, you test sets using the `just` checker:

```
(facts
  [1 2 3] => (just [1 2 3])    ;; true
  [1 2 3] => (just [1 2 3 4])) ;; false
```

The cascalog analog to `just` is the `produces` checker. `produces` works like `just`, but against queries instead of bare collections. Executing the following test shows that the query produces the expected set of pairs, in any order:

```
(facts
  query => (produces [[3 10] [1 5] [5 11]])  ;; true
  query => (produces [[1 5] [3 10] [5 11]])) ;; true
```

You can read this test as saying &quot;query, when executed, produces [3 10], [1 5] and [5 11]. You can also check that a query **doesn't** produce a set of tuples by swapping out =not=&gt; for =&gt;:

```
(fact
  query =not=> (produces [["string!" 11] [1 5] [5 11]])) ;; true
```

Using the `:in-order` keyword after the expected tuple sequence forces the test to respect ordering:

```
(facts    
  query =not=> (produces [[3 10] [5 11] [1 5]] :in-order) ;; true
  query => (produces [[1 5] [3 10] [5 11]] :in-order))    ;; true
```

(`:in-order` is really only helpful in cases where output is sorted, like our query above.)

## produces-some<a id="sec-1-3" name="sec-1-3"></a>

The `produces-some` checker tests that a query's output contains a subset of tuples:

```
(fact
  query => (produces-some [[5 11] [1 5]])) ;; true
```

Note that the behaviour of `produces-some` is similar to the behavior of Midje's `contains` collection checker.

As with produces, you can use the `:in-order` keyword to force `produces-some` to respect ordering. Gaps between tuples are okay.

```
(facts
  query =not=> (produces-some [[5 11] [1 5]] :in-order) ;; true
  query => (produces-some [[1 5] [5 11]] :in-order))    ;; true
```

Adding the `:no-gaps` keyword introduces the constraint that tuples must also be contiguous:

```
(facts    
  query =not=> (produces-some [[1 5] [5 11]] :in-order :no-gaps) ;; true
  query => (produces-some [[1 5] [3 10]] :in-order :no-gaps))    ;; true
```

## produces-prefix and produces-suffix<a id="sec-1-4" name="sec-1-4"></a>

`produce-prefix` mimics the `has-prefix` collection checker by checking that some set of tuples is produced at the beginning of the query's output. `produces-prefix` implicitly assumes that tuples will be produced in order with no gaps:

```
(facts    
  query => (produces-prefix [[1 5]])         ;; true
  query => (produces-prefix [[1 5] [3 10]])) ;; true
```

Similarly, `produce-suffix` mimics the `has-suffix` collection checker by checking that the supplied set of tuples is produced at the tail end of a query:

```
(facts
  query => (produces-suffix [[5 11]])) ;; true
```

## log-level keywords<a id="sec-1-5" name="sec-1-5"></a>

In addition to the keyword options supported above, every one of these checkers supports on optional logging-level keyword. For example, the following two facts are equivalent, but the second one produces `:info` level logging when it runs:

```
(facts
  query => (produces-suffix [[5 11]])        ;; true
  query => (produces-suffix [[5 11]] :info)) ;; true
```

Log level keywords can be useful when debugging tests, as errors will often only appear in the logging output. Currently supported keywords are `:off` (the default), `:fatal`, `:warn`, `:info` and `:debug`. The log level needs to be the first keyword argument if you supply multiple.

## wrap-checker<a id="sec-1-6" name="sec-1-6"></a>

The real power of the `0.4.0` update is the way in which the previous query checkers were defined. Each of the above checkers mimics the behavior of one of Midje's built-in collection checkers with slightly different keyword arguments. This makes sense if you think of a query as a collection of tuples waiting to be produced (by query execution). The above checkers will get you quite a ways, but what if you want to test a query against some other Midje collection checker?

The answer is `wrap-checker`. `wrap-checker` is a higher-order function that accepts a midje collection checker and wraps it up, turning it into a Cascalog query checker. I'll demonstrate the power of this function by wrapping  Midje's `has` checker.

`has` is a powerful way to run functions across every value in some sequence:

```
(fact
  [1 3 5 7 9] => (has every? odd?) ;; true
  [1 3 5 6] => (has some even?))   ;; true
```

If you try to use `has` against a query it will fail, as it expects to be tested against a sequence, not an unexecuted query. Here's how to get around this:

```
(defn odd-tuple? [tuple]
  (odd? (first tuple)))

(defn even-tuple? [tuple]
  (even? (first tuple)))

(def has-tuples
  (wrap-checker has))

(def new-query
  (let [src [[1] [3] [5]]]
    (<- [?x] (src ?x))))

(fact
  new-query     => (has-tuples every? odd-tuple?) ;; true
  new-query =not=> (has-tuples some even-tuple?)) ;; true
```

`has-tuples` will support log-level keywords like any of the predefined query collection checkers.

A few more examples:

```
(defn id-query [src]
  (<- [?x] (src ?x)))

(let [one-of-tuples (wrap-checker one-of)
      two-of-tuples (wrap-checker two-of)
      src [[1] [3] [4]]]
  (facts
    src            => (two-of odd-tuple?)           ;; true
    src            => (one-of even-tuple?)          ;; true
    (id-query src) => (two-of-tuples odd-tuple?)    ;; true
    (id-query src) => (one-of-tuples even-tuple?))) ;; true
```

## Backwards Compatibility<a id="sec-1-7" name="sec-1-7"></a>

All of the collection checkers discussed above can be used with the `fact?&lt;-` and `fact?-` macros:

```
(fact?<- (produces-some [[1 5] [5 11]] :in-order)
         [?x ?sum]
         (src ?x ?y)
         (:sort ?x)
         (c/sum ?y :> ?sum)) ;; true
```

`fact?&lt;-` and `fact?-` are also compatible with all of Midje's unwrapped collection checkers, as discussed [here](http://sritchie.github.com/2011/09/30/testing-cascalog-with-midje.html).

## Conclusion<a id="sec-1-8" name="sec-1-8"></a>

Midje is an astonishingly good testing framework; I'm continually surprised by how well its idioms and conventions satisfy Cascalog's needs. In my next post here I'll go over some of the more subtle details of the `wrap-checker` function. For the curious, [here's the code](https://github.com/sritchie/midje-cascalog/blob/develop/src/midje/cascalog.clj#L39).

If you'd like more information or additional features, please add your thoughts to the [midje-cascalog github issues page](https://github.com/sritchie/midje-cascalog/issues), or let me know in the comments below (or on twitter! I'm @sritchie09.)
