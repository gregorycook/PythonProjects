import math

def fact(n):
	result = 1
	for i in range(n):
		result = result * (i+1)
	return result
	
print fact(59)
print math.factorial(59)