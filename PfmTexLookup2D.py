from OpenGL.GL import *
from OpenGL.GL import shaders
import numpy

vertexShader = """
void main() {
  gl_TexCoord[0] = gl_MultiTexCoord0;
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
}
"""

fragmentShader = """
uniform sampler2D texture0;
uniform sampler2D texture1;

void main() {
  // Look up the UV coordinate in the pfm texture
  vec4 uv = texture2D(texture0, gl_TexCoord[0].xy);

  // And use that UV coordinate to look up the media color
  vec4 col = texture2D(texture1, uv.xy);
  
  gl_FragColor = col;
}
"""

class PfmTexLookup2D:
    """ This class creates a floating-point texture out of the data in
    a pfm file, and performs a two-step texture lookup in the fragment
    shader to compute the warping.  Also see PfmMesh2D for a different
    approach. """

    def __init__(self, pfm, tex):
        self.pfm = pfm
        self.tex = tex
        self.pfmtexobj = None

    def initGL(self):
        # Load the pfm data as a floating-point texture.
        self.pfmtexobj = glGenTextures(1)
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        glBindTexture(GL_TEXTURE_2D, self.pfmtexobj)

        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)

        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB32F, self.pfm.xSize, self.pfm.ySize, 0, GL_RGB, GL_FLOAT, self.pfm.data)

        # Create a VBO with two triangles to make a unit quad.
        verts = [
            [0, 1], [1, 0], [1, 1], 
            [0, 1], [1, 0], [0, 0],
            ]
        verts = numpy.array(verts, dtype = 'float32')
        self.vertdata = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertdata)
        glBufferData(GL_ARRAY_BUFFER, verts, GL_STATIC_DRAW)

        # Compile the shaders.
        vs = shaders.compileShader(vertexShader, GL_VERTEX_SHADER)
        fs = shaders.compileShader(fragmentShader, GL_FRAGMENT_SHADER)
        self.shader = shaders.compileProgram(vs, fs)

        self.texture0 = glGetUniformLocation(self.shader, 'texture0')
        self.texture1 = glGetUniformLocation(self.shader, 'texture1')

    def draw(self):
        glPushAttrib(GL_ENABLE_BIT)
        glPushClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS)

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.pfmtexobj)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.tex.texobj)

        shaders.glUseProgram(self.shader)
        glUniform1i(self.texture0, 0)
        glUniform1i(self.texture1, 1)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_TEXTURE_COORD_ARRAY)

        glBindBuffer(GL_ARRAY_BUFFER, self.vertdata)
        glVertexPointer(2, GL_FLOAT, 0, None)
        glTexCoordPointer(2, GL_FLOAT, 0, None)
        
        glDrawArrays(GL_TRIANGLES, 0, 6)

        glPopClientAttrib(GL_CLIENT_ALL_ATTRIB_BITS)
        glPopAttrib(GL_ENABLE_BIT)
        
