---
title: "Adding Mathjax to your (SBT-)Microsite"
date: 2019-09-26T15:38:02.000Z
slug: adding-mathjax-to-your-sbt-microsite
tags:
  - code
  - scala
categories:
  - programming
math: true
---

I'm obsessed with [sbt-microsites](https://47deg.github.io/sbt-microsites/). Sbt-microsites is a fantastic plugin for SBT (the Scala Build Tool) that makes it easy to generate a beautiful sidecar site for your software project, *full of code checked by your CI!*

I recently built a [microsite for ScalaRL](https://www.scalarl.com), my in-progress [functional Reinforcement Learning library](https://github.com/sritchie/scala-rl), and found that adding support for [Mathjax](https://www.mathjax.org/) (a javascript math equation renderer) to the microsite was not obvious. It's not hard... just not clear from the Mathjax docs how to get past some limitations with sbt-microsites.

This post is a pitch for sbt-microsites, plus a short guide on how to get Mathjax working on your microsite.

## SBT-Microsites

As an example of what you can make with this plugin, check out the [Algebird microsite](http://twitter.github.io/algebird/) I built a couple of years ago. On the initial page you'll see this lovely series of three Scala lines with their results printed as comments below:
{{< figure src="image.png" >}}
That snippet was generated from [this page in the Algebird repository](https://github.com/twitter/algebird/blob/develop/docs/src/main/tut/index.md), specifically from this snippet:

````markdown
### What can you do with this code?

```tut:book
import com.twitter.algebird._
import com.twitter.algebird.Operators._
Map(1 -> Max(2)) + Map(1 -> Max(3)) + Map(2 -> Max(4))
```
````

Sbt-microsites uses the [Tut documentation tool](https://github.com/tpolecat/tut) (which has [its own microsite](http://tpolecat.github.io/tut/), of course) to compile and execute any code block marked as `tut:book`, just like you see above.

This means that if any of the examples in your documentation get out-of-date due to API changes or bugs... your code will no longer compile. If you run your tests in a CI environment, pull requests that break your documentation will fail! This is an incredible advantage, and will put your project levels beyond all of the sad Scala projects out there with out-of-date Github wikis, rotting away and pissing off users.

Here's a page from the Algebird microsite for the `Min` and `Max` data structures: [http://twitter.github.io/algebird/datatypes/min_and_max.html](http://twitter.github.io/algebird/datatypes/min_and_max.html)

This example contains in-line assertions that act as tests that will fail in the documentation if the code compiles, but has some behavior change that brings your example out of date.

````markdown
```tut:book
val loser: Min[TwitterUser] = Min(barackobama) + Min(katyperry) + Min(ladygaga) + Min(miguno) + Min(taylorswift)
assert(miguno == loser.get) // The build will fail if the assertion fails.
```
````

This covers almost none of how to actually set up sbt-microsites, of course. For that, check out these resources:

- [the sbt-microsites microsite's Getting Started docs](https://47deg.github.io/sbt-microsites/docs/)
- [Tut's website](http://tpolecat.github.io/tut/), for examples on inline code blocks
- [MDoc](https://scalameta.org/mdoc/), a more modern inline code block runner inspired by Tut. (Tut runs code like the Repl, while MDoc has more advanced support for a literate programming style.)
- The [ScalaRL microsite](https://www.scalarl.com/), along with its [Settings block in the project's build.sbt file](https://github.com/sritchie/scala-rl/blob/develop/build.sbt#L181)

## Adding Mathjax Support

[Mathjax](https://www.mathjax.org) is a Javascript library that scans a page for blocks of [LaTeX](https://www.latex-project.org/) demarcated by dollar signs, like this: `$<equation here>$` and renders them into beautiful math equations on the page. (Single dollar signs for inline math, double dollars for standalone blocks.) If you wanted to embed the quadratic equation, you could write:

```latex
$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}$$
```

And MathJax would render the block like this:
$$x = {-b \pm \sqrt{b^2-4ac} \over 2a}$$
Usually you install Mathjax by dropping something like the following in your website's footer:

```js
<!--  MathJax -->
<script type="text/x-mathjax-config">
MathJax.Hub.Config({
  tex2jax: {inlineMath: [['$','$'], ['\$','\$']],processEscapes: true},
  TeX: { equationNumbers: { autoNumber: "AMS" } }
});
</script>
<script type="text/javascript" async        
  src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.4/MathJax.js?config=TeX-MML-AM_CHTML">
</script>
```

These two scripts set a configuration for Mathjax and then asynchronously load the script that uses that configuration to render your equations. (This is the config I use on this blog, by the way.)

Sbt-microsites makes the process slightly more difficult. The plugin doesn't give you access to the full page template; instead, it offers various hooks into the template via its large set of configuration options, [documented here](https://47deg.github.io/sbt-microsites/docs/settings.html). The two problems I hit were:

- There's no way that I could find to inject an unescaped block of Javascript into the site's footer.
- Mathjax can't read its configuration from a standalone Javascript file.
- A standalone Javascript file can't pull in another file asynchronously.

### The Solution

I found my answer on the Mathjax documentation's section on ["Loading Mathjax Dynamically"](https://docs.mathjax.org/en/v2.7-latest/advanced/dynamic.html). To get Mathjax working on the site, I had to create a file that would load and configure the library dynamically, and place it in the sbt-microsites default location for custom javascript. 

I created a file at `/docs/src/main/resources/microsite/js/mathjax.js`  ([github link here](https://github.com/sritchie/scala-rl)) with the following content:

```js
(function () {
  var head = document.getElementsByTagName("head")[0], script;
  script = document.createElement("script");
  script.type = "text/x-mathjax-config";
  script[(window.opera ? "innerHTML" : "text")] =
    "MathJax.Hub.Config({\n" +
        "  tex2jax: { inlineMath: [['$','$'], ['\\\$','\\\$']], processEscapes: true},\n" +
        "  TeX: { equationNumbers: { autoNumber: \"AMS\" } }\n" +
    "});";
  head.appendChild(script);
  script = document.createElement("script");
  script.type = "text/javascript";
  script.src  = "https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/MathJax.js?config=TeX-MML-AM_CHTML";
  head.appendChild(script);
})();
```

This block:

- Configures Mathjax to use either `$<equation>$` or `$<equation>$` syntax to block off inline equations, and
- adds support for automatic equation numbering, if you add your block equations like this:

```latex
\begin{equation}
   E = mc^2
\end{equation}
```

You can browse [the Mathjax site](http://docs.mathjax.org/en/latest/options/index.html) for many more configuration options.

Sbt-microsites looks for custom javascript files in the `resources/microsite/js` subdirectory of your `docs` project, but if you like you can override that location in your docs config by adding this key:

```scala
micrositeJsDirectory := (resourceDirectory in Compile).value / "site" / "scripts"
```

Now, I think these scripts *only* get injected into sub-pages., and not onto your main index page. That's probably a bug that the plugin could fix in the future, so [let them know](https://github.com/47deg/sbt-microsites/issues) if you have an index bedazzled with equations.

Best of luck getting this set up on your own projects! Let me know in the comments if you have any questions or run into trouble.
