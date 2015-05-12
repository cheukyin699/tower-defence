import jsonutils
import pygame

class TileSet:
    def __init__(self, data):
        self.fgid = data['firstgid']
        self.imgfn = data['image']              # Image filename
        self.imgheight = data['imageheight']
        self.imgwidth = data['imagewidth']
        self.name = data['name']
        self.tileheight = data['tileheight']
        self.tilewidth = data['tilewidth']
        
        self.image = pygame.image.load(self.imgfn.replace('..', 'res'))
        
    def getMaxTileId(self):
        return self.fgid+(self.imgheight/self.tileheight)*(self.imgwidth/self.tilewidth)

class Layer:
    def __init__(self, data, (tw, th)):
        self.data = data['data']
        self.name = data['name']
        self.width = data['width']              # The number of tiles
        self.height = data['height']            # The number of tiles
        
        self.tilewidth = tw
        self.tileheight = th

    def initSurface(self, tileset):
        # Make the surface
        self.image = pygame.Surface((self.width*self.tilewidth, self.height*self.tileheight))
        # Now, blit EVERYTHING to the surface
        for i in xrange(len(self.data)):
            # REM: 'i' is the index and 'data[i]' is the id
            xc, yc = ((i%self.width), (i//self.width))
            self.image.blit(tileset[self.data[i]], (xc*self.tilewidth, yc*self.tileheight))

class TMXJsonMap:
    def __init__(self, filename):
        self.fn = filename

        # The whole map dictionary
        f = open(self.fn)
        self.map = jsonutils.load(f)
        f.close()

        # The tile's dictionary
        self.tiles = {}
        # Init tilesets
        for ts in self.map['tilesets']:
            tileset = TileSet(ts)
            for x in xrange(tileset.getMaxTileId()-tileset.fgid):
                # First, convert 1d coordinates into 2d
                xc, yc = (x%(tileset.imgwidth/tileset.tilewidth), x//(tileset.imgwidth/tileset.tilewidth))
                # Then, get the rectangle
                rect = pygame.rect.Rect(xc*tileset.tilewidth, yc*tileset.tileheight, tileset.tilewidth, tileset.tileheight)
                # Insert into dictionary
                self.tiles[x+tileset.fgid] = tileset.image.subsurface(rect)
        
        # The layers dictionary
        self.layers = {}
        # Init layers
        for layer in self.map['layers']:
            self.layers[layer['name']] = Layer(layer, [self.map['tilewidth'], self.map['tileheight']])
            self.layers[layer['name']].initSurface(self.tiles)