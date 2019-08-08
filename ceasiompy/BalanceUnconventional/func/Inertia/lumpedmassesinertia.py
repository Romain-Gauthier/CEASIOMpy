"""
    CEASIOMpy: Conceptual Aircraft Design Software

    Developed for CFS ENGINEERING, 1015 Lausanne, Switzerland

    The script evaluates the moment of inertia of an unconventional aircraft
    using the lumped masses method.
    
    Works with Python 2.7
    Author : Stefano Piccini
    Date of creation: 2018-09-27
    Last modifiction: 2019-02-20
    
"""


#=============================================================================
#   IMPORTS
#=============================================================================

import numpy as np
import math

from ceasiompy.utils.ceasiomlogger import get_logger
from ceasiompy.utils import cpacsfunctions as cpf

log = get_logger(__file__.split('.')[0])


#=============================================================================
#   CLASSES
#=============================================================================

"""All classes are defined inside the classes and into 
   the InputClasses/Unconventional folder."""
   
   
#=============================================================================
#   FUNCTIONS
#============================================================================= 
def fuselage_inertia(SPACING, center_of_gravity, mass_seg_i, afg,\
                     cpacs_in):
    """Thefunction evaluates the inertia of the fuselage using the lumped
       masses method.
       
       INPUT
       (float) SPACING  --Arg.: Maximum distance between fuselage nodes [m].
       (float_array) center_of_gravity --Arg.: x,y,z coordinates of the CoG.
       (float_array) mass_seg_i        --Arg.: Mass of each segment of each 
                                               component of the aircraft.   
       (class) afg      --Arg.: AircraftFuseGeometry class.
        ##======= Class is defined in the InputClasses folder =======##
       (char) cpacs_in --Arg.: Cpacs xml file location.
       
       OUTPUT
       (float) sfx --Out.: Lumped nodes x-coordinate [m].
       (float) sfy --Out.: Lumped nodes y-coordinate [m].
       (float) sfz --Out.: Lumped nodes z-coordinate [m].
       (float) Ixx --Out.: Moment of inertia respect to the x-axis [kgm^2].
       (float) Iyy --Out.: Moment of inertia respect to the y-axis [kgm^].
       (float) Izz --Out.: Moment of inertia respect to the z-axis [kgm^2].
    """  
    
    tixi = cpf.open_tixi(cpacs_in)
    tigl = cpf.open_tigl(tixi)
    
    sfx = []
    sfy = []
    sfz = []
    Ixx = 0
    Iyy = 0
    Izz = 0 
    Ixy = 0
    Iyz = 0
    Ixz = 0
    log.info('-------------------------------------------------------------')
    log.info('---- Evaluating fuselage nodes for lumped masses inertia ----')
    log.info('-------------------------------------------------------------')
    for f in range(1,afg.f_nb+1):
        for i in afg.f_seg_sec[:,f-1,2]:
            fx = []
            fy = []
            fz = []
            #Number of subdivisions along the longitudinal axis
            subd_l = math.ceil((afg.fuse_seg_length[int(i)-1][f-1] / SPACING))
            #Number of subdivisions along the perimeter
            SUBD_C0 = math.ceil((afg.fuse_sec_per[int(i)-1][f-1] / SPACING))
            #Number of subdivisions along the radial axis
            subd_r = math.ceil(((afg.fuse_sec_width[int(i)-1][f-1]/2)/ SPACING))
            if subd_l == 0:
                subd_l = 1.0
            if SUBD_C0 == 0:
                SUBD_C0 = 1.0
            if subd_r == 0:
                subd_r = 1.0   
            eta = 1.0 / (subd_l)
            zeta = 1.0 / (SUBD_C0)
            D0 = np.sqrt(np.arange(subd_r*SUBD_C0) / float(subd_r*SUBD_C0))
            D = np.array([t for t in (D0 - (D0[-1] - 0.98)) if not t < 0])
            (xc,yc,zc)=afg.fuse_center_section_point[int(i)-1][f-1][:]
            for j in range(int(subd_l) + 1):
                et = j * eta
                for k in range(int(SUBD_C0) + 1):
                    ze = k * zeta
                    (x0,y0,z0) = tigl.fuselageGetPoint(f, int(i), et, ze)
                    fx.append(x0)
                    fy.append(y0)
                    fz.append(z0)
                    sfx.append(x0)
                    sfy.append(y0)
                    sfz.append(z0)    
                if subd_r > 0.0:
                    deltar = np.sqrt((y0-yc)**2 + (z0-zc)**2)*D
                    theta = np.pi * (3 - np.sqrt(5)) * np.arange(len(D))
                    x = np.zeros(np.shape(deltar)) + x0
                    y = yc + deltar*np.cos(theta)
                    z = zc + deltar*np.sin(theta)
                    fx.extend(x)
                    fy.extend(y)
                    fz.extend(z)
                    sfx.extend(x)
                    sfy.extend(y)
                    sfz.extend(z)    
            M = mass_seg_i[int(i)-1,f-1]/np.max(np.shape(fx))
            fcx = (fx-(np.zeros((np.shape(fx))) + center_of_gravity[0]))
            fcy = (fy-(np.zeros((np.shape(fx))) + center_of_gravity[1])) 
            fcz = (fz-(np.zeros((np.shape(fx))) + center_of_gravity[2]))
            Ixx += np.sum(M * np.add(fcy**2, fcz**2))
            Iyy += np.sum(M * np.add(fcx**2, fcz**2))
            Izz += np.sum(M * np.add(fcx**2, fcy**2))
            Ixy += np.sum(M * fcx * fcy)
            Iyz += np.sum(M * fcy * fcz)
            Ixz += np.sum(M * fcx * fcz)
    
    return(sfx, sfy, sfz, Ixx, Iyy, Izz, Ixy, Iyz, Ixz) 
    
    
