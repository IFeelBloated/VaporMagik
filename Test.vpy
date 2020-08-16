from vapoursynth import *
from VaporMagik import *

RegisterPlugin(core.std)

@AttachToVideo
def Adjust(clip, intensity):
    return clip.Expr(f"x {intensity} +")

@AttachToList
def Grayscale(channels):
    return channels.Expr("x 0.25 * y 0.5 * z 0.25 * + +")

clip = core.std.BlankClip(format = RGBS)
clip = [clip.R, clip.G, clip.B].Grayscale().Transpose().Adjust(0.8)
clip = [clip, [clip, clip.Adjust(-0.4)].Expr("x y + 2 /")].StackHorizontal()
clip.set_output()