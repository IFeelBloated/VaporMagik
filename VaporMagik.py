import ctypes

class PyObject(ctypes.Structure):
    pass

PyObject._fields_ = [
    ('ob_refcnt', ctypes.c_ssize_t),
    ('ob_type', ctypes.POINTER(PyObject)),
]

class NativeMappingProxy(PyObject):
    _fields_ = [('UnderlyingDictionary', ctypes.POINTER(PyObject))]

def Dereference(Pointer):
    ObjectHolder = []
    ctypes.pythonapi.PyList_Append(ctypes.py_object(ObjectHolder), Pointer)
    return ObjectHolder[0]
    
def ExposeAttributeDictionary(Type):
    AttributeMaps = Type.__dict__
    TransparentAttributeMaps = NativeMappingProxy.from_address(id(AttributeMaps))
    return Dereference(TransparentAttributeMaps.UnderlyingDictionary)

def SetTypeAttribute(Type, Name, Attribute):
    AttributeDictionary = ExposeAttributeDictionary(Type)
    AttributeDictionary[Name] = Attribute
    ctypes.pythonapi.PyType_Modified(ctypes.py_object(Type))
    
class InjectorType:
    def __setitem__(self, Name, Attribute):
        SetTypeAttribute(self.TargetType, Name, lambda this, *args, **kw: Attribute(this, *args, **kw))

Injector = InjectorType()
