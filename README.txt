decoupled_matrix_builder.py implements the meter with a metronome tone to avoid the intermodulation distortion that results from the amplitude modulation implementation in matrix_builder.py

# Generate a 12 Hz Alpha Flow matrix in a 4/4 grid at 60 BPM
python decoupled_matrix_builder.py --beat 12.0 --meter 4/4 --bpm 60

# Generate a 2 Hz Delta Entropy Flush in a 3/4 waltz at 72 BPM
python decoupled_matrix_builder.py --beat 2.0 --meter 3/4 --bpm 72

# Overclock to a 40 Hz Gamma engine with a fast 4/4 meter at 120 BPM
python decoupled_matrix_builder.py --beat 40.0 --meter 4/4 --bpm 120