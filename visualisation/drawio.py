# diagram.py
from diagrams import Diagram
from diagrams.generic.blank import Blank

with Diagram("Web Service"):
    Blank("test") >> Blank("Blah")
