from vapoursynth import *
from VaporMagik import *

RegisterPlugin(core.std)

@Inject
def Adjust(clip, intensity):
    return clip.Expr(f"x {intensity} +")

@Inject
def Grayscale(channels):
    return channels.Expr("x 0.25 * y 0.5 * z 0.25 * + +")

clip = BlankClip(format = RGBS)
clip = [clip.R, clip.G, clip.B].Grayscale().Transpose().Adjust(0.8)
clip = [clip, [clip, clip.Adjust(-0.4)].Expr("x y + 2 /")].StackHorizontal()
clip.set_output()