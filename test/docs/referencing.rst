Referencing
===========

.. jl:function:: RefTest_f()

.. jl:module:: RefTest_A

    .. jl:function:: RefTest_f()

    .. jl:module:: RefTest_B

        .. jl:function:: RefTest_f()


        * :jl:func:`RefTest_f`          # f1
        * :jl:func:`RefTest_A.RefTest_f`       # f2
        * :jl:func:`RefTest_A.RefTest_B.RefTest_f`     # f3
        * :jl:func:`.RefTest_f`         # f3
        * :jl:func:`..RefTest_f`       # f2
        * :jl:func:`...RefTest_f`      # f1
        * :jl:func:`..RefTest_B.RefTest_f`     # f3

    * :jl:func:`RefTest_f`          # f1
    * :jl:func:`RefTest_A.RefTest_f`       # f2
    * :jl:func:`RefTest_A.RefTest_B.RefTest_f`     # f3
    * :jl:func:`RefTest_B.RefTest_f`       # f3
    * :jl:func:`.RefTest_B.RefTest_f`      # f3
    * :jl:func:`.RefTest_f`         # f2
    * :jl:func:`..RefTest_f`       # f1
    * :jl:func:`..RefTest_A.RefTest_f`     # f2

* :jl:func:`RefTest_f`
* :jl:func:`RefTest_A.RefTest_f`
* :jl:func:`RefTest_A.RefTest_B.RefTest_f`