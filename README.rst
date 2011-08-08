======
PyCamp
======

Tool for organizing and working with multiple virtual environments.

Home page:     http://github.com/riffm/pycamp

Issue tracker: http://github.com/riffm/pycamp/issues


Installation
============

You can install from pypi by ``easy_install`` or ``pip``::

    % easy_install pycamp
    % pip install pycamp

Or download package and use standard python way::

    % python setup.py install


Usage
=====

You can use ``pycamp`` from any location in your filesystem. Just type::

    % python -m pycamp

``pycamp`` expects a ``pycamp.cfg`` file in that location. It's the main
description of all environments and actions (commands, actualy).

For help run::

    % python -m pycamp --help

----------
pycamp.cfg
----------

Every section in ``pycamp.cfg`` is a name of environment. There is only a few
options for envs

- *python* - a python executable to use in a virtual environment (default is
  ``python``)
- *deps* - a list of dependencies which will be installed by ``pip``.
  If there will be changes in the future you can update existing environment
  packages (optional)
- *base* - a name of an environment you want to inherit from (optional)

--------------------
command descriptions
--------------------

You can provide commands by prefexing section name with ``cmd:``::

    [cmd:test]
    run = %(bin-dir)/nosetests --all-modules

Options

- *run* - actual command to execute. You can use template variables `bin-dir`
  and *python-executable*
- *cwd* optional current working directory for command. Must be relative to
  ``pycamp.cfg`` location
- *env* optional environment name. This option limits execution of a command
  only for certain environment
