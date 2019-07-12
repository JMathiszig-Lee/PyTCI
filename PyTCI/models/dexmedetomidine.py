import math
from PyTCI.models.base import Three

class Dexmed(Three):
    """ base class for demedetomidine"""
    pass

class Hannivoort(Dexmed):

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


class Dyck(Dexmed):
    def __init__(self, height:int):
        """

        Units:
        Height(cm)

        Reference:
        Dyck, JB, et al
        Computer-controlled infusion of intravenous dexmedetomidine hydrochloride in adult human volunteers
        Anesthesiology. 1993 May;78(5):821-8.
        PMID:8098191 DOI:10.1097/00000542-199305000-00003 
        """

        self.v1 = 7.99
        self.v2 = 13.8
        self.v3 = 187

        self.Q1 = round((0.00791*height)-0.928,4)
        self.Q2 = 2.26
        self.Q3 = 1.99

        self.from_clearances()

        self.keo = 0

        self.setup()