"""Explicit common-unit conversions. Unsupported graph-label units require an exact match."""
UNITS={
 'mol':('amount',1),'mmol':('amount',.001),'umol':('amount',1e-6),'µmol':('amount',1e-6),
 'g':('mass',1),'kg':('mass',1000),'mg':('mass',.001),
 'L':('volume',1),'mL':('volume',.001),'uL':('volume',1e-6),'µL':('volume',1e-6),
 'mol/L':('concentration',1),'M':('concentration',1),'mmol/L':('concentration',.001),'mM':('concentration',.001),
 'atm':('pressure',101325),'Pa':('pressure',1),'kPa':('pressure',1000),'bar':('pressure',100000),
 'torr':('pressure',101325/760),'mmHg':('pressure',101325/760),
 'J':('energy',1),'kJ':('energy',1000),'J/mol':('molar_energy',1),'kJ/mol':('molar_energy',1000),
 'cal':('energy',4.184),'kcal':('energy',4184),
 'm':('length',1),'cm':('length',.01),'mm':('length',.001),'um':('length',1e-6),'µm':('length',1e-6),'nm':('length',1e-9),'pm':('length',1e-12),
 's':('time',1),'min':('time',60),'h':('time',3600),
 'V':('potential',1),'mV':('potential',.001),'A':('current',1),'mA':('current',.001)
}
def convert(value,provided,expected):
    if not isinstance(provided,str):raise ValueError('Unit required')
    provided=provided.strip()
    if expected in (None,'dimensionless'):
        if provided not in ('','1','dimensionless'):raise ValueError('A dimensionless result cannot carry a physical unit')
        return value
    if provided==expected:return value
    if provided in ('K','°C','C') or expected in ('K','°C','C'):
        if provided=='K' and expected in ('°C','C'): return value-273.15
        if provided in ('°C','C') and expected=='K': return value+273.15
        if provided in ('°C','C') and expected in ('°C','C'): return value
        raise ValueError('Incompatible or unsupported unit')
    source,target=UNITS.get(provided),UNITS.get(expected)
    if not source or not target or source[0]!=target[0]:raise ValueError('Incompatible or unsupported unit')
    return value*source[1]/target[1]

def supported_units(): return sorted(UNITS|{'K':None,'°C':None,'C':None})
