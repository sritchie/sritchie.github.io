---
title: "Entropy: Combinations and Permutations"
date: 2020-01-29T13:39:36.000Z
slug: entropy-combinations-and-permutations
tags:
  - physics
  - entropy
  - math
categories:
  - math-and-physics
math: true
image: firstchoice-1.png
---

In my ongoing quest to lay a more solid foundation for this new, strange life as a machine learning "researcher", I've been going through various foundational concepts and ideas and trying to build up rock solid intuitions that I can lean on for years. (Why the hell didn't I do this back in school??)

Entropy is my latest obsession - thermodynamic entropy, and information entropy, and the ways in which these two things are similar.

This is the first of a short series of posts building up the mathematical concepts and tools required for a solid understanding of what *entropy* is. The rough plan is to cover:

- permutations vs combinations (this post!), various ones you might want
- How to think about logarithms and exponents, and when to reach for each
- Stirling's approximation for calculating enormous factorials
- Thermodynamic entropy and statistical mechanics
- Information entropy, as defined by Shannon
- How information entropy and Thermodynamic entropy might be the same thing.

Once the series is complete, I'll come back and fill in some reasons why you might be interested in this stuff and generally polish things up. If you've found this post in its current state, read on for an unmotivated account of how many different ways there are to pluck items out of a bag.

## Overview

This post will cover:

- **permutations**: all the different ways you might sort some collection of items.
- **k-permutations**: all the ways possible to sort some some subset of a collection.
- **combinations**: forget order... how many ways can you get distinct subsets of a big set of items?
- **power sets**: what are ALL the possible subsets you can make from some big collection?
- **k-groupings**: how many different ways can I put the items in my collection into $k$ different bins?

For each, I'll present the formula you'll typically see, and then show off some intuitive ways to think about the problem that should let you figure out the formulas on your own whenever you need to use them.

## Permutations

Let's say you have some set of items:
{{< figure src="allset.png" >}}
The *permutations* of the set are all of the possible ways that you can arrange, in order, the items in that set. There are 6 possible permutations of the set above:
{{< figure src="sets.png" caption="Ignore my set notation, please... these are ordered triples!" >}}
Some examples of permutations you might care about are:

