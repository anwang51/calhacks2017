# Magenta code and RNN provided by 
# Ian Simon and Sageev Oore. "Performance RNN: Generating Music with Expressive
# Timing and Dynamics." Magenta Blog, 2017.
# https://magenta.tensorflow.org/performance-rnn
from magenta.music import midi_synth
import IPython
import settings
import os
import sys
from magenta.models.performance_rnn import performance_sequence_generator
from magenta.protobuf import generator_pb2
from magenta.protobuf import music_pb2
import numpy as np
from scipy.io.wavfile import write
import magenta.music as mm
from magenta.music import midi_io
import time
import threading
from playsound import playsound as ps

# Constants.
DEFAULT_SAMPLE_RATE = 44100
SAMPLE_MULT = 1
DURATION = 2.5
# TEMP = 0.3
SLEEP_TIME = 1 * SAMPLE_MULT * DURATION
BUNDLE_DIR = '/Users/wangan/Documents/calhacks2017/magenta/'
MODEL_NAME = 'multiconditioned_performance_with_dynamics'
BUNDLE_NAME = MODEL_NAME + '.mag'
PLAYING_MUSIC1 = False
PLAYING_MUSIC2 = False
SF2_DIR =  '/Users/wangan/Documents/calhacks2017/audio/'
SF2_FILE = "violin.sf2"
SF2_PATH = SF2_DIR + SF2_FILE
REDUCTION = 2
FRACTION = 0.75
settings.init()

def alternate_keys():
	global PLAYING_MUSIC1
	global PLAYING_MUSIC2
	while True:
		PLAYING_MUSIC2 = False
		PLAYING_MUSIC1 = True
		time.sleep(SLEEP_TIME)
		PLAYING_MUSIC1 = False
		PLAYING_MUSIC2 = True
		time.sleep(SLEEP_TIME)

def play_music1():
	global PLAYING_MUSIC1
	while True:
		while not PLAYING_MUSIC1:
			time.sleep(0.00001)
		ps.playsound("/Users/wangan/Documents/calhacks2017/temp_wav/tempViolin1.wav")
		# PLAYING_MUSIC1 = False
		# PLAYING_MUSIC2 = True

def play_music2():
	global PLAYING_MUSIC2
	while True:
		while not PLAYING_MUSIC2:
			time.sleep(0.00001)
		ps.playsound("/Users/wangan/Documents/calhacks2017/temp_wav/tempViolin2.wav")
		# PLAYING_MUSIC2 = False
		# PLAYING_MUSIC1 = True