###==================================== WINGS ===============================##      

def wing_inertia(subd_c, SPACING, fuse, center_of_gravity,
                 mass_seg_i, awg, cpacs_in):
    """The function evaluates the inertia of the wings using the lumped
       masses method.
       
       INPUT
       (float) subd_c   --Arg.:  Number of subdivisions along the perimeter
                                 on each surface, total number of points for
                                 each section subd_c * 2
       (float) SPACING  --Arg.: Maximum distance between wing nodes along
                                the span [m].
       (float) fuse     --Arg.: Number of fuselages.
       (float_array) center_of_gravity --Arg.: x,y,z coordinates of the CoG.
       (float_array) mass_seg_i        --Arg.: Mass of each segment of each 
                                               component of the aircraft.   
       (class) awg      --Arg.: AircraftWingGeometry class.
        ##======= Class is defined in the InputClasses folder =======##
       (char) cpacs_in --Arg.: Cpacs xml file location.
       
       OUTPUT
       (float) swx --Out.: Lumped nodes x-coordinate [m].
       (float) swy --Out.: Lumped nodes y-coordinate [m].
       (float) swz --Out.: Lumped nodes z-coordinate [m].
       (float) Ixx --Out.: Moment of inertia respect to the x-axis [kgm^2].
       (float) Iyy --Out.: Moment of inertia respect to the y-axis [kgm^].
       (float) Izz --Out.: Moment of inertia respect to the z-axis [kgm^2].
       
    """  
    tixi = cpf.open_tixi(cpacs_in)
    tigl = cpf.open_tigl(tixi)
    
    log.info('-------------------------------------------------------------')
    log.info('------ Evaluating wing nodes for lumped masses inertia ------')
    log.info('-------------------------------------------------------------')
    
    Ixx = 0
    Iyy = 0
    Izz = 0
    Ixy = 0
    Iyz = 0
    Ixz = 0
    swx = []
    swy = []
    swz = []
    a = 0
    for w in range(1,awg.w_nb+1):
        DEN = 0.0
        for d in range(int(subd_c+2)):
            DEN = DEN + d
        zeta = 1.0/DEN 
        for i in awg.w_seg_sec[:,w-1,2]:
            if i == 0.0:
                break
            wx = []
            wy = []
            wz = []
            #Number of subdivisions along the longitudinal axis
            subd_l = math.ceil((awg.wing_seg_length[int(i)-1][w+a-1]/SPACING))
            if subd_l == 0:
                subd_l = 1
            eta = 1.0/subd_l            
            et = 0.0
            (xc,yc,zc) = awg.wing_center_seg_point[int(i)-1][w+a-1][:]
            for j in range(int(subd_l)+1):
                et = j * eta
                (xle,yle,zle) =  tigl.wingGetLowerPoint(w,int(i),et,0.0)
                (xle2,yle2,zle2) =  tigl.wingGetLowerPoint(w,int(i),et,1.0)
                if xle < xle2:
                   ZLE = 0.0
                   ze = 0.0
                else:
                   ZLE = 1.0
                   ze = 1.0
                wx.extend((xle,xle2))
                wy.extend((yle,yle2))
                wz.extend((zle,zle2))
                swx.extend((xle,xle2))
                swy.extend((yle,yle2))
                swz.extend((zle,zle2))
                for k in range(int(subd_c) + 1):
                    if ZLE == 0.0:
                        ze += float(k)*zeta 
                    elif ZLE == 1.0:
                        ze -= float(k)*zeta
                    (xl,yl,zl) =  tigl.wingGetLowerPoint(w,int(i),et,ze)
                    (xu,yu,zu) =  tigl.wingGetUpperPoint(w,int(i),et,ze)
                    wx.extend((xl,xu))
                    wy.extend((yl,yu))
                    wz.extend((zl,zu))
                    swx.extend((xl,xu))
                    swy.extend((yl,yu))
                    swz.extend((zl,zu))
            M = mass_seg_i[int(i)-1,fuse+w+a-1]/np.max(np.shape(wx))
            wcx = (wx-(np.zeros((np.shape(wx))) + center_of_gravity[0]))
            wcy = (wy-(np.zeros((np.shape(wy))) + center_of_gravity[1]))
            wcz = (wz-(np.zeros((np.shape(wz))) + center_of_gravity[2]))
            Ixx += np.sum(M * np.add(wcy**2, wcz**2))
            Iyy += np.sum(M * np.add(wcx**2, wcz**2))
            Izz += np.sum(M * np.add(wcx**2, wcy**2))
            Ixy += np.sum(M * wcx * wcy)
            Iyz += np.sum(M * wcy * wcz)
            Ixz += np.sum(M * wcx * wcz)
            if awg.wing_sym[int(w)-1] != 0:
                if awg.wing_sym[int(w)-1] == 1:   # x-y plane
                    symy = 1 + np.zeros(np.shape(wy))
                    symx = 1 + np.zeros(np.shape(wx))
                    symz = -1 + np.zeros(np.shape(wz))
                elif awg.wing_sym[int(w)-1] == 2: # x-z plane
                    symy = -1 + np.zeros(np.shape(wy))
                    symx = 1 + np.zeros(np.shape(wx))
                    symz = 1 + np.zeros(np.shape(wz))    
                elif awg.wing_sym[int(w)-1] == 3: # y-z plane
                    symy = 1 + np.zeros(np.shape(wy))
                    symx = -1 + np.zeros(np.shape(wx))
                    symz = 1 + np.zeros(np.shape(wz))
                wx_t = wx * symx
                wy_t = wy * symy
                wz_t = wz * symz
                [swx.append(x) for x in wx_t]
                [swy.append(y) for y in wy_t]
                [swz.append(z) for z in wz_t] 
                M = mass_seg_i[int(i)-1,fuse+w+a-1]/np.max(np.shape(wx_t))
                wcx_t=(wx_t-(np.zeros((np.shape(wx_t))) + center_of_gravity[0]))
                wcy_t=(wy_t-(np.zeros((np.shape(wy_t))) + center_of_gravity[1])) 
                wcz_t=(wz_t-(np.zeros((np.shape(wz_t))) + center_of_gravity[2]))
                Ixx += np.sum(M * np.add(wcy_t**2,wcz_t**2))
                Iyy += np.sum(M * np.add(wcx_t**2,wcz_t**2))
                Izz += np.sum(M * np.add(wcx_t**2,wcy_t**2))
                Ixy += np.sum(M * wcx_t * wcy_t)
                Iyz += np.sum(M * wcy_t * wcz_t)
                Ixz += np.sum(M * wcx_t * wcz_t)
        if awg.wing_sym[int(w) - 1] != 0:
            a += 1
            
    return(swx, swy, swz, Ixx, Iyy, Izz, Ixy, Iyz, Ixz)   


