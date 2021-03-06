import numpy as np
from stcad.source_dev.utilities import *
from stcad.source_dev.objects import *
from stcad.source_dev.chip import *
import gdsCAD as cad
# import shapely as sh
# import shapely.ops as op
# import os, inspect
# current_directory = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # script directory

class SuspendedDrum(cad.core.Cell):

	# Parent class for all drum types. Returns a suspended drum 'Boundary' with given size, gap, tether width, 

	def __init__(self, drum_size, drum_gap, tether_width):
		super()
		self._objects=[]
		self._references = []
		self._bounding_box = None

		self.drum_size = drum_size
		self.drum_gap = drum_gap
		self.tether_width = tether_width

		self.delta = (1/np.sqrt(2))*tether_width
		self.alpha = (1/np.sqrt(2))*(drum_size-2*self.delta)
		self.gamma = (1/np.sqrt(2))*self.alpha
		
		self.top_width = self.drum_size-2*self.delta
		self.bottom_width = self.top_width+2*self.drum_gap
		self.height = self.drum_gap
		
	def get_details(self):
		return "drum_size = %s, drum_gap = %s, tether_width =  %s." % (self.drum_size, self.drum_gap, self.tether_width)

	def bounding_box(self):
		# Return the smallest rectangle enclosing the drum.
		bb = np.zeros([2,2])
		# if self._bounding_box is not None:
		# 	return self._bounding_box.copy()
		for i in range(len(self._objects)):
			if i == 0:
				bb[0,0] = self._objects[i]._points[:,0].min()
				bb[0,1] = self._objects[i]._points[:,1].min()
				bb[1,0] = self._objects[i]._points[:,0].max()
				bb[1,1] = self._objects[i]._points[:,1].max()
			else:
				bb[0,0] = min(self._objects[i]._points[:,0].min(), bb[0,0])
				bb[0,1] = min(self._objects[i]._points[:,1].min(), bb[0,1])
				bb[1,0] = max(self._objects[i]._points[:,0].max(), bb[1,0])
				bb[1,1] = max(self._objects[i]._points[:,1].max(), bb[1,1])

		self._bounding_box = bb
		return bb

	def translate(self, position):
		# Translates the center of the drum from its original position (0,0) by the vector 'position'
		
		for i in range(len(self._objects)):
			self._objects[i].points = cad.utils.translate(self._objects[i].points, position)
		self.bounding_box()

	def add_to_chip(self, Base_Chip):
		Base_Chip.add(self._objects)

	def add_labl(self, position = (0,0), array_indicator = None):
		if array_indicator != None:
			self.name += array_indicator
		label = cad.shapes.Label(text = self.name, size=3, position = position, horizontal=True, angle=0, layer=None, datatype=None)
		for i in range(len(label)):
			self.add(cad.core.Boundary(label[i].points, layer=1))
		self.bounding_box()

class simple_drum(SuspendedDrum): #Drum with 4 tethers, no rounded corners.
	def __init__(self, drum_size, drum_gap, tether_width):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "
		trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer=1)
		trap1 = cad.utils.translate(trap0, [0,-(self.drum_gap+self.drum_size/2)])
		trap2 = cad.utils.rotate(trap1, 90, center=(0,0))
		trap3 = cad.utils.rotate(trap1, 180, center=(0,0))
		trap4 = cad.utils.rotate(trap1, 270, center=(0,0))

		self.add(trap1)
		self.add(trap2)
		self.add(trap3)
		self.add(trap4)

		self.bounding_box()

	def get_details(self):
		return "drum_size = %s, drum_gap = %s, tether_width =  %s." % (self.drum_size, self.drum_gap, self.tether_width)

