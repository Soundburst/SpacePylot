import random, math
"""This file contains the vector class. A vector can be defined as
a number with a direction, but in this case it is easier to define
vectors just by their x and y components. Values like position, velocity,
and acceleration should all be stored as vectors for simplicity's sake.
Vectors can be created like so:
myvar = Vector(10,-5)
This would create a vector called myvar, which would have an x value of 10
and a y value of -5.
Each vector function has a short comment describing its use."""

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.uBoundX = None
        self.uBoundY = None
        self.lBoundX = None
        self.lBoundY = None

    def __str__(self):
        #by defining this, printing a vector will print this instead
        #of something like "<vector>0x29384000"
        return "X:" + str(self.x)+ ", Y:" + str(self.y) +\
                "\nUpper X Bound: " + str(self.uBoundX) +\
                ", Upper Y Bound: " + str(self.uBoundY) +\
                "\nLower X Bound: " + str(self.lBoundX) +\
                ", Lower Y Bound: " + str(self.lBoundY)

    def clear(self):
        #sets ALL attributes to 0 or None
        self.x = 0
        self.y = 0
        self.clearBounds()

    def bound(self, x=None, y=None):
        #Caps maximum/minimum values vector is allowed to have
        #uses single number, makes it maximum, then negates it
        #and makes that the minimum
        if x < 0 or y < 0:
            raise ValueError("Number below zero.")
        if x != None:
            self.uBoundX = x
            self.lBoundX = -x
        if y != None:
            self.uBoundY = y
            self.lBoundY = -y

    #both bounded functions return -1 if the value is less than the lower bound,
    #return 1 if it is greater than the upper bound, and 0 if it is within
    #both bounds

    def boundedX(self,x):
        if self.lBoundX != None and x <= self.lBoundX:
            return -1
        elif self.uBoundX != None and x >= self.uBoundX:
            return 1
        else:
            return 0

    def boundedY(self,y):
        if self.lBoundY != None and y <= self.lBoundY:
            return -1
        elif self.uBoundY != None and y >= self.uBoundY:
            return 1
        else:
            return 0

    #specifically sets lower bounds only

    def lBound(self, x=None, y=None):
        #sets lower bounds for vector
        if x != None:
            if self.uBoundX != None and x > self.uBoundX:
                raise ValueError("Lower bound is greater than upper bound.")
            self.lBoundX = x
        if y != None:
            if self.uBoundY != None and y > self.uBoundY:
                raise ValueError("Lower bound is greater than upper bound.")
            self.lBoundY = y

    #sets only upper bounds

    def uBound(self, x=None, y=None):
        #sets upper bounds for vector
        if x != None:
            if self.lBoundX != None and x < self.lBoundX:
                raise ValueError("Upper bound is smaller than lower bound.")
            self.uBoundX = x
        if y != None:
            if self.lBoundY != None and y < self.lBoundY:
                raise ValueError("Upper bound is smaller than lower bound.")
            self.uBoundY = y

    def clearBounds(self):
        #sets all caps to None
        self.uBoundX = self.lBoundX = self.uBoundY = self.lBoundY = None

    def add(self, x, y):
        #this function adds x and y to the vector's current x and y values
        #runs test x and y values through the user-set caps
        #if any value is < negCap or > posCap then the value
        #is just set to its respective cap
        xBound = self.boundedX(self.x+x)
        if xBound > 0:
            self.x = self.uBoundX
        elif xBound < 0:
            self.x = self.lBoundX
        else:
            self.x += x
        
        yBound = self.boundedY(self.y+y)
        if yBound > 0:
            self.y = self.uBoundY
        elif yBound < 0:
            self.y = self.lBoundY
        else:
            self.y += y

    def addV(self, vect):
        #adds another vectors x and y values to this one's
        x, y = vect.get()
        #runs test x and y values through the user-set caps
        #if any value is < negCap or > posCap then the value
        #is just set to its respective cap
        xBound = self.boundedX(self.x+x)
        if xBound > 0:
            self.x = self.uBoundX
        elif xBound < 0:
            self.x = self.lBoundX
        else:
            self.x += x
        
        yBound = self.boundedY(self.y+y)
        if yBound > 0:
            self.y = self.uBoundY
        elif yBound < 0:
            self.y = self.lBoundY
        else:
            self.y += y

    def set(self, x, y):
        #sets vector's x and y values to x and y
        #this function is limited by the caps
        xBound = self.boundedX(x)
        if xBound > 0:
            self.x = self.uBoundX
        elif xBound < 0:
            self.x = self.lBoundX
        else:
            self.x = x
        
        yBound = self.boundedY(y)
        if yBound > 0:
            self.y = self.uBoundY
        elif yBound < 0:
            self.y = self.lBoundY
        else:
            self.y = y

    def setV(self, v):
        #sets this vector's values to another vector's values
        #affected by current caps
        x, y = v.get()
        xBound = self.boundedX(x)
        if xBound > 0:
            self.x = self.uBoundX
        elif xBound < 0:
            self.x = self.lBoundX
        else:
            self.x = x
        
        yBound = self.boundedY(y)
        if yBound > 0:
            self.y = self.uBoundY
        elif yBound < 0:
            self.y = self.lBoundY
        else:
            self.y = y

    def get(self):
        return (self.x, self.y)

    def getV(self):
        return Vector(self.x, self.y)

    def integize(self):
        #turns vector's float values to integers
        self.x = int(self.x)
        self.y = int(self.y)

    def round(self, ndigits):
        #rounds vector values to ndigits amount of digits
        self.x = round(self.x,ndigits)
        self.y = round(self.y,ndigits)

    def normalize(self):
        #turns vector into unit vectors, for example a vector pointing
        #straight up would have values x=0,y=1
        length = math.sqrt(self.x*self.x + self.y*self.y)
        if length != 0:
            self.x /= length
            self.y /= length

    def dot(self, c):
        #dot products the vector, essentially multiplies each value by c
        self.x *= c
        self.y *= c

    def theta(self, radians=True):
        #gets the angle of the vector in terms of the unit circle
        #returns in radians unless theta() is called with radians=False
        if self.x != 0 and self.y != 0:
            theta = math.atan(self.y/self.x)
        else:
            theta = 0
        if self.x < 0 and self.y > 0:
            theta += math.pi
        elif self.x < 0 and self.y < 0:
            theta += math.pi
        elif self.x > 0 and self.y < 0:
            theta += 2*math.pi
        elif self.x > 0 and self.y > 0:
            pass
        elif self.x == 0:
            if self.y > 0:
                theta = math.pi/2
            else:
                theta = (3*math.pi)/2
        elif self.y == 0:
            if self.x > 0:
                theta = 0
            else:
                theta = math.pi
        else:
            theta = 0

        if radians:
            return theta
        else:
            return math.degrees(theta)

    def rotate(self,theta):
        #theta should be in radians
        cs = round(math.cos(theta),3)
        sn = round(math.sin(theta),3)
        px = self.x * cs - self.y * sn
        py = self.x * sn + self.y * cs
        self.x = round(px,3)
        self.y = round(py,3)

    def length(self):
        return math.sqrt((self.x*self.x)+(self.y*self.y))
