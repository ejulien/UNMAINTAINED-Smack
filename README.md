Smack
=====

A MIT licensed set of Python 2.7 scripts to generate makefile and IDE projects

Opening Statement
-----------------

smack is a tool by programmers for programmers, meant to remain simple.
The goal is to have it work 75% of the time and remain easy to fix for the
remaining 25% that fails.

Installation
------------

Write a build.py script (see the included build.py for a moderately complex example), run it.

Features
--------

* Output Visual Studio 2010 C++ solutions and projects,
* Qt project support for Visual Studio (Qt-addin isn't required),
* Output Android JNI makefile,
* Project dependencies and automatic link order,
* Dot map generator to output a graph of project dependencies,
* Easy to extend existing generators,
* Paper-thin API meant to stay this way,
* Each generator is independent.

Have a look in the doc/ folder for more informations on what's supported. Contributions are welcome. I am a Python newbie so if you spot something that can be written in a more pythonic way, feel free to do so.

Cheers!
