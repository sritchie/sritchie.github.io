---
title: "SICM Chapter 9: Our Notation"
date: 2020-05-25T02:14:40.000Z
slug: test-mode
draft: true
math: true
---

```
- [Variation Sum Rule](#sec-1)
```

# Variation Sum Rule<a id="sec-1"></a>

The sum rule is easier. Our goal is:

\begin{equation}

\label{eq:var-sum}

\delta_\eta (f + g)[q] = \delta_\eta f[q] + \delta_\eta g[q]

\end{equation}

Expand out the definition of the variation operator, regroup terms, allow $\epsilon \to 0$ and notice that we've recovered our goal.

\begin{equation}

\eqalign{

\sqrt{37} &amp; = \sqrt{\frac{73^2-1}{12^2}} \cr

&amp; = \sqrt{\frac{73^2}{12^2}\cdot\frac{73^2-1}{73^2}} \cr

&amp; = \sqrt{\frac{73^2}{12^2}}\sqrt{\frac{73^2-1}{73^2}} \cr

&amp; = \frac{73}{12}\sqrt{1 - \frac{1}{73^2}} \cr

&amp; \approx \frac{73}{12}\left(1 - \frac{1}{2\cdot73^2}\right)

}

\end{equation}

\begin{equation}

\begin{aligned}

\delta_\eta (f + g)[q] &amp;= \lim_{\epsilon \to 0} \left( {(f[q + \epsilon\eta] + g[q + \epsilon\eta]) - (f[q] + g[q])} \over \epsilon \right) \cr

&amp;= \lim_{\epsilon \to 0} \left( {f[q + \epsilon\eta] - f[q]} \over \epsilon \right) + \lim_{\epsilon \to 0} \left( {g[q + \epsilon\eta] - g[q]} \over \epsilon \right) \cr

&amp;= \delta_\eta f[q] + \delta_\eta g[q]

\end{aligned}

\end{equation}

Done!
