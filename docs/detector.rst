detector Package
================

:mod:`detector` package
-----------------------

.. automodule:: detector
    
:mod:`interface` module
-----------------------

.. automodule:: detector.interface

    :class:`IDetector` interface
    --------------------------------------
    .. autoclass:: detector.interface.IDetector
        :members:
        :show-inheritance:

    :class:`IControl` interface
    ------------------------------------
    .. autoclass:: detector.interface.IControl
        :members:
        :show-inheritance:

    :class:`IData` interface
    ------------------------------------
    .. autoclass:: detector.interface.IData
         :members:
         :show-inheritance:

    :class:`IParameter` interface
    ------------------------------------
    .. autoclass:: detector.interface.IParameter
         :members:
         :show-inheritance:

    :class:`IABCMeta` mix-in
    ---------------------------------
    .. autoclass:: detector.interface.IABCMeta
        :members: _iface_requirements, __subclasshook__
        :show-inheritance:

    Example use of interfaces
    -------------------------
    .. literalinclude:: interface_examples.py
    
:mod:`parameter` module
-----------------------

.. automodule:: detector.parameter

    :class:`Observable`
    -------------------
    .. autoclass:: detector.parameter.Observable
        :members: 
        :private-members:
        :show-inheritance:
        
    
      