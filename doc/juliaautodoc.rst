.. _julia-autodoc:

Julia Autodoc
=============

The autodoc extension is used to automatically extract documentation from source code. Contrary to its python equivalent where introspection is used to obtain the necessary information julia autodoc is file based. This means that the filename where the documented object is defined has to be stated explicitly.

The usage of the autodoc extension will be explained using the following file as example

.. epigraph::

    .. code-block:: julia

        # examples/example.jl
        """
        Symbolic mathematical computation library.
        """

        abstract type MathObject end

        struct Symbol <: MathObject
            name::AbstractString
        end

        struct Sum <: MathObject
            args::Vector{Symbol}
        end

        """
        Add two symbols.

        Arguments
        ---------
        a
            First argument.
        b
            Second argument.
        """
        function add(a::T, b::T) where {T}
            return Sum(Symbol[a, b])
        end

The whole content of the file can automatically be imported into the documentation using the :obj:`:jl:autofile` directive.

.. epigraph::

    .. code-block:: rst

        .. jl:autofile:: examples/example.jl

.. epigraph::

    .. jl:autofile:: examples/example.jl

To document only specific parts of the file one can use the directives :obj:`jl:automodule`, :obj:`jl:autofunction`, :obj:`jl:autotype` and :obj:`jl:autoabstract`.

.. epigraph::

    .. code-block:: rst

        .. jl:autofunction:: examples/example.jl add

.. epigraph::

    .. jl:autofunction:: examples/example.jl add

.. epigraph::

    .. code-block:: rst

        .. jl:autoabstract:: examples/example.jl MathObject

.. epigraph::

    .. jl:autoabstract:: examples/example.jl MathObject


.. epigraph::

    .. code-block:: rst

        .. jl:autotype:: examples/example.jl Sum

.. epigraph::

    .. jl:autotype:: examples/example.jl Sum