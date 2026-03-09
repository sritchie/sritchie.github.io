---
title: "Cascalog 2.0 In Depth"
date: 2015-01-03T20:46:56.000Z
slug: cascalog-2-0-in-depth
tags:
  - code
  - cascalog
  - clojure
categories:
  - programming
---

Cascalog 2.0 has been out for over a year now, and outside of a [post to the mailing list](https://groups.google.com/d/topic/cascalog-user/F8EkFM7HiE0/discussion) and a talk at [Clojure/Conj 2013](https://www.youtube.com/watch?v%3DuuJW3EaN_3Q) ([slides here](https://speakerdeck.com/sritchie/cascalog-2-dot-0-datalog-in-realtime)), I've never written up the

startingly long list of new features brought by that release. So shameful.

This post fixes that. 2.0 was a big deal. Anonymous functions make it easy to reuse your existing, non Cascalog code. The interop story with vanilla Clojure is much better, which is huge for testing. Finally, users can access the JobConf, Cascading's counters and other Cascading guts during operations.

Here's a list of the features I'll cover in this post:

- new def*ops,
- Anonymous function support
- Higher order functions
- Lifting Clojure functions into Cascalog
- expand-query
- Using functions as implicit filters in queries
- prepared functions, and access to Cascading's guts

As if that weren't enough, 2.0 adds a standalone Cascading DSL with an API similar to [Scalding's](https://github.com/twitter/scalding). You can move between this Cascading API and Cascalog. This makes it easy to use Cascading's new features, like optimized joins, that haven't bubbled up to the Cascalog DSL.

I'll go over the Cascading DSL and the support for non-Cascading execution environments in a later post. For now, let's get into it.

If you want to follow along, go ahead and clone [the Cascalog repo](https://github.com/nathanmarz/cascalog), cd into the "cascalog-core" subdirectory and run "lein repl". To try this code out in other projects, run "lein sub install" in the root directory. This will install `[cascalog/cascalog-core "3.0.0-SNAPSHOT"]` locally, so you can add it to your `project.clj` and give the code a whirl.

# def*fn macros

Testing Cascalog operations has always been a pain. Before Cascalog 2.0, when you defined a function with any of the `def*op*` macros, you couldn't call it as a function outside of a Cascalog query. Cascalog has a [great testing story](/testing-cascalog-with-midje/) for queries, but the only way to test single operations was in the context of a Cascalog job.

As of 2.0, functions defined with any of the `def*op` macros are now just normal functions, making it **much** easier to write tests, or to use them outside of Cascalog.

```clojure
(defmapop square [x] (* x x))
(square 10)
;;=> 100

(deftest square-squares-test
  (is (= 100 (square 10))))
;; Passes!
```

I've also deprecated all of the `def*op` macros in favor of `def*fn` macros. Only the suffix has changed; the behaviors are all the same. `defmapop` becomes `defmapfn`, and so on and so forth. All of the `def*op` will continue working, but you'll get a deprecation notice when the old forms are evaluated.

# Anonymous functions

The biggest addition to Cascalog's API is a suite of macros that let you use anonymous functions as Cascalog operations.

Anonymous functions are tricky beasts. They haven't been supported as operations until now because Cascalog has to serialize all operations that it calls, and function serialization is a hellish problem. Thanks to Nathan's strong work on a [serializable function](https://github.com/nathanmarz/cascalog/blob/fd77c4d74eb8bcaf2f2996a280f53b37378c927a/cascalog-core/src/clj/cascalog/logic/fn.clj) macro, Cascalog 2.0 adds anonymous variants on the `def*fn` macros: `mapfn`, `filterfn`, `mapcatfn`, `bufferfn`, `bufferiterfn` and `aggregatefn`.

Here's an example of a pre-2.0 query for squaring numbers:

```clojure
(defn square [x]
    (* x x))

(??<- [!x !squared]
      (src !x)
      (square !x :> !squared))
;;=> ([1 1] [2 4] [3 9] [4 16] [5 25])
```

It's now possible to define `square` inline using `cascalog.api/mapfn`:

```clojure
(??<- [!x !squared]
      (src !x)
      ((mapfn [x] (* x x)) !x :> !squared))
  ;;=> ([1 1] [2 4] [3 9] [4 16] [5 25])
```

Boom. `mapfn`, `filterfn` and `mapcatfn` are the anonymous alternatives to, respectively, `defmapfn`, `deffilterfn` and `defmapcatfn`.

## Anonymous Aggregators

You can also define aggregators inline:

```clojure
(def pairs
  [[1 1] [1 2] [1 3] [2 4] [2 5]])

(let [sum (aggregatefn
           ([] 0)
           ([acc y] (+ acc y))
           ([x] [x]))]
  (??<- [?x ?sum]
        (sum ?y :> ?sum)
        (pairs ?x ?y)))
;;=> ([1 6] [2 9])
```

`sum` here is created using `aggregatefn`, the in-line alternative to `defaggregatefn`. `bufferfn` and `bufferiterfn` mirror `defbufferfn` and `defbufferiterfn`, respectively. All of the required function arities are the same.

You can also turn any two-argument Clojure function into a parallel aggregator with `parallelagg`. The definition of a map-side optimized `sum` operation is now as easy as:

```clojure
(??<- [?x ?sum]
      ((parallelagg +) ?y :> ?sum)
      (pairs ?x ?y))
;;=> ([1 6] [2 9])
```

# higher order functions

One result of the new anonymous function syntax is that higher-order function definitions become easy. To parametrize operations, the old syntax required you to use an extra vector around the operation's name, like this:

```clojure
(defmapop [times [x]]
  [y]
  (* x y))
```

Higher order parameters were supplied with a vector after the operation name:

```clojure
(??<- [!x !y]
      (src !x)
      (times [4] !x :> !y))
;;=> ([1 4] [2 8] [3 12] [4 16] [5 20])
```

What a pain in the ass, right?

In this new, beautiful world, you can accomplish the same goal by writing a vanilla Clojure function that returns an anonymous Cascalog function:

```clojure
(defn times [x]
  (mapfn [y] (* x y)))

(let [times-four (times 4)]
  (??<- [!x !y]
        (src !x)
        (times-four !x :> !y)))
;;=> ([1 4] [2 8] [3 12] [4 16] [5 20])
```

So GOOD! Now you can pass Cascalog operations around as first class objects, just like any other clojure function.

# Make Functions, Not Vars

Before Cascalog 2.0, if you wanted to write functions that returned queries, any operation passed as a function argument needed to be passed in as a var:

```clojure
(def src [1 2 3 4 5])

(defn square [x] (* x x))

(defn my-query [op]
  (??<- [!x !y]
        (src !x)
        (op !x :> !y)))

(my-query #'square)
;;=> ([1 1] [2 4] [3 9] [4 16] [5 25])
```

In Cascalog 2.0, bare functions work great as arguments:

```clojure
(my-query square)
```

This means that you can pass functions (or anonymous functions defined using the new macros) directly to `defparallelagg`:

```clojure
(defparallelagg sum
  :init-var identity
  :combine-var +)
```

# Function Lifting

Cascalog 2.0 includes a suite of functions that let you turn Clojure operations into Cascalog operations. Here's an example of how to use the new `mapop` and `mapcatop` functions to turn `clojure.core/str` into a mapping operation or a mapcat operation.

This first block shows `str` wrapped in `mapop`:

```clojure
(def src [["four"] ["score"]])

(let [map-str (mapop str)]
  (??<- [?string ?string-copy]
        (src ?string)
        (map-str ?string :> ?string-copy))
  ;;=> (("four" "four") ("score" "score"))
  )
```

Calling `str` on each of the strings in `src` just kicks the input string back out, so the result is a sequence of pairs of the same string.

Wrapping `str` in `mapcatop` produces a different result:

```clojure
(let [mapcat-str (mapcatop str)]
  (??<- [?string ?letter]
        (src ?string)
        (mapcat-str ?string :> ?letter)))
    ;;=> (("four" \f) ("four" \o) ("four" \u)
    ;;    ("four" \r) ("score" \s) ("score" \c)
    ;;    ("score" \o) ("score" \r) ("score" \e))
```

Here, the result of `(mapcatop str)` is interpreted as a **sequence of tuples**, rather than as a sequence of fields. Because a string is a sequence of characters, the operation generates a new tuple for every character in its input string.

The new functions in `cascalog.api` are `mapop`, `filterop`, `mapcatop`, `bufferop`, `aggregateop`, `bufferiterop` and `parallelagg`.

(Note: `mapop` and `filterop` are really no-ops, since Cascalog interprets vanilla Clojure functions as mapping operations if an output variable is supplied, and as a filter if outputs aren't. You might as well just use the vanilla operation directly.)

To belabor the point, you can think of these `*op` wrappers as a way to apply the `def*fn` macros to a function defined with `defn`. For example, in this block:

```clojure
(defn some-function*
  ([x] ,,,,))

(def some-function (aggregateop some-function*))
```

The `some-function` operation will work exactly the same as the one defined here:

```clojure
(defaggregatefn some-function
    ([x] ,,,,))
```

# expand-query

`expand-query` is extremely helpful for understanding how predicate macros and other syntax shortcuts affect your Cascalog queries.

The syntax is the same as `??<-` or `<-`. Just replace either of those macros with `expand-query`.

The following query has a couple of implicit filters:

- The count of each `?string` must be even
- calling `(str ?string "fun")` on each `?string` must produce "fourfun"

Let's look at the expansion.

```clojure
(let [src [["four"] ["score"]]]
  (expand-query [?string ?string-copy]
                (src ?string)
                (count ?string :> even?)
                (str ?string "fun" :> "fourfun")))
;; (<- [?string ?string-copy]
;;     ([[four] [score]]  :> ?string)
;;     (#'clojure.core/even? !G__8494)
;;     (#'clojure.core/count ?string :> !G__8494)
;;     (#'clojure.core/= fourfun !G__8495)
;;     (#'clojure.core/str ?string fun :> !G__8495)
;;     )
```

The three defined predicates expand out to five predicates.

The `count` operation actually outputs to a randomly named variable, which is tested against `clojure.core/even?` in a separate predicate.

The call to `(str ?string "fun")` generates a temporary variable, `!G__8495`, which gets compared to "fourfun" in a separate, expanded filter. Pretty cool!

# Functions as guards

Cascalog has always let you filter logic variables against constants by writing predicates like `(src ?a "handle")`. To filter using a function, you used to have to expand out that filter yourself, like this:

```clojure
(def pairs [[1 2] [2 4] [3 3]])

(??<- [?b]
      (* ?b 3 :> ?by-three)
      (even? ?by-three)
      (pairs odd? ?b))
;;=> ((2))
```

In Cascalog 2.0 you can place a function in an output variable position. Cascalog will automatically generate that filter for you.

```clojure
(??<- [?b]
      (* ?b 3 :> even?)
      (pairs odd? ?b))
;;=> ((2))
```

Swapping `expand-query` in for `??<-` shows the filters generated in the source and multiplication:

```clojure
(expand-query [?b]
                (* ?b 3 :> even?)
                (pairs odd? ?b))
  ;; (<- [?b]
  ;;     (#'clojure.core/even? !G__8294)
  ;;     (#'clojure.core/* ?b 3 :> !G__8294)
  ;;     (#'clojure.core/odd? !G__8295)
  ;;     (#'cascalog.api/pairs  :> !G__8295 ?b)
  ;;     )
```

The first variable produced by `pairs`, `!G__8295`, is filtered by `odd?`. The result of the multiplication gets assigned to a temporary variable, and that variable gets filtered against `even?`.

# prepared functions

Cascalog 2.0's `prepfn` and `defprepfn` makes it easy to get access to the [FlowProcess](http://docs.cascading.org/cascading/2.0/javadoc/cascading/flow/FlowProcess.html) and [ConcreteCall](http://docs.cascading.org/cascading/2.0/javadoc/cascading/operation/ConcreteCall.html) instances provided by Cascading. This lets you increment counters and get access to the `JobConf` within your operations. Here's an example of how to use `prepfn`:

```clojure
(import 'cascading.flow.hadoop.HadoopFlowProcess)
(import 'cascading.operation.ConcreteCall)

(defprepfn times-with-path
  [^HadoopFlowProcess a ^ConcreteCall b]
  (let [multiplier 2]
    (mapfn [y] [(* multiplier y)
                (-> (.getConfigCopy a)
                    (.get "mapred.input.dir"))])))
```

This operation outputs the double of the input, along with the temporary file that Cascalog's generated for Cascading to use as a source. Notice that you can use a `let` binding to perform setup before returning an operation.

`defprepfn` creates a higher-order function of two parameters that Cascading calls after the Hadoop job begins. Cascading passes in the `HadoopFlowProcess` and `ConcreteCall` instances, and use the returned function as the operation:

```clojure
(??<- [!x !y !conf]
      (src !x)
      (times-with-path !x :> !y !conf))
;;=> ([1 2 "file:/211a1120-fb5e-4d10-aa9e-25227fd95935"]
      [2 4 "file:/211a1120-fb5e-4d10-aa9e-25227fd95935"]
      [3 6 "file:/211a1120-fb5e-4d10-aa9e-25227fd95935"]
      [4 8 "file:/211a1120-fb5e-4d10-aa9e-25227fd95935"]
      [5 10 "file:/211a1120-fb5e-4d10-aa9e-25227fd95935"])
```

`prepfn` is the anonymous version of `defprepfn`. You can use `prepfn` along with the higher-order function trick described above to parametrize prepared functions created with `prepfn`:

```clojure
(defn times-with-path [x]
  (prepfn [^HadoopFlowProcess a ^ConcreteCall b]
          (mapfn [y] [(* x y) (-> (.getConfigCopy a)
                                  (.get "mapred.input.dir"))])))

(??<- [!x !y !conf]
      (src !x)
      ((times-with-path 2) !x :> !y !conf))
```

If you need to perform some sort of cleanup - say, closing a connection to an external database, or incrementing some final counter - just return a map from the body of your `prepfn`. Cascalog will use the operation under the `:operate` key as the actual operation. At the end of operation, Cascalog will call the function you store under `:cleanup`.

This example uses `mapfn` for operation and cleanup because these functions have to be serializable:

```clojure
(defn times-with-path [x]
  (prepfn [^HadoopFlowProcess a ^ConcreteCall b]
          {:operate (mapfn [y] [(* x y) (-> (.getConfigCopy a)
                                            (.get "mapred.input.dir"))])
           :cleanup (mapfn [] (println "FINISHED!"))}))
```

# Questions?

If you have any questions on this new functionality, feel free to comment below, hit up [the mailing list](https://groups.google.com/forum/#!forum/cascalog-user), or hit me up [on Twitter](https://twitter.com/sritchie). If you're still on Cascalog 1.x I'd love to help you migrate.
