import sys
sys.path.append("..")
from data import getPowerLevels
import time

start = time.time()
pi, battery, solar, none = getPowerLevels()
end = time.time()


elapsed = end - start
print(f"Function execution time: {elapsed}")
print(f"Pi Current: {pi.current}") # python execution increases current and gives to high readings :(