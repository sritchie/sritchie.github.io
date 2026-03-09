---
title: "Optics and the Principle of Least Time"
date: 2020-06-10T18:40:57.000Z
slug: optics-and-the-principle-of-least-time
tags:
  - physics
  - proof
  - optics
categories:
  - math-and-physics
math: true
---

(This is a writeup of [Exercise 1.3](https://tgvaughan.github.io/sicm/chapter001.html#Exe_1-3) from Sussman and Wisdom's &quot;Structure and Interpretation of Classical Mechanics&quot;. See the [solutions repository](https://github.com/sritchie/sicm) for more.)

- [Law of Reflection](#sec-1-1)
<ul>
<li>[Geometry](#sec-1-1-1)
- [Calculus](#sec-1-1-2)

</li>
<li>[Law of Refraction](#sec-1-2)

- [Calculus](#sec-1-2-1)
- [Geometry](#sec-1-2-2)

</li>
</ul>

The problem explores some consequences for optics of the principle of least time. The exercise states:

> Fermat observed that the laws of reflection and refraction could be accounted for by the following facts: Light travels in a straight line in any particular medium with a velocity that depends upon the medium. The path taken by a ray from a source to a destination through any sequence of media is a path of least total time, compared to neighboring paths. Show that these facts imply the laws of reflection and refraction.

## Law of Reflection<a id="sec-1-1"></a>

The [law of reflection](https://en.wikipedia.org/wiki/Reflection_(physics)#Laws_of_reflection) is described in the footnote:

> For reflection the angle of incidence is equal to the angle of reflection.

Here's the setup. The horizontal line is a mirror. The law states that $\theta_1 = \theta_2$.

![img](https://github.com/sritchie/sicm/raw/master/images/Lagrangian_Mechanics/2020-06-10_10-31-24_screenshot.png)

We have to show that if we consider all possible paths from a given starting point to a given endpoint, the path of minimum time will give us the law of reflection.

The *actual* path of minimum time is the straight line that avoids the mirror, of course. If we force the light to bounce off of the mirror, then we have to figure out where it will hit, where $x_p$ is, to minimize the time between the start and end points.

There are two ways to solve this problem. We can use geometry and visual intuition, or we can use calculus.

### Geometry<a id="sec-1-1-1"></a>

First, recall this fact from the problem text:

> Light travels in a straight line in any particular medium with a velocity that depends upon the medium.

There's no medium change, so if there were no mirror in its path, the light beam would continue in a straight line. Instead of figuring out what the beam will do when it hits the mirror, reflect the endpoint across the mirror and draw a straight line between the start and &quot;end&quot; points:

![img](https://github.com/sritchie/sicm/raw/master/images/Lagrangian_Mechanics/2020-06-10_10-36-53_screenshot.png)

The angle that the beam makes with the plane of the mirror is the same on both sides of the mirror.

Now reflect the the &quot;end&quot; point and the segment of the beam that's crossed the mirror back up. By symmetry, $\theta_1 = \theta_2$, and we've proved the law of reflection.

### Calculus<a id="sec-1-1-2"></a>

We can also solve this with calculus. Because the beam doesn't change media, its speed $v$ stays constant, so minimizing the total distance $d$ is equivalent to minimizing the time $t = {d \over v}$.

Set $x_1 = 0$ for convenience, and write the total distance the light travels as a function of $x_p$:

\begin{equation}

d(x_p) = \sqrt{y_1^2 + x_p^2} + \sqrt{(x_2 - x_p)^2 + y_2^2}

\end{equation}

For practice, we can also define this function in Scheme.

```scheme
(define ((total-distance x1 y1 x2 y2) xp)
  (+ (sqrt (+ (square (+ x1 xp))
              (square y1)))
     (sqrt (+ (square (- x2 (+ x1 xp)))
              (square y2)))))
```

Here's the function again, generated from code, with general $t_1$:

```scheme
(->tex-equation
 ((total-distance 'x_1 'y_1 'x_2 'y_2) 'x_p))
```

\begin{equation}

\sqrt{{{x}_{1}}^{2} + 2 {x}_{1} {x}_{p} + {{x}_{p}}^{2} + {{y}_{1}}^{2}} + \sqrt{{{x}_{1}}^{2} - 2 {x}_{1} {x}_{2} + 2 {x}_{1} {x}_{p} + {{x}_{2}}^{2} - 2 {x}_{2} {x}_{p} + {{x}_{p}}^{2} + {{y}_{2}}^{2}}

\end{equation}

To find the $x_p$ that minimizes the total distance,

- take the derivative with respect to $x_p$,
- set it equal to 0 and
- solve for $x_p$.

The derivative will look cleaner in code if we keep the components of the sum separate and prevent Scheme from &quot;simplifying&quot;. Redefine the function to return a tuple:

```scheme
(define ((total-distance* x1 y1 x2 y2) xp)
  (up (sqrt (+ (square (+ x1 xp))
               (square y1)))
      (sqrt (+ (square (- x2 (+ x1 xp)))
               (square y2)))))
```

Here are the sum components:

```scheme
(->tex-equation
 ((total-distance* 0 'y_1 'x_2 'y_2) 'x_p))
```

\begin{equation}

\begin{pmatrix} \displaystyle{ \sqrt{{{x}_{p}}^{2} + {{y}_{1}}^{2}}} \cr \cr \displaystyle{ \sqrt{{{x}_{2}}^{2} - 2 {x}_{2} {x}_{p} + {{x}_{p}}^{2} + {{y}_{2}}^{2}}}\end{pmatrix}

\end{equation}

Taking a derivative is easy with `scmutils`. Just wrap the function in `D`:

```scheme
(let* ((distance-fn (total-distance* 0 'y_1 'x_2 'y_2))
       (derivative (D distance-fn)))
  (->tex-equation
   (derivative 'x_p)))
```

\begin{equation}

\begin{pmatrix} \displaystyle{ {{{x}_{p}}\over {\sqrt{{{x}_{p}}^{2} + {{y}_{1}}^{2}}}}} \cr \cr \displaystyle{ {{ - {x}_{2} + {x}_{p}}\over {\sqrt{{{x}_{2}}^{2} - 2 {x}_{2} {x}_{p} + {{x}_{p}}^{2} + {{y}_{2}}^{2}}}}}\end{pmatrix}

\end{equation}

The first component is the base of base $x_p$ of the left triangle over the total length. This ratio is equal to $\cos \theta_1$:

![img](https://github.com/sritchie/sicm/raw/master/images/Lagrangian_Mechanics/2020-06-10_10-36-53_screenshot.png)

The bottom component is $-\cos \theta_2$, or ${- (x_2 - x_p)}$ over the length of the right segment. Add these terms together, set them equal to 0 and rearrange:

\begin{equation}

\label{eq:reflect-laws}

\cos \theta_1 = \cos \theta_2 \implies \theta_1 = \theta_2

\end{equation}

This description in terms of the two incident angles isn't so obvious from the Scheme code. Still, you can use Scheme to check this result.

If the two angles are equal, then the left and right triangles are similar, and the ratio of each base to height is equal:

\begin{equation}

\label{eq:reflect-ratio}

{x_p \over y_1} = {{x_2 - x_p} \over y_2}

\end{equation}

Solve for $x_p$ and rearrange:

\begin{equation}

\label{eq:reflect-ratio2}

x_p = {{y_1 x_2} \over {y_1 + y_2}}

\end{equation}

Plug this in to the derivative of the original `total-distance` function, and we find that the derivative equals 0, as expected:

```scheme
(let* ((distance-fn (total-distance 0 'y_1 'x_2 'y_2))
       (derivative (D distance-fn)))
  (->tex-equation
   (derivative (/ (* 'y_1 'x_2) (+ 'y_1 'y_2)))))
```

\begin{equation}

0

\end{equation}

If a beam of light travels in a way that minimizes total distance (and therefore time in a constant medium), then it will reflect off of a mirror with the same angle at which it arrived. The law of reflection holds.

## Law of Refraction<a id="sec-1-2"></a>

The law of refraction is also called [Snell's law](https://en.wikipedia.org/wiki/Snell%27s_law). Here's the description from the footnote:

> Refraction is described by Snell's law: when light passes from one medium to another, the ratio of the sines of the angles made to the normal to the interface is the inverse of the ratio of the refractive indices of the media. The refractive index is the ratio of the speed of light in the vacuum to the speed of light in the medium.

First we'll tackle this with calculus.

### Calculus<a id="sec-1-2-1"></a>

The setup here is slightly different. We have a light beam traveling from one medium to another and changing speeds at a boundary located $a$ to the right of the starting point. The goal is to figure out the point where the light will hit the boundary, if we assume that the light will take the path of least time.

![img](https://github.com/sritchie/sicm/raw/master/images/Lagrangian_Mechanics/2020-06-10_12-03-11_screenshot.png)

The refractive index $n_i = {c \over v_i}$, the speed of light $c$ in a vacuum over the speed in the material. Rearranging, $v_i = {c \over n_i}$.

Time is distance over speed, so the total time that the beam spends between the start and end points as a function of $y_p$, the point of contact with the boundary, is:

\begin{equation}

\begin{split}

t(y_p) & = {c \sqrt{a^2 + y_p^2}\over v_1} + {c \sqrt{(x_2 - x_p)^2 + y_2^2} \over v_2} \\

& = {n_1 \over c} \sqrt{a^2 + y_p^2} + {n_2 \over c} \sqrt{(x_2 - x_p)^2 + y_2^2}

\end{split}

\end{equation}

Take the derivative:

\begin{equation}

Dt(y_p) = {1 \over c} \left({n_1 y_p \over \sqrt{a^2 + y_p^2}} - {n_2 (x_2 - x_p) \over \sqrt{(x_2 - x_p)^2 + y_2^2}}\right)

\end{equation}

Set the derivative equal to 0 and split terms:

\begin{equation}

\label{eq:almost-snell}

{n_1 y_p \over \sqrt{a^2 + y_p^2}} = {n_2 (x_2 - x_p) \over \sqrt{(x_2 - x_p)^2 + y_2^2}}

\end{equation}

Similar to the law of reflection's result, each term (up to its $n_i$ multiple) is equal to the height of the left or right triangle over the length of the beam's path on the left or right of the boundary.

Equation \eqref{eq:almost-snell} simplifies to:

\begin{equation}

n_1 \sin \theta_1 = n_2 \sin \theta_2

\end{equation}

Rearranging yields Snell's law:

\begin{equation}

{n_1 \over n_2} = {\sin \theta_2 \over \sin \theta_1}

\end{equation}

### Geometry<a id="sec-1-2-2"></a>

I won't recreate this here, but the [Feynman Lectures on Physics](https://www.feynmanlectures.caltech.edu/I_26.html), in [Lecture 26](https://www.feynmanlectures.caltech.edu/I_26.html), has a fantastic discussion about, and derivation of, the law of refraction using no calculus, just geometry. I highly recommend you check out that lecture. Feynman lays out a number of examples of how the principle of least time is not just a restatement of the optical rules we already knew.

You can use the idea to guess what shape of mirror you'd want to build to focus many light rays on a single point (a parabola), or how you might force all light rays coming out of a single point to meet up again at another point (build a converging lens).

This whole area of optics and least time has obsessed scientists for hundreds of years. Spend a few minutes [poking around](https://www.feynmanlectures.caltech.edu/I_26.html) and see what you find.
