from gaudges.utils.kivy_utils import normalize_stops

stops = [(0.2, 1, 1, 1), (0.3, 0, 1, 0), (0.8, 0, 0, 0)]


print(normalize_stops(.5,*stops))

