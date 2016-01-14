from mat import Mat
import math

## Task 1
def identity(labels = {'x','y','u'}):
    '''
    In case you have never seen this notation for a parameter before,
    the way it works is that identity() now defaults to having labels 
    equal to {'x','y','u'}.  So you should write your procedure as if 
    it were defined 'def identity(labels):'.  However, if you want the labels of 
    your identity matrix to be {'x','y','u'}, you can just call 
    identity().  Additionally, if you want {'r','g','b'}, or another set, to be the
    labels of your matrix, you can call identity({'r','g','b'}).  
    '''
    return Mat((labels, labels), {(k,k):1 for k in labels})


## Task 2
def translation(x,y):
    '''
    Input:  An x and y value by which to translate an image.
    Output:  Corresponding 3x3 translation matrix.
    '''
    trans = identity({"x","y","u"})
    trans["x","u"] = x
    trans["y","u"] = y
    return trans

## Task 3
def scale(a, b):
    '''
    Input:  Scaling parameters for the x and y direction.
    Output:  Corresponding 3x3 scaling matrix.
    '''
    scale = identity({"x","y","u"})
    scale["x","x"] = a
    scale["y","y"] = b
    return scale

def abs(x):
    result = x
    if (result < 0):
        result = -result
    return result

def close_enough_to_zero(x):
    result = x;
    if (abs(result) < 1e-10):
        result = 0
    return result;

## Task 4
def rotation(angle):
    '''
    Input:  An angle in radians to rotate an image.
    Output:  Corresponding 3x3 rotation matrix.
    Note that the math module is imported.
    '''
    mat = identity({"x","y","u"})
    ##angle = angle * math.pi / 180
    mat["x","x"] = math.cos(angle)
    mat["y","x"] = math.sin(angle)
    mat["x","y"] = -math.sin(angle)
    mat["y","y"] = math.cos(angle)
    return mat

##help(math)
##print(rotation(math.pi/4))

## Task 5
def rotate_about(x,y,angle):
    '''
    Input:  An x and y coordinate to rotate about, and an angle
    in radians to rotate about.
    Output:  Corresponding 3x3 rotation matrix.
    It might be helpful to use procedures you already wrote.
    '''
    return translation(x,y) * rotation(angle) * translation(-x,-y)

## Task 6
def reflect_y():
    '''
    Input:  None.
    Output:  3x3 Y-reflection matrix.
    '''
    mat = identity({"x","y","u"})
    mat["x","x"] = -1
    return mat

## Task 7
def reflect_x():
    '''
    Inpute:  None.
    Output:  3x3 X-reflection matrix.
    '''
    mat = identity({"x","y","u"})
    mat["y","y"] = -1
    return mat
    
## Task 8    
def scale_color(scale_r,scale_g,scale_b):
    '''
    Input:  3 scaling parameters for the colors of the image.
    Output:  Corresponding 3x3 color scaling matrix.
    '''
    mat = identity({"r","g","b"})
    mat["r","r"] = scale_r
    mat["g","g"] = scale_g
    mat["b","b"] = scale_b
    return mat

## Task 9
def grayscale():
    '''
    Input: None
    Output: 3x3 greyscale matrix.
    '''
    mat = identity({"r","g","b"})
    mat["r","r"] = mat["g","r"] = mat["b","r"] = 77/256
    mat["r","g"] = mat["g","g"] = mat["b","g"] = 151/256
    mat["r","b"] = mat["g","b"] = mat["b","b"] = 28/256
    return mat


## Task 10
def reflect_about(p1,p2):
    '''
    Input: 2 points that define a line to reflect about.
    Output:  Corresponding 3x3 reflect about matrix.
    '''
    angle = -math.atan((p2.y-p1.y)/(p2.x-p1.x))
    rotate_mat = rotation(angle)
    unrotate_mat = rotation(-angle)
    text_point = rotate_mat * Vec({"x","y","u"}, {"x":p1.x, "y":p1.y, "u":1})
    translate_mat = translate(0, -text_point["y"])
    untranslate_mat = translate(0, text_point["y"])
    return unrotate_mat * untranslate_mat * reflect_y() * translate_mat * rotate_mat

