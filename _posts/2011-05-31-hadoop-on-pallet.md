---
layout: post
title: Simple Hadoop Clusters
---

{{ page.title }}
================

<p class="meta">31 May 2011 - Washington, DC</p>

# Introducing Pallet-Hadoop #

I'm very excited to announce [Pallet-Hadoop](https://github.com/pallet/pallet-hadoop), a configuration library written in Clojure for Apache's [Hadoop](http://hadoop.apache.org/). For simple, quick instructions on getting your first Hadoop cluster running on EC2, head over to the [Pallet-Hadoop Example Project](https://github.com/pallet/pallet-hadoop-example) and follow along with the README. For a more in-depth discussion, read on.

## Background ##

For those of you not in the know, Hadoop is an Apache java framework that allows for distributed processing of enormous datasets across large clusters. It combines a computation engine based on [MapReduce](http://en.wikipedia.org/wiki/MapReduce) with [HDFS](http://hadoop.apache.org/hdfs/docs/current/hdfs_design.html), a distributed filesystem based on the [Google File System](http://en.wikipedia.org/wiki/Google_File_System).

Abstraction layers such as [Cascading](https://github.com/cwensel/cascading) (for Java) and [Cascalog](https://github.com/nathanmarz/cascalog) (for [Clojure](http://clojure.org/)) make writing MapReduce queries quite nice. Indeed, running hadoop locally with cascalog [couldn't be easier](http://nathanmarz.com/blog/introducing-cascalog-a-clojure-based-query-language-for-hado.html).

Unfortunately, graduating one's MapReduce jobs to the cluster level isn't so easy. Amazon's [Elastic MapReduce](http://aws.amazon.com/elasticmapreduce/) is a great option for getting up and running fast; but what to do if you want to configure your own cluster?

After surveying existing tools, I decided to write my own layer over [Pallet](https://github.com/pallet/pallet), a wonderful cloud provisioning library written in Clojure. Pallet runs on top of [jclouds](https://github.com/jclouds/jclouds), which allows pallet to define its operations independent of any one cloud provider. Switching between clouds involves a change of login credentials, nothing more.

## Cluster Description ##

The goal of this project was to write an abstraction layer capable of converting a data-driven representation of a Hadoop cluster into the real thing, running on one of the many clouds.

Let's think of a cluster as a data structure composed of a number of groups of identically configured machines -- *node groups*. A node group has four properties:

1. *server spec*: a description of the software payload installed on each node.
2. *machine spec*: The hardware configuration of each node.
3. *property map*: Hadoop configuration properties unique to the node group.
3. *count*: the number of nodes within the group.

(Machine spec and property map are also defined at the cluster level; node group values are merged in, knocking out cluster-wide options where defined.)

##### Server Spec ####

A node group's server spec can be described by some combination of the following four roles (ignoring secondary namenode for now):

* *Jobtracker*:  This is the king of mapreduce.
* *Tasktracker*: Jobtracker parcels out tasks to the tasktrackers.
* *Namenode*:    The king of HDFS.
* *Datanode*:    Datanodes hold HDFS chunks; they're coordinated by the namenode.

Tasktrackers and datanodes are slave nodes, and are usually assigned together to some node group. The jobtracker and namenode are master nodes; they act as coordinators for MapReduce and HDFS, respectively, and only one of each should exist. (A single node may share both responsibilities.)

##### Machine Spec ####

Pallet and jclouds give us the tools to describe a node group's machine-spec in a very high level way. For example, a 64-bit machine running Ubuntu Linux 10.10 with at least 4 gigs of ram can be described by this Clojure map:
       
{% highlight clojure %}
 {:os-family :ubuntu
  :os-version-matches "10.10"
  :os-64-bit true
  :min-ram (* 4 1024)}
{% endhighlight %}

A whole host of options are supported; all valid map keys can be found [here](https://github.com/jclouds/jclouds/blob/master/compute/src/main/clojure/org/jclouds/compute.clj#L446).

##### Property Map ####


Tom White (said it best)[http://goo.gl/Sq2lM]: "Hadoop has a bewildering number of configuration properties", each of which are dependent in some way on the power of the machines composing each cluster. As this is probably the most confusing part of Hadoop, the next main gloal of this project will be to provide intelligent defaults that modify themselves based on the machine specs of the nodes in each node group.

Hadoop has four configuration files of note: `mapred-site.xml`, `hdfs-site.xml`, `core-site.xml` and `hadoop-env.sh`. Properties for each of these files are defined with a clojure map:

{% highlight clojure %}
{:hdfs-site {:dfs.data.dir "/mnt/dfs/data"
             :dfs.name.dir "/mnt/dfs/name"}
 :mapred-site {:mapred.task.timeout 300000
               :mapred.reduce.tasks 60
               :mapred.tasktracker.map.tasks.maximum 15
               :mapred.tasktracker.reduce.tasks.maximum 15
               :mapred.child.java.opts "-Xms1024m -Xmx1024m"
 :hadoop-env {:JAVA_LIBRARY_PATH "/path/to/libs"}}}
{% endhighlight %}

k-v  pairs for each of the three XML files are processed into XML, while k-v pairs under `:hadoop-env` are expanded as lines in `hadoop-env.sh`, formatted like so:

     {:JAVA_LIBRARY_PATH "/path/to/libs"}
     => export JAVA_LIBRARY_PATH=/path/to/libs

TODO: Add resources for understanding hadoop properties.

## Setting Up ##

To get your first cluster running, you'll need to [create an AWS account](https://aws-portal.amazon.com/gp/aws/developer/registration/index.html). Once you've done this, navigate to [your account page](http://aws.amazon.com/account/) and follow the "Security Credentials" link. Under "Access Credentials", you should see a tab called "Access Keys". Note down your Access Key ID and Secret Access Key for future reference.

I'm going to assume that you have some basic knowledge of clojure, and know how to get a project running using [leiningen](https://github.com/technomancy/leiningen) or [cake](https://github.com/ninjudd/cake). Go ahead and download [this example project](https://github.com/pallet/pallet-hadoop-example) to follow along:

    $ git clone git://github.com/pallet/pallet-hadoop-example.git
    $ cd pallet-hadoop-example
    $ lein deps
    $ lein repl

This will get you to a REPL in `pallet-hadoop-example.core`.

### Compute Service ###

Pallet abstracts away details about specific cloud providers through the idea of a "compute service". The combination of our cluster definition and our compute service will be enough to get our cluster running. We define a compute service at our REPL like so:

{% highlight clojure %}
=> (use 'pallet.compute)
nil
=> (def ec2-service
       (compute-service "aws-ec2"
                        :identity "ec2-access-key-id"
                        :credential "ec2-secret-access-key"))
#'pallet-hadoop-example.core/ec2-service
{% endhighlight %}

Alternatively, if you want to keep these out of your code base, save the following to `~/.pallet/config.clj`:

{% highlight clojure %}
(defpallet
  :services {:aws {:provider "aws-ec2"
                   :identity "ec2-access-key-id"
                   :credential "ec2-secret-access-key"}})
{% endhighlight %}

and define `ec2-service` with:

{% highlight clojure %}
=> (def ec2-service (compute-service-from-config-file :aws))
#'pallet-hadoop-example.core/ec2-service
{% endhighlight %}
<br/>
### Helper Functions ###

The `pallet-hadoop-example.core` namespace has a few helper functions defined for us. Let's go through it quickly.

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
<br/>
### Cluster Definition ###

Here's how we define a node group containing a single jobtracker node with a single, node-group-specific customization of `mapred-site.xml`:

    (node-group [:jobtracker] 1 :props {:mapred-site {:some-prop "val"}})

And the same node, with an additional `namenode` role and no customizations:

    (node-group [:jobtracker :namenode])

`node-group` knows that this is a master node group, and defaults the count to 1. Currently, `:props` and `:spec` are supported as keyword arguments, and define group-specific customizations of, respectively, the hadoop property map and the machine spec for all nodes in the group.

Let's define a cluster on EC2, with two node groups: The first will contain one node that functions as jobtracker and namenode, while the second will contain three slave nodes. We'll need the following definitions:

{% highlight clojure %}
   (node-group [:jobtracker :namenode])
   (slave-group 3)
{% endhighlight %}

(`slave-group` is shorthand for `(node-group [:datanode :tasktracker] ...)`.)

Pallet required that each node group be paired with some unique, arbitrary key identifier. Let's wrap our node group definitions like so:

{% highlight clojure %}
{:jobtracker (node-group [:jobtracker :namenode])
 :slaves (slave-group 3)}
{% endhighlight %}

This brings us most of the way to a full cluster. The only remaining pieces are the cluster-level hadoop properties, and the base machine spec for all nodes in the cluster. `cluster-spec` accepts these as optional keyworded arguments, after the two required arguments of `ip-type` and the node group map, shown above.

*ip-type* can be either `:public` or `:private`, and determines what type of IP address the cluster nodes use to communicate with one another. EC2 instances require private IP addresses; if one were setting up a cluster of virtual machines, `:public` would be necessary.

Here, we define a cluster with private IP addresses, the two node groups referenced above, and a number of customizations to the default hadoop settings. Our machine spec declares that all nodes in the cluster should be the fastest 64 bit machines Amazon has to offer, all running Ubuntu 10.10.

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

And that's all there is to it! Type that in at the REPL, and let's get this this running.

### Booting the Cluster ###

Now that we have our compute service and our cluster defined, booting the cluster is as simple as the following:

{% highlight clojure %}
=> (create-cluster test-cluster ec2-service)
{% endhighlight %}

The logs you see flying by are Pallet's SSH communications with the nodes in the cluster. After startup, Pallet uses your local SSH key to gain passwordless access to each node. 

### Running Word Count ###

Once `create-cluster` returns, it's time to log in and run a MapReduce job. Head over to the [EC2 Console](https://console.aws.amazon.com/ec2/), log in, and click "Instances" on the left. You should see four nodes running; click on the node whose security group contains "jobtracker", and scroll the lower pane down to retrieve the public DNS address for the node. It'll look something like

    ec2-50-17-103-174.compute-1.amazonaws.com

I'll refer to this address as `jobtracker.com`. Point your browser to `jobtracker.com:50030`, and you'll see jobtracker console for mapreduce jobs. `jobtracker.com:50070` points to the namenode console, with information about HDFS.

Head into a terminal and run the following commands:

     $ ssh jobtracker.com (insert actual address, enter yes to continue connecting)
     $ sudo su - hadoop

(That's as far as I am for now!)

Download a text file. Show how to run a sample word count in MapReduce, as shown in [this blog post](http://www.michael-noll.com/tutorials/running-hadoop-on-ubuntu-linux-multi-node-cluster/#running-a-mapreduce-job). Get it back [like this](http://www.michael-noll.com/tutorials/running-hadoop-on-ubuntu-linux-single-node-cluster/#retrieve-the-job-result-from-hdfs).

### Killing the Cluster ###

When we're all finished, we can kill our cluster with this command:

{% highlight clojure %}
=> (destroy-cluster test-cluster ec2-service)
{% endhighlight %}
<br/>

### Future Plans ###

Where can this go? Clean up all of the stuff in the pallet-hadoop README.

### More Reading ###

Links to further reading.

### Next Installment ###

Let's talk about how to test these sorts of clusters in a local virtual machine environment.

Then, we'll talk about how to get a cascalog query working on Hadoop.
