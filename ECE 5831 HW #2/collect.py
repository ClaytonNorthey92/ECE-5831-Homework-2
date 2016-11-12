# Script can be run to extract data from face database
# this file must be in the same directroy as the orl_faces 
# directory extracted from the compressed files
import copy

FACES_DIR = 'orl_faces'

# takes in the conent of a file and returns information about the 
# file according to PGM spec

class Face:
	magic_number = None
	dimensions = None
	max_val = None
	content = None
	parsed_content = None

	def __init__(self, content):
		parts = content.split('\n')
		self.magic_number = parts[0]
		self.dimensions = parts[1].split(' ')
		self.max_val = parts[2]
		self.content = parts[3]
		self._set_content()

	def get_dimensions(self):
		return [int(d) for d in self.dimensions]

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

if __name__=='__main__':
	faces = {}
	for dir_i in range(1, 41):
		faces_tmp = []
		for file_i in range(1, 11):
			f = open('{}/s{}/{}.pgm'.format(FACES_DIR, dir_i, file_i), 'rb')
			file_content = f.read()
			f.close()
			this_face = Face(file_content)
			faces_tmp.append(this_face)
		faces[dir_i] = copy.copy(faces_tmp)
	print(faces)
