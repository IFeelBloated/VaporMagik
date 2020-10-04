from vapoursynth import VideoNode, core, GRAY, RGB, YUV
import ctypes
import builtins
import inspect
import os

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

def CallableToFunction(CallableObject):
    return lambda *args, **kw: CallableObject(*args, **kw)
    
def Inject(Filter):
    ParameterDictionary = inspect.signature(Filter).parameters
    ParameterNames = [Name for Name in ParameterDictionary]
    Parameters = [ParameterDictionary[Name] for Name in ParameterNames]
    if len(Parameters) == 0:
        return
    SelfParameter = Parameters[0]
    if SelfParameter.annotation != inspect._empty:
        SetTypeAttribute(SelfParameter.annotation, Filter.__name__, CallableToFunction(Filter))
    else:
        SetTypeAttribute(VideoNode, Filter.__name__, CallableToFunction(Filter))
        SetTypeAttribute(list, Filter.__name__, CallableToFunction(Filter))
        SetTypeAttribute(tuple, Filter.__name__, CallableToFunction(Filter))
    return Filter

def RegisterNativeFilter(Filter, NamingPolicy = None):
    FilterName = Filter.name if NamingPolicy is None else NamingPolicy(Filter.plugin.namespace, Filter.name)
    setattr(builtins, FilterName, Filter)
    ArgumentList = Filter.signature.replace(' ', '').split(';')
    ArgumentList = [x for x in ArgumentList if x != '']
    if len(ArgumentList) == 0:
        return
    SelfArgument = ArgumentList[0].split(':')
    SelfArgumentType = SelfArgument[1]
    if '[]' in SelfArgumentType:
        SetTypeAttribute(list, FilterName, CallableToFunction(Filter))
        SetTypeAttribute(tuple, FilterName, CallableToFunction(Filter))
    if 'clip' in SelfArgumentType:
        SetTypeAttribute(VideoNode, FilterName, CallableToFunction(Filter))

def RegisterPlugin(Plugin, NamingPolicy = None):
    FilterList = Plugin.get_functions().keys()
    for x in FilterList:
        RegisterNativeFilter(getattr(Plugin, x), NamingPolicy)

def TraceFilePathOfTheRunningScript():
    Frame = inspect.currentframe()
    Callers = inspect.getouterframes(Frame)
    del Frame
    for x in Callers:
        if x.filename.endswith('.vpy'):
            return os.path.abspath(x.filename)

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
setattr(builtins, '__script__', TraceFilePathOfTheRunningScript())