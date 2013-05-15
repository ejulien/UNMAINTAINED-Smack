Smack
=====

A MIT licensed set of Python 2.7 scripts to generate makefile and IDE projects

Opening Statement
-----------------

smack is a tool by programmers for programmers, meant to remain simple.
The goal is to have it work 75% of the time and easy to fix for the 25% that fail.

Installation
------------

Write a build.py script (see the included build.py for a moderately complex example), run it.

Features
--------

* Visual Studio 2010 C++ solutions and project generator,
* Qt extension for the vs2010 generator (Qt-addin isn't required),
* VSAndroid (Android for Visual Studio) extension for the vs2010 generator,
* Native Android JNI makefile generator,
* Project dependencies to inherit build properties and automatic makefile link order,
* Graphviz generator to output a graph of project dependencies,
* Output several solutions/project/targets from the same build file,
* Paper-thin API meant to stay this way,
* Easy to extend existing generators,
* Each generator is independent,
* Free beer.

Have a look in the doc/ folder for more informations on what's supported. Contributions are welcome.
I am a Python newbie so if you spot something that can be written in a more pythonic way, feel free to do so.

Cheers!
