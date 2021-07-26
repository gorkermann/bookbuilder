import os
import re
import sys
import argparse

RE_CHAPTER_SEPARATOR = re.compile('//(.*)')

def log(line):
	with open('log.txt', 'a') as logfile:
		logfile.write(line + '\n')

	print(line)

class Chapter:
	def __init__(self, name, text):
		if not name:
			raise Exception('Chapter name cannot be empty')

		if text is None:
			raise Exception('Chapter text cannot be None')

		self.name = name.strip()	# name of this chapter
		self.text = text			# text of chapter, one big string

	def wordcount(self):
		lines = self.text.split('\n')

		result = 0

		for line in lines:
			if not line:
				continue

			if len(line) > 1 and line[:2] == '//':
				continue

			result += line.count(' ') + 1

		return result

class ChapterBatch:
	def __init__(self):
		self.chapters = {}		# dict of Chapters, keyed on chapter.name

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
			log('')

		text_file = open(filename)
		if not text_file:
			raise Exception('File not found: ' + filename)

		if self.verbose:
			log(filename)
			bar = '-' * len(filename)
			log(bar)

		current_chapter = None
		chapter_count = 0
		in_italics = False

		for line in text_file:

			match = RE_CHAPTER_SEPARATOR.match(line)

			# new chapter or first chapter
			if match is not None or current_chapter is None:
				if current_chapter is not None:
					self.add_chapter(current_chapter)

				# make a new chapter
				chapter_count += 1
				chapter_name = prefix + '_' + str(chapter_count)

				if match is not None and len(match.group(1)) > 0:
					chapter_name = prefix + '_' + match.group(1).strip()

				current_chapter = Chapter(chapter_name, '')

			# regular line, add it to the current chapter
			if match is None:
				line = line.strip()

				if len(line) > 0:
					line = '\t' + line

				old_line = ''
				while True:
					old_line = line

					if not in_italics:
						line = line.replace('*', '\n\\i\n', 1)
						if line == old_line:
							break
							
						in_italics = True
					else:
						line = line.replace('*', '\n\\i0\n', 1)
						if line == old_line:
							break

						in_italics = False

				line = line + '\\line\n' # .rtf line ending is \line

				current_chapter.text += line

		# add last chapter to list
		if current_chapter is not None:
			self.add_chapter(current_chapter)

	def add_chapter(self, chapter):

		# chapter names must be unique
		if chapter.name in self.chapters:
			raise Exception('Multiple chapters named %s' % (chapter.name))

		if self.verbose:
			snippet = ''
			snippet_length = 20
			info_string = ''

			if len(chapter.text) < snippet_length:
				snippet = chapter.text
			else:
				snippet = chapter.text[:snippet_length]

			info_string = chapter.name + ' \"' + snippet + '...\"'

			# approximate word count by number of spaces
			info_string += ' (' + str(chapter.wordcount()) + ')'
			log(info_string)

		self.chapters[chapter.name] = chapter

	def wordcount(self):
		total = 0

		for chapter_name in self.chapters:
			total += self.chapters[chapter_name].wordcount()

		return total

# Check arguments
if len(sys.argv) < 3:
    print('Usage: bookbuilder.py [chapter structure file] [output file] [chapter batch 1] [chapter batch 2] ...')
    exit()

# clear log file
with open('log.txt', 'w') as logfile:
	pass

# read in chapter batches (one batch per POV character)
batch_filenames = {}
chapter_batch = ChapterBatch()
prev_wordcount = 0
filenames = sys.argv[3:]

for filename in filenames:

	if filename in batch_filenames:
		raise Exception('Duplicate chapter batch %s' % (filename))
	batch_filenames[filename] = True

	prefix = os.path.splitext(filename)[0]
	chapter_batch.read_in_text_file(prefix, filename)

	log('Total: %d' % (chapter_batch.wordcount() - prev_wordcount))
	prev_wordcount = chapter_batch.wordcount()

# output chapters
structure_file = open(sys.argv[1])
output_file = open(sys.argv[2], 'w')
all_chapter_names = {}
total_wordcount = 0

# build book
output_file.write('{\\rtf1\\ansi\\deff0\n') # start of .rtf file

for i, line in enumerate(structure_file):
	line = line.strip()
	words = line.split(' ')
	label = 'CHAPTER %d' % (i + 1)

	if len(words) < 1:
		continue

	chapter_name = words[0]

	if len(words) >= 2:
		label += ' (' + words[1] + ')'	  

	# check for duplicate chapters
	if chapter_name in all_chapter_names:
		raise Exception('Duplicate chapter name %s' % (chapter_name))
	all_chapter_names[chapter_name] = True

	# check that chapter exists
	if chapter_name not in chapter_batch.chapters:
		raise Exception('Chapter not found: %s' % (chapter_name))

	# add text to output
	output_file.write(label + '\\line\n')
	output_file.write('\\line\n')
	output_file.write(chapter_batch.chapters[chapter_name].text)
	total_wordcount += chapter_batch.chapters[chapter_name].wordcount()

	log(label + ' ' + chapter_name)

output_file.write('}\n') # end of .rtf file

log('')
log('Overall Total: %d' % total_wordcount)