class rounded_drum(SuspendedDrum): #Drum with 4 tethers, rounded corners. Gaps are created by joining a trapezoid to a partial disk.
	def __init__(self, drum_size, drum_gap, tether_width):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "

		trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer=1)

		disk_offset = drum_gap-self.gamma
		disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=45,final_angle=135)

		gap0 = join_polygons(disk0, trap0, format_shapely=False)

		gap1 = cad.utils.translate(gap0, [0,-(drum_gap+drum_size/2)])
		gap2 = cad.utils.rotate(gap1, 90, center=(0,0))
		gap3 = cad.utils.rotate(gap1, 180, center=(0,0))
		gap4 = cad.utils.rotate(gap1, 270, center=(0,0))

		self.add(gap1)
		self.add(gap2)
		self.add(gap3)
		self.add(gap4)

		self.bounding_box()

class simple_drum3(SuspendedDrum): #Drum with 3 tethers, no rounding of corners.
	def __init__(self, drum_size, drum_gap, tether_width):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "
		self.detla = tether_width/(np.sin(np.deg2rad(30)))
		
		self.top_width = self.drum_size-2*self.delta
		self.bottom_width = 2*(np.tan(np.deg2rad(60))*drum_gap)+self.top_width
		self.height = drum_gap

		trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer=1)

		trap1 = cad.utils.translate(trap0, [0,-(drum_gap+0.5*np.tan(np.deg2rad(30))*drum_size)])
		trap2 = cad.utils.rotate(trap1, 120, center = (0,0))
		trap3 = cad.utils.rotate(trap1, 240, center = (0,0))
		self.add(trap1)
		self.add(trap2)
		self.add(trap3)

		self.bounding_box()

class rounded_base_drum3(SuspendedDrum): #Drum with 3 tethers, rounded corners. Gaps are made by joining a trapezoid and a partial disk. At the interface between the partical disk and the trapezoid the radius of the disk is such that the connection to the trapezoid is smooth (no corner). The corners at the base of the trapezoid are rounded using the function round_corner.
	def __init__(self, drum_size, drum_gap, tether_width, corner_rad, nr_of_points):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "


		self.corner_rad = corner_rad
		self.nr_of_points = nr_of_points

		self.delta = tether_width/(np.sin(np.deg2rad(30)))
		
		self.top_width = self.drum_size-2*self.delta
		self.bottom_width = 2*(np.tan(np.deg2rad(60))*drum_gap)+self.top_width
		self.height = drum_gap

		trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer=1)

		# corner_rad = .90

		self.alpha = 0.5*self.top_width/(np.sin(np.deg2rad(30)))
		self.gamma = 0.5*self.top_width/(np.tan(np.deg2rad(30)))

		disk_offset = self.drum_gap-self.gamma
		disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=60,final_angle=120)
		gap0 = join_polygons(disk0, trap0, format_shapely=False)
	
		gap0_rounded_points = round_corner(gap0.points,[gap0.points.shape[0]-3,gap0.points.shape[0]-2], corner_rad=corner_rad,nr_of_points=self.nr_of_points) # Point list now starts at first point of the disk!

		gap0_rounded = cad.core.Boundary(gap0_rounded_points)

		gap1 = cad.utils.translate(gap0_rounded, [0,-(drum_gap+0.5*np.tan(np.deg2rad(30))*drum_size)])
		gap2 = cad.utils.rotate(gap1, 120, center = (0,0))
		gap3 = cad.utils.rotate(gap1, 240, center = (0,0))

		self.add(gap1)
		self.add(gap2)
		self.add(gap3)

		self.bounding_box()

class rounded_base_drum4(SuspendedDrum): #Drum with 4 tethers, rounded corners. Gaps are made by joining a trapezoid and a partial disk. At the interface between the partical disk and the trapezoid the radius of the disk is such that the connection to the trapezoid is smooth (no corner). The corners at the base of the trapezoid are rounded using the function round_corner.
	def __init__(self, drum_size, drum_gap, tether_width, corner_rad, nr_of_points):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "
		self.corner_rad = corner_rad
		self.nr_of_points = nr_of_points
		trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer=1)

		corner_rad = .90

		disk_offset = drum_gap-self.gamma
		disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=45,final_angle=135)
		gap0 = join_polygons(disk0, trap0, format_shapely=False)
	
		gap0_rounded_points = round_corner(gap0.points,[gap0.points.shape[0]-3,gap0.points.shape[0]-2], corner_rad=corner_rad,nr_of_points=self.nr_of_points) # Point list now starts at first point of the disk!

		gap0_rounded = cad.core.Boundary(gap0_rounded_points)


		gap1 = cad.utils.translate(gap0_rounded, [0,-(drum_gap+drum_size/2)])
		gap2 = cad.utils.rotate(gap1, 90, center=(0,0))
		gap3 = cad.utils.rotate(gap1, 180, center=(0,0))
		gap4 = cad.utils.rotate(gap1, 270, center=(0,0))

		self.add(gap1)
		self.add(gap2)
		self.add(gap3)
		self.add(gap4)

		self.bounding_box()

