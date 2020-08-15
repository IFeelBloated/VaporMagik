from vapoursynth import *
from VaporMagik import Injector

def Pad(clip, left, right, top, bottom):
    w = clip.width
    h = clip.height
    return clip.Resample(w+left+right, h+top+bottom, -left, -top, w+left+right, h+top+bottom, kernel="point")

Injector.TargetType = VideoNode
Injector['Transpose'] = core.std.Transpose
Injector['Resample'] = core.fmtc.resample
Injector['Pad'] = Pad
Injector.TargetType = list
Injector['StackHorizontal'] = core.std.StackHorizontal

clip = core.std.BlankClip()
clip = clip.Transpose().Pad(1, 2, 3, 4)
clip = [clip, clip].StackHorizontal()
clip.set_output()