import re
from orphics.tools.output import bcolors
import numpy as np
from scipy.interpolate import interp1d




def loadTheorySpectraFromCAMB(cambRoot,unlensedEqualsLensed=False,useTotal=False,TCMB = 2.7255e6,lpad=9000):
    '''
    Given a CAMB path+output_root, reads CMB and lensing Cls into 
    an orphics.theory.gaussianCov.TheorySpectra object.

    The spectra are stored in dimensionless form, so TCMB has to be specified. They should 
    be used with dimensionless noise spectra and dimensionless maps.

    All ell and 2pi factors are also stripped off.

 
    '''
    
    if useTotal:
        uSuffix = "_totCls.dat"
        lSuffix = "_lensedtotCls.dat"
    else:
        uSuffix = "_scalCls.dat"
        lSuffix = "_lensedCls.dat"

    uFile = cambRoot+uSuffix
    lFile = cambRoot+lSuffix

    theory = TheorySpectra()

    ell, lcltt, lclee, lclbb, lclte = np.loadtxt(lFile,unpack=True,usecols=[0,1,2,3,4])
    mult = 2.*np.pi/ell/(ell+1.)/TCMB**2.
    lcltt *= mult
    lclee *= mult
    lclte *= mult
    lclbb *= mult
    theory.loadCls(ell,lcltt,'TT',lensed=True,interporder="linear",lpad=lpad)
    theory.loadCls(ell,lclte,'TE',lensed=True,interporder="linear",lpad=lpad)
    theory.loadCls(ell,lclee,'EE',lensed=True,interporder="linear",lpad=lpad)
    theory.loadCls(ell,lclbb,'BB',lensed=True,interporder="linear",lpad=lpad)

    ell, cldd = np.loadtxt(cambRoot+"_lenspotentialCls.dat",unpack=True,usecols=[0,5])
    clkk = 2.*np.pi*cldd/4. #/ell/(ell+1.)
    theory.loadGenericCls(ell,clkk,"kk",lpad=lpad)


    if unlensedEqualsLensed:

        theory.loadCls(ell,lcltt,'TT',lensed=False,interporder="linear",lpad=lpad)
        theory.loadCls(ell,lclte,'TE',lensed=False,interporder="linear",lpad=lpad)
        theory.loadCls(ell,lclee,'EE',lensed=False,interporder="linear",lpad=lpad)
        theory.loadCls(ell,lclbb,'BB',lensed=False,interporder="linear",lpad=lpad)

    else:
        ell, cltt, clee, clte = np.loadtxt(uFile,unpack=True,usecols=[0,1,2,3])
        mult = 2.*np.pi/ell/(ell+1.)/TCMB**2.
        cltt *= mult
        clee *= mult
        clte *= mult
        clbb = clee*0.

        theory.loadCls(ell,cltt,'TT',lensed=False,interporder="linear",lpad=9000)
        theory.loadCls(ell,clte,'TE',lensed=False,interporder="linear",lpad=9000)
        theory.loadCls(ell,clee,'EE',lensed=False,interporder="linear",lpad=9000)
        theory.loadCls(ell,clbb,'BB',lensed=False,interporder="linear",lpad=9000)


    return theory

def validateMapType(mapXYType):
    assert not(re.search('[^TEB]', mapXYType)) and (len(mapXYType)==2), \
      bcolors.FAIL+"\""+mapXYType+"\" is an invalid map type. XY must be a two" + \
      " letter combination of T, E and B. e.g TT or TE."+bcolors.ENDC



class TheorySpectra:
    '''
    Essentially just an interpolator that takes a CAMB-like
    set of discrete Cls and provides lensed and unlensed Cl functions
    for use in integrals
    '''
    

    def __init__(self):


        self._uCl={}
        self._lCl={}
        self._gCl = {}

        self._lowWarn = False
        self._highWarn = False
        self._negWarn=False
        self._ellMaxes = {}

    def loadGenericCls(self,ells,Cls,keyName,lpad=9000):
        self._gCl[keyName] = interp1d(ells[ells<lpad],Cls[ells<lpad],bounds_error=False,fill_value=0.)
        

    def gCl(self,keyName,ell):
        try:
            return self._gCl[keyName](ell)
        except:
            return self._gCl[keyName[::-1]](ell)
        
    def loadCls(self,ell,Cl,XYType="TT",lensed=False,interporder="linear",lpad=9000):

        # Implement ellnorm

        mapXYType = XYType.upper()
        validateMapType(mapXYType)


            
        #print bcolors.OKBLUE+"Interpolating", XYType, "spectrum to", interporder, "order..."+bcolors.ENDC
        f=interp1d(ell[ell<lpad],Cl[ell<lpad],kind=interporder,bounds_error=False,fill_value=0.)
        if lensed:
            self._lCl[XYType]=f
        else:
            self._uCl[XYType]=f

    def _Cl(self,XYType,ell,lensed=False):

            
        mapXYType = XYType.upper()
        validateMapType(mapXYType)

        if mapXYType=="ET": mapXYType="TE"
        ell = np.array(ell)

        if lensed:    
            retlist = np.array(self._lCl[mapXYType](ell))
            return retlist
        else:
            retlist = np.array(self._uCl[mapXYType](ell))
            return retlist

    def uCl(self,XYType,ell):
        return self._Cl(XYType,ell,lensed=False)
    def lCl(self,XYType,ell):
        return self._Cl(XYType,ell,lensed=True)
    