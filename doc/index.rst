============
Sphinx-Julia
============

Sphinx-Julia provides two separate extensions for sphinx:

:ref:`julia-domain`
    A sphinx domain for Julia.

:ref:`julia-autodoc`
    Automatic docstring extraction from Julia source files.



Installation
============


PyPI - the Python Package Index
-------------------------------

You can download the latest package from the official Python Package Index

https://pypi.python.org/pypi/Sphinx-Julia


Source
------

Development happens on github (https://github.com/bastikr/sphinx-julia.git) and the source code can be obtained by

.. code-block:: bash

    >> git clone https://github.com/bastikr/sphinx-julia.git

Make sure sphinx can find the extensions by either adding this repository to the :envvar:`PATHONPATH` e.g.

.. code-block:: bash

    >> export PYTHONPATH=$PYTHONPATH:~/sphinx-julia

or alternatively add the path directly in the sphinx config file :file:`conf.py`

.. code-block:: python

    # conf.py
    import sys
    import os
    sys.path.insert(0, os.path.abspath('~/sphinx-julia'))


Usage
-----

To be able to actually use the functionality of these extensions in your documentation you have to specify this in the :file:`conf.py` file by adding :obj:`sphinxjulia.juliadomain` and :obj:`sphinxjulia.juliaautodoc` to the extensions list. If you docstrings in numpy or google style you can also add :obj:`sphinx.ext.napoleon` which will give much nicer output.

.. code-block:: python

    extensions = [
        'sphinxjulia.juliadomain',
        'sphinxjulia.juliaautodoc',
        'sphinx.ext.napoleon',
    ]

The directives provided by these extensions are explained in :ref:`julia-domain` and :ref:`julia-autodoc`. The documentation for the napoleon extension can be found at http://sphinx-doc.org/latest/ext/napoleon.html.

