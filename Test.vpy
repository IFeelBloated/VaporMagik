from vapoursynth import *
from VaporMagik import *

RegisterPlugin(core.std)

@AttachToVideo
def Adjust(clip, intensity):
    return clip.Expr(f"x {intensity} +")

@AttachToList
def Average(clips):
    return clips.Expr("x y + 2 /")

clip = core.std.BlankClip(format = GRAYS)
clip = clip.Transpose().Adjust(0.8)
clip = [clip, [clip, clip.Adjust(-0.4)].Average()].StackHorizontal()
clip.set_output()