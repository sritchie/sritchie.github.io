---
layout: post
title: Simple Hadoop Clusters
---

{{ page.title }}
================

<p class="meta">31 May 2011 - Washington, DC</p>

# Pallet and Hadoop #

Over the past few months, I've grown increasingly frustrated with the complexity of cluster configuration tools for Apache's [Hadoop](http://hadoop.apache.org/). For those of you not in the know, Hadoop is an Apache java framework that allows for distributed processing of enormous datasets across large clusters. It combines a computation engine based on [MapReduce](http://en.wikipedia.org/wiki/MapReduce) with [HDFS](http://hadoop.apache.org/hdfs/docs/current/hdfs_design.html), a distributed filesystem based on the [Google File System](http://en.wikipedia.org/wiki/Google_File_System).

Abstraction layers such as [Cascading](https://github.com/cwensel/cascading) (for Java) and [Cascalog](https://github.com/nathanmarz/cascalog) (for [Clojure](http://clojure.org/)) make writing MapReduce queries quite nice. Indeed, running hadoop locally with cascalog [couldn't be easier](http://nathanmarz.com/blog/introducing-cascalog-a-clojure-based-query-language-for-hado.html).

Unfortunately, graduating one's MapReduce jobs to the cluster level isn't so easy. Amazon's [Elastic MapReduce](http://aws.amazon.com/elasticmapreduce/) is a great option; but what to do if you want to configure your own cluster?

Current solutions include [crane](https://github.com/getwoven/crane/tree/), which I found to be poorly documented, and [Cluster Chef](https://github.com/infochimps/cluster_chef/tree/version_2), which actually looks quite nice. Cluster Chef allows the user to supply a data driven description of a cluster, and boot it up using a command line utility written in Ruby.

I decided to forgo these options in favor of writing my own layer over [Pallet](https://github.com/pallet/pallet), a wonderful cloud provisioning library written in Clojure. Pallet runs on top of [jclouds](https://github.com/jclouds/jclouds), which allows pallet to define its operations independent of any one cloud provider. Switching between clouds involves a change of login credentials, nothing more.

## Goals ##

The goal of this project was to write an abstraction layer capable of converting a data-driven representation of a Hadoop cluster into the real thing, running on one of the many clouds.

Let's think of a cluster as a data structure composed of a number of groups of identically configured machines -- *node groups*. A node group has four properties:

1. **server spec**: a description of the software payload installed on each node
2. **machine spec**: The hardware configuration of each node
3. **property map**: Hadoop configuration properties unique to the node group
3. **count**: the number of nodes within the group.

#### Server Spec ####

A node group's server spec can be described by some combination of the following four roles:

* Jobtracker:  This is the king of mapreduce.
* Tasktracker: Jobtracker parcels out tasks to the tasktrackers.
* Namenode:    The king of HDFS.
* Datanode:    Datanodes hold HDFS chunks; they're coordinated by the namenode.

(I'll expand this to cover the secondary namenode soon.)

Tasktrackers and datanodes are slave nodes, and are usually assigned together to some node group. The jobtracker and namenode are master nodes; they act as coordinators for MapReduce and HDFS, respectively, and no more than one of each should exist. (A single node may share both responsibilities.)

#### Machine Spec ####

Pallet and jclouds give us the tools to describe a node group's machine-spec in a very high level way. For example, a 64-bit machine running Ubuntu Linux 10.10 with at least 4 gigs of ram can be described by this Clojure map:
       
{% highlight clojure %}
 {:os-family :ubuntu
  :os-version-matches "10.10"
  :os-64-bit true
  :min-ram (* 4 1024)}
{% endhighlight %}

A whole host of options are supported; all valid map keys can be found [here](https://github.com/jclouds/jclouds/blob/master/compute/src/main/clojure/org/jclouds/compute.clj#L446).

#### Property Map ####

Hadoop allows for a rather bewildering number of configuration options, each of which are dependent in some way on the power of the machines composing each cluster. (Because this is probably the most confusing part of Hadoop configuration, one of the main goals of this project is to provide intelligent defaults that modify themselves based on the machine specs of the nodes in each node group.)

Hadoop has four configuration files of note:

1. mapred-site.xml: 
2. hdfs-site.xml:
3. core-site.xml:
4. hadoop-env.sh:

TODO: Add resources for understanding hadoop properties.

(The number of reduce tasks per machine, for example, tends to scale directly with the processing power of the machine and the number of child JVM tasks that can be launched, which the total number of reduce tasks allowed per job scales with some factor of this number. Lots of little rules. (At the end, I'll provide some of the resources I've found to be most helpful in navigating the Hadoop jungle.)

#### Cluster Level Properties ####

While it's important to have properties common to an entire cluster, each group of nodes should be able to maintain its own set of hadoop properties, tailored for its specific hardware configuration. Same goes for the machine spec.

TODO:
machine spec and property map are supported at the cluster level, as well -- the other two properties must be defined at the node group level.

## Setting Up ##

To boot up a hadoop cluster properly, you'll need to [create an AWS account](https://aws-portal.amazon.com/gp/aws/developer/registration/index.html). Once you've done this, navigate to [your account page](http://aws.amazon.com/account/) and follow the "Security Credentials" link. Under "Access Credentials", you should see a tab called "Access Keys". Note down your Access Key ID and Secret Access Key for future reference.

I'm going to assume that you have some basic knowledge of how to create a clojure project using [leiningen](https://github.com/technomancy/leiningen) or [cake](https://github.com/ninjudd/cake). Go ahead and download [this example project](https://github.com/pallet/pallet-hadoop-example) to follow along:

    $ git clone git://github.com/pallet/pallet-hadoop-example.git
    $ cd pallet-hadoop-example
    $ lein deps
    $ lein repl

This should get you to the `pallet-hadoop-example.core` REPL. This namespace has a few helper functions defined for us; let's go through it quickly.

The namespace declaration brings in `pallet-hadoop.node`, where all of the cluster forming magic lies.

{% highlight clojure %}

(ns pallet-hadoop-example.core
  (:use pallet-hadoop.node
        [pallet.crate.hadoop :only (hadoop-user)]
        [pallet.extensions :only (def-phase-fn)])
  (:require [pallet.core :as core]
            [pallet.resource.directory :as d]))

{% endhighlight %}

*Phases* are a key concept in pallet. A phase is a group of operations meant to be applied to some set of nodes. EC2 instances have the property that the bulk of their allotted [ephemeral storage](http://goo.gl/ZplJg) is mounted as `mnt/`. To use our distributed file system effectively, we must change the permissions on this drive to allow the default hadoop user to gain access.

The following phase function, when applied to all nodes in the cluster, will ensure that HDFS will have no trouble.

{% highlight clojure %}

(def-phase-fn authorize-mnt
  "Authorizes the `/mnt` volume for use by the default hadoop user;
  Necessary to take advantage of space Changes the permissions on
  /mnt, for ec2 systems."
  []
  (d/directory "/mnt"
               :owner hadoop-user
               :group hadoop-user
               :mode "0755"))

{% endhighlight %}

`create-cluster` accepts a data description of a hadoop cluster and a compute service, starts all nodes, runs our `authorize-mnt` phase, and starts up all appropriate hadoop services for each group of nodes. `destroy-cluster` (surprise!) shuts everything down.

(Don't worry about `remote-env`, here. We're making sure pallet knows to deal with all nodes in parallel, rather than configuring each node in sequence.)

{% highlight clojure %}

(def remote-env
  {:algorithms {:lift-fn pallet.core/parallel-lift
                :converge-fn pallet.core/parallel-adjust-node-counts}})

(defn create-cluster
  [cluster compute-service]
  (do (boot-cluster cluster
                    :compute compute-service
                    :environment remote-env)
      (lift-cluster cluster
                    authorize-mnt
                    :compute compute-service
                    :environment remote-env)
      (start-cluster cluster
                     :compute compute-service
                     :environment remote-env)))

(defn destroy-cluster
  [cluster compute-service]
  (kill-cluster cluster
                :compute compute-service
                :environment remote-env))

{% endhighlight %}

### Compute Service ###

Pallet abstracts away details about specific cloud providers through the idea of a "compute service". The combination of our cluster definition and our compute service will be enough to get our cluster running. We define a compute service like so:

{% highlight clojure %}
=> (use 'pallet.compute)
nil
=> (def ec2-service
       (compute-service "aws-ec2"
                        :identity "ec2-access-key-id"
                        :credential "ec2-secret-access-key"))
#'pallet-hadoop-example.core/ec2-service
{% endhighlight %}

Alternatively, you could place the following in `~/.pallet/config.clj`:

{% highlight clojure %}
(defpallet
  :services {:aws {:provider "aws-ec2"
                   :identity "ec2-access-key-id"
                   :credential "ec2-secret-access-key"}})
{% endhighlight %}

and define the compute service with

{% highlight clojure %}
=> (def ec2-service (compute-service-from-config-file :aws))
#'pallet-hadoop-example.core/ec2-servic
{% endhighlight %}

### Cluster Definition ###

Here's how we define a node group containing a single jobtracker node, with a custom value of `"val"` for the `some-prop` key in `mapred-site.xml`:

    (node-group [:jobtracker] 1 :props {:mapred-site {:some-prop "val"}})

And the same node, with an additional `namenode` role and no customizations:

    (node-group [:jobtracker :namenode])

`node-group` knows that this is a master node group, so the count defaults to 1. Currently, `:props` and `:spec` are supported as keyword arguments to `node-group`, and define group-specific customizations of, respectively, the hadoop properties map and the machine spec for all nodes in the group.

Let's define a cluster for EC2, with four nodes -- one's a jobtracker and namenode, the other three will be slavenodes. We'll need the following definitions:

{% highlight clojure %}

   (node-group [:jobtracker :namenode])
   (slave-group 3)

{% endhighlight %}

`slave-group` is shorthand for `(node-group [:datanode :tasktracker] ...)`.

This brings us most of the way to a full cluster. The only remaining pieces are the cluster-level hadoop properties, and the base machine spec for all nodes in the cluster. `cluster-spec` accepts these as optional keyworded arguments, after the two required arguments of `ip-type` and a map of node tags to node group definitions. (The tags must be unique, but can be arbitrary.)

*ip-type* can be either `:public` or `:private`, and determines what type of IP address the cluster nodes use to communicate with one another. EC2 instances require private IP addresses; if one were setting up a cluster of virtual machines, `:public` would be necessary.

Here, we define a cluster with private IP addresses, the two node groups referenced above (keyed to `:jobtracker` and `:slaves`), and a number of customizations to the default hadoop settings. Our machine spec declares that all nodes in the cluster will be the fastest 64 bit machines Amazon has to offer, all running Ubuntu 10.10.

{% highlight clojure %}

(def test-cluster
    (cluster-spec
     :private
     {:jobtracker (node-group [:jobtracker :namenode])
      :slaves (slave-group 3)}
     :base-machine-spec {:os-family :ubuntu
                         :os-version-matches "10.10"
                         :os-64-bit true
                         :fastest true}
     :base-props {:hdfs-site {:dfs.data.dir "/mnt/dfs/data"
                              :dfs.name.dir "/mnt/dfs/name"}
                  :mapred-site {:mapred.task.timeout 300000
                                :mapred.reduce.tasks 60
                                :mapred.tasktracker.map.tasks.maximum 15
                                :mapred.tasktracker.reduce.tasks.maximum 15
                                :mapred.child.java.opts "-Xms1024m -Xmx1024m"}}))

{% endhighlight %}

And that's all there is to it! Type that in at the REPL, and let's boot this thing.

### Booting the Cluster ###

Now that we have our compute service and our cluster defined, booting the cluster is as simple as the following:

{% highlight clojure %}
=> (create-cluster test-cluster ec2-service)
{% endhighlight %}

The logs you see flying by are Pallet's communications with the nodes in the cluster. After startup, Pallet uses your local SSH key to gain passwordless access to each node. 

### Testing ###

Go to EC2 console, get the public DNS address of the jobtracker. Go to address:50030, you'll see hadoop running.

Download a text file. Show how to run a sample word count in MapReduce, as shown in [this blog post](http://www.michael-noll.com/tutorials/running-hadoop-on-ubuntu-linux-multi-node-cluster/#running-a-mapreduce-job). Get it back [like this](http://www.michael-noll.com/tutorials/running-hadoop-on-ubuntu-linux-single-node-cluster/#retrieve-the-job-result-from-hdfs).

### Killing the Cluster ###

When we're all finished, we can kill our cluster with this command:

{% highlight clojure %}
=> (destroy-cluster test-cluster ec2-service)
{% endhighlight %}

### Future Plans ###

Where can this go? Clean up all of the stuff in the pallet-hadoop README.

### More Reading ###

Links to further reading.

### Next Installment ###

Let's talk about how to test these sorts of clusters in a local virtual machine environment.

Then, we'll talk about how to get a cascalog query working on Hadoop.
