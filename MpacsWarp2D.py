from MpacsWarp import MpacsWarp
from TextureImage import TextureImage
from OpenGL.GL import *
from PIL import Image
import sys

class MpacsWarp2D(MpacsWarp):
    """ The base class for performing warping in the "2d" profile
    specified in the mpcdi file.  This warps media according to a 2-d
    pfm file and applies a blending map. """

    def __init__(self, mpcdi, region):
        MpacsWarp.__init__(self, mpcdi, region)

        # This class only supports the "2d" profile.
        assert self.mpcdi.profile == '2d'

        self.mediaFilename = None
        self.media = None

        # This is the gamma value of the source media image.
        self.mediaGamma = self.blendGamma

        self.pfm = self.mpcdi.extractPfmFile(self.region.geometryWarpFile.path)

    def setMediaFilename(self, mediaFilename):
        self.mediaFilename = mediaFilename
        self.media = TextureImage(self.mediaFilename)

    def initGL(self):
        MpacsWarp.initGL(self)
        self.media.initGL()
