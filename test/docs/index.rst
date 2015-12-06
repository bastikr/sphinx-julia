
Welcome to autodoc-julia's documentation!
=========================================


Pythondomain
------------

.. py:module:: A

.. py:method:: B

    Module B description.

.. py:class:: t

    Type t.

    asdsdfdsf



Juliadomain
-----------

.. jl:module:: A

    Module A description.

    .. jl:module:: B

        Module B description.

        .. jl:abstract:: t

            Type t.

            asdsdfdsf

        .. jl:function:: testfunc{S, T}(a::Int, b=1; c="z")


Autofile example
----------------

.. jl:autofile:: example.jl


Autofile example2
-----------------

.. jl:autofile:: example2.jl


Autoabstract
------------

.. jl:autoabstract:: example.jl t


Automodule
----------

.. jl:automodule:: example.jl B


Autofunction
------------

.. jl:autofunction:: DormandPrince45.jl interpolate


Autofile DormandPrince
----------------------

.. jl:autofile:: ../src/DormandPrince45.jl


:jl:type:`DormandPrince45.CType`

:jl:abstract:`AType`

:jl:func:`testfunc`

:jl:func:`DormandPrince45.ode`

:jl:mod:`B`
