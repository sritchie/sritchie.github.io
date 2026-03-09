---
title: "Half Angles from Euler's Formula"
date: 2020-06-05T15:59:10.000Z
slug: half-angles-from-eulers-formula
tags:
  - math
  - complex-number
  - proof
categories:
  - math-and-physics
math: true
image: euler-1.png
cover:
  image: "euler-1.png"
  hidden: true
---

I've been reading the lovely [Visual Complex Analysis](https://amzn.to/2UdJtv8) by [Tristan Needham](https://www.usfca.edu/faculty/tristan-needham), and the visual-style proofs he's been throwing down have been wonderful and refreshing. I'll write more about this book and its goals later, but I was inspired this AM to write up a proof of the [half angle identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities#Half-angle_formulae) from trigonometry using some of the tools from the book.

Here's the half angle identity for cosine:

\begin{equation}
\label{eq:half-angle}
\cos {\theta \over 2} = \sqrt{{\cos \theta + 1} \over 2}
\end{equation}

This is an equation that lets you express the cosine for *half* of some angle $\theta$ in terms of the cosine of the angle itself. As you can imagine, there are double-angle, triple angle, all sorts of identities that you can sweat out next time you find yourself in a 9th grade classroom.

It turns out that these derivations all become much more fun with [Euler's Formula](https://www.youtube.com/watch?v=v0YEaeIClKY):

\begin{equation}
\label{eq:euler}
e^{i\theta} = \cos\theta + i \sin\theta
\end{equation}

Let's say you want to figure out the half-angle identity. You have some function of cosine of half of an angle, and you want to pull the $1 \over 2$ out of the cosine.

(This came up for me a couple of days ago in a problem Dave and I ran into working on [Hephaestus](https://github.com/dpetrovics/hephaestus), our quantum mechanics simulator in Clojure. More on that later.)

If you fiddle with the $e^{i \theta}$ representation of complex numbers, a very clear relationship appears:

\begin{equation}
\label{eq:expansion}
e^{i\theta} = e^{2 i{\theta \over 2}} = (e^{i{\theta \over 2}})^2
\end{equation}

Next, use Euler's equation $\eqref{eq:euler}$ and observe that we can rewrite the right side of equation $\eqref{eq:expansion}$ as $(e^{i {\theta \over 2}})^2 = (\cos{\theta \over 2} + i \sin{\theta \over 2})^2$. Expand this out:

\begin{equation}
\label{eq:newnum}
\cos^2 {\theta \over 2} - \sin^2 {\theta \over 2} + i (2 \sin {\theta \over 2} \cos{\theta \over 2})
\end{equation}

Remember, from equation $\eqref{eq:expansion}$, that this is a new complex number that equals $e^{i\theta} = \cos\theta + i \sin\theta$. The real parts of both sides are equal:

\begin{equation}
\cos \theta = \cos^2 {\theta \over 2} - \sin^2 {\theta \over 2}
\label{eq:real}
\end{equation}

and the imaginary parts are equal:

\begin{equation}
\label{eq:imag}
\sin \theta = 2 \sin {\theta \over 2} \cos{\theta \over 2}
\end{equation}

Interesting.

Next, use the $1 - \sin^2 \theta = \cos^2 \theta$ identity on the right side of $\eqref{eq:real}$ and simplify:

\begin{equation}
\label{eq:real-simple}
\cos \theta = 2 \cos^2{\theta \over 2} - 1
\end{equation}

Rearrange and take the square root to get (gasp!) the half-angle identity:

\begin{equation}
\label{eq:cos-half}
\cos {\theta \over 2} = \sqrt{{\cos \theta + 1} \over 2}
\end{equation}

The familiar half angle identity is a nice consequence of equation $\eqref{eq:real}$.

We still have equation $\eqref{eq:imag}$. Could that lead us to the half-angle identity for sine?

Here's the imaginary component again:

\begin{equation}
\label{eq:imag2}
\sin \theta = 2 \sin {\theta \over 2} \cos{\theta \over 2}
\end{equation}

Substitute what we just derived for the cosine half-angle:

\begin{equation}
\label{eq:5}
\sin {\theta} = 2 \sin {\theta \over 2} \sqrt{{\cos \theta + 1} \over 2}
\end{equation}

Square each side and cancel:

\begin{equation}
\label{eq:6}
\sin^2 {\theta} = 2 \sin^2 {\theta \over 2} (\cos \theta + 1)
\end{equation}

Use our identity from before on the left side:

\begin{equation}
\label{eq:10}
\sin^2 \theta = 1 - \cos^2 \theta = (1 + \cos \theta)(1 - \cos \theta)
\end{equation}

Divide through, and take the square root:

\begin{equation}
\label{eq:sin-half}
\sin {\theta \over 2} = \sqrt{{1 - \cos \theta} \over 2}
\end{equation}

And, boom, there it is! the half-angle identity for sine.

## Sums and Differences

If you look back at equation $\eqref{eq:expansion}$ you'll see that this trick would work for any factor inside the exponent, just just the $1 \over 2$. A similar trick can help you figure out any of [sum and difference identities](https://en.wikipedia.org/wiki/List_of_trigonometric_identities#Angle_sum_and_difference_identities), using observations like this:

\begin{equation}
\label{eq:sumdiff}
e^{i(\theta + \phi)} = e^{i\theta}e^{i\phi} = (\cos \theta + i \sin \theta)(\cos \phi + i \sin \phi)
\end{equation}

## Conclusion

The derivation above was much easier for me to understand and push through than the usual geometric derivations I've seen. And, eerily, in going after one of the half angle identities, the other one came along for the ride.

As Tristan Needham says, &quot;every complex equation says two things at once.&quot; (p15, [Visual Complex Analysis](https://amzn.to/2UdJtv8)).

Check out the book, leave it by the bedside, and bend your mind a little by digging into the mysteries of complex numbers.
