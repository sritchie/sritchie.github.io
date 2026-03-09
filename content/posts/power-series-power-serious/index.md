---
title: "Power Series, Power Serious"
date: 2020-11-09T20:05:45.000Z
slug: power-series-power-serious
math: true
---

This post spawned from work I've been doing on the [SICMUtils](https://github.com/littleredcomputer/sicmutils) library; I've just [released 0.13.0](https://github.com/littleredcomputer/sicmutils/releases/tag/v0.13.0) and I hope you'll give it a try.

SICMUtils is the engine behind the wonderful "Structure and Interpretation of Classical Mechanics", an advanced physics textbook by Gerald Sussman of SICP fame. I'm trying to get the textbook [running in the browser](https://roadtoreality.substack.com/p/the-dynamic-notebook) as a Clojurescript library, and as part of that effort I've had to re-implement quite a bit of numerical code in Clojure.

Can I admit that I've gone deeper than necessary? After I'd gotten to know the library, I noted that the power series implementation could use some work. Jack Rusher pointed me at a  gorgeous power series implementation by Doug McIlroy (my Uncle's boss at Bell Labs!). See [his website](https://www.cs.dartmouth.edu/~doug/powser.html) for 10-lines version of beautiful Haskell.

 Doug's paper, ["Power Series, Power Serious"](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.333.3156&rep=rep1&type=pdf), goes into more detail on the implementation, which leans hard on Haskell's lazy evaluation. Clojure has lazy sequences too! I implemented [the paper here](https://github.com/littleredcomputer/sicmutils/blob/master/src/sicmutils/series/impl.cljc), then went further and made power series executable, and extended them to play with the whole generic arithmetic system in [this namespace](https://github.com/littleredcomputer/sicmutils/blob/master/src/sicmutils/series.cljc).

This post is a rendered, literate programming version of `impl.cljc`, the core power series implementation based on Doug's work. It's exactly the same code we use in the library.

Enjoy!

- [Sequence Operations](#sequence-operations)
  - [Negation](#negation)
  - [Addition](#addition)
  - [Subtraction](#subtraction)
  - [Multiplication](#multiplication)
  - [Division](#division)
  - [Reciprocal](#reciprocal)
  - [Functional Composition](#functional-composition)
  - [Reversion](#reversion)
  - [Series Calculus](#series-calculus)
  - [Exponentiation](#exponentiation)
  - [Square Root of a Series](#square-root-of-a-series)
- [Examples](#examples)
- [Various Power Series](#various-power-series)
- [Generating Functions](#generating-functions)
  - [Catalan numbers](#catalan-numbers)

The following code builds up a power series implementation that backs two `sicmutils` types:

- `Series`, which represents a generic infinite series of arbitrary values, and
- `PowerSeries`, a series that represents a power series in a single variable; in other words, a series where the nth entry is interpreted as the coefficient of $x^n$:

\begin{equation}

\label{eq:4}

[a\ b\ c\ d\ ...] = a + bx + cx^2 + dx^3 + ...

\end{equation}

We'll proceed by building up implementations of the arithmetic operations `+`, `-`, `*`, `/` and a few others using bare Clojure lazy sequences.

The implementation follows Doug McIlroy's beautiful paper, ["Power Series, Power Serious"](http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.333.3156&rep=rep1&type=pdf). Doug also has a 10-line version in Haskell on [his website](https://www.cs.dartmouth.edu/~doug/powser.html).

Let's go!

# Sequence Operations

A 'series' is an infinite sequence of numbers, represented by Clojure's lazy sequence. First, a function `->series` that takes some existing sequence, finite or infinite, and coerces it to an infinite seq by concatenating it with an infinite sequence of zeros. (We use `v/zero-like` so that everything plays nicely with generic arithmetic.)

```clojure
(defn ->series
  "Form the infinite sequence starting with the supplied values. The
  remainder of the series will be filled with the zero-value
  corresponding to the first of the given values."
  [xs]
  (lazy-cat xs (repeat (v/zero-like (first xs)))))
```

```clojure
(take 10 (->series [1 2 3 4]))
```

```clojure
(1 2 3 4 0 0 0 0 0 0)
```

The core observation we'll use in the following definitions (courtesy of McIlroy) is that a power series $F$ in a variable $x$:

\begin{equation}

F(x)=f_{0}+x f_{1}+x^{2} f_{2}+\cdots

\end{equation}

Decomposes into a head element $f_0$ plus a tail series, multiplied by $x$:

\begin{equation}

\label{eq:3}

F(x) = F_0(x) = f_0 + x F_1(x)

\end{equation}

We'll use this observation to derive the more complicated sequence operations below.

## Negation

To negate a series, negate each element:

```clojure
(defn negate [xs]
  (map g/negate xs))
```

Example:

```clojure
(take 7 (negate (->series [1 2 3 4])))
```

```clojure
(-1 -2 -3 -4 0 0 0)
```

## Addition

We can derive series addition by expanding the series $F$ and $G$ into head and tail and rearranging terms:

\begin{equation}

\label{eq:5}

F+G=\left(f+x F_{1}\right)+\left(g+xG_{1}\right)=(f+g)+x\left(F_{1}+G_{1}\right)

\end{equation}

This is particularly straightforward in Clojure, where `map` already merges sequences elementwise:

```clojure
(defn seq:+ [f g]
  (map g/+ f g))
```

```clojure
(take 5 (seq:+ (range) (range)))
```

```clojure
(0 2 4 6 8)
```

A constant is a series with its first element populated, all zeros otherwise. To add a constant to another series we only need add it to the first element. Here are two versions, constant-on-left vs constant-on-right:

```clojure
(defn c+seq [c f]
  (lazy-seq
   (cons (g/+ c (first f)) (rest f))))

(defn seq+c [f c]
  (lazy-seq
   (cons (g/+ (first f) c) (rest f))))
```

```clojure
(let [series (->series [1 2 3 4])]
  [(take 6 (seq+c series 10))
   (take 6 (c+seq 10 series))])
```

```clojure
[(11 2 3 4 0 0) (11 2 3 4 0 0)]
```

## Subtraction

Subtraction comes for free from the two definitions above:

```clojure
(defn seq:- [f g]
  (seq:+ f (negate g)))
```

```clojure
(take 5 (seq:- (range) (range)))
```

```clojure
(0 0 0 0 0)
```

We *should* get equivalent results from mapping `g/-` over both sequences, and in almost all cases we do… but until we understand and fix [this bug](https://github.com/littleredcomputer/sicmutils/issues/151) that method would return different results.

Subtract a constant from a sequence by subtracting it from the first element:

```clojure
(defn seq-c [f c]
  (lazy-seq
   (cons (g/- (first f) c) (rest f))))
```

```clojure
(take 5 (seq-c (range) 10))
```

```clojure
(-10 1 2 3 4)
```

To subtract a sequence from a constant, subtract the first element as before, but negate the tail of the sequence:

```clojure
(defn c-seq [c f]
  (lazy-seq
   (cons (g/- c (first f)) (negate (rest f)))))
```

```clojure
(take 5 (c-seq 10 (range)))
```

```clojure
(10 -1 -2 -3 -4)
```

## Multiplication

What does it mean to multiply two infinite sequences? As McIlroy notes, multiplication is where the lazy-sequence-based approach really comes into its own.

First, the simple cases of multiplication by a scalar on either side of a sequence:

```clojure
(defn seq*c [f c] (map #(g/mul % c) f))
(defn c*seq [c f] (map #(g/mul c %) f))
```

To multiply sequences, first recall from above that we can decompose each sequence $F$ and $G$ into a head and tail.

Mutiply the expanded representations out and rearrange terms:

\begin{equation}

\label{eq:6}

F \times G=\left(f+x F_{1}\right) \times\left(g+x G_{1}\right)=f g+x\left(f G_{1}+F_{1} \times G\right)

\end{equation}

$G$ appears on the left and the right, so use an inner function that closes over $g$ to simplify matters, and rewrite the above definition in Clojure:

```clojure
(defn seq:* [f g]
  (letfn [(step [f]
            (lazy-seq
             (let [f*g  (g/mul (first f) (first g))
                   f*G1 (c*seq (first f) (rest g))
                   F1*G (step (rest f))]
               (cons f*g (seq:+ f*G1 F1*G)))))]
    (step f)))
```

This works just fine on two infinite sequences:

```clojure
(take 10 (seq:* (range) (->series [4 3 2 1])))
```

```clojure
(0 4 11 20 30 40 50 60 70 80)
```

NOTE This is also called the "[Cauchy Product](https://en.wikipedia.org/wiki/Cauchy_product)" of the two sequences. The description on the Wikipedia page has complicated index tracking that simply doesn't come in to play with the stream-based approach. Amazing!

## Division

The quotient $Q$ of $F$ and $G$ should satisfy:

\begin{equation}

\label{eq:7}

F = Q \times G

\end{equation}

From McIlroy, first expand out $F$, $Q$ and one instance of $G$:

\begin{equation}

\begin{aligned}

f+x F_{1} &=\left(q+x Q_{1}\right) \times G \cr

&=q G+x Q_{1} \times G=q\left(g+x G_{1}\right)+x Q_{1} \times G \cr

&=q g+x\left(q G_{1}+Q_{1} \times G\right)

\end{aligned}

\end{equation}

Look at just the constant terms and note that $q = \frac{f}{g}$.

Consider the terms multiplied by $x$ and solve for $Q_1$:

\begin{equation}

\label{eq:8}

Q_1 = \frac{(F_1 - qG_1)}{G}

\end{equation}

There are two special cases to consider:

- If $g=0$, $q = \frac{f}{g}$ can only succeed if $f=0$; in this case, $Q = \frac{F_1}{G1}$, from the larger formula above.
- If $f=0$, $Q_1 = \frac{(F_1 - 0 G_1)}{G} = \frac{F_1}{G}$

Encoded in Clojure:

```clojure
(defn div [f g]
  (lazy-seq
   (let [f0 (first f) fs (rest f)
         g0 (first g) gs (rest g)]
     (cond (and (v/nullity? f0) (v/nullity? g0))
           (div fs gs)

           (v/nullity? f0)
           (cons f0 (div fs g))

           (v/nullity? g0)
           (u/arithmetic-ex "ERROR: denominator has a zero constant term")

           :else (let [q (g/div f0 g0)]
                   (cons q (-> (seq:- fs (c*seq q gs))
                               (div g))))))))
```

A simple example shows success:

```clojure
(let [series (->series [0 0 0 4 3 2 1])]
  (take 5 (div series series)))
```

```clojure
(1 0 0 0 0)
```

## Reciprocal

We could generate the reciprocal of $F$ by dividing $(1, 0, 0, ...)$ by $F$. Page 21 of an earlier [paper by McIlroy](https://swtch.com/~rsc/thread/squint.pdf) gives us a more direct formula.

We want $R$ such that $FR = 1$. Expand $F$:

\begin{equation}

\label{eq:9}

(f + xF_1)R = 1

\end{equation}

Solve for R:

\begin{equation}

\label{eq:10}

R = \frac{1}{f} (1 - x(F_1 R))

\end{equation}

A recursive definition is no problem in the stream abstraction:

```clojure
(defn invert [f]
  (lazy-seq
   (let [finv    (g/invert (first f))
         F1*Finv (seq:* (rest f) (invert f))
         tail    (c*seq finv (negate F1*Finv))]
     (cons finv tail))))
```

This definition of `invert` matches the more straightforward division implementation:

```clojure
(let [series (iterate inc 3)]
  (= (take 5 (invert series))
     (take 5 (div (->series [1]) series))))
```

```clojure
true
```

An example:

```clojure
(let [series (iterate inc 3)]
  [(take 5 (seq:* series (invert series)))
   (take 5 (div series series))])
```

```clojure
[(1N 0N 0N 0N 0N) (1 0 0 0 0)]
```

Division of a constant by a series comes easily from our previous multiplication definitions and `invert`:

```clojure
(defn c-div-seq [c f]
  (c*seq c (invert f)))
```

It's not obvious that this works:

```clojure
(let [nats (iterate inc 1)]
  (take 6 (c-div-seq 4 nats)))
```

```clojure
(4 -8 4 0 0 0)
```

But we can recover the initial series:

```clojure
(let [nats       (iterate inc 1)
      divided    (c-div-seq 4 nats)
      seq-over-4 (invert divided)
      original   (seq*c seq-over-4 4)]
  (take 5 original))
```

```clojure
(1N 2N 3N 4N 5N)
```

To divide a series by a constant, divide each element of the series:

```clojure
(defn seq-div-c [f c]
  (map #(g// % c) f))
```

Division by a constant undoes multiplication by a constant:

```clojure
(let [nats (iterate inc 1)]
  (take 5 (seq-div-c (seq*c nats 2) 2)))
```

```clojure
(1 2 3 4 5)
```

## Functional Composition

To compose two series $F(x)$ and $G(x)$ means to create a new series $F(G(x))$. Derive this by substuting $G$ for $x$ in the expansion of $F$:

\begin{equation}

\begin{aligned}

F(G)&=f+G \times F_{1}(G) \cr

&=f+\left(g+x G_{1}\right) \times F_{1}(G) \cr

&=\left(f+g F_{1}(G)\right)+x G_{1} \times F_{1}(G)

\end{aligned}

\end{equation}

For the stream-based calculation to work, we need to be able to calculate the head element and attach it to an infinite tail; unless $g=0$ above the head element depends on $F_1$, an infinite sequence.

If $g=0$ the calculation simplifies:

\begin{equation}

\label{eq:12}

F(G)=f + x G_{1} \times F_{1}(G)

\end{equation}

In Clojure, using an inner function that captures $G$:

```clojure
(defn compose [f g]
  (letfn [(step [f]
            (lazy-seq
             ;; NOTE I don't understand why we get a StackOverflow if I move
             ;; this assertion out of the ~letfn~.
             (assert (zero? (first g)))
             (let [[f0 & fs] f
                   gs (rest g)
                   tail (seq:* gs (step fs))]
               (cons f0 tail))))]
    (step f)))
```

Composing $x^2 = (0, 0, 1, 0, 0, ...)$ should square all $x$s, and give us a sequence of only even powers:

```clojure
(take 10 (compose (repeat 1)
                  (->series [0 0 1])))
```

```clojure
(1 0 1 0 1 0 1 0 1 0)
```

## Reversion

The functional inverse of a power series $F$ is a series $R$ that satisfies $F(R(x)) = x$.

Following McIlroy, we expand $F$ (substituting $R$ for $x$) and one occurrence of $R$:

\begin{equation}

\label{eq:13}

F(R(x))=f+R \times F_{1}(R)=f+\left(r+x R_{1}\right) \times F_{1}(R)=x

\end{equation}

Just like in the composition derivation, in the general case the head term depends on an infinite sequence. Set $r=0$ to address this:

\begin{equation}

\label{eq:14}

f+x R_{1} \times F_{1}(R)=x

\end{equation}

For this to work, the constant $f$ must be 0 as well, hence

\begin{equation}

\label{eq:15}

R_1 = \frac{1}{F_1(R)}

\end{equation}

This works as an implementation because $r=0$. $R_1$ is allowed to reference $R$ thanks to the stream-based approach:

```clojure
(defn revert [f]
  {:pre [(zero? (first f))]}
  (letfn [(step [f]
            (lazy-seq
             (let [F1   (rest f)
                   R    (step f)]
               (cons 0 (invert
                        (compose F1 R))))))]
    (step f)))
```

An example, inverting a series starting with 0:

```clojure
(let [f (cons 0 (iterate inc 1))]
  (take 5 (compose f (revert f))))
```

```clojure
(0 1 0 0 0)
```

## Series Calculus

Derivatives of power series are simple and mechanical:

\begin{equation}

\label{eq:16}

D(a x^n) = aD(x^n) = a n x^{n-1}

\end{equation}

Implies that all entries shift left by 1, and each new entry gets multiplied by its former index (ie, its new index plus 1).

```clojure
(defn deriv [f]
  (map g/* (rest f) (iterate inc 1)))
```

```clojure
(take 6 (deriv (repeat 1)))
```

```clojure
(1 2 3 4 5 6)
```

Which of course we interpret as

\begin{equation}

\label{eq:17}

1 + 2x + 3x^2 + ...

\end{equation}

The definite integral $\int_0^{x}F(t)dt$ is similar. To take the anti-derivative of each term, move it to the right by appending a constant term onto the sequence and divide each element by its new position:

```clojure
(defn integral
  ([s] (integral s 0))
  ([s constant-term]
   (cons constant-term
         (map g/div s (iterate inc 1)))))
```

With a custom constant term:

```clojure
(take 6 (integral (iterate inc 1) 5))
```

```clojure
(5 1 1 1 1 1)
```

By default, the constant term is 0:

```clojure
(take 6 (integral (iterate inc 1)))
```

```clojure
(0 1 1 1 1 1)
```

## Exponentiation

Exponentiation of a power series by some integer is simply repeated multiplication. The implementation here is more efficient the iterating `seq:*`, and handles negative exponent terms by inverting the original sequence.

```clojure
(defn expt [s e]
  (letfn [(expt [base pow]
            (loop [n pow
                   y (->series [1])
                   z base]
              (let [t (even? n)
                    n (quot n 2)]
                (cond
                  t (recur n y (seq:* z z))
                  (zero? n) (seq:* z y)
                  :else (recur n (seq:* z y) (seq:* z z))))))]
    (cond (pos? e)  (expt s e)
          (zero? e) (->series [1])
          :else (invert (expt s (g/negate e))))))
```

We can use `expt` to verify that $(1+x)^3$ expands to $1 + 3x + 3x^2 + x^3$:

```clojure
(take 5 (expt (->series [1 1]) 3))
```

```clojure
(1 3 3 1 0)
```

## Square Root of a Series

The square root of a series $F$ is a series $Q$ such that $Q^2 = F$. We can find this using our calculus methods from above:

\begin{equation}

\label{eq:18}

D(F) = 2Q D(Q)

\end{equation}

or

\begin{equation}

\label{eq:19}

D(Q) = \frac{D(F)}{2Q}

\end{equation}

When the head term of $F$ is nonzero, ie, $f \neq 0$, the head of $Q = \sqrt{F}$ must be $\sqrt{f}$ for the multiplication to work out.

Integrate both sides:

\begin{equation}

\label{eq:20}

Q = \sqrt{f} + \int_0^x \frac{D(F)}{2Q}

\end{equation}

One optimization appears if the first two terms of $F$ vanish, ie, $F=x^2F_2$. In this case $Q = 0 + x \sqrt{F_2}$.

Here it is in Clojure:

```clojure
(defn sqrt [[f1 & [f2 & fs] :as f]]
  (if (and (v/nullity? f1)
           (v/nullity? f2))
    (cons f1 (sqrt fs))
    (let [const (g/sqrt f1)
          step  (fn step [g]
                  (lazy-seq
                   (-> (div (deriv g)
                            (c*seq 2 (step g)))
                       (integral const))))]
      (step f))))
```

And a test that we can recover the naturals:

```clojure
(let [xs (iterate inc 1)]
  (take 6 (seq:* (sqrt xs)
                 (sqrt xs))))
```

```clojure
(1 2 3 4 5 6)
```

We can maintain precision of the first element is the square of a rational number:

```clojure
(let [xs (iterate inc 9)]
  (take 6 (seq:* (sqrt xs)
                 (sqrt xs))))
```

```clojure
(9 10N 11N 12N 13N 14N)
```

We get a correct result if the sequence starts with $0, 0$:

```clojure
(let [xs (concat [0 0] (iterate inc 9))]
  (take 6 (seq:* (sqrt xs)
                 (sqrt xs))))
```

```clojure
(0 0 9 10N 11N 12N)
```

# Examples

Power series computations can encode polynomial computations. Encoding $(1-2x^2)^3$ as a power series returns the correct result:

```clojure
(take 10 (expt (->series [1 0 -2]) 3))
```

```clojure
(1 0 -6 0 12 0 -8 0 0 0)
```

Encoding $\frac{1}{(1-x)}$ returns the power series $1 + x + x^2 + \ldots$ which sums to that value in its region of convergence:

```clojure
(take 10 (div (->series [1])
              (->series [1 -1])))
```

```clojure
(1 1 1 1 1 1 1 1 1 1)
```

$\frac{1}{(1-x)^2}$ is the derivative of the above series:

```clojure
(take 10 (div (->series [1])
              (-> (->series [1 -1])
                  (expt 2))))
```

```clojure
(1 2 3 4 5 6 7 8 9 10)
```

# Various Power Series

With the above primitives we can define a number of series with somewhat astonishing brevity.

$e^x$ is its own derivative, so $e^x = 1 + e^x$:

```clojure
(def expx
  (lazy-seq
   (integral expx 1)))
```

This bare definition is enough to generate the power series for $e^x$:

```clojure
(take 10 expx)
```

```clojure
(1 1 1/2 1/6 1/24 1/120 1/720 1/5040 1/40320 1/362880)
```

$sin$ and $cos$ afford recursive definitions. $D(sin) = cos$ and $D(cos) = -sin$, so (with appropriate constant terms added) on:

```clojure
(declare cosx)
(def sinx (lazy-seq (integral cosx)))
(def cosx (lazy-seq (c-seq 1 (integral sinx))))
```

```clojure
(take 10 sinx)
```

```clojure
(0 1 0 -1/6 0 1/120 0 -1/5040 0 1/362880)
```

```clojure
(take 10 cosx)
```

```clojure
(1 0 -1/2 0 1/24 0 -1/720 0 1/40320 0)
```

tangent and secant come easily from these:

```clojure
(def tanx (div sinx cosx))
(def secx (invert cosx))
```

Reversion lets us define arcsine from sine:

```clojure
(def asinx (revert sinx))
(def atanx (integral (cycle [1 0 -1 0])))
```

These two are less elegant, perhaps:

```clojure
(def acosx (c-seq (g/div 'pi 2) asinx))
(def acotx (c-seq (g/div 'pi 2) atanx))
```

The hyperbolic trig functions are defined in a similar way:

```clojure
(declare sinhx)
(def coshx (lazy-seq (integral sinhx 1)))
(def sinhx (lazy-seq (integral coshx)))
(def tanhx (div sinhx coshx))
(def asinhx (revert sinhx))
(def atanhx (revert tanhx))

(def log1-x
  (integral (repeat -1)))

;; https://en.wikipedia.org/wiki/Mercator_series
(def log1+x
  (integral (cycle [1 -1])))
```

# Generating Functions

## Catalan numbers

These are a few more examples from McIlroy's "Power Serious" paper, presented here without context.

```clojure
(def catalan
  (lazy-cat [1] (seq:* catalan catalan)))
```

```clojure
(take 10 catalan)
```

```clojure
(1 1 2 5 14 42 132 429 1430 4862)
```

ordered trees…

```clojure
(declare tree' forest' list')
(def tree' (lazy-cat [0] forest'))
(def list' (lazy-cat [1] list'))
(def forest' (compose list' tree'))
```

```clojure
(take 10 tree')
```

```clojure
(0 1 1 2 5 14 42 132 429 1430)
```

The catalan numbers again!

```clojure
(def fib (lazy-cat [0 1] (map + fib (rest fib))))
```

See here for the recurrence relation: [https://en.wikipedia.org/wiki/Binomial_coefficient#Multiplicative_formula](https://en.wikipedia.org/wiki/Binomial_coefficient#Multiplicative_formula)

```clojure
(defn binomial* [n]
  (letfn [(f [acc prev n k]
            (if (zero? n)
              acc
              (let [next (/ (* prev n) k)
                    acc' (conj! acc next)]
                (recur acc' next (dec n) (inc k)))))]
    (persistent!
     (f (transient [1]) 1 n 1))))
```

```clojure
(defn binomial
  "The coefficients of (1+x)^n"
  [n]
  (->series (binomial* n)))
```
