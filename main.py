"""
Random colorful image generator.

Usage:
  main.py [options]

Options:
  --runs=<count>       Generate this number of random images. [default: 3]
  --output=<folder>    Target folder for output images. [default: output]
  --width=<width>      Width of image output [default: 1920]
  --height=<height>    Height of image output [default: 1080]
  --verbose

  -h --help        Show this screen.
  -v --version     Show version.
"""

SPACES="     "

import os, random, math
from PIL import Image, ImageDraw, ImageFont
from numpy.linalg import norm
from docopt import docopt
import numpy, time

def get_distance_to_line(line_point1,line_point2,point):
    p1=numpy.array(line_point1)
    p2=numpy.array(line_point2)
    p3=numpy.array(point)
    return norm(numpy.cross(p2-p1, p1-p3))/norm(p2-p1)

def get_random_point(width,height):
    return random.randint(0,width),random.randint(0,height)

def get_random_color():
    "random color, slight bias for brighter, non-grey colors"
    c=[255,255,255]
    for i in range(3):
        c[random.randint(0,2)]=random.randint(0,255)
    return tuple(c)

def clamp(value,minimum,maximum):
    return min(max(value,minimum),maximum)

def get_intensity_function(width,height):    
    p1=get_random_point(width,height)
    p2=get_random_point(width,height)
    if p1[0]>p2[0]:
        p1,p2=p2,p1 #p1 is always left of p2
    
    values=[random.randint(1,8) for i in range(5)]
    
    w=random.randint(1,width)
    w=random.randint(w,width)
    w=random.randint(w,width)
    distance_denominator=w
    below_line=random.choice((True,False))
    
    # f(x) = ax+b
    a=abs((p2[1]-p1[1])/(p2[0]-p1[0]))
    if p1[1]>p2[1]:
        a*=-1
    b=p1[1]-a*p1[0]
    
    def oval_function(x,y):
        dx=abs(x-p1[0])/values[0]
        dy=abs(y-p1[1])/values[1]
        adjust=(values[0]+values[1])/2
        distance=adjust*(dx**2+dy**2)**0.5
        return 1-clamp(distance/distance_denominator,0,1)
    
    def radial_function(x,y):
        dx=abs(x-p1[0])
        dy=abs(y-p1[1])
        distance=(dx**2+dy**2)**0.5
        return 1-clamp(distance/distance_denominator,0,1)
    
    def linear_function(x,y):
        is_below_line=y<a*x+b
        if is_below_line:
            return 1
        
        point=(x,y)
        
        distance=get_distance_to_line(p1,p2,point)
        return 1-clamp(distance/distance_denominator,0,1)
    
    functions=(oval_function,radial_function,linear_function)
    return random.choice(functions)

def blend_colors(x,y,color1,color2,alpha_function):
    a=alpha_function(x,y)
    a_inverse=1-a
    return (int(color1[0]*a+color2[0]*a_inverse),
            int(color1[1]*a+color2[1]*a_inverse),
            int(color1[2]*a+color2[2]*a_inverse))

def generate_image(width,height,path,verbose=False):
    print("\nGenerating '%s'."%path)
    image=Image.new("RGB",(width,height),(0,0,0))
    pixel_map=image.load()
    
    functions=[get_intensity_function(width,height) for i in range(3)]    
    colors=[get_random_color() for i in range(4)]
    
    start_time=time.time()
    last_update_time=start_time
    update_interval=5
    
    if verbose:
        print(SPACES+"colors = ",end="")
        for c in colors:
            print(str(c),end=SPACES)
        print("")
    
    for x in range(width):
        
        if verbose and time.time()-last_update_time>update_interval:
            last_update_time=time.time()
            print(SPACES+"%s%% done."%round(100*x/width,1))
            
        for y in range(height):
            blend1=blend_colors(x,y,colors[0],colors[1],functions[0])
            blend2=blend_colors(x,y,colors[2],colors[3],functions[1])
            new_color=blend_colors(x,y,blend1,blend2,functions[2])            
            pixel_map[x,y]=new_color
    
    if verbose:
        print(SPACES+"Saving '%s'"%path)
    image.save(path)
    image.close()

def main(args):
    width=int(args["--width"])
    height=int(args["--height"])
    output=args["--output"]
    run_count=int(args["--runs"])
    
    zero_count=math.ceil(math.log(run_count,10))
    
    if not os.path.exists(output):
        os.makedirs(output)
    
    for i in range(run_count):
        path=output+os.sep+"image"+str(i).zfill(zero_count)+".png"
        generate_image(width,height,path,verbose=args["--verbose"])

if __name__ == "__main__":
    args = docopt(__doc__, version="1.0")
    main(args)