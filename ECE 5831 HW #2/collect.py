# Script can be run to extract data from face database
# this file must be in the same directroy as the orl_faces 
# directory extracted from the compressed files
import copy
import numpy
import datetime
FACES_DIR = 'orl_faces'
META_BYTES = 14
DIMENSIONS = [92, 112]
# takes in the conent of a file and returns information about the 
# file according to PGM spec

# Face class
# constructor takes in contents of the PGM file and 
# creates an instance of a Face
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


# gets the average face given a list of faces (get's avg per person - 10 images) 
# if the use_class variable is True, then it assumes a list of classes is passed in as faces
# if the use_class variable is False then it assumes a list of face content is pass in as faces
def get_average_face(faces, use_class=True):
	num_faces = float(len(faces))
	face_content = None
	if use_class:
		face_content = [f.get_content() for f in faces]
	else:
		face_content = faces
	avg_face = sum(face_content)/len(face_content)
	return avg_face
	

# returns the difference between total_avg face matrix and another face martrix
# in matrix form
def get_distance_per_average(total_avg, face_avg):
	return face_avg - total_avg


# returns the covariance of a list of faces
def get_covariance(faces):
	covs = [numpy.cov(face) for face in faces]
	return sum(covs)/len(faces)

# compresses the a list of faces based on eigen vectors
# the result is a 40x40 matrix of 1x112 matrices
def reconstruct_face(top_eigen_vectors, distance_faces):
	d_length = len(distance_faces)
	t_length = len(top_eigen_vectors)
	new_face = [[None]*d_length for x in range(t_length)]
	for i in range(d_length):
		for j in range(t_length):
			new_face[j][i] = top_eigen_vectors[j].transpose()*distance_faces[i]

	return new_face


# returns a list of all 400 faces in compressed format
# each face is 40x1 with all elements 1x112
def get_some_original_face(total_avg):
	faces = []
	for i in range(1,41):
		for j in range(1,11):
			f = open('{}/s{}/{}.pgm'.format(FACES_DIR, i, j), 'rb')
			file_content = f.read()
			f.close()
			this_face = Face(file_content)
			distance_face = get_distance_per_average(total_avg, this_face.get_content())
			face_covariance = get_covariance([distance_face])
			eigen_values, eigen_vectors = numpy.linalg.eig(face_covariance)
			top_eigen_vectors[:40]
			new_face = reconstruct_face(top_eigen_vectors, [distance_face])
			faces.append(new_face)
	return faces

if __name__=='__main__':
	# start timer for runtime analysis
	start = datetime.datetime.now()
	faces = {}
	avg_faces = []
	distance_faces = []
	all_faces = []

	# gather average faces since there are 400 images of 40 people, there
	# are 10 images of each person, we average these and store them
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

	# compute distance faces, this is the difference between each
	# average face and the mean of all faces
	for face in avg_faces:
		distance_faces.append(get_distance_per_average(total_avg, face))

	# get the covariance of the faces
	faces_covariance = get_covariance(distance_faces)
	
	# get the eigen_vectors, we take the top M, which we set to 40
	eigen_values, eigen_vectors = numpy.linalg.eig(faces_covariance)
	top_eigen_vectors = eigen_vectors[:40]

	# create out 40x40 matrix of 1x112 matrices that store a compressed
	# version of the distance between each face and the mean
	new_face = reconstruct_face(top_eigen_vectors, distance_faces)
	correct_faces = 0
	incorrect_faces = 0
	stored_faces = []

	# convert columns to rows for comparison of out compressed
	# distance faces
	for i in range(40):
		stored_faces.append([new_face[j][i] for j in range(40)])


	# for every of the 400 faces, we atttempt to classify each one, then
	# we record what we classify it as and what it should have been classified as
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
	
	# print out our results, what we classify as, what we should have classified as,
	# number of correct results, number of incorrect results, and the percentage correct,
	# and the runtime
	correct = 0
	incorrect = 0
	for key in classifed:
		expected = key/10
		if expected == classifed[key]:
			correct += 1
		else:
			incorrect += 1
		print "Classified {} as {}, expected {}".format(key, classifed[key], expected)
	print "{} correct, {} incorrect, which is a success rate of {}%".format(correct, incorrect, float(correct)/float(correct+incorrect) * 100)
	diff_time = datetime.datetime.now() - start
	print "runtime {}".format(diff_time)

