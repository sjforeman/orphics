import orphics.tools.cmb as cmb
import orphics.tools.io as io
import numpy as np
from pyfisher.lensInterface import lensNoise
from ConfigParser import SafeConfigParser 
import argparse


# Get the name of the experiment and lensing type from command line
parser = argparse.ArgumentParser(description='Run a Fisher test.')
parser.add_argument('expName', type=str,help='The name of the experiment in input/params.ini')
parser.add_argument('lensName',type=str,help='The name of the CMB lensing section in input/params.ini. ',default="")
args = parser.parse_args()
expName = args.expName
lensName = args.lensName

# Read config
iniFile = "../pyfisher/input/params.ini"
Config = SafeConfigParser()
Config.optionxform=str
Config.read(iniFile)


#cls = np.loadtxt("data/Nov10_highAcc_CDM_lensedCls.dat")
cls = np.loadtxt("data/highell_lensedCls.dat")

print cls.shape


ells = np.arange(0,cls.shape[0])
cltt = cls[:,1]

fwhm = 18./60.
rms_noise = 0.1

nls = cmb.noise_func(ells,fwhm,rms_noise,TCMB=1.)*ells*(ells+1.)/2./np.pi

lcross = ells[nls>cltt][0]
print lcross

pl = io.Plotter(scaleY='log',scaleX='log')
pl.add(ells,cltt)
pl.add(ells,nls)
pl._ax.axvline(x=lcross)
pl.done("cls.png")

lmax = 60000

#cambRoot = "data/Nov10_highAcc_CDM"
#cambRoot = "data/highell"
clist = ["data/highell","data/highell_hf5","data/Nov10_highAcc_CDM"]
lablist = ['non-linear=3','non-linear=3 hf5','non-linear=1']
colist = ["C0","C1","C2"]
pl = io.Plotter(scaleY='log',scaleX='log')
namells,namclkk = np.loadtxt("data/nam_clkk.csv",delimiter=',',unpack=True)
pl.add(namells,namclkk,marker="o",ls="none",color="C3")

for cambRoot,lab,col in zip(clist,lablist,colist):
    theory = cmb.loadTheorySpectraFromCAMB(cambRoot,unlensedEqualsLensed=False,useTotal=False,TCMB = 2.7255e6,lpad=lmax)


    ls,Nls,ellbb,dlbb,efficiency,cc = lensNoise(Config,expName,lensName,beamOverride=None,noiseTOverride=None,lkneeTOverride=None,lkneePOverride=None,alphaTOverride=None,alphaPOverride=None,gradCut=2000,deg=2.,px=0.1,theoryOverride=theory,bigell=lmax)

    ells = np.arange(2,lmax,1)
    clkk = theory.gCl("kk",ells)


    pl.add(ells,clkk,label=lab,ls="-",color=col)
    pl.add(ls,Nls,label=lab+" Nl",ls="--",color=col)
pl.legendOn(loc='lower left',labsize=10)
pl._ax.set_ylim(1.e-12,1.e-5)
pl._ax.set_xlim(10,1e5)
pl.done("clkk.png")


