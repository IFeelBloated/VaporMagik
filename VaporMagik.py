from vapoursynth import VideoNode, core, GRAY, RGB, YUV
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
        SetTypeAttribute(self.TargetType, Name, lambda *args, **kw: Attribute(*args, **kw))

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
        
def RegisterPlugin(Plugin):
    FilterList = Plugin.get_functions().keys()
    for x in FilterList:
        RegisterNativeFilter(getattr(Plugin, x))

@property
def R(self):
    if self.format.color_family != RGB:
        raise AttributeError()
    return core.std.ShufflePlanes(self, 0, GRAY)

@property
def G(self):
    if self.format.color_family != RGB:
        raise AttributeError()
    return core.std.ShufflePlanes(self, 1, GRAY)

@property
def B(self):
    if self.format.color_family != RGB:
        raise AttributeError()
    return core.std.ShufflePlanes(self, 2, GRAY)

@property
def Y(self):
    if self.format.color_family != YUV:
        raise AttributeError()
    return core.std.ShufflePlanes(self, 0, GRAY)

@property
def Cb(self):
    if self.format.color_family != YUV:
        raise AttributeError()
    return core.std.ShufflePlanes(self, 1, GRAY)

@property
def Cr(self):
    if self.format.color_family != YUV:
        raise AttributeError()
    return core.std.ShufflePlanes(self, 2, GRAY)

SetTypeAttribute(VideoNode, 'R', R)
SetTypeAttribute(VideoNode, 'G', G)
SetTypeAttribute(VideoNode, 'B', B)
SetTypeAttribute(VideoNode, 'Y', Y)
SetTypeAttribute(VideoNode, 'Cb', Cb)
SetTypeAttribute(VideoNode, 'Cr', Cr)