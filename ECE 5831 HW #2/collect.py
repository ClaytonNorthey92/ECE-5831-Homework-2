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

def reconstruct_face(top_eigein_vectors, distance_faces):
	new_face = [[None]*len(distance_faces) for x in range(len(top_eigein_vectors))]
	for i in range(len(distance_faces)):
		for j in range(len(top_eigein_vectors)):
			new_face[j][i] = top_eigein_vectors[j].transpose()*distance_faces[i]

	return new_face


def get_some_original_face(total_avg):
	faces = []
	for i in range(1,41):
		for j in range(1,11):
			f = open('{}/s{}/{}.pgm'.format(FACES_DIR, i, j), 'rb')
			file_content = f.read()
			f.close()
			this_face = Face(file_content)
			distance_face = get_distance_per_average(total_avg, this_face.get_content())
			face_covariance = get_covariance([distance_face], total_avg)
			eigen_values, eigen_vectors = numpy.linalg.eig(face_covariance)
			top_eigein_vectors[:40]
			new_face = reconstruct_face(top_eigein_vectors, [distance_face])
			faces.append(new_face)
	return faces
# To find corresponding face, funnel the error distances into a 1x40 array
# Do a minnimum of the the array, return min index


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

	top_eigein_vectors = eigen_vectors[:40]

	new_face = reconstruct_face(top_eigein_vectors, distance_faces)
	correct_faces = 0
	incorrect_faces = 0
	stored_faces = []
	for i in range(40):
		stored_faces.append([new_face[j][i] for j in range(40)])
	classifed = {}
	for f_index, face in enumerate(get_some_original_face(total_avg)):
		current_face = f_index / 10
		this_face = [element[0] for element in face]
		errors = {}
		for i in range(len(stored_faces)):
			diff = abs(numpy.array(this_face) - numpy.array(stored_faces[i]))
			if i not in errors:
				errors[i] = 0
			errors[i] += numpy.sum(diff)
		min_error = None
		min_key = None
		for key in errors:
			if not min_error or errors[key] < min_error:
				min_error = errors[key]
				min_key = key
		classifed[f_index] = min_key
	correct = 0
	incorrect = 0
	for key in classifed:
		expected = key/10
		if expected == classifed[key]:
			correct += 1
		else:
			incorrect += 1
		print "Classified {} as {}, expected {}".format(key, classifed[key], expected)
	print "{} correct, {} incorrect".format(correct, incorrect)

