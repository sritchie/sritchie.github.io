---
title: "Taylor Series and Imaginary Numbers"
date: 2020-02-10T14:56:03.000Z
slug: taylor-series-and-imaginary-numbers
math: true
---

I wanted to share some of the intuition I've been developing around [complex numbers](https://en.wikipedia.org/wiki/Complex_number); some of the resources that have been helpful, for understanding why anyone would come up with an idea like $i$, the square root of -1, and then build an entire number system on top of it.

### History

My knowledge of the history here is probably at the level of a [Just-So Story](https://en.wikipedia.org/wiki/Just_So_Stories); still, I've been finding it helpful to have some vague idea of *why* folks started developing some area of mathematics before digging into the details, so I'll pass on what I've got to you.

My understanding (backed up by [Wikipedia](https://en.wikipedia.org/wiki/Complex_number)) is that the idea of $i$ came up as a sort of naughty, wtf-is-going-on way of finding solutions to equations like this:
$$x^2 + 1 = 0$$
If you look at the graph of $y = x^2 + 1$, you can see that there is *no* point where some $x$ gives you 0 back out.
{{< figure src="image-4.png" >}}
But what if you just went into overdrive and solved the equation anyway? $x^2=-1$, so just make up a new thing, call it $i$. What is $i$? Well, it's something that, when you square it, gives you back $-1$. Now that equation has *two* solutions, like any good quadratic function: $i$ and $-i$.

According to [Wikipedia](https://en.wikipedia.org/wiki/Complex_number#History), Descartes was the first person to call this number *imaginary:*

> [...] sometimes only imaginary, that is one can imagine as many as I said in each equation, but sometimes there exists no quantity that matches that which we imagine. ([Wikipedia](https://en.wikipedia.org/wiki/Complex_number#History))

This name is a mathematical micro-aggression. It's another step in the centuries-long discomfort mathematicians have had with opening up the idea of what a "number" is, from natural numbers, to rational, to real, and now, with $i$, the first step toward the idea of a *complex number* of the form $a + bi$, where $a$ and $b$ are both real numbers.

### Geometry and the Complex Plane

$i = \sqrt{-1}$ as an accounting device didn't work for me at all. Why does this matter? 

What did work well was Gauss's realization that you can think of a complex number — again, a number of the form $a + bi$ — as a point in a two dimensional plane (the "complex plane").

- FIGURE of a point

It turns out that you can visualize multiplication by $i$ as a 90 degree rotation in the complex plane.

You can see from this that if you have some number $a$, and you multiply it by $i$, $ai$ now lives on the y axis of the graph, 90 degrees from where you started.

- SHOW!

If you multiply $ai$ by $i$, you get $ai^2 = -a$, which lives back on the x axis, another 90 degrees around, or 180 degrees from where you began. ($i^2 = -1$, a 180 degree rotation, or a reflection across the y axis. See?)

- SHOW

Keep going around to get $-ai$:

- SHOW

And a final multiplication by $i$ gets you back to $-ai \cdot i = -ai^2 = -(-a) = a$, a full 360 degrees around from where you started.

Here's Gauss, expressing his frustration at the "imaginary" terminology:

> If this subject has hitherto been considered from the wrong viewpoint and thus enveloped in mystery and surrounded by darkness, it is largely an unsuitable terminology which should be blamed. Had $+1$, $-1$ and $\sqrt{-1}$, instead of being called positive, negative and imaginary (or worse still, impossible) unity, been given the names say , of direct, inverse and lateral unity, there would hardly have been any scope for such obscurity.” - Gauss, via [Wikipedia](https://en.wikipedia.org/wiki/Complex_number#History)

### General Rotations

If you imagine $ai$ as a number along the y axis of a complex plane, and $a$ as some number along the x axis, the next natural step is to imagine how you'd represent arbitrary points on the plane.

- MY WHOLE THING ABOUT POINTS ON THE PLANE

If you call the axes "1" and "$i$" instead of $\hat{i}$ and $\hat{j}$, you'll see that you can write every point as $a + bi$.

You should also be able to see from the pictures above that you could represent each point, each complex number, as a vector, a line segment stretching from the origin of the complex plane to the point $(a, b)$.

Okay. We saw about that multiplication by $i$ is the same as rotating a number around the origin by 90 degrees.

I'm going to claim that not only is *that* fact true... but that multiplying any complex number $x$ by another complex number $y$ transforms the vector represented by $x$ by:

- scaling its length by $y$'s length
- rotating it around the origin by the angle that $y$'s vector formed with the horizontal axis

First, let's do it symbolically, then with a picture.

#### Symbolic

TODO work out the math:

\begin{equation}
(a + bi)(c + di) = ac + adi + bci + bd(i^2) = (ac - bd) + (ad + bc)i
\end{equation}

\begin{equation}
r_1(\cos \theta_1 + i \sin \theta_1)r_2(\cos \theta_2 + i \sin \theta_2)
\label{eq:angles}
\end{equation}

\begin{equation}
r_1 r_2 ((\cos \theta_1 \cos \theta_2 - \sin \theta_1 \sin \theta_2)+ i (\cos \theta_1 \sin \theta_2 + \sin \theta_1 \cos \theta_2))
\end{equation}

Next, go look up a table of trig identities and realize that the orderly arrangements here of $\sin$ and $\cos$ look very much like the [angle difference identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities#Angle_sum_and_difference_identities):

\begin{equation}
\cos \theta_1 \cos \theta_2 - \sin \theta_1 \sin \theta_2 = \cos{\theta_1 + \theta_2}
\end{equation}

and:

\begin{equation}
\cos \theta_1 \sin \theta_2 + \sin \theta_1 \cos \theta_2 = \sin{\theta_1 + \theta_2}
\end{equation}

Using those, the original product collapses down to:

\begin{equation}
r_1 r_2 (cos(\theta_1 + \theta_2) + i \sin(\theta_1 + \theta_2))
\label{eq:confirmangles}
\end{equation}

#### Geometric

Might be more obvious from this picture:
{{< figure src="image-5.png" caption="From Wikipedia." >}}
This picture shows visually all of the relationships we need to verify that you can think of complex number multiplication as rotation and scaling in the complex plane. That is, if you have the patience to go verify all the triangle relationships.

The two complex numbers that this picture represents are $c_1 = \cos \beta + i \sin \beta$ and $c_2 = \cos \alpha + i \sin \alpha$. 

Imagine the red triangle rotated up by an additional angle of $\alpha$. We can work out the same math as in $\eqref{eq:angles}$ above, with $\alpha$ and $\beta$ subbed in, and $r_1 = r_2 = 1$:

\begin{equation}
(\cos \alpha + i \sin \alpha)(\cos \beta + i \sin \beta)
\end{equation}

If you look at the white triangle on the left, you can verify that the final triangle has dimensions:

\begin{equation}
(cos(\alpha + \beta) + i \sin(\alpha + \beta))
\end{equation}

Just like we verified in $\eqref{eq:confirmangles}$.

## Polar Coordinates

The algebra above is a mess. Is there a better way to write these things?

Yes!

It turns out that you can use the amazing [Euler's Formula](https://en.wikipedia.org/wiki/Euler%27s_formula):

\begin{equation}
e^{ix} = \cos x + i \sin x
\label{eq:euler}
\end{equation}

To write any complex number $a + bi$ as $r (\cos \theta + i \sin \theta) = r e^{i \theta}$.

This feels fairly spooky. It *does* make the math easier. When you multiply powers, you simply add the exponents, so the product of two complex numbers both becomes easy, *and* checks out with what we found above:

\begin{equation}
(a + bi)(c + di) = r_1 e^{i \theta_1} r_2 e^{i \theta_2} = r_1 r_2 e^{i (\theta_1 + \theta_2)}
\end{equation}

The new complex number has magnitude $r_1 r_2$ and an angle equal $\theta_1 + \theta_2$.

But why does this work? Where did $e$ come from, and how is it linked to angles, cosine and sine?

To answer *that *question we need our final piece of machinery: the Taylor series approximation.

### Taylor Series Approximation

Notes from memory, though originally I found [this page](https://medium.com/@andrhew.chamberlain/an-easy-way-to-remember-the-taylor-series-expansion-a7c3f9101063) helpful.

The goal here is to motivate *why* we can talk about complex numbers as $e^{i\theta}$.

blah, get after it, smooth functions, show the steps:

\begin{equation}
f(x) = a_0 + a_1 (x - c) + a_2 (x - c)^2 + ... + a_n (x - c)^n
\end{equation}

What can we say about the coefficients? Figuring out the coefficients is the key to figuring out the taylor series expansion of some function.

To get $a_0$, calculate $f(c)$,  and all other terms go to 0.

\begin{equation}
f(c) = a_0
\end{equation}

How about $a_1$? If the function is "smooth", then every derivative exists. That's a clue. Take 

\begin{equation}
f'(x) = a_1 + 2 a_2 (x - c) + ... + n a_n (x - c)^{n-1}
\end{equation}

Taking the derivative subtracts $1$ from each exponent, conveniently setting the constant term to zero and bringing the next coefficient within our grasp.

In general, the coefficient of the $(x-c)^n$ term will have to 

\begin{equation}
a_n = \frac{f^n(c)}{n!}
\end{equation}

So the whole taylor series expansion is:

\begin{equation}
f(x) = f(c) + f'(c) (x - c) + \frac{f''(c)}{2} (x - c)^2 + ... + \frac{f^n(c)}{n!} (x - c)^n
\end{equation}

Or, more compactly:

\begin{equation}
f(x) = \sum_{j = 0}^{n} \frac{f^j(c)}{j!} (x - c)^j
\end{equation}

### Taylor Series Approximation of $e^x$

How does this help us?

Well... $e^x$ is its own derivative! $f(x) = f^n(x) = e^x$.

The taylor series expansion of $e^x$ around $c=0$ is:

\begin{equation}
e^x = 1 + x + \frac{1}{2} x^2 + ... + \frac{1}{n!} x^n = \sum_{j= 0}^{n} \frac{1}{j!} x^j
\end{equation}

### Taylor Series Approximation of $\cos x$ and $\sin x$

Then, for $\cos x$ around 0:

\begin{equation}
\cos x =  1 + \frac{f''(c)}{2} (x - c)^2 + ... + \frac{f^n(c)}{n!} (x - c)^n = \sum_{j= 0}^{n} \frac{1}{j!} x^j
\end{equation}

then $\sin x$ around 0:

\begin{equation}
e^x =  f(c) + f'(c) (x - c) + \frac{f''(c)}{2} (x - c)^2 + ... + \frac{f^n(c)}{n!} (x - c)^n = \sum_{j= 0}^{n} \frac{1}{j!} x^j
\end{equation}

Stare at these...

then do the steps for $e^x$, which is its own derivative.

- show a drawing for how I think about the derivative of cos and sin, and how to remember which is which
- show how you can add them up to equal $e^{i \theta}$

### Euler's Formula

That gets us back to the amazing equation $\eqref{eq:euler}$, repeated here:

\begin{equation}
e^{ix} = \cos x + i \sin x
\end{equation}

Stare at the terms, get it to make sense.

This means that multiplication by a number that looks like $e^{i \theta}$ is equivalent to a rotation of $\theta$ in the complex plane.

### Conclusion

Where can you use this?
