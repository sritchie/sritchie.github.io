---
title: "Hardcore Cascalog: Dynamic Queries"
date: 2015-01-01T03:09:32.000Z
slug: dynamic-cascalog-queries
tags:
  - code
  - cascalog
  - clojure
categories:
  - programming
---

A little side note before I get started - pivoting from my last post on [ski mountaineering racing](/skimo-racing/) to this post on advanced [Cascalog](https://github.com/nathanmarz/cascalog) patterns has made me realize that I'm a full-fledged connoisseur of the esoteric. I'm embracing it! This is the first in a series of posts on hardcore Cascalog. If you're stoked, leave me a comment telling me what you want to learn more about and we'll go from there.

While Cascalog's primitives and operations can get you pretty far down the Big Data yellow brick road, advanced users will need to go beyond the basics and generate queries and predicates dynamically. Because Cascalog queries are just Clojure data structures, you can abstract out patterns by writing functions that return custom Cascalog queries. Here's a contrived example:

```clojure
(defn perform-on-all [src f]
  (<- [?result]
      (src ?x)
      (f ?x :> ?result)))
```

This function takes a source (of 1-tuples) and a function, and returns a new source with that function applied to all tuples. (In vanilla Clojure, this is `map`). It works because the number of predicates in the query doesn't depend on any of the function arguments. It's always just that one predicate. But what if you wanted to generate *more* predicates based on the function's arguments?

The [cascalog.logic.ops](https://github.com/nathanmarz/cascalog/blob/103d206728100083267564f6e57e930535418df3/cascalog-core/src/clj/cascalog/logic/ops.clj) namespace defines a bunch of higher order functions that require this trick. This post is going to walk through the implementation of one of those functions - `cascalog.logic.ops/juxt`. Cascalog's `juxt` works like [Clojure's juxt](https://clojuredocs.org/clojure.core/juxt), but can accept any Cascalog operation as an argument, not just Clojure functions. As we'll see, `juxt` needs to generate one predicate for every argument, and should support any number of arguments. Let's look at Clojure's `juxt` to see how to begin.

# Juxt!

In vanilla Clojure, you use `juxt` to apply multiple operations to the same input variables:

```clojure
(let [compound-fn (juxt inc square dec)]
  (compound-fn 10))
;;=> [11 100 9]
```

`juxt` returns a function that generates a vector with an entry for each of the functions passed to `juxt`. [ClojureDocs](https://clojuredocs.org) has some [nice examples](https://clojuredocs.org/clojure.core/juxt).

What's the Cascalog equivalent of `juxt`? This pattern, applying a bunch of operations to the same input, shows up all over. Here's a contrived example - for each of a collection of numbers, calculate the increment, the decrement and the square.

```clojure
(defn square [x] (* x x))

(let [src [[1] [2] [3]]]
  (??<- [?incs ?squares ?decs]
        (src ?x)
        (inc ?x :> ?incs)
        (square ?x :> ?squares)
        (dec ?x :> ?decs)))
;;=> ([2 1 0] [3 4 1] [4 9 2])
```

The query is similar to this Clojure code block:

```clojure
(let [src    [1 2 3]
      step-1 (map inc src)
      step-2 (map square src)
      step-3 (map dec src)]
  (map vector step-1 step-2 step-3))
;;=> ([2 1 0] [3 4 1] [4 9 2])
```

Here's the same block, using `juxt` and killing the `let` binding:

```clojure
(map (juxt dec square inc) [1 2 3])
;;=> ([2 1 0] [3 4 1] [4 9 2])
```

Clojure's `juxt` allowed us to clean up the boilerplate of passing `src` into each of those functions. What we want in Cascalog is a function, call it `juxt*`, that'll let us avoid the repetition that showed up in the example query above. Here's a new query written in [wishful thinking](http://c2.com/cgi/wiki?WishfulThinking) style:

```clojure
(let [src [[1] [2] [3]]]
  (??<- [?incs ?squares ?decs]
        (src ?x)
        ((juxt* inc square dec) ?x :> ?incs ?squares ?decs)))
```

How can we implement `juxt*`? One option would be to write a function that takes functions returns a [predicate macro](http://cascalog.org/articles/predicate_macros.html). (See the end of the post for a short refresher on predicate macros.) It's easy for a few of the arities, but things quickly devolve.

```clojure
(defn juxt*
  ([f]
     (<- [!x :> !a]
         (f !x :> !a)))
  ([f g]
     (<- [!x :> !a !b]
         (f !x :> !a)
         (g !x :> !b)))
  ([f g h]
     (<- [!x :> !a !b !c]
         (f !x :> !a)
         (g !x :> !b)
         (h !x :> !c)))
  ,,,, ;; madness!
  )
```

The problem here is that you need one predicate for each of the input functions. To match Clojure's `juxt`, `juxt*` needs to be able to handle as many functions as you throw at it. If `<-` were a function instead of a macro, we could just `apply` it to the predicates. "Oh my god," I hear you sigh. "Could a function version of `<-` exist?" Boom, from stage left, enter `cascalog.api/construct`.

# construct

The `<-` macro is a thin wrapper around the `cascalog.api/construct` function. All `<-` does is

- convert symbols beginning with `?` or `!` into strings (since Cascalog variables are represented by strings, not symbols),
- allow you to use lists instead of vectors for the predicates in your queries,
- that's it. There's nothing else. Isn't it so simple?

The following queries are all identical. Here's a Cascalog query written in the style I use in my examples:

```clojure
(def src [[1] [2] [3]])

(<- [?x ?square]
    (src ?x)
    (odd? ?x)
    (* ?x ?x :> ?square))
```

Because `<-` converts logic variables to strings, doing that conversion ourselves is a no-op:

```clojure
(<- ["?x" "?square"]
    (src "?x")
    (odd? "?x")
    (* "?x" "?x" :> "?square"))
```

Using vectors instead of lists is fine too. I think lists look prettier, but if `<-` were a function, Clojure would treat those lists as function applications. In fact, the lists are little special collections of operations and variables.

```clojure
(<- ["?x" "?square"]
    [src "?x"]
    [odd? "?x"]
    [* "?x" "?x" :> "?square"])
```

And finally, the same query using `construct`, with all macro sugar removed.

```clojure
(let [outputs    ["?x" "?square"]
      predicates [[src "?x"]
                  [odd? "?x"]
                  [* "?x" "?x" :> "?square"]]]
  (construct outputs predicates))
```

`construct` takes two arguments - the first is a a sequence of output variables, and the second is a sequence of predicates. `construct` solves `juxt*`'s problem. Because `construct` is a function, not a macro, the `juxt*` function can take any number of input functions and generate a predicate for each, then pass all those predicates into `construct`.

# Defining Juxt

First, I'll show the final definition of `juxt*`, then I'll go through it line by line. Here she blows:

```clojure
(require '[cascalog.logic.vars :as v])

(defn juxt*
  "Accepts any number of predicate operations and returns a new
  predicate that is the juxtaposition of those ops."
  [& ops]
  (let [outvars (v/gen-nullable-vars (count ops))]
    (construct
     ["!input" :>> outvars]
     (map (fn [o v] [o "!input" :> v])
          ops
          outvars))))
```

The first thing this `juxt*` implementation does is generate a randomly-named logic variable for each supplied operation using `v/gen-nullable-vars`. This list is bound to `outvars`.If you look at the first query example:

```clojure
(let [src [[1] [2] [3]]]
  (<- [?incs ?squares ?decs]
      (src ?x)
      (inc ?x :> ?incs)
      (square ?x :> ?squares)
      (dec ?x :> ?decs)))
```

Every operation that acts on `?x` has a distinct output. Calling `(juxt* inc square dec)` generates three logic variables internally and binds them to `outvars`.

Next, `construct`'s two arguments are declared inline. This version of `juxt*` only allows a single input variable to each function, so we can just make up a variable name. Let's call it `!input`. (I'll go over how to extend `juxt` to multiple inputs in a future post.)

The outputs are the `outvars` generated before. As discussed in the [Predicate Operators](http://cascalog.org/articles/predicate_operators.html) section of the docs, `:>>` allows a predicate to use a vector of logic variables as its output. The same rule applies to predicate macro signatures.

All that's left to create are the predicates. Predicates are vectors of the form `[<operation> !input :> <output-variable>]`. (The grammar's more complicated, but this will do for now.) Because predicates are **just** vectors, and `construct` needs a sequence of predicates, we can generate that sequence by mapping across the supplied ops:

```clojure
(map (fn [o v] [o "!input" :> v])
     ops
     outvars)
```

Mapping across `op` and `outvars` at the same time pairs each operation up with one of the fresh logic variables. And, just as we wanted, for each pair the anonymous function we're mapping outputs `[o "!input" :> v]`.

With this new definition, the wishful thinking example from above compiles and runs!

```clojure
(let [src [[1] [2] [3]]]
    (??<- [?incs ?squares ?decs]
          (src ?x)
          ((juxt* inc square dec) ?x :> ?incs ?squares ?decs)))
;;=> ([2 1 0] [3 4 1] [4 9 2])
```

So, there you have it. Dynamic query generation. Wasn't that easy?

In the next post, I'll show how to extend `juxt*` to handle multiple input arguments. If you want a head start, check out [Cascalog's definition of juxt](https://github.com/nathanmarz/cascalog/blob/103d206728100083267564f6e57e930535418df3/cascalog-core/src/clj/cascalog/logic/ops.clj#L86). The definition uses destructuring in the generated predicate macro, which, like the recipe for Coca Cola, is a feature that probably only a couple of living souls know about. If you know what I'm talking about, explain the feature in the comments and I'll come up with some sort of prize.

As I said in the beginning, I'm planning on writing more of these, and would love feedback on what parts of Cascalog you all want to hear more about. Leave me a comment below and I'll see what I can do.

To wrap things up, here's the promised primer on predicate macros.

# Predicate Macros :)

Even though "[predicate macro](http://cascalog.org/articles/predicate_macros.html)" has the word "macro" in it, you shouldn't be scared. (The smiley in the heading is a friendly smile, not a creepy one.) A predicate macro is just Cascalog's way of grouping together a bunch of operations into one new black-box operation. Predicate macros are how you declare "functions" in Cascalog's logic land.

For example, if you wanted to write a function that calculated the average value of some input variable, you'd probably want to reuse the efficient `sum` and `div` operations Cascalog provides in `cascalog.logic.ops`. Because `sum` is an aggregator, you can't compose these with `comp` like you would normal Clojure functions. Predicate macros make this composition easy:

```clojure
(def avg
  "Predicate operation that produces the average value of the
  supplied input variable.

  "
  (<- [!v :> !avg]
      (count !c)
      (sum !v :> !s)
      (div !s !c :> !avg)))
```

A predicate macro looks exactly like a normal query, except predicate macros allow input variables. You can tell that a query is a predicate macro because it'll have a `:>` or `:>>` in the argument vector separating input variables from output variables. Predicate macros like `avg` can be used in other queries like any operation:

```clojure
(let [src [[1] [2]]]
  (<- [?avg]
      (src ?x)
      (avg ?x :> ?avg)))
;;=> ([1.5])
```

Go forth and macro, my children.
