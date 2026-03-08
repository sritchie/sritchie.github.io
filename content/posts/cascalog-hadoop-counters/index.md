---
title: "Cascalog + Hadoop Counters, Finally!"
date: 2015-02-21T00:08:06.000Z
slug: cascalog-hadoop-counters
tags:
  - code
  - cascalog
  - clojure
categories:
  - programming
---

I've just merged a Cascalog [pull request of mine](https://github.com/nathanmarz/cascalog/pull/270) that gives Cascalog operations access to the statistics that Cascading generates at the end of each job. I've also added global `inc!` and `inc-by!` functions that let you increment custom Hadoop counters from within your functions and operations without having to deal with all that `prepfn` nastiness we introduced in Cascalog 2.0. Here's [a link to the code](https://github.com/nathanmarz/cascalog/blob/develop/cascalog-core/src/clj/cascalog/cascading/stats.clj#L49). If you want to follow along, or just want to get the hell away from this blog and start playing with the code now, get yourself a copy of the new snapshot:

```
[cascalog/cascalog-core "3.0.0-SNAPSHOT"]
```

Or, for those of you who are like me and hate SNAPSHOT builds:

```
[cascalog/cascalog-core "3.0.0-20150220.233712-1"]
```

### Counters

With the new interface you can increment Hadoop's counters inside your functions:

```
(defn square [x]
  (stats/inc-by! "tuples" x)
  (* x x))
```

If you call that definition of `square` outside of a Cascalog query - in a test, for example - the `inc-by!` call is a no-op. Inside of a running query you'll increment the relevant Hadoop counter.

### Stats Access

I've also added a new option predicate, `:stats-fn`, that lets you access these stats at the end of a job run. `:stats-fn` takes a function that accepts an instance of `cascalog.cascading.StatsMap`. (Oh, yeah - I'm obsessed with Prismatic's [Schema](https://github.com/Prismatic/schema). I'm holding out hope that the fantastic documentation that library provides will finally entice more contributors into the murky swamps of Cascalog's codebase.)

There are three default stats functions in the [cascalog.cascading.stats](https://github.com/nathanmarz/cascalog/blob/develop/cascalog-core/src/clj/cascalog/cascading/stats.clj) namespace:

- [`(stdout)`](https://github.com/nathanmarz/cascalog/blob/develop/cascalog-core/src/clj/cascalog/cascading/stats.clj#L125) prints out any custom counters you've used in tab-separated format to stdout. You can also supply a custom group name, if you've namespaced your stats.
- [`(clojure-file &lt;filename&gt;)`](https://github.com/nathanmarz/cascalog/blob/develop/cascalog-core/src/clj/cascalog/cascading/stats.clj#L141) prints the entire stats object in Clojure format to the supplied path.
- [`(json-file &lt;filename&gt;)`](https://github.com/nathanmarz/cascalog/blob/develop/cascalog-core/src/clj/cascalog/cascading/stats.clj#L147) does the same, but formats the output as JSON.

Here's an example query using the new option:

```
(??<- [?x ?y]
      ([1 2 3] ?x)
      (:stats-fn (stats/stdout))
      (square ?x :> ?y))
```

(Check out `square` above again to see how I'm incrementing the counter.) Executing that query returns the following:

```
user>
(??<- [?x ?y]
      ([1 2 3] ?x)
      (:name "StatsTestJob")
      (:stats-fn (stats/stdout))
      (square ?x :> ?y))
Custom counters for group CascalogStats:
tuples    6
;;=> ([1 1] [2 4] [3 9])
```

Boom! Custom counters printed out for your pleasure. The full stats object looks more like this:

The actual stats object is a lot more detailed, so you'll have to play around yourself. Oh, what the hell, I'll print it. It looks like this:

```
{:name "StatsTestJob",
 :start-time 1424474244707,
 :run-time 1424474244807,
 :duration 101,
 :counters
 {"org.apache.hadoop.mapred.FileInputFormat$Counter" {"BYTES_READ" 0},
  "cascading.flow.SliceCounters"
  {"Write_Duration" 0,
   "Process_End_Time" 1424474244790,
   "Read_Duration" 1,
   "Tuples_Read" 3,
   "Tuples_Written" 3,
   "Process_Begin_Time" 1424474244775},
  "org.apache.hadoop.mapred.FileOutputFormat$Counter"
  {"BYTES_WRITTEN" 124},
  "CascalogStats" {"counter" 6},
  "FileSystemCounters"
  {"FILE_BYTES_READ" 4619437, "FILE_BYTES_WRITTEN" 5918762},
  "cascading.flow.StepCounters" {"Tuples_Read" 3, "Tuples_Written" 3},
  "org.apache.hadoop.mapred.Task$Counter"
  {"SPILLED_RECORDS" 0,
   "MAP_INPUT_BYTES" 3,
   "MAP_INPUT_RECORDS" 3,
   "MAP_OUTPUT_RECORDS" 3,
   "SPLIT_RAW_BYTES" 294,
   "COMMITTED_HEAP_BYTES" 344981504}},
 :finished-time 1424474244808,
 :successful? true,
 :submit-time 1424474244739,
 :id "D9AA6A80E4AB4BFDBB260C66957D981D",
 :skipped? false,
 :failed? false,
 :stopped? false}
```

This feature has been a long time coming. Huge thanks to the Factual guys for supporting Cascalog development and giving me a chance to work on this in my spare time. Check out `3.0.0-SNAPSHOT` and let me know what you think, in the comments below or on the [Cascalog mailing list](https://groups.google.com/forum/#!forum/cascalog-user).
