import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad


from stcad.source_dev.drums import *


chipsize = 10000
chip = Base_Chip('TEST', chipsize, chipsize,label=False)
drum = simple_drum2(drum_size=400, drum_gap=20, tether_width=4, drum_length=40, tether_length=10)
# drum = circ_gap_drum(drum_size=20, tether_width=2, number_of_tethers=7)
# drum = rounded_drum(drum_size=40, drum_gap=5, tether_width=1)
circuit_drum = circuit_drum(drum=drum, oversize = 80, lead_length = 100, lead_width = 20, cut_out_height = 150, cut_out_width = 150)
print(circuit_drum)
# circuit_drum.translate(position = [100,100])
circuit_drum.add_to_chip(Base_Chip=chip)

chip.save_to_gds(show=True, save=True,loc='')