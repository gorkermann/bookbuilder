import os
import re
import sys
import argparse

RE_CHAPTER_SEPARATOR = re.compile('//(.*)')

class Chapter:
	def __init__(self, prefix, name, text):
		if not name:
			raise Exception('Chapter name cannot be empty')

		if text is None:
			raise Exception('Chapter text cannot be None')

		self.prefix = prefix.strip()
		self.name = name.strip()	# name of this chapter
		self.text = text		# text of chapter, one big string
		self.id = self.prefix + '_' + self.name
	
	def get_info_string(self):
		snippet = ''
		snippet_length = 20
		info_string = ''

		if len(self.text) < snippet_length:
			snippet = self.text
		else:
			snippet = self.text[:snippet_length]

		info_string = self.id + ' \"' + snippet + '...\"'
		info_string += ' (' + str(self.get_word_count()) + ')'
		
		return info_string

	def get_word_count(self):
	
		# approximate word count by number of spaces and non-empty lines
		space_count = self.text.count(' ')

		line_count = len(filter(lambda x: len(x) > 0, self.text.splitlines(False)))

		return space_count + line_count

class ChapterBatch:
	def __init__(self):
		self.chapters = {}		# dict of Chapters, keyed on chapter.id

		self.verbose = True
	"""		
		read_file

		prefix: prefix which will be prepended to all input chapters
		filename: name of text file

		prefix: charon
		base name of chapter: river
		resulting name: charon_river	
	"""
	def read_in_text_file(self, prefix, filename):

		if self.verbose:
			print('')

		text_file = open(filename)
		if not text_file:
			raise Exception('File not found: ' + filename)

		if self.verbose:
			print(filename)
			bar = '-' * len(filename)
			print(bar)

		current_chapter = None
		chapter_count = 0

		for line in text_file:

			match = RE_CHAPTER_SEPARATOR.match(line)

			# new chapter or first chapter
			if match is not None or current_chapter is None:
				if current_chapter is not None:
					self.add_chapter(current_chapter)

				# make a new chapter
				chapter_count += 1
				chapter_name = str(chapter_count)

				# grab the part after the '//'
				if match is not None and len(match.group(1)) > 0:
					chapter_name = match.group(1).strip()

				current_chapter = Chapter(prefix, chapter_name, '')

			# regular line, add it to the current chapter
			if match is None:
				current_chapter.text += line

		# add last chapter to list
		if current_chapter is not None:
			self.add_chapter(current_chapter)

	def add_chapter(self, chapter):

		# chapter ids must be unique
		if chapter.id in self.chapters:
			raise Exception('Multiple chapters named %s' % (chapter.id))

		if self.verbose:
			print(chapter.get_info_string())

		self.chapters[chapter.id] = chapter

if __name__ == '__main__':

	# Check arguments
	if len(sys.argv) < 3:
	    print('Usage: bookbuilder.py [chapter structure file] [output file] [chapter batch 1] [chapter batch 2] ...')
	    exit()

	#
	# read in chapters
	#
	num_batches = len(sys.argv) - 3
	batch_filenames = {}
	chapter_batch = ChapterBatch()

	for i in range(num_batches):
		batch_filename = sys.argv[3 + i]

		if batch_filename in batch_filenames:
			raise Exception('Duplicate chapter batch %s' % (batch_filename))
		batch_filenames[batch_filename] = True

		prefix = os.path.splitext(batch_filename)[0]
		chapter_batch.read_in_text_file(prefix, batch_filename)

	#
	# build book
	#
	structure_file = open(sys.argv[1])
	output_file = open(sys.argv[2], 'w')
	output_section_names = {}	# keyed on chapter_name
	output_chapters = []		# list of Chapters
	last_prefix = None
	current_chapter = None

	for line in structure_file:
		chapter_name = line.strip()

		# empty line forces a new chapter
		if not len(chapter_name):
			current_chapter = None
			last_prefix = None
			continue

		# check for duplicate chapters
		if chapter_name in output_section_names:
			raise Exception('Duplicate chapter name %s' % (chapter_name))
		output_section_names[chapter_name] = True

		# check that chapter exists
		if chapter_name not in chapter_batch.chapters:
			raise Exception('Chapter not found: %s' % (chapter_name))

		# make a new chapter if there is none, or on a new prefix
		section = chapter_batch.chapters[chapter_name]
		if current_chapter is None or section.prefix != last_prefix:			
			current_chapter = Chapter(section.prefix, section.name, section.text)
			output_chapters.append(current_chapter)

		# add text to current chapter
		else:
			current_chapter.text += section.text
			
		last_prefix = section.prefix		
		
	# write to file
	for i, chapter in enumerate(output_chapters):
		chapter_number = str(i + 1)
		output_file.write('CHAPTER ' + chapter_number + '\n\n')
		output_file.write(chapter.text)
		
	output_file.close()

	# check for unused chapters
	missing_chapter_names = []

	for chapter_name in chapter_batch.chapters:
		if chapter_name not in output_section_names:
			missing_chapter_names.append(chapter_name)

	#
	# print info about output file
	#
	if True:
		print('\nOUTPUT: ' + sys.argv[2])
		with open(sys.argv[2]) as output_file:
			output = Chapter('output', 'full', output_file.read())
			
			print(output.get_info_string())
			
		for chapter in output_chapters:
			partial_id = chapter.id[:20]
			partial_id += ' ' * (20 - len(partial_id))
			
			print(partial_id + ' ' + str(chapter.get_word_count()))

		if missing_chapter_names:
			print('\nMissing Chapters:')
			for chapter_name in missing_chapter_names:
				print(chapter_name)
		
