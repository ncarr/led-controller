from time import monotonic, sleep
from controller import Gradient, ColorStop, Scene, Layer, Color, AnimatedColor, Keyframe

c = AnimatedColor([Keyframe(Color(255, 0, 0), 0.0),
                   Keyframe((Color(0, 0, 255)), 10.0)])
c.start()
g = Gradient(colorstops=[ColorStop(c, location=0.0),
                         ColorStop(Color(0, 0, 0), location=1.0)])
s = Scene([Layer(g)])

print(g.getColorAtPositionAndTime(0.5, monotonic() + 5))