class rounded_base_drum5(SuspendedDrum): #Drum with 5 tethers, rounded corners. Holes are made by joining a trapezoid and a partial disk. At the interface between the partical disk and the trapezoid the radius of the disk is such that the connection to the trapezoid is smooth (no corner). The corners at the base of the trapezoid are rounded using the function round_corner.
	def __init__(self, drum_size, drum_gap, tether_width, corner_rad, nr_of_points):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "


		self.corner_rad = corner_rad
		self.nr_of_points = nr_of_points

		self.delta = tether_width/(np.sin(np.deg2rad(54)))
		
		self.top_width = self.drum_size-2*self.delta
		self.bottom_width = 2*(np.tan(np.deg2rad(36))*drum_gap)+self.top_width
		self.height = drum_gap

		trap0 = symmetric_trapezoid(self.bottom_width, self.top_width, self.height, layer=1)

		corner_rad = .90

		self.alpha = 0.5*self.top_width/(np.sin(np.deg2rad(54)))
		self.gamma = 0.5*self.top_width/(np.tan(np.deg2rad(54)))

		disk_offset = self.drum_gap-self.gamma
		disk0= cad.shapes.Disk((0,disk_offset),self.alpha,initial_angle=36,final_angle=144)
		gap0 = join_polygons(disk0, trap0, format_shapely=False)
	
		gap0_rounded_points = round_corner(gap0.points,[gap0.points.shape[0]-3,gap0.points.shape[0]-2], corner_rad=corner_rad,nr_of_points=self.nr_of_points) # Point list now starts at first point of the disk!

		gap0_rounded = cad.core.Boundary(gap0_rounded_points)

		gap1 = cad.utils.translate(gap0_rounded, [0,-(drum_gap+0.5*np.tan(np.deg2rad(54))*drum_size)])
		gap2 = cad.utils.rotate(gap1, 72, center = (0,0))
		gap3 = cad.utils.rotate(gap1, 144, center = (0,0))
		gap4 = cad.utils.rotate(gap1, 216, center = (0,0))
		gap5 = cad.utils.rotate(gap1, 288, center = (0,0))

		self.add(gap1)
		self.add(gap2)
		self.add(gap3)
		self.add(gap4)
		self.add(gap5)

		self.bounding_box()

class simple_drum2(SuspendedDrum): # Rectangular drum with 2 tethers. no rounded corners.
	def __init__(self, drum_size, drum_length, drum_gap, tether_width, tether_length):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "
		self.points = [[-(0.5*drum_length + tether_length),0],[-(0.5*drum_length + tether_length),drum_gap+0.5*(drum_size-tether_width)],[-(0.5*drum_length),drum_gap+0.5*(drum_size-tether_width)],[-(0.5*drum_length),drum_gap],[(0.5*drum_length),drum_gap],[(0.5*drum_length),drum_gap+0.5*(drum_size-tether_width)],[(0.5*drum_length + tether_length),drum_gap+0.5*(drum_size-tether_width)],[(0.5*drum_length + tether_length),0],[-(0.5*drum_length + tether_length),0]]
		gap0 = cad.core.Boundary(self.points)
		gap1 = cad.utils.translate(gap0,[0,-(0.5*(drum_size+tether_width)+drum_gap)])
		gap2 = cad.utils.rotate(gap1, 180, center=(0,0))

		self.add(gap1)
		self.add(gap2)

		self.bounding_box()

