---
layout: post
title: Haskell in Emacs
---

{{ page.title }}
================

<p class="meta">Sept 25 - San Francisco</p>

I spent some time today getting my emacs config set up to learn Haskell, and ran into a few issues; I figured I'd go ahead and document the process here for everyone's enjoyment. We're going to install and configure Haskell mode, then add a few extensions that'll make learning Haskell fun and easy!

## Haskell!

Before any of this Emacs jazz, we have to get Haskell, of course. The easiest way to do is to download the [Haskell Platform](http://hackage.haskell.org/platform/), a "Batteries Included" package of the Glasgow Haskell Compiler.

## Emacs Haskell Mode

The [Haskell Mode for Emacs](http://www.haskell.org/haskellwiki/Haskell_mode_for_Emacs) page at the Haskell wiki is the logical place to start, and describes how to install [haskell-mode](http://projects.haskell.org/haskellmode-emacs/). I found it easier to use ELPA, the Emacs Lisp Package Archive (install instructions [here](http://tromey.com/elpa/install.html)). If you're using the [Emacs starter kit](https://github.com/technomancy/emacs-starter-kit), you've already got ELPA.

Once elpa's all set, run `M-x package-list-packages` in Emacs, tap `i` by `haskell-mode`, and hit `x` to the start the install.

## Emacs Config

First, the basics. Add the following to your emacs config (`~/.emacs`, or `~/.emacs.d/init.el`, if you're using the Starter kit):

{% highlight scm %}

(add-hook 'haskell-mode-hook 'turn-on-haskell-doc-mode)

;; hslint on the command line only likes this indentation mode;
;; alternatives commented out below.
(add-hook 'haskell-mode-hook 'turn-on-haskell-indentation)
;;(add-hook 'haskell-mode-hook 'turn-on-haskell-indent)
;;(add-hook 'haskell-mode-hook 'turn-on-haskell-simple-indent)

;; Ignore compiled Haskell files in filename completions
(add-to-list 'completion-ignored-extensions ".hi")

{% endhighlight %}

At this point, you should be able to start using Haskell. Create a file called `test.hs` somewhere, and type `C-c C-z` to get to the Haskell REPL, supplied by [inf-haskell mode](http://www.haskell.org/haskellwiki/Haskell_mode_for_Emacs#inf-haskell.el:_the_best_thing_since_the_breadknife). Now, add the following to `test.hs`:

{% highlight haskell %}

square :: Integral a => a -> a
square x = x * x

{% endhighlight %}

And type `C-c C-l` in that buffer to load the file's contents into the REPL. `C-c C-z` over the repl, and try it out:

{% highlight haskell %}

*Main> square 10
100
*Main> square 34
1156

{% endhighlight %}

Nice.

## Hs-Lint

Next, we're going to add support for Flymake. This is a piece of Emacs functionality that'll run our Haskell files through the compiler every few seconds and associate any warnings and errors with a specific line in our file.

While we're at it, we'll configure hs-lint, which we can run periodically on our Haskell files for a list of hints as to how to structure code better. For example, running `hs-lint` on a Haskell file containing `times2 x = (*) 2 x` yields a buffer with:

    hlint /Users/sritchie/test.hs
    /Users/sritchie/test.hs:1:1: Error: Eta reduce
    Found:
      times2 x = (*) 2 x
    Why not:
      times2 = (*) 2

    1 suggestion

Definitely helpful in the learning process.

{% highlight scm %}

(require 'hs-lint)    ;; https://gist.github.com/1241059

(defun flymake-haskell-init
  "When flymake triggers, generates a tempfile containing the
  contents of the current buffer, runs `hslint` on it, and
  deletes file. Put this file path (and run `chmod a+x hslint`)
  to enable hslint: https://gist.github.com/1241073"
  ()
  (let* ((temp-file   (flymake-init-create-temp-buffer-copy
                       'flymake-create-temp-inplace))
         (local-file  (file-relative-name
                       temp-file
                       (file-name-directory buffer-file-name))))
    (list "hslint" (list local-file))))

(defun flymake-haskell-enable
  "Enables flymake-mode for haskell, and sets <C-c d> as command
to show current error."
  ()
  (when (and buffer-file-name
             (file-writable-p
              (file-name-directory buffer-file-name))
             (file-writable-p buffer-file-name))
    (local-set-key (kbd "C-c d") 'flymake-display-err-menu-for-current-line)
    (flymake-mode t)))

(custom-set-faces
 '(flymake-errline ((((class color)) (:underline "red"))))
 '(flymake-warnline ((((class color)) (:underline "yellow")))))

{% endhighlight %}

Now, let's add autocompletion.

{% highlight scm %}

(require 'haskell-ac) ;; https://gist.github.com/1241063

(defun my-haskell-mode-hook
  "hs-lint binding, plus autocompletion and paren face, and paredit."
  ()
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

{% endhighlight %}

You can find a copy of all of these extensions here... (provide a link to a gist of the elisp file.)
