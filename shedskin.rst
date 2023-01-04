========
Shedskin
========

---------------------------------------------------
An experimental (restricted) Python-to-C++ Compiler
---------------------------------------------------

:Date:   2022-11-03
:Version: 0.9.5
:Manual section: 1

SYNOPSIS
========

shedskin [OPTION]... FILE

DESCRIPTION
===========

Shed Skin is an experimental compiler, that can translate pure, but implicitly statically typed Python (2.4-2.7) programs into optimized C++. It can generate stand-alone programs or extension modules that can be imported and used in larger Python programs.

Besides the typing restriction, programs cannot freely use the Python standard library (although about 25 common modules, such as random and re, are currently supported). Also, not all Python features, such as nested functions and variable numbers of arguments, are supported.

OPTIONS
=======

 -a --ann               Output annotated source code (.ss.py)

 -b --nobounds          Disable bounds checking

 -c --nogc              Disable garbage collection

 -e --extmod            Generate extension module

 -f --flags             Provide alternate Makefile flags

 -g --nogcwarns         Disable runtime GC warnings

 -l --long              Use long long integers

 -m --makefile          Specify alternate Makefile name

 -n --silent            Silent mode, only show warnings

 -o --noassert          Disable assert statements

 -r --random            Use fast random number generator (rand())

 -w --nowrap            Disable wrap-around checking

 -x --traceback         Print traceback for uncaught exceptions

 -L --lib               Add a library directory
