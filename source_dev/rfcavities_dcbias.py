import numpy as np
import gdsCAD as cad

class ShuntCavity():

    def __init__(self, name, dict_cavity):

        self.name = name
        self.dict_cavity = dict_cavity

        self.layer_bottom = 1
        self.layer_diel = 2
        self.layer_top = 3

        self.cell = cad.core.Cell('RF_CAVITY')

        self.length = self.dict_cavity['length']
        self.centerwidth = self.dict_cavity['centerwidth']
        self.gapwidth = self.dict_cavity['gapwidth']
        self.shunts = self.dict_cavity['shunts']
        self.holedim = self.dict_cavity['holedim']
        self.holemarker = self.dict_cavity['holemarker']

        self.center = 8500
        self.launcherwidth = 490
        self.llstart = 3100     # x coordinate of launcher lead start
        self.llength = self.dict_cavity['leadlauncher']
        self.llend = self.llstart + self.llength #3400       # x coordinate of launcher lead end

        self.shuntheight = 420
        self.shuntlength = 155
        self.top_dx = 32.5
        self.top_dy = 106
        self.diel_dxy = 5 

        self.r0 = 150
        self.top_cv = 8350
        self.bot_cv = 7350 #7594

    def gen_cavities(self):

        length = self.length
        centerwidth = self.centerwidth
        gapwidth = self.gapwidth
        shunts = self.shunts

        if shunts!=1 and shunts!=2:
            raise ValueError('Number of shunts has to be either 1 or 2!')

        center = self.center

        # Create first launcher
        launcherwidth = self.launcherwidth
        llstart = self.llstart          
        llend = self.llend      
        launcherpoints = [(700, center+(launcherwidth+centerwidth)/2),
                        (1900, center+(launcherwidth+centerwidth)/2),
                        (llstart, center+centerwidth/2),
                        (llstart, center-centerwidth/2),
                        (1900, center-(launcherwidth+centerwidth)/2),
                        (700, center-(launcherwidth+centerwidth)/2)]
        launcher = cad.core.Boundary(launcherpoints)

        # Create first shunt
        shunt1 = self.gen_shunt((llstart,self.llength),0)

        # Cavity length starts here
        startx0 = shunt1[5]
        stopx0 = startx0 + self.dict_cavity['lead1']
        
        shunt1_cavity_points = [(startx0,center),(stopx0,center)]
        start_cavity = cad.core.Path(shunt1_cavity_points,centerwidth)

        r0 = self.r0
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = self.top_cv
        bot_cv = self.bot_cv
        
        # Calculate cavity length
        A = (stopx0-startx0) + 2*np.pi*r0 * 2 + (top_cv-bot_cv) * 4
        endx0 = stopx0+r0*8
        self.endx = length - (A - endx0)

        curve1 = cad.shapes.Disk((stopx0,top_cv),radius,inner_radius=inner_radius,initial_angle=90,
            final_angle=0)
        curve1_lead = cad.core.Path([(stopx0+r0, top_cv),(stopx0+r0,bot_cv)],centerwidth)
        curve2 = cad.shapes.Disk((stopx0+r0*2,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve2_lead = cad.core.Path([(stopx0+r0*3,bot_cv),(stopx0+r0*3,top_cv)],centerwidth)
        curve3 = cad.shapes.Disk((stopx0+r0*4,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=0)
        curve3_lead = cad.core.Path([(stopx0+r0*5,top_cv),(stopx0+r0*5,bot_cv)],centerwidth)
        curve4 = cad.shapes.Disk((stopx0+r0*6,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve4_lead = cad.core.Path([(stopx0+r0*7,bot_cv),(stopx0+r0*7,top_cv)],centerwidth)
        curve5 = cad.shapes.Disk((endx0,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=90)
        final_lead = cad.core.Path([(endx0,center),(self.endx,center)],centerwidth)

        # Create second shunt (optional)
        if shunts==2:
            shunt2 = self.gen_shunt((self.endx,70),125)
            # Create second launcher
            launcher2 = cad.utils.reflect(launcher,'y',origin=(5000,5000))
            launcher2 = cad.utils.translate(launcher2,(shunt2[5]-(10000-llstart),0))
        else:
            # Create second launcher
            launcher2 = cad.utils.reflect(launcher,'y',origin=(5000,5000))
            holex0 = self.endx
            holedim = self.holedim
            launcher2 = cad.utils.translate(launcher2,((holex0+holedim[0])-(10000-llstart),0))

        # Create cavity
        cavity1 = [cad.core.Elements()] * 3
        # Add all elements with layer 1
        for toadd in [launcher, shunt1[0], shunt1[1], shunt1[4],
                    start_cavity, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead,
                    launcher2]:
            toadd.layer = self.layer_bottom
            cavity1[0].add(toadd)
        
        # Add all elements with layer 2
        for toadd in [shunt1[2]]:
            toadd.layer = self.layer_diel
            cavity1[1].add(toadd)

        # Add all elements with layer 3
        for toadd in [shunt1[3]]:
            toadd.layer = self.layer_top
            cavity1[2].add(toadd)

        if shunts==2:
            for toadd in [shunt2[0], shunt2[1], shunt2[4]]:
                toadd.layer = self.layer_bottom
                cavity1[0].add(toadd)
            for toadd in [shunt2[2]]:
                toadd.layer = self.layer_diel
                cavity1[0].add(toadd)
            for toadd in [shunt2[3]]:
                toadd.layer = self.layer_top
                cavity1[0].add(toadd)
        
        
        # Create second cavity as mirrored version of first one
        cavity2 = [cad.utils.reflect(cavity1[i],'x',origin=(5000,5000)) for i in range(3)]
        
        self.cell.add(cavity1[0])
        self.cell.add(cavity2[0])
        

    def gen_shunt(self,leadin,leadout,gap=0):

        # Connect in to shunt
        startx_in = leadin[0]
        stopx_in = startx_in+leadin[1]
        leadpoints_in = [(startx_in, self.center),(stopx_in,self.center)]
        lead_in = cad.core.Path(leadpoints_in,self.centerwidth)

        # Create shunt
        shuntheight = self.shuntheight + 2*gap
        shuntlength = self.shuntlength + 2*gap
        shunt_x1 = stopx_in - gap
        shunt_y1 = self.center - shuntheight/2
        shunt_x2 = shunt_x1 + shuntlength
        shunt_y2 = shunt_y1 + shuntheight
        shunt_points = [(shunt_x1, shunt_y1),(shunt_x2, shunt_y2)]

        top_dx = self.top_dx
        top_dy = self.top_dy
        shunt_top_points = [(shunt_x1-top_dx, shunt_y1-top_dy),
                            (shunt_x2+top_dx, shunt_y2+top_dy)]

        diel_dxy = self.diel_dxy      # 5um overlap
        shunt_diel_points = [(shunt_x1-top_dx-diel_dxy, shunt_y1-top_dy-diel_dxy),
                            (shunt_x2+top_dx+diel_dxy, shunt_y2+top_dy+diel_dxy)]
        
        shunt = cad.shapes.Rectangle(shunt_points[0],shunt_points[1])
        shunt_diel = cad.shapes.Rectangle(shunt_diel_points[0],shunt_diel_points[1])
        shunt_top = cad.shapes.Rectangle(shunt_top_points[0],shunt_top_points[1])

        # Connect shunt to out
        startx_out = shunt_x2
        stopx_out = startx_out+leadout
        leadpoints_out = [(startx_out, self.center),(stopx_out,self.center)]
        lead_out = cad.core.Path(leadpoints_out,self.centerwidth)

        return (lead_in, shunt, shunt_diel, shunt_top, lead_out, stopx_out)



    def gen_full(self):

        length = self.length
        centerwidth = self.centerwidth + 2*self.gapwidth
        gapwidth = self.gapwidth
        shunts = self.shunts

        if shunts!=1 and shunts!=2:
            raise ValueError('Number of shunts has to be either 1 or 2!')

        center = self.center
        # Create first launcher
        launcherwidth = self.launcherwidth
        llstart = self.llstart          
        llend = self.llend      
        launcherpoints = [(-500, center+(launcherwidth+centerwidth)/2+230),
                        (1900, center+(launcherwidth+centerwidth)/2+230),
                        (llstart, center+centerwidth/2),
                        (llstart, center-centerwidth/2),
                        (1900, center-(launcherwidth+centerwidth)/2-230),
                        (-500, center-(launcherwidth+centerwidth)/2-230)]
        launcher = cad.core.Boundary(launcherpoints)

        # Create first shunt
        shunt1 = self.gen_shunt((llstart,self.llength),0,gap=gapwidth)

        # Cavity length starts here
        startx0 = shunt1[5]
        stopx0 = startx0 + self.dict_cavity['lead1']
        
        shunt1_cavity_points = [(startx0,center),(stopx0,center)]
        start_cavity = cad.core.Path(shunt1_cavity_points,centerwidth)

        r0 = self.r0
        radius = r0+centerwidth/2
        inner_radius = r0-centerwidth/2
        top_cv = self.top_cv
        bot_cv = self.bot_cv
        
        # Calculate cavity length from before
        
        endx0 = stopx0+r0*8
        endx = self.endx

        curve1 = cad.shapes.Disk((startx0,top_cv),radius,inner_radius=inner_radius,initial_angle=90,
            final_angle=0)
        curve1_lead = cad.core.Path([(startx0+r0, top_cv),(startx0+r0,bot_cv)],centerwidth)
        curve2 = cad.shapes.Disk((startx0+r0*2,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve2_lead = cad.core.Path([(startx0+r0*3,bot_cv),(startx0+r0*3,top_cv)],centerwidth)
        curve3 = cad.shapes.Disk((startx0+r0*4,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=0)
        curve3_lead = cad.core.Path([(startx0+r0*5,top_cv),(startx0+r0*5,bot_cv)],centerwidth)
        curve4 = cad.shapes.Disk((startx0+r0*6,bot_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=360)
        curve4_lead = cad.core.Path([(startx0+r0*7,bot_cv),(startx0+r0*7,top_cv)],centerwidth)
        curve5 = cad.shapes.Disk((endx0,top_cv),radius,inner_radius=inner_radius,initial_angle=180,
            final_angle=90)
        final_lead = cad.core.Path([(endx0,center),(endx - self.gapwidth,center)],centerwidth)

        # Add hole for gJJ
        holex0 = endx - self.gapwidth
        holedim = self.holedim
        holemarker = self.holemarker
        gJJ_box = cad.shapes.Rectangle((holex0, center-holedim[1]/2),(holex0+holedim[0],center+holedim[1]/2))
        if holemarker == True:
            gJJ_marker = [cad.core.Elements()] * 4
            #for i in range(2):
            box1 = cad.shapes.Rectangle((holex0+5,center+40),(holex0+10,center+45))
            box2 = cad.shapes.Rectangle((holex0+10,center+35),(holex0+15,center+40))
            gJJ_marker[0].add(box1)
            gJJ_marker[0].add(box2)
            gJJ_marker[1] = cad.utils.reflect(gJJ_marker[0],'x',origin=(holex0+holedim[0]/2,center))
            gJJ_marker[2] = cad.utils.reflect(gJJ_marker[0],'y',origin=(holex0+holedim[0]/2,center))
            gJJ_marker[3] = cad.utils.reflect(gJJ_marker[1],'y',origin=(holex0+holedim[0]/2,center))

        # Create second launcher
        launcher2 = cad.utils.reflect(launcher,'y',origin=(5000,5000))
        launcher2 = cad.utils.translate(launcher2,((holex0+holedim[0])-(10000-llstart),0))

        # Create cavity
        cavity1 = cad.core.Elements()
        # Add all elements with layer 1
        for toadd in [launcher, shunt1[0], shunt1[1], shunt1[4],
                    start_cavity, curve1,
                    curve1_lead, curve2, curve2_lead, curve3, curve3_lead,
                    curve4, curve4_lead, curve5, final_lead,
                    gJJ_box, gJJ_marker[0], gJJ_marker[1], gJJ_marker[2], gJJ_marker[3],
                    launcher2,]:
            toadd.layer = self.layer_bottom
            cavity1.add(toadd)
        
        # Create second cavity as mirrored version of first one
        cavity2 = cad.utils.reflect(cavity1,'x',origin=(5000,5000))
        
        self.cell.add(cavity1)
        self.cell.add(cavity2)
    

