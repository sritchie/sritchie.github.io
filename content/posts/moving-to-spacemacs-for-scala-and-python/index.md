---
title: "Moving to Spacemacs for Scala and Python"
date: 2019-09-23T23:53:39.000Z
slug: moving-to-spacemacs-for-scala-and-python
tags:
  - code
  - emacs
categories:
  - programming
image: 68747470733a2f2f7777772e6e61737365722e73706163652f696d67732f73706163656d6163732d6c6f676f2e706e67.png
cover:
  image: "68747470733a2f2f7777772e6e61737365722e73706163652f696d67732f73706163656d6163732d6c6f676f2e706e67.png"
  hidden: true
---

I've just finished retooling my development environment, and the process was annoying enough that I thought I'd write it up here, for myself in the future, and for you in the present.

**tl;dr; I ended up porting my old Emacs config, based on the literate emacs24-starter-kit, over to Spacemacs, and ended up with a great Scala and Python setup.**

Read on for the details.

## Goals

I've been an Emacs user since my first days with Clojure, and I'm hooked, fully in love. Those Clojure days were a long time ago; as I've spent more time developing in Scala and Python, I've made do with basically just code formatting and syntax highlighting, delegating to an external build tool like SBT in a terminal window to give me compilation feedback every so often. My Emacs config is crusty and old, and way out of date.

I've been working on ScalaRL ([github page](https://github.com/sritchie/scala-rl), [microsite](https://www.scalarl.com/)), a functional, monadic reinforcement learning framework in Scala, and I've been feeling the pain of my setup. It was time for an overhaul.

I had two goals this weekend:

- Upgrade my Emacs config to support [Metals](https://scalameta.org/metals/docs/editors/emacs.html), the latest and greatest (and only!) Emacs... IDE? out there today.
- Understand the absolutely insane world of Python packaging well enough that I could dig into some of the latest deep learning examples out there in a reproducible way, more similar to the self-contained Clojure and Scala projects I'm used to.

## Spacemacs

Reading about modern Emacs configs it became clear that my old strategy of just manually installing packages that seemed nice had led me into a hellish, non-reproducible setup. I decided to declare bankruptcy and start again with [Spacemacs](http://spacemacs.org/).

Spacemacs is a batteries-and-steroids-included configuration for Emacs designed to lure you into a modal style of editing, like [Vim](https://www.vim.org/) provides. It also provides a large number of community-provided "layers", which are declarative bundles of packages and config hooks designed to add support for different features and languages to Spacemacs.

The [Scala layer for Spacemacs](http://develop.spacemacs.org/layers/+lang/scala/README.html) looked great, and had support for [Metals](https://scalameta.org/metals/docs/editors/emacs.html), a Scala language server designed to give IDE-like functionality to a bunch of different editors. ([Ensime](https://ensime.github.io/) is dead! Long live Ensime!)

The Python mode looked great too.

### Installation

Here's what I did to install Spacemacs:

First, I went through my `.bashrc` file and culled out all of the old crap that had accumulated over multiple jobs and many years of building up an environment. The biggest thing I did was to delete any reference to Macports from my machine and my path. The multiple-installation ecosystem for Ruby and Python has always been a pain for me; I suspect that's due to a Linux environment that I built up over years without really knowing what was going on under the hood.

Next, I moved my old `$USER/.emacs.d` directory to `$USER/emacs.d.old` so I could reference its settings, and as backup in case I botched what came next.

I deleted my old emacs installation with `brew uninstall emacs` and killed my alias in `/Applications/Emacs.app`, then reinstalled the latest and greatest Emacs with the instructions in the [Spacemacs beginner's tutorial](https://github.com/syl20bnr/spacemacs/blob/develop/doc/BEGINNERS_TUTORIAL.org).

- First, install [Homebrew](https://brew.sh/).
- Run these two commands:

```sh
brew tap d12frosted/emacs-plus
brew install emacs-plus
# brew linkapps emacs-plus
```

The final, commented-out command won't work anymore, since Homebrew no longer has a `linkapps` subcommand. Instead, run this to create a symlink in your Applications directory:

```sh
ln -s /usr/local/opt/emacs-plus/Emacs.app /Applications
```

To install Spacemacs itself, run the following commands:

```sh
git clone https://github.com/syl20bnr/spacemacs ~/.emacs.d
cd ~/.emacs.d
git checkout 3e93dec6635bf54fa8a36ac8da6d6b98a9775541
```

This will get Spacemacs up to the revision I used in my configuration, which I know works great for Scala and Python development with [my spacemacs.d config](https://github.com/sritchie/spacemacs.d).

If you want the fresh Spacemacs experience, you can go ahead and launch `Emacs.app` by double-clicking the new icon in your `/Applications` folder and following the rest of the [beginner's tutorial here](https://github.com/syl20bnr/spacemacs/blob/develop/doc/BEGINNERS_TUTORIAL.org#installation-and-setup).

Read on for more details about my specific configuration. I'm still using Spacemacs in "holy-mode", or Emacs mode, ie, without the Vim keybindings. I'll work on that next.

## Configuring Spacemacs

Here's my old [Emacs config directory](https://github.com/sritchie/emacs.d), based on the [emacs24-starter-kit](https://github.com/eschulte/emacs24-starter-kit) and now almost a decade old.

Spacemacs completely commandeers `.emacs.d`; instead of writing config there, you get to play in either a `.spacemacs` file or a `.spacemacs.d` directory. Either way, Spacemacs generates a big template config for you that you can modify as you get started.

I did the latter, and once I got everything converted I pushed the whole directory to Github. It lives at [https://github.com/sritchie/spacemacs.d](https://github.com/sritchie/spacemacs.d).

Most of my configuration changes were keybindings that I wanted to keep from my old setup. Here are some examples.

This remaps the Apple command key to Meta, and the option key to super.

```elisp
(setq mac-option-modifier 'super)
(setq mac-command-modifier 'meta)
```

This snippet removes the titlebar, making the installation look super smooth:

```elisp
(add-to-list 'default-frame-alist '(ns-transparent-titlebar . t))
```

I also installed the [Source Code Pro](https://github.com/adobe-fonts/source-code-pro/releases/tag/2.030R-ro%2F1.050R-it) font that Spacemacs prefers. It does look good!

You can check out the Spacemacs [dotfile configuration page](http://spacemacs.org/doc/DOCUMENTATION.html#dotfile-configuration) for more tips. I didn't change too much about the default setup; I was focused on customizing the Scala and Python experiences, as I'll go into next.

Here's my `[init.el](https://github.com/sritchie/spacemacs.d/blob/master/init.el)` file if you want to peruse the whole range of defaults that you can tweak.

I stuffed all of my language-specific configuration, and the layers I decided to install, into my own layers, which you can find [here](https://github.com/sritchie/spacemacs.d/tree/master/layers).

I didn't quite finish; I still have a bunch of Clojure, Lisp and Haskell code to convert over. I'm going to wait to do that until I have the pleasure of programming in those languages again for a project. Until then I'm keeping the org files that used to generate my customizations in this ["random" folder in the spacemacs directory](https://github.com/sritchie/spacemacs.d/tree/master/random).

## Python and Scala

I'm going to save the details of customizing Spacemacs for these two development environments for two further posts. I'll link them here when they're complete. Stay tuned!