class circular_drum2(SuspendedDrum): # Circular drum with 2 tethers, no rounded corners.
	def __init__(self, drum_size, drum_gap, tether_width):
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)

		disk0 = cad.shapes.Disk((0,0),radius=drum_size/2+drum_gap, inner_radius=drum_size/2, initial_angle=0, final_angle=180, number_of_points=199)
		disk1 = cad.utils.translate(disk0,[0,tether_width])
		disk2 = cad.utils.rotate(disk1, 180, center=(0,0))

		self.add(disk1)
		self.add(disk2)

		self.bounding_box()

class circ_gap_drum(SuspendedDrum): # Drums created by making gaps out of Disk shapes centered along a circle with radius depending on drum_size, tether_width, and number_of_tethers. 
	def __init__(self,drum_size, tether_width, number_of_tethers):
		
		self.number_of_tethers = number_of_tethers

		alpha = 360/(self.number_of_tethers)
		self.gap_radius = (tether_width/2 - np.sin(np.deg2rad(alpha/2))*drum_size)/(np.sin(np.deg2rad(alpha/2))-1)
		self.name = f"{tether_width}, {round(2*self.gap_radius,1)}, {drum_size} "
		SuspendedDrum.__init__(self, drum_size, 2*self.gap_radius, tether_width)
		print(self.gap_radius)
		size = drum_size + self.gap_radius
		points = []
		i=0
		while i < number_of_tethers:
			new_point = [np.cos(np.deg2rad(i*alpha))*size,np.sin(np.deg2rad(i*alpha))*size]
			gap = cad.shapes.Disk(center = new_point, radius = self.gap_radius)
			self.add(gap)
			if i == 0:
				points = [new_point]
			else:
				points = np.vstack([points, new_point])
			i += 1
		print(points)

		
		self._references = []
		self.bounding_box()

class diving_board(SuspendedDrum): # Rectangular drum with 2 tethers. no rounded corners.
	def __init__(self, drum_size, drum_gap, tether_width):
		SuspendedDrum.__init__(self, drum_size, drum_gap, tether_width)
		self.name = f"{tether_width}, {drum_gap}, {drum_size} "
		self.points = [[0,0],[drum_gap + drum_size,0],[drum_gap + drum_size,-(2*drum_gap + tether_width)],[0,-(2*drum_gap + tether_width)],[0, -(drum_gap + tether_width)], [drum_size, -(drum_gap + tether_width)],[drum_size, -drum_gap], [0,-drum_gap],[0,0]]
		board = cad.core.Boundary(self.points)
		self.add(board)
		self.bounding_box()

