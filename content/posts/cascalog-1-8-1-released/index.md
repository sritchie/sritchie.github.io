---
title: "Cascalog 1.8.1 Released"
date: 2011-09-26T22:24:00.000Z
slug: cascalog-1-8-1-released
tags:
  - code
  - cascalog
  - clojure
categories:
  - programming
---

[Nathan Marz](http://nathanmarz.com/) and I are releasing Cascalog 1.8.1 today! We've added a few interesting features, and I thought I'd provide a bit more detail here for anyone interested.

## Cross Join<a id="sec-1-1" name="sec-1-1"></a>

`cascalog.api` now includes support for [cross-joins](http://en.wikipedia.org/wiki/Join_(SQL)#Cross_join); just add `(cross-join)` to your query as its own predicate.

Think of a cross-join as a "tuple comprehension", or cartesian product, with similar results to `clojure.core/for`; it's not very efficient, as it forces all tuples through a single reducer (and causes a massive blowup in the number of tuples!). Here's an example:

```clojure
(let [a-src [[1] [2]]
      b-src [[3] [4]]]
  (?<- (stdout)
       [?a ?b]
       (a-src ?a)
       (b-src ?b)
       (cross-join)))
```

This results in the following on `stdout`:

```
RESULTS
-----------------------
1       3
1       4
2       3
2       4
-----------------------
```

If you're interested, here's the implementation:

```clojure
(def cross-join
  (<- [:>] (identity 1 :> _)))
```

This is the only predicate macro I know of that can get away with no input OR output vars.

## defmain<a id="sec-1-2" name="sec-1-2"></a>

When running a cascalog query on a cluster, usual practice is to include `(:gen-class)` in the namespace form, and write a `-main` method that gets AOT-compiled and called by Hadoop. This can be a little annoying, if you have a bunch of small queries you want to run.

`defmain` lets you skip the `:gen-class` form and write something like:

```clojure
;; inside myproject.jobs...  
(defmain FirstQuery [in-path out-path]
  (?- (hfs-textline out-path)
      (some-query in-path)))

(defmain SecondQuery [out-path]
  (?<- (hfs-textline out-path)
       [?a ?b] ...))
```

Each `defmain` will compile to a class with the supplied name, prefixed by the namespace. (`myproject.jobs.FirstQuery` and `myproject.jobs.SecondQuery`, in this example.)

(As always, make sure to add the `:aot [myproject.jobs]`, kv-pair to `project.clj`, including each namespace containing a `defmain` or `(:gen-class)` in the vector. If you want to call some `defmain` function directly, `(defmain Query ...)` can be called from the REPL with `(Query-main ...)`.) I recommend keeping your `defmain` functions skinny, and testing the components it calls.

## with-serializations<a id="sec-1-3" name="sec-1-3"></a>

Damn you, serializations. This one JobConf entry, "io.serializations", has caused me much pain. We've added `with-serializations`, which makes the supplied Hadoop serializations available to all queries enclosed within the form. These forms nest, and play well with the existing `with-job-conf`. For example:

```clojure
;; You can specify serializations in string form...
(with-serializations ["org.apache.hadoop.io.serializer.JavaSerialization"]
  (<- [?a] ...))

;; ... or directly, with the class.
(import 'org.apache.hadoop.io.serializer.JavaSerialization)

(with-serializations [JavaSerialization]
  (<- [?a] ...))

;; Serializations nest and unique against each other!
(with-job-conf {"io.serializations" "my.ns.SomeSerialization"}
  (with-serializations [JavaSerialization OtherSerialization]
    (with-serializations ["my.ns.SomeSerialization" ThirdSerialization]
      (<- [?a] ...))))
```

## cascalog.ops/first-n<a id="sec-1-4" name="sec-1-4"></a>

`first-n` can now handle straight-up vectors, lists, and cascading taps, in addition to queries.

Say we've previously run a wordcount job that output `[?word ?count]` 2-tuples to a sequencefile, and we want to pull the top 100 words by count. Here's how we do that with first-n:

```clojure
(use 'cascalog.api)
(require '[cascalog.ops :as c])

(defn wordcount-tap [path]
  (-> (hfs-seqfile path)
      (name-vars ["?word" "?count"])))

(defn top-100 [file-path]
  (c/first-n (wordcount-tap path)
             100
             :sort ["?count"]
             :reverse true))

(defmain Top100 [tuple-path results-path]
  (?- (hfs-textline results-path)
      (top-100 tuple-path)))
```

`first-n` with vectors and lists is mostly interesting for testing purposes.

## Other Bugfixes<a id="sec-1-5" name="sec-1-5"></a>

Just a few bugfixes to note:

- Fixed a bug preventing cascalog-taps in `(:trap (some-tap ...))` option predicates.
- Fixed bug preventing keywords as static arguments (as [demonstrated here](https://github.com/nathanmarz/cascalog/blob/master/test/cascalog/api_test.clj#L439)).
- Failed cascading flows now always throw errors. (This is a workaround to a Cascading bug that allows some flows to fail silently.)
