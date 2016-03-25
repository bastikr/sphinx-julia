.. _julia-domain:

Julia Domain
============

This extension provides a sphinx `domain <http://sphinx-doc.org/latest/domains.html>`_ for the Julia language using the name :obj:`jl`. A domain is basically a collection of `directives <http://sphinx-doc.org/latest/rest.html#directives>`_ and roles which define markup constructs that then can be rendered to different outputs like html and latex. E.g. the python domain provides the directives :obj:`py:class`, :obj:`py:exception`, :obj:`py:method`, :obj:`py:classmethod`, :obj:`py:staticmethod`, :obj:`py:attribute`, :obj:`py:module`, :obj:`py:currentmodule`, :obj:`py:decorator` and :obj:`py:decoratormethod`. Additionally it provides tools for indexing and cross-referencing these constructs.

Reusing the python implementation is mostly not possible since the underlying model of Python and Julia are too different. E.g. Julia has no notion of methods associated to classes and therefore :obj:`py:method`, :obj:`py:classmethod`, :obj:`py:staticmethod` are all meaningless concepts. On the other hand Julia implements abstract types, type restraints and macros.


.. _julia-domain-directives:

Directives
----------

Types
^^^^^

There are two directives :obj:`type` and :obj:`abstract` representing composite types and abstract types respectively. Both of them are rather straight forward to use. E.g.

.. epigraph::

    .. code-block:: rst

        .. jl:abstract:: Theory

            The general principles or ideas that relate to a particular subject

        .. jl:type:: QuantumTheory <: Theory

             A theory based on the idea that energy is made of small separate units of energy.

is rendered as

.. epigraph::

    .. jl:abstract:: Theory

        The general principles or ideas that relate to a particular subject.

    .. jl:type:: QuantumTheory <: Theory

        A theory based on the idea that energy is made of small separate units of energy.


Modules
^^^^^^^

Modules are created by using the :obj:`module` directive and can be used to group other objects together. They can also be nested and provide a common namespace which is indicated by indentation and can be seen in the following example

.. epigraph::

    .. code-block:: rst

        .. jl:module:: linalg

            .. jl:abstract:: Array

                General array type.

            .. jl:module:: sparse

                Sparse linear algebra functionality.

                .. jl:type:: SparseMatrix <: Array

                    Sparse matrix implementation.

            .. jl:type:: Matrix <: Array

                Dense matrix implementation.

which gives the following output

.. epigraph::

    .. jl:module:: linalg

        .. jl:abstract:: Array

            General array type.

        .. jl:module:: sparse

            Sparse linear algebra functionality.

            .. jl:type:: SparseMatrix <: Array

                Sparse matrix implementation.

        .. jl:type:: Matrix <: Array

            Dense matrix implementation.


Functions
^^^^^^^^^

Using the directive :obj:`jl:function` allows us to define a function by giving the functions signature as argument. The simple example

.. epigraph::

    .. code-block:: rst

        .. jl:function:: f(a)

renders as

.. epigraph::

    .. jl:function:: f(a)

Additional text in the body of the directive can be used for documentation of the function

.. epigraph::

    .. code-block:: rst

        .. jl:function:: f(a::Int, b=1)

            Detailed explanation of everything.

and looks like

.. epigraph::

    .. jl:function:: f(a::Int, b=1)

        Detailed explanation of everything.


Also more complicated signatures are possible and also most of the roles defined for the python domain can be used allowing for a nice description of the parameters. E.g.

.. epigraph::

    .. code-block:: rst

        .. jl:function:: myfunc{T}(a::T, b=1; state="Foo", flag::Boolean, kwargs...)

            Solve all the things.

            :param a: Very important parameter
            :type a: T
            :param b: Not so important parameter
            :kwparam state: It's a trap.
            :kwparam flag: Do. Or do not. There is no try.

gives the following output

.. epigraph::

    .. jl:function:: myfunc{T}(a::T, b=1; state="Foo", flag=True, kwargs...)

        Solve all the things.

        :param a: Very important parameter
        :type a: T
        :param b: Not so important parameter
        :kwparam state: It's a trap.
        :kwparam flag: Do. Or do not. There is no try.


.. _julia-domain-roles:

Roles
-----

Every directive introduced above can be referenced via the roles :obj:`type`, :obj:`abstract`, :obj:`mod` and :obj:`func`.

Using ``:jl:type:`Matrix``` (:jl:type:`Matrix`) and ``:jl:abstract:`Array``` (:jl:abstract:`Array`) creates references to these types .

Targets can be referenced fully qualified ``:jl:mod:`linalg.sparse``` (:jl:mod:`linalg.sparse`) or shortened as ``:jl:mod:`sparse``` (:jl:mod:`sparse`).

Functions are in the simplest case identified just by their name, e.g. ``:jl:func:`myfunc``` (:jl:func:`myfunc`). In order to distinguish between methods of the same name one can additionally use pattern matching like ``:jl:func:`f(a)``` (:jl:func:`f(a)`), ``:jl:func:`f(a,b)``` (:jl:func:`f(a,b)`), ``:jl:func:`f(a::Int,)``` (:jl:func:`f(a::Int,)`) or ``:jl:func:`f(,=1)``` (:jl:func:`f(,=1)`).

