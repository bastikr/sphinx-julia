Sphinx-Julia's documentation
============================

Sphinx-Julia provides two separate extensions for sphinx:

juliadomain
    A sphinx domain for julia.

juliaautodoc
    Automatic code extraction from julia source files.


Installation
------------

At the moment the only way is to clone the git repository from https://github.com/bastikr/sphinx-julia.git

.. code-block:: bash

    >> git clone https://github.com/bastikr/sphinx-julia.git

and either add the directory to the :envvar:`PATHONPATH` e.g.

.. code-block:: bash

    >> export PYTHONPATH=$PYTHONPATH:~/sphinx-julia

or alternatively add the path directly in the sphinx :file:`conf.py`

.. code-block:: python

    import sys
    import os
    sys.path.insert(0, os.path.abspath('~/sphinx-julia'))

The extensions can then be specified in the :file:`conf.py`

.. code-block:: python

    extensions = [
        'sphinxjulia.juliaautodoc',
        'sphinxjulia.juliadomain',
        'sphinx.ext.napoleon',
    ]


Julia domain
------------

This extension provides a sphinx `domain <http://sphinx-doc.org/latest/domains.html>`_ for the julia language using the name :obj:`jl`. A domain is basically a collection of `directives <http://sphinx-doc.org/latest/rest.html#directives>`_ and roles which define markup constructs that then can be rendered to different outputs like html and latex. E.g. the python domain provides the directives :obj:`py:class`, :obj:`py:exception`, :obj:`py:method`, :obj:`py:classmethod`, :obj:`py:staticmethod`, :obj:`py:attribute`, :obj:`py:module`, :obj:`py:currentmodule`, :obj:`py:decorator` and :obj:`py:decoratormethod`. Additionally it provides tools for indexing and cross-referencing these constructs.

Reusing the python implementation is mostly not possible since the underlying model of Python and Julia are too different. E.g. Julia has no notion of methods associated to classes and therefore :obj:`py:method`, :obj:`py:classmethod`, :obj:`py:staticmethod` are all meaningless concepts. On the other hand Julia implements abstract types, type restraints and macros.

At this early point of development juliadomain provides only a fraction of that functionality, i.e. only functions are supported through the :obj:`jl:function` directive.

Example

.. code-block:: rst

    .. jl:function:: myfunc{T}(a::T, b=1; state="Foo", flag::Boolean=True, kwargs...)

            Solve all the things.

            :param a: Very important parameter
            :type a: T
            :param b: Not so important parameter
            :kwparam state: It's a trap.
            :kwparam Boolean flag: Do. Or do not. There is no try.


Julia Autodoc
-------------

.. code-block:: julia

    """
    Solve all the things.

    Parameters
    ----------
    a
        Very important parameter.
    b
        Not so important parameter

    Keyword Parameters
    ------------------
    state
        It's a trap.
    flag
        Do. Or do not. There is no try.
    """
    function myfunc{T}(a::T, b=1; state="Foo", flag::Boolean=True, kwargs...)
        # Do stuff
        return a + b + state + flag + kwargs
    end


.. Contents:

.. .. toctree::
   :maxdepth: 2





.. Indices and tables
    ==================

..    * :ref:`genindex`
    * :ref:`modindex`
    * :ref:`search`

