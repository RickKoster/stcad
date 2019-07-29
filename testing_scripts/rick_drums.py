import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad


from stcad.source_dev.drums import *

chipsize = 10000
chip = Base_Chip('TEST', chipsize, chipsize,label=False)


# --------------------------------------------- Array -----------------------------------

start_pos = [[-4000,4000],[100,4000],[-4000,-750]]
# start_pos = [[-4000,4000],[100,4000]]
array_separation = 200

array_indicators = ["A","B","C","D"]

for i in range(len(start_pos)):
	drum_sizes=[5,10,20,40]
	drum_gaps=[2,3,5,10,15]
	tether_widths=[.5,.8,1,2]

	# Array = simple_drum_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths, separation=100)
	# for i in range(len(Array.get_dependencies())):
	# 	chip.add(Array.get_dependencies()[i]._objects)

	position = start_pos[i]
	Array1 = simple_drum_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array1.translate(position=position)
	# Array1.add_labl()
	print(Array1._bounding_box)
	Array1.add_to_chip(Base_Chip=chip)
	position = [Array1._bounding_box[1,0]+array_separation,start_pos[i][1]]

	Array2 = rounded_base_drum4_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array2.translate(position=position)
	# Array2.add_labl(text = "RBD")
	Array2.add_to_chip(Base_Chip=chip)
	position = [Array2._bounding_box[1,0]+array_separation,start_pos[i][1]]

	Array4 = simple_drum3_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array4.translate(position=position)
	Array4.add_to_chip(Base_Chip=chip)
	position = [Array4._bounding_box[1,0]+array_separation,start_pos[i][1]]

	Array3 = simple_drum2_Array(drum_sizes = drum_sizes, drum_length = 30, drum_gaps = drum_gaps, tether_widths = tether_widths, tether_length=5,array_indicator=array_indicators[i])
	Array3.translate(position=position)
	Array3.add_to_chip(Base_Chip=chip)
	position = [Array3._bounding_box[1,0]+array_separation,start_pos[i][1]]

	Array5 = circular_drum2_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array5.translate(position=position)
	Array5.add_to_chip(Base_Chip=chip)
	position = [Array5._bounding_box[1,0]+array_separation,start_pos[i][1]]

	Array7 = rounded_base_drum5_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array7.translate(position=position)
	Array7.add_to_chip(Base_Chip=chip)
	position = [Array7._bounding_box[1,0]+array_separation,start_pos[i][1]]

	drum_sizes=[20,30,50,100]
	drum_gaps=[1,2,3,5]
	tether_widths=[.5,.8,1,1.5]
	
	Array6 = rounded_base_drum3_Array(drum_sizes=drum_sizes,drum_gaps=drum_gaps,tether_widths=tether_widths,array_indicator=array_indicators[i])
	Array6.translate(position=position)
	Array6.add_to_chip(Base_Chip=chip)
	position = [Array6._bounding_box[1,0]+array_separation,start_pos[i][1]]

start_pos = [100,0]

array_separation = 300

position = start_pos

drum_sizes = [1,2,4,10,15]
drum_gaps = [2,4,10, 30]
tether_widths = [0.5,2,4,10,15]
board_array = diving_board_Array(drum_sizes, drum_gaps, tether_widths, separation = 50)
board_array.translate(position=position)
board_array.add_to_chip(Base_Chip=chip)

position = [board_array._bounding_box[1,0]+array_separation,start_pos[1]]
drum_sizes = [20, 10, 5, 3]
tether_widths = [0.5, 1, 2, 4]
numbers_of_tethers = [5,6,7]
circ_array1 = circ_gap_drum_Array(drum_sizes=drum_sizes,tether_widths=tether_widths,numbers_of_tethers=numbers_of_tethers,array_indicator="A")
circ_array1.translate(position=position)
circ_array1.add_to_chip(Base_Chip=chip)

position = [board_array._bounding_box[0,0], board_array._bounding_box[0,1]-array_separation]
drum1 = circ_gap_drum(drum_size=20,tether_width=1,number_of_tethers=7)
circuit_drum1 = circuit_drum(drum=drum1, oversize = 80, lead_length = 100, lead_width = 70, cut_out_height = 150, cut_out_width = 150)
circuit_drum1.translate(position=position)
circuit_drum1.add_to_chip(Base_Chip=chip)

position = [circuit_drum1._bounding_box[0,0], circuit_drum1._bounding_box[0,1]-array_separation]
drum2 = circ_gap_drum(drum_size=20,tether_width=2,number_of_tethers=7)
circuit_drum2 = circuit_drum(drum=drum2, oversize = 80, lead_length = 100, lead_width = 70, cut_out_height = 150, cut_out_width = 150)
circuit_drum2.translate(position=position)
circuit_drum2.add_to_chip(Base_Chip=chip)