def generate_music():
	global PLAYING_MUSIC1
	global PLAYING_MUSIC2
	mm.musicxml_parser.DEFAULT_MIDI_PROGRAM = 3
	mm.notebook_utils.download_bundle(BUNDLE_NAME, BUNDLE_DIR)
	bundle = mm.sequence_generator_bundle.read_bundle_file(os.path.join(BUNDLE_DIR, BUNDLE_NAME))
	generator_map = performance_sequence_generator.get_generator_map()
	generator = generator_map[MODEL_NAME](checkpoint=None, bundle=bundle)
	generator.initialize()
	generator_options = generator_pb2.GeneratorOptions()
	generator_options.args['temperature'].float_value = settings.TEMP # Higher is more random; 1.0 is default. 
	generate_section = generator_options.generate_sections.add(start_time=0, end_time=DURATION)
	sequence = generator.generate(music_pb2.NoteSequence(), generator_options)

	# Play and view this masterpiece.
	# mm.plot_sequence(sequence)
	# audio_object = modified_play_sequence(sequence, mm.midi_synth.fluidsynth, sample_rate=DEFAULT_SAMPLE_RATE * SAMPLE_MULT)
	# mm.play_sequence(sequence, mm.midi_synth.fluidsynth, sample_rate=DEFAULT_SAMPLE_RATE * SAMPLE_MULT)

	sample_rate=DEFAULT_SAMPLE_RATE * SAMPLE_MULT
	array_of_floats = mm.midi_synth.fluidsynth(sequence, sample_rate=sample_rate, sf2_path=SF2_PATH)
	write('/Users/wangan/Documents/calhacks2017/temp_wav/tempViolin1.wav', 44100, array_of_floats)
	# audio_killed = int(sample_rate * 1)
	# array_of_floats = array_of_floats[audio_killed:]

	# IPython.display.Audio(array_of_floats, rate=sample_rate, autoplay=True)

	i = 1
	while(True):
		print("Size of NoteSequence: ", sys.getsizeof(sequence))
		performance_sequence_generator.DEFAULT_NOTE_DENSITY = settings.NOTE_DENSITY / REDUCTION
		performance_sequence_generator.DEFAULT_PITCH_HISTOGRAM = settings.PITCH
		while PLAYING_MUSIC1:
			time.sleep(0.00001)
		array_of_floats = []
		generator_map2 = performance_sequence_generator.get_generator_map()
		generator2 = generator_map2[MODEL_NAME](checkpoint=None, bundle=bundle)
		generator2.initialize()
		generator_options2 = generator_pb2.GeneratorOptions()
		generator_options2.args['temperature'].float_value = settings.TEMP  # Higher is more random; 1.0 is default. 
		generate_section = generator_options2.generate_sections.add(start_time=(i*DURATION), end_time=(i+1)*DURATION)
		sequenceNew = generator2.generate(sequence, generator_options2)

		# Play and view this masterpiece.
		mm.plot_sequence(sequenceNew)
		# audio_object = modified_play_sequence(sequence, mm.midi_synth.fluidsynth, sample_rate=DEFAULT_SAMPLE_RATE * SAMPLE_MULT)
		# mm.play_sequence(sequence, mm.midi_synth.fluidsynth, sample_rate=DEFAULT_SAMPLE_RATE * SAMPLE_MULT)

		sample_rate= DEFAULT_SAMPLE_RATE * SAMPLE_MULT
		array_of_floats = mm.midi_synth.fluidsynth(sequenceNew, sample_rate=sample_rate, sf2_path=SF2_PATH)
		sequence = sequenceNew
		sequence.notes._values = sequence.notes._values[int(FRACTION * len(sequence.notes)):len(sequence.notes)]

		# audio_killed = int(sample_rate * 1.5)
		old_array_size = int(sample_rate * DURATION * i)
		array_of_floats = array_of_floats[old_array_size:]
		# array_of_floats = array_of_floats[:-audio_killed]
		write('/Users/wangan/Documents/calhacks2017/temp_wav/tempViolin1.wav', 44100, array_of_floats)
		del generator_map2
		del generator2
		del generator_options2
		del generate_section
		del sequenceNew
		i += 1

		performance_sequence_generator.DEFAULT_NOTE_DENSITY = settings.NOTE_DENSITY / REDUCTION
		performance_sequence_generator.DEFAULT_PITCH_HISTOGRAM = settings.PITCH
		while PLAYING_MUSIC2:
			time.sleep(0.00001)
		array_of_floats2 = []
		generator_map2 = performance_sequence_generator.get_generator_map()
		generator2 = generator_map2[MODEL_NAME](checkpoint=None, bundle=bundle)
		generator2.initialize()
		generator_options2 = generator_pb2.GeneratorOptions()
		generator_options2.args['temperature'].float_value = settings.TEMP  # Higher is more random; 1.0 is default. 
		generate_section = generator_options2.generate_sections.add(start_time=(i*DURATION), end_time=(i+1)*DURATION)
		sequenceNew = generator2.generate(sequence, generator_options2)

		sample_rate= DEFAULT_SAMPLE_RATE * SAMPLE_MULT
		array_of_floats2 = mm.midi_synth.fluidsynth(sequenceNew, sample_rate=sample_rate, sf2_path=SF2_PATH)
		sequence = sequenceNew
		sequence.notes._values = sequence.notes._values[int(FRACTION * len(sequence.notes)):len(sequence.notes)]


		# audio_killed = int(sample_rate * 1.5)
		old_array_size = int(sample_rate * DURATION * i)
		array_of_floats2 = array_of_floats2[old_array_size:]
		# array_of_floats = array_of_floats[:-audio_killed]

		write('/Users/wangan/Documents/calhacks2017/temp_wav/tempViolin2.wav', 44100, array_of_floats2)
		del generator_map2
		del generator2
		del generator_options2
		del generate_section
		del sequenceNew
		i += 1
	#     array_of_floats = array_of_floats[audio_killed:]

		# *********** IMPORTANT ************
		# music_thread = threading.Thread(target=play_music, args=[array_of_floats], name="temp")
		# music_thread.run()


	#     play_music(array_of_floats)

def run():
	generateThread = threading.Thread(target=generate_music)
	generateThread.start()
	playThread1 = threading.Thread(target=play_music1)
	playThread1.start()
	playThread2 = threading.Thread(target=play_music2)
	playThread2.start()
	time.sleep(3)
	alternating = threading.Thread(target=alternate_keys)
	alternating.start()
