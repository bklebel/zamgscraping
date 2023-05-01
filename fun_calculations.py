from numpy import around

m_W = 18.016  # kg/kmol (molecular weight of water vapor)
R = 8314.3    # J/(kmol*K) (universelal gas constant)


def saturation_pressure(T):
	"""calculate the saturation pressure
	temperature input in celsius"""
	if T < 0: 
		a = 7.6
		b = 240.7
	else:
		a = 7.5
		b = 237.3

	return 6.1078 * 10**( (a*T)/(b+T)   )



def vapor_pressure(r, T):
	return r/100 *  saturation_pressure(T)


def temperature_kelvin(T):
	return T + 273.15

def humidity_absolute(r, T):
	return around(1e5 * m_W/R * vapor_pressure(r, T)/temperature_kelvin(T), decimals=2)