position = [circuit_drum1._bounding_box[1,0]+array_separation, circuit_drum1._bounding_box[1,1]]
circ_array2 = circ_gap_drum_Array(drum_sizes=drum_sizes,tether_widths=tether_widths,numbers_of_tethers=numbers_of_tethers,array_indicator="B")
circ_array2.translate(position=position)
print(circ_array2._bounding_box)
circ_array2.add_to_chip(Base_Chip=chip)

position = [circ_array2._bounding_box[1,0]+array_separation, circ_array2._bounding_box[1,1]-array_separation]
drum3 = circ_gap_drum(drum_size=20,tether_width=3,number_of_tethers=7)
circuit_drum3 = circuit_drum(drum=drum3, oversize = 80, lead_length = 100, lead_width = 50, cut_out_height = 150, cut_out_width = 150)
circuit_drum3.translate(position=position)
circuit_drum3.add_to_chip(Base_Chip=chip)

position = [circuit_drum3._bounding_box[0,0], circuit_drum3._bounding_box[0,1]-array_separation]
drum4 = circ_gap_drum(drum_size=20,tether_width=4,number_of_tethers=7)
circuit_drum4 = circuit_drum(drum=drum4, oversize = 80, lead_length = 100, lead_width = 50, cut_out_height = 150, cut_out_width = 150)
circuit_drum4.translate(position=position)
circuit_drum4.add_to_chip(Base_Chip=chip)

position = [circuit_drum3._bounding_box[1,0]+array_separation, circuit_drum3._bounding_box[1,1]]
drum5 = circ_gap_drum(drum_size=10,tether_width=2,number_of_tethers=7)
circuit_drum5 = circuit_drum(drum=drum5, oversize = 80, lead_length = 100, lead_width = 40, cut_out_height = 150, cut_out_width = 150)
circuit_drum5.translate(position=position)
circuit_drum5.add_to_chip(Base_Chip=chip)

position = [circuit_drum5._bounding_box[0,0], circuit_drum5._bounding_box[0,1]-array_separation]
drum6 = circ_gap_drum(drum_size=5,tether_width=1,number_of_tethers=8)
circuit_drum6 = circuit_drum(drum=drum6, oversize = 80, lead_length = 100, lead_width = 40, cut_out_height = 150, cut_out_width = 150)
circuit_drum6.translate(position=position)
circuit_drum6.add_to_chip(Base_Chip=chip)

position = [circuit_drum5._bounding_box[1,0]+array_separation, -1000]
drum_sizes = [1,2,4,10,15]
drum_gaps = [2,4,10, 30]
tether_widths = [0.5,2,4,10,15]
board_array2 = diving_board_Array(drum_sizes, drum_gaps, tether_widths, separation = 50)
board_array2.translate(position=position)
board_array2.add_to_chip(Base_Chip=chip)

position = [circ_array1._bounding_box[1,0]+array_separation+500, 0]
drum7 = circ_gap_drum(drum_size=30,tether_width=4,number_of_tethers=10)
circuit_drum7 = circuit_drum(drum=drum7, oversize = 80, lead_length = 150, lead_width = 100, cut_out_height = 150, cut_out_width = 150)
circuit_drum7.translate(position=position)
circuit_drum7.add_to_chip(Base_Chip=chip)

position = [circuit_drum7._bounding_box[0,0], circuit_drum7._bounding_box[0,1]-array_separation]
drum8 = circ_gap_drum(drum_size=10,tether_width=4,number_of_tethers=10)
circuit_drum8 = circuit_drum(drum=drum8, oversize = 80, lead_length = 150, lead_width = 50, cut_out_height = 150, cut_out_width = 150)
circuit_drum8.translate(position=position)
circuit_drum8.add_to_chip(Base_Chip=chip)

position = [circuit_drum7._bounding_box[1,0]+array_separation, circuit_drum7._bounding_box[1,1]]
drum9 = circ_gap_drum(drum_size=10,tether_width=2,number_of_tethers=10)
circuit_drum9 = circuit_drum(drum=drum9, oversize = 80, lead_length = 150, lead_width = 50, cut_out_height = 150, cut_out_width = 150)
circuit_drum9.translate(position=position)
circuit_drum9.add_to_chip(Base_Chip=chip)

position = [circuit_drum9._bounding_box[0,0], circuit_drum9._bounding_box[0,1]-array_separation]
drum10 = circ_gap_drum(drum_size=10,tether_width=2,number_of_tethers=5)
circuit_drum10 = circuit_drum(drum=drum10, oversize = 80, lead_length = 150, lead_width = 50, cut_out_height = 150, cut_out_width = 150)
circuit_drum10.translate(position=position)
circuit_drum10.add_to_chip(Base_Chip=chip)

points_square = [[0,0], [1000,0],[1000,-1000],[0,-1000],[0,0]]
square = cad.core.Boundary(points_square)
square.translate([1500,-1500])
chip.add(square)

# ------------------------------------------- Array End ----------------------------------

chip.save_to_gds(show=True, save=True,loc='')