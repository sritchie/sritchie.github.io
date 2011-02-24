---
layout: post
title: This is a draft
---

{{ page.title }}
================

<p class="meta">Date - Philadelphia</p>

Well, here we are with another draft. I've been doing some coding in clojure, lately.

{% highlight clojure %}
(defn datetime->period
  "Converts a given set of date pieces into a reference time interval
at the same temporal resolution as a MODIS product at the supplied
resolution. Input can be any number of pieces of a date, from greatest
to least significance. See clj-time's date-time function for more
information."
  [res & int-pieces]
  (let [date (apply date-time int-pieces)]
    ((period-func res) ref-date date)))
{% endhighlight %}	