def round_corner(arr, points, corner_rad, nr_of_points):
	# Takes a point from a point list and replaces it by a series of points that create a partial circle connected to the points above and below on the list.
	corners = arr
	# print("Points: ",points)
	amnt_points = arr.shape[0]
	# print("amnt_points",amnt_points)
	corners_temp = corners
	for i in range(len(points)):
		if points[i] > amnt_points:
			print("There is no point with number ",points[i])
		point_nr = points[i]+i*(nr_of_points-1) #Points will be pushed down by those added with the circle
		point = corners_temp[point_nr,:]
		# print("point: ", point)
		if point_nr == amnt_points-1:    #Find vector between the last point on the list and the first point.
			vec1 = corners_temp[0,:] - point
			# print("vec1_A = ", vec1)
		else:
			vec1 = corners_temp[point_nr+1,:] - point
			# print("vec1_B = ", vec1)
		if point_nr == 0:
			vec2 = corners_temp[amnt_points-2,:] - point
		else:
			vec2 = corners_temp[point_nr-1,:] - point
		angle1 = angle(vec1)
		angle2 = angle(vec2)
		angle_delta = angle1 - angle2

		length1 = np.sqrt(vec1.dot(vec1))
		length2 = np.sqrt(vec2.dot(vec2))

		if corner_rad > length1 or corner_rad > length2:
			print("Corner_rad too large")
		
		circ_delta = corner_rad/(np.sin(np.deg2rad(angle_delta/2)))
		corner_center_point = (point[0]+circ_delta*np.cos(np.deg2rad(angle2 + angle_delta/2)), point[1] + circ_delta*np.sin(np.deg2rad(angle2 + angle_delta/2)))

		vec3 = corner_center_point - point
		angle3 = angle(vec3)

		proj3_1 = ((vec3.dot(vec1))/(length1**2))*vec1
		vec4 = proj3_1-vec3
		angle4 = angle(vec4)

		proj3_2 = ((vec3.dot(vec2))/(length2**2))*vec2
		vec5 = proj3_2-vec3
		angle5 = angle(vec5)

		if angle4 > angle5:
			angle4 -= 360

		circ_init_angle = angle5 #ensure initial angle is always larger than final angle in case angle() gives a negative value. Partial circle is then drawn in correct direction (clockwise).
		circ_fin_angle = angle4
		
		# print("vec2 = ", vec2)
		# print("corner_center_point = ",corner_center_point)
		# print("vec3 = ", vec3)
		# print("vec4 = ", vec4)
		# print("vec5 = ", vec5)
		# print("corner_rad = ",corner_rad)
		# print("angle5 = ", angle5)
		# print("angle4 = ", angle4)
		circ=cad.shapes.Circle(corner_center_point, corner_rad, 0,initial_angle=circ_init_angle, final_angle=circ_fin_angle, number_of_points=20, layer=None, datatype=None)

		corners_temp = np.delete(corners_temp,point_nr,0)
		corners_temp = np.insert(corners_temp,point_nr, circ.points, axis=0)

		# Close the loop again if the start/end point was rounded
		if point_nr == 0:
			new_amnt_points = corners_temp.shape[0]
			end_point = corners_temp[0,:]
			corners_temp = np.delete(corners_temp, new_amnt_points-1,0)
			corners_temp = np.vstack([corners_temp, end_point])
	return corners_temp;

class Array(cad.core.Layout): # Parent class for all drum array types.
	def __init__(self, label_separation=15, separation=30, sub_array_separation = 60, array_indicator=None):
		super()
		self.label_separation = label_separation
		self.separation = separation
		self.sub_array_separation = sub_array_separation
		if array_indicator != None:
			self.array_indicator = array_indicator

	def add_to_chip(self, Base_Chip):
		for i in range(len(self.get_dependencies())):
			Base_Chip.add(self.get_dependencies()[i]._objects)

	def translate(self, position):
		for i in range(len(self.get_dependencies())):
			self.get_dependencies()[i].translate(position)
		self.bounding_box()

	def bounding_box(self):
		# Return the smallest rectangle enclosing the drum.
		bb = np.zeros([2,2])
		# if self._bounding_box is not None:
		# 	return self._bounding_box.copy()
		for i in range(len(self.get_dependencies())):
			if i == 0:
				bb[0,0] = self.get_dependencies()[i]._bounding_box[0,0]
				bb[0,1] = self.get_dependencies()[i]._bounding_box[0,1]
				bb[1,0] = self.get_dependencies()[i]._bounding_box[1,0]
				bb[1,1] = self.get_dependencies()[i]._bounding_box[1,1]
			else:
				bb[0,0] = min(self.get_dependencies()[i]._bounding_box[0,0], bb[0,0])
				bb[0,1] = min(self.get_dependencies()[i]._bounding_box[0,1], bb[0,1])
				bb[1,0] = max(self.get_dependencies()[i]._bounding_box[1,0], bb[1,0])
				bb[1,1] = max(self.get_dependencies()[i]._bounding_box[1,1], bb[1,1])

		self._bounding_box = bb

	def add_labl(self, text = "SD4"): # not used.
		self.text = text
		label = cad.shapes.Label(text = self.text, size=200, position = (self._bounding_box[1,0]+50, self._bounding_box[1,1] - 200), horizontal=False, angle=0, layer=None, datatype=None)
		bb = np.zeros([2,2])
		container = cad.core.Cell(name=label)
		for i in range(len(label)):
			character_temp = cad.core.Boundary(label[i].points, layer=1)
			character_temp.name = f"{i}"
			container.add(character_temp)
			
			if i == 0:
				bb[0,0] = label[i].points[:,0].min()
				bb[0,1] = label[i].points[:,1].min()
				bb[1,0] = label[i].points[:,0].max()
				bb[1,1] = label[i].points[:,1].max()
			else:
				bb[0,0] = min(label[i].points[:,0].min(), bb[0,0])
				bb[0,1] = min(label[i].points[:,1].min(), bb[0,1])
				bb[1,0] = max(label[i].points[:,0].max(), bb[1,0])
				bb[1,1] = max(label[i].points[:,1].max(), bb[1,1])
		container._bounding_box = bb
		self.add(container)


		self.bounding_box()

