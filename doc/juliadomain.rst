.. _julia-domain:

Julia Domain
------------

This extension provides a sphinx `domain <http://sphinx-doc.org/latest/domains.html>`_ for the Julia language using the name :obj:`jl`. A domain is basically a collection of `directives <http://sphinx-doc.org/latest/rest.html#directives>`_ and roles which define markup constructs that then can be rendered to different outputs like html and latex. E.g. the python domain provides the directives :obj:`py:class`, :obj:`py:exception`, :obj:`py:method`, :obj:`py:classmethod`, :obj:`py:staticmethod`, :obj:`py:attribute`, :obj:`py:module`, :obj:`py:currentmodule`, :obj:`py:decorator` and :obj:`py:decoratormethod`. Additionally it provides tools for indexing and cross-referencing these constructs.

Reusing the python implementation is mostly not possible since the underlying model of Python and Julia are too different. E.g. Julia has no notion of methods associated to classes and therefore :obj:`py:method`, :obj:`py:classmethod`, :obj:`py:staticmethod` are all meaningless concepts. On the other hand Julia implements abstract types, type restraints and macros.

At this early point of development :obj:`juliadomain` provides only a fraction of that functionality, i.e. only functions are supported through the :obj:`jl:function` directive.


Functions
^^^^^^^^^

Using the directive :obj:`jl:function` allows us to define a function by giving the functions signature as argument. The simple example

.. code-block:: rst

    .. jl:function:: f(a)

renders as

.. jl:function:: f(a)

Additional text in the body of the directive can be used for documentation of the function

.. code-block:: rst

    .. jl:function:: f(a)

        Detailed explanation of everything.

and looks like

.. jl:function:: f(a)

    Detailed explanation of everything.


Also more complicated signatures are no problem and also most of the roles defined for the python domain can be used allowing for a nice description of the parameters. E.g.

.. code-block:: rst

    .. jl:function:: myfunc{T}(a::T, b=1; state="Foo", flag::Boolean, kwargs...)

        Solve all the things.

        :param a: Very important parameter
        :type a: T
        :param b: Not so important parameter
        :kwparam state: It's a trap.
        :kwparam flag: Do. Or do not. There is no try.

gives the following output

.. jl:function:: myfunc{T}(a::T, b=1; state="Foo", flag=True, kwargs...)

        Solve all the things.

        :param a: Very important parameter
        :type a: T
        :param b: Not so important parameter
        :kwparam state: It's a trap.
        :kwparam flag: Do. Or do not. There is no try.

