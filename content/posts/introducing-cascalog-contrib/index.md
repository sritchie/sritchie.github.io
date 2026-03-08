---
title: "Introducing Cascalog-Contrib"
date: 2011-11-16T00:24:00.000Z
slug: introducing-cascalog-contrib
tags:
  - code
  - cascalog
  - clojure
categories:
  - programming
---

I've had the pleasure of working with [Cascalog](https://github.com/nathanmarz/cascalog) for about ten months now, and have seen the community produce some fantastic work. A [number of businesses](https://www.assembla.com/spaces/cascalog/wiki/Who's_using_Cascalog) are using Cascalog in production; I use Cascalog at Twitter every day to write MapReduce queries for the new [Twitter Web Analytics](http://techcrunch.com/2011/09/13/twitter-analytics/) product.

One thing Cascalog doesn't yet have is a community repository for generic queries and operations. To fill this gap we've created [cascalog-contrib](https://github.com/nathanmarz/cascalog-contrib).

Cascalog-contrib will be home to any higher-level abstractions over Cascalog that the community is willing to submit. If you have an idea for a module, file a pull request on GitHub or bring it up on the [mailing list](http://groups.google.com/group/cascalog-user) for discussion.

The first cascalog-contrib modules are now live on [clojars](http://clojars.org/cascalog-contrib). To include them in your leiningen or cake project, add any of the following to `project.clj`:

```
[cascalog-checkpoint "0.1.1"]
[cascalog-incanter "0.1.0"]
[cascalog-math "0.1.0"]
```

Contrib currently has three modules: `cascalog.math`, `cascalog.incanter` and `cascalog.checkpoint`. `math` and `incanter` are still fairly sparse, but `checkpoint` is quite interesting and battle-tested at Twitter. Read on if you're interested in the details of the `checkpoint` module; otherwise, I'll see you on the mailing list!

## cascalog.contrib.checkpoint<a id="sec-1-1" name="sec-1-1"></a>

The `workflow` macro in the checkpoint module allows you to break complicated workflows out into small, checkpointed steps. If one of these steps causes a job to fail and you restart the job, the workflow macro will skip every step up to the previous point of failure. Fault-tolerant MapReduce topologies ftw!

Let's look at the workflow macro in action. The following function takes an input-path to some existing Twitter data and an output-path, and executes a tweet-processing workflow with five steps:

```
(defn -main
  [input-path output-path]
  (workflow ["/tmp/example-checkpoint"]          
            step-1     ([:tmp-dirs [staging-path]]
                          (transfer-tweets input-path staging-path))

            step-2     ([:deps :last :tmp-dirs user-path]
                          (harvest-users staging-path user-path))

            step-3a    ([:deps step-2 :tmp-dirs [cluster-path friend-path]]
                          (cluster-users user-path cluster-path)
                          (count-friends user-path friend-path))

            step-3b    ([:deps step-2 :tmp-dirs age-path]
                          (examine-ages user-path age-path))

            final-step ([:deps :all]
                          (big-analysis cluster-path
                                        friend-path
                                        age-path
                                        output-path))))
```

Let's look at this one piece at a time. The first argument to `workflow` is a vector with some path that the workflow can use to stage temporary files.

```
(workflow ["/tmp/example-checkpoint"] ...)
```

It doesn't matter what path you choose; just make sure that Hadoop has access and can write data to the folder.

Following this vector, `workflow` expects pairs of the form

```
step-name ([:deps <optional-deps, defaults to :last>]
             :tmp-dirs [<optional, creates temp-dirs if supplied>]
             ...<body, same as inside let>...)
```

Steps can identify other steps as dependencies by referencing their step-names with the `:deps` keyword argument.

The first step creates a temporary directory by supplying the symbol `staging-path` to the `:tmp-dirs` keyword argument. It then transfers tweets from the input directory into this staging directory, where they will remain available for future steps to consume.

```
step-1 ([:tmp-dirs [staging-path]]
          (transfer-tweets input-path staging-path))
```

Step 2 marks `:last` as a dependency. `:last` is the default, and marks the step as dependent only on the step directly above. A step will not execute until all of its dependencies have completed successfully.

`step-2` uses `staging-path` defined in `step-1` and creates a new temp directory (`user-path`) for its results.

If `step-2` fails for any reason and you restart the workflow, the workflow macro will skip `step-1`, destroy any temporary directories created in the previous run of `step-2`, and start `step-2` afresh.

```
step-2 ([:deps :last :tmp-dirs user-path]
          (harvest-users staging-path user-path))
```

The next two steps, `step-3a` and `step-3b`, each mark `step-2` as a dependency. Once `step-2` completes, `step-3a` and `step-3b` will run in parallel.

```
step-3a ([:deps step-2 :tmp-dirs [cluster-path friend-path]]
           (cluster-users user-path cluster-path)
           (count-friends user-path friend-path))
  
step-3b ([:deps step-2 :tmp-dirs age-path]
           (examine-ages user-path age-path))
```

The final step marks its dependencies as `:all`. This signifies that the step must wait for every step defined above it to complete before running. Again, if `final-step` fails and the workflow restarts, all previous successful steps will be skipped.

```
final-step ([:deps :all]
              (big-analysis cluster-path
                            friend-path
                            age-path
                            output-path))
```

## In Conclusion<a id="sec-1-2" name="sec-1-2"></a>

I'm quite excited about the Cascalog-contrib project and hope you all make heavy use of it as its functionality grows. In the short-term, I'm planning on hooking Cascalog in to [Incanter's](http://incanter.org/) amazing visualization suite through the `cascalog.incanter` module.
