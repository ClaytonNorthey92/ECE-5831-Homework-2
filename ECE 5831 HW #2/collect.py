# Script can be run to extract data from face database
# this file must be in the same directroy as the orl_faces 
# directory extracted from the compressed files
import copy
import numpy
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
		self.parsed_content = numpy.matrix(output_matrix)

	def get_content(self):
		return self.parsed_content


# gets the average face give a list of faces (get's avg per person - 10 images) 
def get_average_face(faces, use_class=True):
	num_faces = float(len(faces))
	face_content = None
	if use_class:
		face_content = [f.get_content() for f in faces]
	else:
		face_content = faces
	avg_face = sum(face_content)/len(face_content)
	return avg_face
	

def get_distance_per_average(total_avg, face_avg):
	return face_avg - total_avg


# assumes faces is a list of matrixes
# for every face, Fi, Cij = (Fi-u)(Fj-u)
def get_covariance(faces, avg_face):
	covs = [numpy.cov(face) for face in faces]
	return sum(covs)/len(faces)

def project_face():
	#to-do
	pass

if __name__=='__main__':
	faces = {}
	avg_faces = []
	distance_faces = []
	all_faces = []
	for dir_i in range(1, 41):
		faces_tmp = []
		for file_i in range(1, 11):
			f = open('{}/s{}/{}.pgm'.format(FACES_DIR, dir_i, file_i), 'rb')
			file_content = f.read()
			f.close()
			this_face = Face(file_content)
			faces_tmp.append(this_face)
			all_faces.append(this_face)
		faces[dir_i] = copy.copy(faces_tmp)
		avg_faces.append(get_average_face(faces[dir_i]))
	total_avg = get_average_face(avg_faces, use_class=False)
	for face in avg_faces:
		distance_faces.append(get_distance_per_average(total_avg, face))
	faces_covariance = get_covariance(distance_faces, total_avg)
	eigen_values, eigen_vectors = numpy.linalg.eig(faces_covariance)

	project_face()
