---
title: "How to Publish CLJSJS Jars to Clojars"
date: 2020-07-28T12:23:18.000Z
slug: publishing-cljsjs-jars-to-clojars
tags:
  - clojure
  - code
categories:
  - programming
---

I've been doing a lot of [work in Clojurescript](https://github.com/littleredcomputer/sicmutils) lately, and the time finally came to pull in my first [vanilla Javascript dependency](https://github.com/infusion/Complex.js/). The default way to do this seems to be the [CLJSJS project](http://cljsjs.github.io/).

CLJSJS publishes many [Javascript packages](https://github.com/cljsjs/packages) in a form that you can consume from a Clojure project. For projects like React, you'll find the latest versions of the JS libraries, packaged up and ready to go. For less active libraries like [bignumber.js](https://github.com/MikeMcl/bignumber.js/) you might have to go bump a version and open up a pull request against [CLJSJS's `packages` repository](https://github.com/cljsjs/packages)... or maybe package and add the library from scratch, [as I did recently with Complex.js](https://github.com/cljsjs/packages/pull/2120).

I have to say that this was a complete pain. I'll eventually write a guide describing what I had to do to [upgrade or add six JS libraries](https://github.com/cljsjs/packages/pulls/sritchie), since this was not easy and I know it's blocking other people.

For now, I want to describe the steps I had to take to publish a namespaces version of `cljsjs/complex` to [Clojars](https://clojars.org/org.clojars.sritchie09/complex), so that I could start using it immediately without waiting for the maybe-weeks-long turnaround time of a new CLJSJS release.

# Publishing to Clojars

[Clojars.org](https://clojars.org/) is the place of record for all Clojure dependencies. It's the easiest way I know of to get a library published for consumption in other projects.

The goal here is to publish a CLJSJS library that you'll eventually depend on like this:

```clojure
[cljsjs/complex "2.0.11-0"]
```

With a prefix, so that you can use it *today*, like this:

```clojure
[org.clojars.sritchie09/complex "2.0.11-0"]
```

(The prefixing is important because you can't publish with the `cljsjs` prefix unless you're authorized by the CLJSJS maintainers.)

### Clojars Account + Deploy Token

You'll publish the new dependency to Clojars. Head to https://clojars.org and make an account.

Click on ["Deploy Tokens"](https://clojars.org/tokens) page at the top right:
{{< figure src="image.png" >}}
Follow the instructions and make a token (the name doesn't matter). It will appear on the screen looking something like `CLOJARS_1313123123` . Save it (and your Clojars username) by adding two entries like this to your `~/.bashrc` or `~/.bash_profile`:

```bash
export CLOJARS_USER=sritchie09
export CLOJARS_PASS=CLOJARS_1313123123
```

- Run `source ~/.bashrc` to pick up the new environment variables.

### Check out CLJSJS

The CLJSJS packages live in [this repository](https://github.com/cljsjs/packages). Get it onto your machine by running this command in some directory:

```bash
git clone git@github.com:cljsjs/packages.git && cd packages
```

Now find the dependency you want to release. If you're doing this, you're probably living on a git branch, like I was for the [Complex.js pull request](https://github.com/cljsjs/packages/pull/2120). Check out the branch:

```bash
git checkout sritchie/complex_dep2
```

Each JS library has its own folder with a `build.boot` file in it. Open up, for example, `complex/build.boot` and locate the entry that looks like this:

```clojure
(task-options!
 push {:ensure-clean false}
 pom  {:project     'cljsjs/complex
       :version     +version+
       :description "A well tested JavaScript library to work with complex number arithmetic in JavaScript."
       :url         "https://github.com/infusion/Complex.js"
       :license     {"MIT" "http://opensource.org/licenses/MIT"}
       :scm         {:url "https://github.com/cljsjs/packages"}})
```

Change the value referenced by `:project` from `'cljsjs/complex` to '`org.clojars.YOUR_CLOJARS_USERNAME/complex`. This was `org.clojars.sritchie09/complex`, in my case.

### Deploying

We're so close.

The latest version of Boot won't let you deploy to Clojars (dependency problem!). You can force yourself back to a working version by creating a file called `boot.properties` in the `packages` directory with these contents:

```
BOOT_VERSION=2.8.2
```

Finally, run this command in the subfolder containing the dependency you want to release. `complex`, in this case:

```bash
boot package push --ensure-release --repo clojars \
--repo-map "{:url \"https://clojars.org/repo/\" :username \"$CLOJARS_USER\" :password \"$CLOJARS_PASS\"}"
```

If you've set the environment variables correctly, you should see output ending with this:

```
Writing pom.xml and pom.properties...
Writing complex-2.0.11-0.jar...
Checksums match
Deploying complex-2.0.11-0.jar...
Sending complex-2.0.11-0.jar to https://clojars.org/repo/ (13k)
Sending complex-2.0.11-0.pom to https://clojars.org/repo/ (1k)
Sending maven-metadata.xml to https://clojars.org/repo/ (1k)
```

That's it! Your dependency will now be live at a URL like [https://clojars.org/org.clojars.sritchie09/complex](https://clojars.org/org.clojars.sritchie09/complex), and you'll be able to include it as a dependency using any of the forms that Clojars displays on that page. For example:

```clojure
[org.clojars.sritchie09/complex "2.0.11-0"]
```

Hopefully this has saved you some trouble. Enjoy!

### Troubleshooting

If you see output like this:

```
clojure.lang.ExceptionInfo: Failed to deploy artifacts: Could not transfer artifact org.clojars.sritchie09:complex:jar:2.0.11-0 from/to clojars (https://clojars.org/repo/): Failed to transfer file: https://clojars.org/repo/org/clojars/sritchie09/complex/2.0.11-0/complex-2.0.11-0.jar. Return code is: 401, ReasonPhrase: Unauthorized.
```

Make sure that you've properly set the environment variables `$CLOJARS_USER` and `$CLOJARS_PASS`.
