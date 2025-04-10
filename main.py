


import shapefile
from math import hypot, atan2, pi, cos, sin
import numpy as np
from pathlib import Path
import rasterio
import matplotlib.pyplot as plt
from tqdm import tqdm

# constantes
ROUTEGEOMETRIE_SHAPE = "/home/breinbaas/Documents/Waternet/Shapes/Geotechnische Dijkvakken toetsing.shp"
AHN5_PATH = "/home/breinbaas/Documents/AHN/ahn5"
OUTPUT_PATH = "/home/breinbaas/Documents/Waternet/Crosssections"
HOH_AFSTAND = 10
LENGTE_POLDER = 50
LENGTE_BOEZEM = 20
INTERVAL = 0.5

# read shapefile
shape = shapefile.Reader(ROUTEGEOMETRIE_SHAPE)



class Tile:
    def __init__(self, filename, xmin, ymax, xmax, ymin, nodata):
        self.filename = filename
        self.xmin = xmin
        self.xmax = xmax
        self.ymin = ymin
        self.ymax = ymax
        self.nodata = nodata
        self.data = None
        self.r = None
        

    def point_in_data(self, x, y):
        return self.xmin <= x and x < self.xmax and self.ymin < y and y <= self.ymax
    
    def z_at(self, x, y):
        if not self.point_in_data(x,y):
            return None
        
        if self.data is None:
            self.r = rasterio.open(self.filename)
            self.data = self.r.read(1)
        
        row, col = self.r.index(x, y)
        z = self.data[row, col]
        if z == self.nodata:
            return np.nan
        return z
    
class AHNData:
    def __init__(self, tiles=[]):
        self.tiles = tiles

    def z_at(self, x, y):
        for tile in self.tiles:
            if tile.point_in_data(x,y):
                return tile.z_at(x,y)
            
        raise ValueError(f"Punt {x}, {y} valt buiten het gebied dat door de AHN tiles bedekt wordt.")
            

class ReflinePart:
    def __init__(self, traject, start, end, points):
        self.traject = traject
        self.start = start
        self.end = end
        self.points = points
        self.cxya = [] 

        self._post_process()

    @property
    def c_max(self):
        cs = [p[0] for p in self.cxya]
        return max(cs)

    def _post_process(self):
        # voeg metrering toe
        dl = self.start
        self.cxya = [[dl, self.points[0][0], self.points[0][1],0]]

        for i in range(1,len(self.points)):
            x1,y1 = self.points[i-1]
            x2,y2 = self.points[i]
            dx = x2 - x1
            dy = y2 - y1
            dl += hypot(dx, dy)
            a = atan2(dy, dx)
            self.cxya.append([dl,x2,y2,a])
            if i==1:
                self.cxya[0][-1] = a

    def xya_at(self, c):
        for i in range(1, len(self.cxya)):
            c1,x1,y1,a = self.cxya[i-1]
            c2,x2,y2,_ = self.cxya[i]

            if c1 <= c and c <= c2:
                x = x1 + (c-c1)/(c2-c1) * (x2-x1)
                y = y1 + (c-c1)/(c2-c1) * (y2-y1)
                return x,y,a
            
        cs = [p[0] for p in self.cxya]
        raise ValueError(f"Invalid chainage '{c}', should be between {min(cs)} and {max(cs)}")        

def main():
    print("Take a coffee.. this might take a while...")
    
    # we expect a metadata file of the raster files in the AHN5_PATH 
    # if it's not there we will create it
    ahn_data = AHNData()
    p = Path(AHN5_PATH) / "metadata.csv"
    if not p.exists():        
        with open(p, 'w') as csv_out:
            csv_out.write(f"filename,xmin,ymax,xmax,ymin\n")
            tile_files = Path(AHN5_PATH).glob("*.TIF")
            for f in tile_files:
                r = rasterio.open(f)
                topleft = r.transform * (0,0)
                bottomright = r.transform * (r.width, r.height)
                csv_out.write(f"{f},{int(topleft[0])},{int(topleft[1])},{int(bottomright[0])},{int(bottomright[1])},{r.nodata}\n")                
    else:
        for line in open(p, 'r').readlines()[1:]:
            args = [s.strip() for s in line.split(',')]
            ahn_data.tiles.append(Tile(filename=args[0], xmin=int(args[1]), ymax=int(args[2]), xmax=int(args[3]), ymin=int(args[4]), nodata=float(args[5])))

    
    
    parts = []
    for shape_record in shape.iterShapeRecords():
        geometry = shape_record.shape  # This is the geometry (the actual shape)
        record = shape_record.record 
        parts.append(ReflinePart(record.TRAJECT, record.VAN, record.TOT, geometry.points))

    # create shape with all crosssections
    w = shapefile.Writer(Path(OUTPUT_PATH) / "crosssections", shapeType=shapefile.POLYLINE)
    w.field('name', 'C') 

    for part in tqdm(parts):
        # create a path to the dijktraject if it does not yet exist
        p = Path(OUTPUT_PATH) / part.traject
        p.mkdir(parents=True, exist_ok=True)

        cs = np.arange(part.start, part.end, HOH_AFSTAND)
        dl = LENGTE_BOEZEM + LENGTE_POLDER
        steps = int(dl / INTERVAL)
        for c in cs:
            name = f"{part.traject}_{int(c):05d}"
            points = []
            csv_lxyz = open(p / f"{name}.lxyz.csv", 'w')
            csv_lz = open(p / f"{name}.lz.csv", 'w')
            csv_lxyz.write("l,x,y,z\n")
            csv_lz.write("l,z\n")
            try:
                xc,yc,ac = part.xya_at(c)            
                x1 = xc + LENGTE_BOEZEM * cos(ac + pi / 2)
                y1 = yc + LENGTE_BOEZEM * sin(ac + pi / 2)
                x2 = xc + LENGTE_POLDER * cos(ac - pi / 2)
                y2 = yc + LENGTE_POLDER * sin(ac - pi / 2)

                for i in range(steps + 1):  
                    x = x1 + (x2 - x1) * (i / steps)
                    y = y1 + (y2 - y1) * (i / steps)
                    l = -LENGTE_BOEZEM + INTERVAL * i
                    z = ahn_data.z_at(x,y)
                    points.append((l,z))
                    if not np.isnan(z):
                        csv_lxyz.write(f"{l:.1f},{x:.2f},{y:.2f},{z:.3f}\n")
                        csv_lz.write(f"{l:.1f},{z:.3f}\n")
                
                w.line([[(x1,y1),(x2,y2)]])
                w.record(name)

                _, ax = plt.subplots(figsize=(8, 6))
                ax.plot([p[0] for p in points], [p[1] for p in points])
                ax.set_xlim(-LENGTE_BOEZEM, LENGTE_POLDER)
                ax.set_title(f"Dwarsprofiel {name}")
                ax.set_xlabel("afstand tov referentielijn [m]")
                ax.set_ylabel("hoogte tov NAP [m]")
                ax.grid(which='both')
                plt.savefig(p / f"{name}.png")
                plt.close()                
            except Exception as e:
                print(e)
            finally:
                csv_lxyz.close()
                csv_lz.close()   
    w.close() 

if __name__=="__main__":
    main()