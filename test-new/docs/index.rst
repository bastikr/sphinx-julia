
Welcome to autodoc-julia's documentation!
=========================================


.. py:class:: Test

    And a little bit of text

    .. py:method:: meth(a)

        more text :math:`a^2 + b^2 = c^2`


.. py:function:: fpython(a, b, c)

    Python function decstring

.. jl:autotype:: ../src/DormandPrince45.jl CType

.. jl:autoabstract:: ../src/DormandPrince45.jl AType

.. jl:autofunction:: ../src/DormandPrince45.jl ode


.. jl:autofile:: ../src/DormandPrince45.jl


.. jl:module:: MyModule

    Module docstring

    .. jl:function:: f{T}(x::T,y)

        Test faslfjsaldf :math:`a^2 + b^2 = c^2`

    .. jl:type:: MyType

        My type docstring

.. jl:abstract:: MyAbstractType

    MyAbstract type docstring
