#!/usr/bin/env python
# coding: utf-8

# In[1]:


from xsequence.lattice import Lattice
from xsequence.conversion_utils import conv_utils


# Lattices can be imported from different sources. Currently only limited to FCC-ee lattice without complicated Solenoid IR descriptions.
# 
# Different examples:
#  - From cpymad instance
#  - From MAD-X sequence file
#  - From SAD using built in SAD2MAD converter (tilted Solenoid)
#  - From pyAT
# 

# In[2]:


# Import from cpymad instance
madx_lattice = conv_utils.create_cpymad_from_file("FCCee_h.seq", energy=120)
lat = Lattice.from_cpymad(madx_lattice, 'l000013')

# Import from madx sequence file (through cpymad)
lat_mad = Lattice.from_madx_seqfile("FCCee_h.seq", 'l000013', energy=120)


# In[3]:


# Import from sad sequence file
lat_sad = Lattice.from_sad("FCCee_h.sad", 'ring', energy=120)


# In[4]:


# Import from pyat instance
pyat_lattice = conv_utils.create_pyat_from_file("FCCee_h.mat")
lat = Lattice.from_pyat(pyat_lattice)


# A lattice can also be created from scratch in Python

# In[5]:


import xsequence.elements as xe

# Create elements
q1 = xe.Quadrupole('q1', length=1, k1=0.2, location=1)
q2 = xe.Quadrupole('q2', length=1, k1=-0.2, location=3)
q3 = xe.Quadrupole('q3', length=1, k1=0.2, location=5)

element_dict = {'q1':q1, 'q2':q2, 'q3':q3}
lat = Lattice('lat_name', element_dict, key='sequence')

# Create elements
d0 = xe.Drift('d0', length=1)
q1 = xe.Quadrupole('q1', length=1, k1=0.2)
d1 = xe.Drift('d1', length=1)
q2 = xe.Quadrupole('q2', length=1, k1=-0.2)
d2 = xe.Drift('d1', length=1)
q3 = xe.Quadrupole('q3', length=1, k1=0.2)

element_dict = {'d0':d0, 'q1':q1, 'd1':d1, 
                'q2':q2, 'd2':d2, 'q3':q3}
lat = Lattice('lat_name', element_dict, key='line')


# A Lattice() instance contains two representations of the lattice:
# 
# sequence: List of elements without drifts, based on positions
# 
# line: List of elements with explicit drifts

# In[30]:


# Import from sad sequence file
lat = Lattice.from_madx_seqfile("FCCee_h.seq", 'l000013', energy=120)

print(lat.sequence)


# In[7]:


print(lat.line)


# Some basic functionalities and manipulations can be done

# In[8]:


# Get elements of specific type
quad_sext = lat.sequence.get_class(['Quadrupole', 'Sextupole'])
print(quad_sext)


# In[9]:


# Find element by name
print(lat.sequence['bg6.1'])


# In[10]:


# Select element ranges using positions or elements
print(lat.sequence['qg7.1':'qd3.4'])


# In[11]:


print(lat.sequence[1150:1200])


# In[12]:


# Obtain s positions of Lattice
print(lat.sequence.names)
print(lat.sequence.positions)


# In[13]:


# Teapot slicing using default 1 slice
sliced_lat = lat.sliced

# Change slice number
quad_sext = lat.sequence.get_class(['Quadrupole', 'Sextupole'])
for name, el in quad_sext.items():
    el.num_slices = 5

sliced_lat = lat.sliced
print(sliced_lat.sequence[1:10])


# Quick optics calculations can be done for checks, currently without radiation and tapering. Note no matchin is done currently, so should be updated

# In[31]:


df_mad = lat.optics(engine='madx', drop_drifts=True)
df_pyat = lat.optics(engine='pyat', drop_drifts=True)


# In[32]:


get_ipython().run_line_magic('matplotlib', 'inline')
from matplotlib.pyplot import plot, show
from xsequence.helpers.fcc_plots import fcc_axes

ax, = plot(df_mad['s'], df_mad['betx'])
ax, = plot(df_pyat['s'], df_pyat['betx'])
show()


# A useful tool to debug changes and track differences between lattices. In this case the difference between an FCC-ee Higgs physics lattice from SAD and from MAD-X.
# 

# In[16]:


from xsequence.helpers.compare_lattices import compare_lattices
compare_lattices(lat_sad, lat_mad)


# The lattice can be exported to cpymad, pyat and xline. 

# In[17]:


madx = lat.to_cpymad()
pyat = lat.to_pyat()
line = lat.to_xline()


# The 'xdeps' dependencies package from R. de Maria has been implemented into Lattices to import dependencies from cpymad. 
# 
# Dependency manager is contained in:
#    - lat.manager
# 
# The references to the different objects are stored as:
#    - lat.vref  --> Reference to variables
#    - lat.sref  --> Reference to sequence
#     

# In[18]:


from cpymad.madx import Madx
cpymad_ins = Madx(stdout=False)
cpymad_ins.call("lhc.seq")
cpymad_ins.call("optics.madx")

lat = Lattice.from_cpymad(cpymad_ins, seq_name="lhcb1", 
  dependencies=True)

print(lat.sequence["mqxa.1r1"].k1)


# In[19]:


lat.vref["kqx.r1"] = 0.01
print(lat.sequence["mqxa.1r1"].k1)


# New knobs can be created to tune specific magnets. Here, a new knob called 'mqxa_knob' is created that adds a value to the strengths of all 'mqxa' elements.
# 
#  - element.k1 = current_expression + mqxa_knob
# 
# Note the that the syntax is still under development and will be polished to offer much more intuitive functionalities.

# In[20]:


for el in lat.sequence.find_elements("mqxa*"):
    lat.sref[el].k1 = lat.manager.tasks[lat.sref[el].k1].expr + lat.vref["mqxa_knob"]

for name, el in lat.sequence.find_elements("mqxa*").items():
    print(el.k1)


# The new expression for element 'mqxa.1l1' is now:

# In[21]:


print(lat.manager.tasks[lat.sref["mqxa.1l1"].k1].expr)


# A change of the knob value will result in the desired change of k1 strengths.

# In[22]:


lat.vref["mqxa_knob"] = 0.015

for name, el in lat.sequence.find_elements("mqxa*").items():
    print(el.k1)


# In[ ]:




