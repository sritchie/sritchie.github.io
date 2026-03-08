---
title: "Haskell in Emacs"
date: 2011-09-25T22:24:00.000Z
slug: haskell-in-emacs
tags:
  - code
  - haskell
categories:
  - programming
---

I spent some time today getting my emacs config set up to learn Haskell, and ran into a few issues; I figured I'd go ahead and document the process here for everyone's enjoyment. We're going to install and configure Haskell mode, then add a few extensions that'll make learning Haskell fun and easy!

I'm currently running haskell-mode for emacs, with the `hs-lint` plugin, Haskell support for FlyMake (which provides on-the-fly syntax checking from the Haskell compiler), and code autocompletion. The steps covered by this tutorial are:

1. Installing Haskell
2. Configuring Haskell-Mode for Emacs
3. Installing Haskell-Mode Extensions (Flymake support, `hs-lint` and autocompletion)

## Installing Haskell<a id="sec-1-1" name="sec-1-1"></a>

Before any of this Emacs jazz, we have to get Haskell, of course. The easiest way to do is to download the [Haskell Platform](http://hackage.haskell.org/platform/), a &quot;Batteries Included&quot; package of the Glasgow Haskell Compiler.

## Emacs Haskell Mode<a id="sec-1-2" name="sec-1-2"></a>

The [Haskell Mode for Emacs](http://www.haskell.org/haskellwiki/Haskell_mode_for_Emacs) page at the Haskell wiki is a nice place to start your explorations, and describes how to install [haskell-mode](http://projects.haskell.org/haskellmode-emacs/). I found it easier to use ELPA, the Emacs Lisp Package Archive (install instructions [here](http://tromey.com/elpa/install.html)). If you're using the [Emacs starter kit](https://github.com/technomancy/emacs-starter-kit), you've already got ELPA.

Once elpa's all set, install `haskell-mode` with the following:

1. run `M-x package-list-packages` in Emacs
2. tap `i` by `haskell-mode`
3. hit `x` to the start the install.

## Configuring emacs.el<a id="sec-1-3" name="sec-1-3"></a>

Before we get into linting or any other customizations, Add the following to your emacs config (`~/.emacs`, or `~/.emacs.d/init.el`, if you're using the Starter kit):

```
(add-hook 'haskell-mode-hook 'turn-on-haskell-doc-mode)

;; hslint on the command line only likes this indentation mode;
;; alternatives commented out below.
(add-hook 'haskell-mode-hook 'turn-on-haskell-indentation)
;;(add-hook 'haskell-mode-hook 'turn-on-haskell-indent)
;;(add-hook 'haskell-mode-hook 'turn-on-haskell-simple-indent)

;; Ignore compiled Haskell files in filename completions
(add-to-list 'completion-ignored-extensions ".hi")
```

At this point, you should be able to start using Haskell in emacs. Let's write our first function.

- Create a file called `test.hs`.
- type `C-c C-z` to get to the Haskell REPL, supplied by [inf-haskell mode](http://www.haskell.org/haskellwiki/Haskell_mode_for_Emacs#inf-haskell.el:_the_best_thing_since_the_breadknife)

Now, add the following to `test.hs`:

```
module Examples where

square :: Integral a => a -> a
square x = x * x
```

Then type `C-c C-l` in that buffer to load the file's contents into the REPL. `C-c C-z` over to the repl again and try it out:

```
*Main> square 10
100
*Main> square 34
1156
```

Nice.

## Flymake<a id="sec-1-4" name="sec-1-4"></a>

Next, we're going to add support for Flymake, the emacs syntax-checker. This is a piece of Emacs functionality that'll run our Haskell files through the compiler every few seconds and associate any warnings and errors with some specific line in our Haskell file.

While we're at it, we'll configure `hs-lint`, which we can run periodically on our Haskell files for a list of hints as to how to structure code better. For example, running `hs-lint` on a Haskell file containing `times2 x = (*) 2 x` yields a buffer with:

```
hlint /Users/sritchie/test.hs
/Users/sritchie/test.hs:1:1: Error: Eta reduce
Found:
  times2 x = (*) 2 x
Why not:
  times2 = (*) 2

 1 suggestion
```

Definitely helpful in the learning process.

Flymake depends on an external perl script, `hslint`, to pass the contents of the current buffer into the Haskell compiler.

- Download `hslint` from [this gist](https://gist.github.com/1241073) and place it somewhere on your path.
- run `chmod a+x hslint` to give the file executable privileges

Add the following to `.emacs`:

```
(defun flymake-haskell-init ()
  "When flymake triggers, generates a tempfile containing the
  contents of the current buffer, runs `hslint` on it, and
  deletes file. Put this file path (and run `chmod a+x hslint`)
  to enable hslint: https://gist.github.com/1241073"
  (let* ((temp-file   (flymake-init-create-temp-buffer-copy
                       'flymake-create-temp-inplace))
         (local-file  (file-relative-name
                       temp-file
                       (file-name-directory buffer-file-name))))
    (list "hslint" (list local-file))))

(defun flymake-haskell-enable ()
  "Enables flymake-mode for haskell, and sets <C-c d> as command
  to show current error."
  (when (and buffer-file-name
             (file-writable-p
              (file-name-directory buffer-file-name))
             (file-writable-p buffer-file-name))
    (local-set-key (kbd "C-c d") 'flymake-display-err-menu-for-current-line)
    (flymake-mode t)))

;; Forces flymake to underline bad lines, instead of fully
;; highlighting them; remove this if you prefer full highlighting.
(custom-set-faces
 '(flymake-errline ((((class color)) (:underline "red"))))
 '(flymake-warnline ((((class color)) (:underline "yellow")))))
```

## Haskell Extensions<a id="sec-1-5" name="sec-1-5"></a>

### Auto Complete Mode<a id="sec-1-5-1" name="sec-1-5-1"></a>

Now, let's add autocompletion. Autocomplete mode is awesome; it provides IDE-like word tab completion of words based on info in open buffers, and some knowledge of the modes of the emacs buffer you're currently working in. In Haskell, we'll get autocompletion of every function we define, plus help with core language constructs. Head over to [Auto Complete Mode](http://cx4a.org/software/auto-complete/index.html) to download the package, and install with the following:

1. Download and unpack Autocomplete mode
2. Open emacs, and run `M-x load-file`
3. Point the minibuffer to `&lt;autocomplete-root&gt;/etc/install.el`
4. Follow the remaining [AC install instructions](http://cx4a.org/software/auto-complete/manual.html#Installation).

That should get you all set for the next step.

### Linting!<a id="sec-1-5-2" name="sec-1-5-2"></a>

1. Download [hs-lint.el](https://gist.github.com/1241059) and [haskell-ac.el](https://gist.github.com/1241063) and place each file inside of `~/.emacs.d`. (`hs-lint` is our linter, of course, and `haskell-ac.el` provides autocomplete mode with some knowledge of a few core Haskell constructs.

Add the following to your `.emacs` file:

```
(require 'hs-lint)    ;; https://gist.github.com/1241059
(require 'haskell-ac) ;; https://gist.github.com/1241063

(defun my-haskell-mode-hook ()
  "hs-lint binding, plus autocompletion and paredit."
  (local-set-key "\C-cl" 'hs-lint)
  (setq ac-sources
        (append '(ac-source-yasnippet
                  ac-source-abbrev
                  ac-source-words-in-buffer
                  my/ac-source-haskell)
                ac-sources))
  (dolist (x '(haskell literate-haskell))
    (add-hook
     (intern (concat (symbol-name x)
                     "-mode-hook"))
     'turn-on-paredit)))

(eval-after-load 'haskell-mode
  '(progn
     (require 'flymake)
     (push '("\\.l?hs\\'" flymake-haskell-init) flymake-allowed-file-name-masks)
     (add-hook 'haskell-mode-hook 'flymake-haskell-enable)
     (add-hook 'haskell-mode-hook 'my-haskell-mode-hook)))
```

The above code binds `C-c l` to `hs-lint` inside of Haskell buffers, and configures a large number of Haskell keywords for autocompletion. Go and test it out inside of `test.hs`; you should find that `square` autocompletes when you begin typing.

Now go ahead and add the following line to `test.hs`:

```
face :: Int -> Bool
```

Upon save, or within seconds, you should see an angry red underline. Move the cursor over that line and type `C-c d`, and you'll see a tooltip with the following text:

```
1: The type signature for `face' lacks an accompanying binding.
```

Adding this will clear things up:

```
face x = 5 < x
```

## Finishing Up<a id="sec-1-6" name="sec-1-6"></a>

I hope this helped those of you looking to get started exploring Haskell! Please let me know in the comments if anything could be clearer; I'll be posting more down the road, and all requests are welcome.
