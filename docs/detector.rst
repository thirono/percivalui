detector Package
================

:mod:`percival.detector` package
-----------------------

.. automodule:: percival.detector
    
:mod:`percival.detector.interface` module
-----------------------

.. automodule:: percival.detector.interface

    :class:`IDetector` interface
    --------------------------------------
    .. autoclass:: percival.detector.interface.IDetector
        :members:
        :show-inheritance:

    :class:`IControl` interface
    ------------------------------------
    .. autoclass:: percival.detector.interface.IControl
        :members:
        :show-inheritance:

    :class:`IData` interface
    ------------------------------------
    .. autoclass:: percvial.detector.interface.IData
         :members:
         :show-inheritance:

    :class:`IParameter` interface
    ------------------------------------
    .. autoclass:: percival.detector.interface.IParameter
         :members:
         :show-inheritance:

    :class:`IABCMeta` mix-in
    ---------------------------------
    .. autoclass:: percival.detector.interface.IABCMeta
        :members: _iface_requirements, __subclasshook__
        :show-inheritance:

    Example use of interfaces
    -------------------------
    .. literalinclude:: interface_examples.py
    
:mod:`percival.detector.parameter` module
-----------------------

.. automodule:: percival.detector.parameter

    :class:`Observable`
    -------------------
    .. autoclass:: percival.detector.parameter.Observable
        :members: 
        :private-members:
        :show-inheritance:
        
    
      