class simple_drum_Array(Array): # Puts drums of type simple_drum with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()

		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = simple_drum(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = simple_drum(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class rounded_drum_Array(Array): # Puts drums of type rounded_drum with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()
		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = rounded_drum(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = rounded_drum(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class rounded_base_drum4_Array(Array): # Puts drums of type rounded_base_drum4 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, corner_rad = 1, nr_of_points = 20, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()
		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = rounded_base_drum4(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=.5, corner_rad = 1, nr_of_points=20)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = rounded_base_drum4(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i],corner_rad = 1, nr_of_points = 20)
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class rounded_base_drum3_Array(Array): # Puts drums of type rounded_base_drum3 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, corner_rad = 1, nr_of_points = 20, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()
		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = rounded_base_drum3(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=.5, corner_rad = 1, nr_of_points=20)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = rounded_base_drum3(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i],corner_rad = .5, nr_of_points = 20)
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class rounded_base_drum5_Array(Array): # Puts drums of type rounded_base_drum5 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, corner_rad = 1, nr_of_points = 20, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()
		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = rounded_base_drum5(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=.5, corner_rad = 1, nr_of_points=20)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = rounded_base_drum5(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i],corner_rad = 1, nr_of_points = 20)
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class simple_drum2_Array(Array): # Puts drums of type simple_drum2 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_length, drum_gaps, tether_widths, tether_length, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()

		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = simple_drum2(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5, drum_length=drum_length, tether_length=10)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = simple_drum2(drum_size=drum_sizes[k], drum_length=drum_length, drum_gap=drum_gaps[j], tether_width=tether_widths[i], tether_length=10)
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class simple_drum3_Array(Array): # Puts drums of type simple_drum3 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()

		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = simple_drum3(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = simple_drum3(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class circular_drum2_Array(Array): # Puts drums of type circular_drum2 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()
		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)

		max_drum = circular_drum2(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=5)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(tether_widths)):
			for j in range(len(drum_gaps)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = circular_drum2(drum_size=drum_sizes[k],drum_gap=drum_gaps[j], tether_width=tether_widths[i])
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-j*(max_height+self.separation)-i*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class circ_gap_drum_Array(Array): # Puts drums of type circ_gap_drum with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self,drum_sizes = [5], tether_widths = [2], numbers_of_tethers = [3,4,5,6,7], array_indicator = None ):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()
		
		sub_array_offset = 0
		for i in range(len(drum_sizes)):
			max_drum_size = drum_sizes[i]
			self.separation = 4*max_drum_size

			max_tether_width = min(tether_widths)
			max_nr_of_tethers = min(numbers_of_tethers)

			max_drum = circ_gap_drum(drum_size=max_drum_size, tether_width=max_tether_width, number_of_tethers=max_nr_of_tethers)
			max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

			bb = max_drum.bounding_box()
			max_width = abs(bb[0,0]-bb[1,0])
			max_height = abs(bb[0,1]-bb[1,1])

			if i != 0:
				sub_array_offset += max_width/2
				self.sub_array_separation = 4*drum_sizes[i-1]
			else:
				self.sub_array_separation = 8*drum_sizes[0]


			sub_array_height = (max_height)*len(tether_widths)+ self.sub_array_separation
			sub_array_width = (max_width)*len(numbers_of_tethers)+ self.sub_array_separation

			

			for j in range(len(tether_widths)):
				for k in range(len(numbers_of_tethers)):
					# name = f"{i}.{j}.{k}"

					# print(name)
					drum_temp = circ_gap_drum(drum_size=drum_sizes[i],tether_width=tether_widths[j], number_of_tethers=numbers_of_tethers[k])
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation) + sub_array_offset,-j*(max_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []

					self.add(drum_temp)
					print("drum_temp",drum_temp)
					print("drum_temp.elements",drum_temp.elements)
			sub_array_offset += sub_array_width
			self.bounding_box()

class diving_board_Array(Array): # Puts drums of type simple_drum2 with a range of parameters in an array. Bounding box of the largest drum is used to determine spacing between drums, such that they dont overlap.
	def __init__(self, drum_sizes, drum_gaps, tether_widths, array_indicator = None, separation=50):
		Array.__init__(self)
		if array_indicator != None:
			self.array_indicator = array_indicator
		else:
			self.array_indicator = " "
		super()

		self.separation = separation

		max_drum_size = max(drum_sizes)
		max_drum_gap = max(drum_gaps)
		max_tether_width = max(tether_widths)

		max_drum = diving_board(drum_size=max_drum_size, drum_gap=max_drum_gap, tether_width=max_tether_width)
		max_drum.add_labl(position = (min(max_drum._bounding_box[:,0]),min(max_drum._bounding_box[:,1])-self.label_separation))

		bb = max_drum.bounding_box()
		max_width = abs(bb[0,0]-bb[1,0])
		max_height = abs(bb[0,1]-bb[1,1])
		sub_array_height = (max_height+self.sub_array_separation)*len(drum_gaps)


		for i in range(len(drum_gaps)):
			for j in range(len(tether_widths)):
				for k in range(len(drum_sizes)):
					# name = f"{i}.{j}.{k}"
					# print(name)
					drum_temp = diving_board(drum_size=drum_sizes[k], drum_gap=drum_gaps[i], tether_width=tether_widths[j])
					# drum_temp.name=name


					# print(drum_temp._objects)
					drum_temp.translate(position=[k*(max_width+self.separation),-i*(max_height+self.separation)-j*(sub_array_height+self.separation)])
					drum_temp.add_labl(position = (min(drum_temp._bounding_box[:,0]),min(drum_temp._bounding_box[:,1])-self.label_separation), array_indicator=self.array_indicator)
					# print(drum_temp._objects[:])
					drum_temp._references = []
					self.add(drum_temp)
		self.bounding_box()

class circuit_drum(SuspendedDrum):
	def __init__(self, drum = None, oversize = 80, lead_length = 100, lead_width = 20, cut_out_height = 150, cut_out_width = 150):
		super()
		self._objects=[]
		self._references = []
		self._bounding_box = None
		
		# drum_bb = drum.bounding_box()
		# drum_size = bb[1][0]bb[0][0]
		min_gap = 20
		if drum == None:
			drum_size = 30

		drum_bb = drum.bounding_box()
		# print(drum_bb)
		drum_size = max(abs(drum_bb[0][0] - drum_bb[1][0]),abs(drum_bb[0][1] - drum_bb[1][1]))
		disk_radius = drum_size/2 + oversize
		if cut_out_height < 2*disk_radius +2*min_gap:
			cut_out_height = 2*disk_radius +2*min_gap
			print("cut_out_height too small, increased to accomodate drum")

		if cut_out_width < lead_length + 2*disk_radius + min_gap:
			cut_out_width = lead_length + 2*disk_radius + min_gap
			print("cut_out_width too small, increased to accomodate drum")
		self.name = f"{oversize}, {lead_length}, {lead_width}, {round(cut_out_height,1)},{round(cut_out_width,1)} "
		alpha = np.rad2deg(np.arcsin((lead_width/2)/disk_radius))

		# disk_offset = lead_length + self.drum.bounding_box()/2 + self.oversize
		disk_offset = lead_length + drum_size/2 + oversize
		platform = cad.shapes.Disk(center = (0,0),radius = disk_radius,initial_angle=-180+alpha,final_angle=180-alpha, number_of_points=100)
		# print(platform.points)
		disk_end = platform.points[0]
		cut_out_points = np.delete(np.flip(platform.points,0), 0, 0)
		disk_start = cut_out_points[0]

		#	Adding points to create cut-out around drum.
		next_point_temp = disk_end + [-lead_length,0]
		cut_out_points = np.vstack([cut_out_points, next_point_temp])
		next_point_temp = next_point_temp + [0,-((cut_out_height-lead_width)/2)]
		cut_out_points = np.vstack([cut_out_points, next_point_temp])
		next_point_temp = next_point_temp + [cut_out_width,0]
		cut_out_points = np.vstack([cut_out_points, next_point_temp])
		next_point_temp = next_point_temp + [0,cut_out_height]
		cut_out_points = np.vstack([cut_out_points, next_point_temp])
		next_point_temp = next_point_temp + [-cut_out_width,0]
		cut_out_points = np.vstack([cut_out_points, next_point_temp])
		next_point_temp = next_point_temp + [0,-((cut_out_height-lead_width)/2)]
		cut_out_points = np.vstack([cut_out_points, next_point_temp])
		cut_out_points = np.vstack([cut_out_points, cut_out_points[0]])
		
		# Creating boundary from new point list
		cut_out = cad.core.Boundary(cut_out_points)
		# print(cut_out_points[len(cut_out_points)-2])
		drum.translate(-cut_out_points[len(cut_out_points)-2])
		cut_out.translate(-cut_out_points[len(cut_out_points)-2])
		# print(drum.bounding_box())

		self.add(cut_out)
		self.add(drum.elements)
		self.bounding_box()
		self.add_labl(position = (min(self._bounding_box[:,0]),min(self._bounding_box[:,1])-20))
		self.bounding_box()
		# print(self)
		# print(cut_out_points)

	def get_details(self):
		return "drum_size = %s, drum_gap = %s, tether_width =  %s." % (self.drum_size, self.drum_gap, self.tether_width)

	def bounding_box(self):
		# Return the smallest rectangle enclosing the drum.
		bb = np.zeros([2,2])
		# if self._bounding_box is not None:
		# 	return self._bounding_box.copy()
		for i in range(len(self._objects)):
			if i == 0:
				bb[0,0] = self._objects[i]._points[:,0].min()
				bb[0,1] = self._objects[i]._points[:,1].min()
				bb[1,0] = self._objects[i]._points[:,0].max()
				bb[1,1] = self._objects[i]._points[:,1].max()
			else:
				bb[0,0] = min(self._objects[i]._points[:,0].min(), bb[0,0])
				bb[0,1] = min(self._objects[i]._points[:,1].min(), bb[0,1])
				bb[1,0] = max(self._objects[i]._points[:,0].max(), bb[1,0])
				bb[1,1] = max(self._objects[i]._points[:,1].max(), bb[1,1])

		self._bounding_box = bb
		return bb

	def translate(self, position):
		# Translates the center of the drum from its original position (0,0) by the vector 'position'
		
		for i in range(len(self._objects)):
			self._objects[i].points = cad.utils.translate(self._objects[i].points, position)
		self.bounding_box()

	def add_to_chip(self, Base_Chip):
		Base_Chip.add(self._objects)

	def add_labl(self, position = (0,0), array_indicator = None):
		if array_indicator != None:
			self.name += array_indicator
		label = cad.shapes.Label(text = self.name, size=3, position = position, horizontal=True, angle=0, layer=None, datatype=None)
		for i in range(len(label)):
			self.add(cad.core.Boundary(label[i].points, layer=1))
		self.bounding_box()

class MyLabel(cad.core.Cell):
	def __init__(self, text):
		super()







