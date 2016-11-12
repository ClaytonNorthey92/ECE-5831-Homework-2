# Script can be run to extract data from face database
# this file must be in the same directroy as the orl_faces 
# directory extracted from the compressed files
import copy

FACES_DIR = 'orl_faces'
META_BYTES = 14
DIMENSIONS = [92, 112]
# takes in the conent of a file and returns information about the 
# file according to PGM spec

class Face:
	magic_number = None
	dimensions = None
	max_val = None
	content = None
	parsed_content = None

	def __init__(self, content):
		self.dimensions = DIMENSIONS
		self.content = content[META_BYTES:]
		self._set_content()

	def get_dimensions(self):
		return self.dimensions

	def _set_content(self):
		columns = self.get_dimensions()[1]
		content_tmp = copy.copy(self.content)
		output_matrix = []
		while content_tmp:
			output_matrix.append([ord(c) for c in content_tmp[:columns]])
			content_tmp = content_tmp[columns:]
		self.parsed_content = output_matrix

	def get_content(self):
		return self.parsed_content


# gets the average face give a list of faces (get's avg per person - 10 images) 
def get_average_face(faces):
	num_faces = float(len(faces))
	face_content = [f.get_content() for f in faces]
	dimensions = faces[0].get_dimensions()
	avg_face = [[0.0]*dimensions[1]]*dimensions[0]
	for r_index, row in enumerate(avg_face):
		for c_index, column in enumerate(row):
			avg_face[r_index][c_index] = sum(f[r_index][c_index] for f in face_content)/num_faces
	return avg_face


# gets avg of all 40 avg faces
def get_avg_array(num_images): 
	list_len = len(num_images)
	avg_face = [[0.0]*DIMENSIONS[1]]*DIMENSIONS[0]
	for r_index, row in enumerate(avg_face):
		for c_index, column in enumerate(row):
			avg_face[r_index][c_index] = sum(f[r_index][c_index] for f in num_images)/list_len
	return avg_face

def get_distance_per_average(total_avg, face_avg):
	distance_face = [[0.0]*DIMENSIONS[1]]*DIMENSIONS[0]
	for r_index, row in enumerate(distance_face):
		for c_index, column in enumerate(row):
			distance_face[r_index][c_index] = face_avg[r_index][c_index] - total_avg[r_index][c_index]
	return distance_face

if __name__=='__main__':
	faces = {}
	avg_faces = {}
	distance_faces = {}
	for dir_i in range(1, 41):
		faces_tmp = []
		for file_i in range(1, 11):
			f = open('{}/s{}/{}.pgm'.format(FACES_DIR, dir_i, file_i), 'rb')
			file_content = f.read()
			f.close()
			this_face = Face(file_content)
			faces_tmp.append(this_face)
		faces[dir_i] = copy.copy(faces_tmp)
		avg_faces[dir_i] = get_average_face(faces[dir_i])
	tot_avg = get_avg_array([avg_faces[i] for i in range(1,11)])
	for i in range(1,41):
		distance_faces[i] = get_distance_per_average(tot_avg, avg_faces[i])
	print(distance_faces[1][0])









