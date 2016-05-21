
class SomeBaseClass(object):
    def __init__(self, value):
        print value
        print('SomeBaseClass.__init__(self) called')

    def test_m(self):
    	print('SomeBaseClass test method')

"""
class Child(SomeBaseClass):
    def __init__(self):
        print('Child.__init__(self) called')
        super(SomeBaseClass, self).__init__()
        #SomeBaseClass.__init__(self)

    def test_c_m(self):
    	self.test_m()
    	self.test_mm()

    def test_mm(self):
    	print('Child test method')

c = Child()
c.test_c_m()
"""

class SuperChild(SomeBaseClass):
    def __init__(self):
        print self
        print('SuperChild.__init__(self) called')
        super(SuperChild, self).__init__("value")      # this calls __init__ in SomeBaseClass
        #super(SomeBaseClass, self).__init__()   # this calls not __init__ in SomeBaseClass 
        #SomeBaseClass.__init__(self)           # this also calls __init__ in SomeBaseClass
        print self

    def test_sc_m(self):
    	self.test_m()
    	self.test_mm()

    def test_mm(self):
    	print('SuperChild test method')


s = SuperChild()
s.test_sc_m()

class Polygon(object):
    def __init__(self, id):
        self.id = "polygon id"

class Rectangle(Polygon):
    def __init__(self):#, id, width, height):
        super(self.__class__, self).__init__(id)
        #self.shape = (width, height)
        #print self.shape
        print id
        print self.id

class Square(Rectangle):
    pass


#mRec = Rectangle()#"id", "width", "height")