#=============================================================================

def engine_inertia(center_of_gravity, EngineData):
    """The function evaluates the inertia of the fuselage using the lumped
       masses method.
       
       INPUT
       (float_array) center_of_gravity --Arg.: x,y,z coordinates of the CoG.
       
       (class) EngineData --Arg.: EngineData class.
       ##======= Class is defined in the InputClasses folder =======##

       OUTPUT
       (float) Ixx --Out.: Moment of inertia respect to the x-axis [kgm^2].
       (float) Iyy --Out.: Moment of inertia respect to the y-axis [kgm^].
       (float) Izz --Out.: Moment of inertia respect to the z-axis [kgm^2].
    """  
    Ixx = 0
    Iyy = 0
    Izz = 0
    Ixy = 0
    Iyz = 0
    Ixz = 0
    
    for e in range(0,EngineData.NE):
        cx = EngineData.EN_PLACEMENT[e,0] - center_of_gravity[0]
        cy = EngineData.EN_PLACEMENT[e,1] - center_of_gravity[1]
        cz = EngineData.EN_PLACEMENT[e,2] - center_of_gravity[2]
        Ixx += EngineData.en_mass * np.add(cy**2,cz**2)
        Iyy += EngineData.en_mass * np.add(cx**2,cz**2)
        Izz += EngineData.en_mass * np.add(cx**2,cy**2)
        Ixy += EngineData.en_mass * cx * cy
        Iyz += EngineData.en_mass * cy * cz
        Ixz += EngineData.en_mass * cx * cx
        
    return(Ixx, Iyy, Izz, Ixy, Iyz, Ixz)
    
    
#==============================================================================
#   MAIN
#==============================================================================

if __name__ == '__main__': 
    log.warning('#########################################################')
    log.warning('# ERROR NOT A STANDALONE PROGRAM, RUN Balanceuncmain.py #')
    log.warning('#########################################################')   
 
