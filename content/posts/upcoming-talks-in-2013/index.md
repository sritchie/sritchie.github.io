---
title: "Upcoming Talks in 2013"
date: 2013-08-24T22:24:00.000Z
slug: upcoming-talks-in-2013
tags:
  - code
  - talks
---

This is the year I teach myself to become a better public speaker. I've spent the past year coding up a number of powerful [Scala and Clojure projects](http://sritchie.github.io/projects/), all the while avoiding the important and difficult work of teaching and writing about the import and use of those projects. Well, no longer.

To mind that gap I'll be giving a number of talks in 2013 on my recent work on Summingbird and Cascalog. If you're in the Bay Area, Boston, or Northern VA (my home town!), I'd love to meet you.

#### Introduction to Summingbird (Sept 3rd, Bay Area Storm Users)

[Oscar Boykin](http://twitter.com/posco) and I will be giving an Introduction to Summingbird at the Bay Area Storm Users meetup on Tuesday, September 3rd. Summingbird is a streaming MapReduce framework we developed at Twitter that allows you to write a streaming computation once and execute it in batch-mode on Scalding, in realtime mode on Storm, or on both Scalding and Storm in a hybrid batch/realtime mode that has very attractive fault tolerance properties. Sound exciting? RSVP at the event's [meetup page](http://www.meetup.com/Bay-Area-Storm-Users/events/135403842/).

#### Realtime MapReduce at Twitter(Sept 22nd, CUFP)

Check this one out at the [Commercial Users of Functional Programming](http://cufp.org/conference/sessions/2013/sam-ritchie-twitter-inc-realtime-mapreduce-twitter) conference, September 22nd-24th in Boston. This talk will focus more on the functional programming ideas we used in the design of Summingbird's real-time MapReduce DSL and its component libraries ([Storehaus](https://github.com/twitter/storehaus), [Bijection](https://github.com/twitter/bijection), and [Algebird](https://github.com/twitter/algebird)). Which ideas helped our design? What hurt?

#### Summingbird, Scala and Storm (Sept 25th, Boston Storm Users)

Another Introduction to Summingbird talk, with a focus on how Scala's type system and style helps us write correct Storm topologies. Register at the Boston Storm Users' [meetup page](http://www.meetup.com/Boston-Storm-Users/events/135630522/).

#### Twitter: Taking Hadoop Realtime with Summingbird (Oct 19th, PNWScala)

This talk at the [Pacific Northwest Scala Conference](http://pnwscala.org/) will get into the guts of Summingbird's batch/realtime merging abstraction and the streaming MapReduce graph planner we've developed. Here's the abstract:

> Twitter's Summingbird library allows developers and data scientists to build massive streaming MapReduce pipelines without worrying about the usual mess of systems issues that come with realtime systems at scale. This talk will discuss the development of Summingbird's hybrid Batch and Realtime operating mode, the power of clean, mathematical abstractions and the massive creative leverage that functional design constraints can give to a project.
> The talk will also discuss some of the applications for these technologies currently being used at Twitter.

Registration is filling up fast, so [sign up today!](https://pnwscala2013.eventbrite.com/?ref%3Delink)

## Streaming MapReduce in Clojure (Nov 14-16, Clojure/Conj)

This talk will discuss my work on [Cascalog 2](https://groups.google.com/forum/#!topic/cascalog-user/F8EkFM7HiE0) and its new &quot;execution platform&quot; abstraction. The recent Cascalog 2 redesign split the datalog compiler apart from the underlying Cascading functions that get called when you run a Cascalog query on a MapReduce cluster. With luck, by the time I deliver the talk, Cascalog will be able to run on [Trident](https://github.com/nathanmarz/storm/wiki/Trident-tutorial) and [Spark](https://github.com/mesos/spark).

I'll be delivering this talk in my hometown of Alexandria, VA at this year's [Clojure/Conj](http://clojure-conj.org/).

#### So You Want to Build a MapReduce DSL? (Jan 11th, Data Day Texas, Austin TX)

Still working on the meat of this one, but some initial thoughts - I'd like discuss the vast number of choices in the MapReduce DSL world. Spark, Scoobi, Summingbird, Scalding… folks are writing Hadoop DSLs in Ruby, in Mathematica, in Clojure. Where does it end? What's the right level of abstraction? This talk will discuss why so many different options exist and some pitfalls to beware of when choosing between them.

More information on Data Day Texas, including registration info, on the [event page](http://datadaytexas.com/).
