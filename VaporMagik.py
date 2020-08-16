from vapoursynth import *
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

def AttachToVideo(Filter):
    Injector.TargetType = VideoNode
    Filter.VaporMagikTag = 'VideoNode -> ?'
    Injector[Filter.__name__] = Filter
    del Injector.TargetType
    return Filter
    
def AttachToList(Filter):
    Injector.TargetType = list
    Filter.VaporMagikTag = '[] -> ?'
    Injector[Filter.__name__] = Filter
    del Injector.TargetType
    return Filter

def RegisterNativeFilter(Filter):
    FilterName = Filter.name
    ArgumentList = Filter.signature.replace(' ', '').split(';')
    ArgumentList = [x for x in ArgumentList if x != '']
    if len(ArgumentList) == 0:
        return
    SelfArgument = ArgumentList[0]
    SelfArgumentType = SelfArgument.split(':')[1]
    if '[]' in SelfArgumentType:
        Injector.TargetType = list
        Injector[FilterName] = Filter
    if 'clip' in SelfArgumentType:
        Injector.TargetType = VideoNode
        Injector[FilterName] = Filter
    if hasattr(Injector, 'TargetType'):
        del Injector.TargetType
        
def RegisterPlugin(Instance):
    FilterList = Instance.get_functions().keys()
    for x in FilterList:
        RegisterNativeFilter(getattr(Instance, x))