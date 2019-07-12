import math
from PyTCI.models.base import Three

class Hannivoort(Three):

    def __init__(self, weight:int):
        """ 3 compartment dexmedetomidine Pk model

        Units:
        weight(kg)

        Reference:
        Hannivoort, L, et al 
        Development of an Optimized Pharmacokinetic Model of Dexmedetomidine Using Target-controlled Infusion in Healthy Volunteers
        Anesthesiology 8 2015, Vol.123, 357-367. 
        doi:10.1097/ALN.0000000000000740 
        """ 

        self.v1 = 1.78 * (weight/70) 
        self.v2 = 30.3 * (weight/70)
        self.v3 = 52.0 * (weight/70) 

        self.Q1 = 0.686 * ((weight/70))**0.75
        self.Q2 = 2.98 * (self.v2/30.3)**0.75
        self.Q3 = 0.602 * (self.v3/52.0)**0.75

        self.from_clearances()

        self.keo = 0

        self.setup()