- The number of possible anagrams you can form out of a word
- Every possible way to choose a lineup of kids in a dodgeball game
- All the possible ways to assign wedding guests to chairs (7.16 * $10^{118}$ for an 80 person wedding, around a thousand trillion times more than the number of [elementary particles](https://en.wikipedia.org/wiki/Elementary_particle) in the known universe

Is there some link between the number of items in a set of size $n$ and the number of possible permutations of those items?

Of course there is! The number of permutations is

\begin{equation}
permutations(n) = n!
\label{eq:permutations}
\end{equation}

where $n!$ is the factorial function:

\begin{equation}
n! = n \cdot n - 1 \cdot n -2 \cdot  ... 1 = \prod_{i=1}^n n_i
\label{eq:factorial}
\end{equation}

This checks out for a few examples:

- If the set had only contained 1 item, as in $\{a\}$, the only permutation would be to take the item itself: $(a)$. $1 = 1!$, so this works.
- If there had been only 2 items, say $\{a, b\}$, there are only 2 ways to permute them - $(a, b)$ and $(b, a)$. $2 = 2! = 2 \cdot 1$, so this checks out.
- The set of 3 items above had 6 permutations, or $3! = 3 \cdot 2 \cdot 1$.

Why is this relationship generally true? Let's first look at a visual example of how you'd generate permutations from some set, then look at some code.

### Choosing Items

If we have a set of $n$ items, to generate a permutation we have to start by making a single choice. We have $n$ different choices we can make, each of which is a valid start to a permutation. Each of those choices will leave $n-1$ items left in the set.

Here's a drawing of each possible choice, linked to the remaining items.
{{< figure src="firstchoice.png" >}}
for each of the remaining items we can play the same game. We have $n-1$ choices in each set; after each choice, we'll have $n-2$ remaining items.
{{< figure src="tree.png" >}}
Stay focused on those first two levels for a second. Each of the $n-1$ choices above is for the *second* item in a permutation; because we had $n$ original choices, each of which resulted in $n-1$ more possible decisions, we've learned that there are $n(n -1)$ possible ways to make our first two choices.

This game continues all the way down until each branch has a single choice left. By that time, we've made $n!$ total choices:

\begin{equation}
n! = n \cdot n - 1 \cdot n -2 \cdot  ... 1
\label{eq:fac2}
\end{equation}

Factorials show up when you're counting up groups of things where each choice takes an item out of the mix.

### Trees and Paths

You can also visualize permutations as the number of total possible paths through a tree, where each branch plucks some item off of the set. The diagram above is a tree:
{{< figure src="tree.png" >}}
This [post by Shawn O'Mara](https://buildingvts.com/intuition-behind-permutations-and-combinations-db6ffa5272be) has a wonderful set of diagrams and descriptions of permutations and other combinatoric goodies using trees. Here's a diagram similar to mine for the set $\{a, b, c, d\}$:
{{< figure src="image-7.png" caption="From 'Intuition behind Permutations and Combinations'" >}}
Each path through the tree represents a permutation.

If you could the number of branches at each level of the tree, you'll see that they slowly descend from 4 branches at the first level, to 3, then 2, then 1. Each level of branching represents the "[many worlds](https://en.wikipedia.org/wiki/Many-worlds_interpretation)" that a choice between the level's branches represents.

You can also count the number of items at each level. Each path has to end in a final "leaf", so counting leaves is the same as counting paths. The tree above has $4 \cdot 3 \cdot 2 \cdot 1 = 24 = 4!$ leaves, just like we expected.

### Permutations in Scala

How do you generate permutations in code? Here's one attempt in Scala:

```scala
/**
  This function generates the set of all possible permutations of the items in
  the input set.
  */
def permutations[A](items: Set[A]): Set[List[A]] =
  if (items.isEmpty) Set(List.empty)
  else {
    items.flatMap { x =>
      // For every item in the input set:
      //
      // - generate all possible permutations of the set WITHOUT that item
      //   present; we expect (n - 1)! total permutations.
      // - loop through all of those permutations and stick the removed item
      //   onto the beginning to generate (n -1)! permutations, each with the
      //   removed item on the front.
      // - the "flatMap" above calls this inner function once for each of the
      // n items, then sews together all of the returned sets... this gives us
      // a final set of size n * (n - 1)! = n!
      permutations(items - x).map(x :: _)
    }
  }
```

Again, in English:

- If you give me the empty set, return a set of a single permutation - the empty set.
- Otherwise, for every item, go get every permutation of the set you get by *removing* that item; then stick the item on the beginning of every permutation.
- Fuse all of those permutations together, $n$ groups of whatever size $permutations(n-1)$ returns. Because you descend down to $1$ eventually, the total number of permutations is $n * permutations(n-1) * permutations(n-2)...1$, or $n!$.

The function generates the actual permutations, but if you track the size of the sets that are passed down into recursive calls of `permutations`, you'll notice that each recursive call removes one item from the set. If `permutations` receives an *empty* input set, it returns a set with 1 item in it.

Think of a "loop counter" associated with each call to `permutations`. The function gets called $n$ times on each loop; on each call, `permutations` is called with $n - 1$ items, then the results are all fused together.

We know that each item is distinct because sets can't contain duplicates, and we add the removed item back on only after the recursive call.

The function above is very close to a proof that the total number of permutations for a set of size $n$ equals $n!$.

### More Permutations in Scala

Here's another implementation in Scala that generates permutations in a different way:

```scala
def permutationsTwo[A](input: Set[A]): Set[List[A]] = {

  // we use an inner function called "loop" so that we can hide the fact that
  // we're converting the input set into a list. Sets don't have ordering, but
  // we need to enforce one for this approach.
   def loop(items: List[A]): Set[List[A]] =
    items match {
      // the base case returns a set with 1 item.
      case Nil => Set(List.empty)

      // this pattern match breaks the items into the first item in the list and
      // the remaining items; xs has size n - 1, 1 fewer than the size of
      // `items`.
      case x :: xs =>

        // loop is called recursively here with a "loop counter" of n - 1.
        loop(xs).flatMap { permutation =>

          // Each of those n - 1 entries looks something like (b,a,c). For
          // each of these, the next block of code generates new lists by:
          //
          // - inserting the element that was NOT passed down into the loop -
          //   say, "d" - into the slot AFTER every one of the existing
          //   elements, and
          // - adding one extra list with "d" at the beginning

          // for a total of n new permutations for each of the (n - 1) passed
          // back up through the loop.
          //
          // n * permutations(n - 1) = n! total permutations, since we bottom
          // out at 1.
          (0 to permutation.size).map { i =>
            val (pre, post) = permutation.splitAt(i)
            pre ++ List(x) ++ post
          }
        }
    }

  loop(input.toList)
}
```

Different approach to generating cardinalities; same logic for tracking how the sizes of the returned set increase with each new item in the input set.

### Permutations of the Empty Set

What happens if you pass the empty set into the functions above? How many permutations can you take from a set with nothing in it?

You'd think it would be $0$, and that $0! = 0$. The problem is that $0$ is the *multiplicative identity*, and if the definition of factorial let you go all the way down to $0$, as in $3 \cdot 2 \cdot 1 \cdot 0$, the $0$ would destroy everything and set the factorial equal to $0$ ALWAYS.

It's obvious in the code examples above that to make everything work, you have to return a set that contains ONE permutation - the empty set! $0! = 1$ for any implementation I can think of in Scala.

The mathematical argument for why this has to be true feels silly, but there's no reason it can't hold.

The permutations of a set are all of the possible distinct orderings that contain the same number of items as the original set. Well, there is ONE list (an ordered data structure) that contains the same number of items... the empty list! There are no other lists with 0 items, so we can rule out every ordered thing... except for the empty list. If we can't rule out a permutation, we have to include it, so there it is: the permutations of $\{\} = \{()\}$, and $0! = 1$.

## K-Permutations (in progress)

[https://en.wikipedia.org/wiki/Permutation#k-permutations_of_n](https://en.wikipedia.org/wiki/Permutation#k-permutations_of_n)

What if you want to stop? Well...

What's the equation here? We just stop when we have k items remaining. How do we express that as a nice formula?
{{< figure src="helper.png" >}}
### Examples

- All of the possible words of length k that you can make at ALL with some set of letters.
- Every possible hand of cards &lt;=

### Grabbing Items

same as before.

### Trees

Same as before, we just stop.

### Code

Very similar, but this

```scala
def kPermutations[A](items: Set[A], k: Int): Set[List[A]] = {
  assert(k >= 0 && k <= items.size)

  if (k == 0) Set(List.empty)
  else {
    items.flatMap { x =>
      kPermutations(items - x, k - 1).map(x :: _)
    }
  }
}
```

### Helpful References

- $nPr$ notations
- [https://en.wikipedia.org/wiki/Permutation](https://en.wikipedia.org/wiki/Permutation)
- This was useful for the first thing: [http://hyperphysics.phy-astr.gsu.edu/hbase/Math/permut.html#c2](http://hyperphysics.phy-astr.gsu.edu/hbase/Math/permut.html#c2)

## Combinations

then combinations, you're plucking sets. $nPr / r!$, divide out the permutations of $r$ items buried in.

### Examples

- Drawing cards... actual hands
- entropy example.

```scala
def combinations[A](items: Set[A], k: Int): Set[Set[A]] =
  kPermutations(items, k).map(_.toSet)
    
def factorial(n: Int): Int =
  if (n == 0) 1 else n * factorial(n - 1)

def numCombinations(n: Int, k: Int): Int =
  factorial(n) / (factorial(n - k) * factorial(k))
```

## 

### Binomial Coefficients

Why does the binomial coefficient equal the number of combinations here?? That is super weird. Go through and get some intuition here.

## Power Sets

Side note... if you add up the number of combinations of $k$ from 0 to $n$, you get what's called the "power set", which has cardinality $2^k$.

WHY IS THAT?

Well... imagine a bit-mask, a series of 1 or 0 that you'll lay over the items in the set. How many possible combinations of 1s and 0s of length n can you make?

Well, we have two choices at first... then we keeping going, and every time we make a choice we multiply.

- show that the formulas work. Super strange.

note about how we can add up all the k permutations to get the total powerset: [https://en.wikipedia.org/wiki/Binomial_coefficient#Sums_of_the_binomial_coefficients](https://en.wikipedia.org/wiki/Binomial_coefficient#Sums_of_the_binomial_coefficients)

```scala
// This gets ALL combinations...
  def powerset[A](items: Set[A]): Set[Set[A]] = {

    @tailrec
    def loop(remaining: List[A], ret: Set[Set[A]]): Set[Set[A]] =
      remaining match {
        case Nil => ret
        case x :: xs => loop(xs, ret ++ ret.map(_ + x))
      }

    loop(items.toList, Set(Set.empty))
  }

  // nice short way that uses foldLeft to accumulate.
  def powerset[A](items: Set[A]): Set[Set[A]] =
    items.foldLeft(Set(Set.empty[A])) { case (acc, a) =>
      acc ++ acc.map(_ + a)
    }
```

You can sort of see here that the cardinality is the cardinality of... well, think it through.

## Multiset Permutations

- [https://en.wikipedia.org/wiki/Permutation#Permutations_of_multisets](https://en.wikipedia.org/wiki/Permutation#Permutations_of_multisets)

how many ways can I put n items into k bins? THEN we have to talk about this fantastic derivation of the number of ways to put something into k bins: [https://en.wikipedia.org/wiki/Multinomial_theorem#Interpretations](https://en.wikipedia.org/wiki/Multinomial_theorem#Interpretations)

- Give some examples here, then draw it out.
- Show that we can think of the bin boundaries as items, and then construct the formula THAT way.
