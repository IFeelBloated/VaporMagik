from vapoursynth import *
from VaporMagik import Injector

def Adjust(clip, intensity):
    return clip.Expr(f"x {intensity} +")

Injector.TargetType = VideoNode
Injector['Transpose'] = core.std.Transpose
Injector['Expr'] = core.std.Expr
Injector['Adjust'] = Adjust
Injector.TargetType = list
Injector['StackHorizontal'] = core.std.StackHorizontal
Injector['Expr'] = core.std.Expr

clip = core.std.BlankClip(format = GRAYS)
clip = clip.Transpose().Adjust(0.8)
clip = [clip, [clip, clip.Adjust(-0.4)].Expr("x y + 2 /")].StackHorizontal()
clip.set_output()