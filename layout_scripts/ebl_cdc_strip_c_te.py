"""
Application of CDCs DOE builder script

@author: Mustafa Hammood
"""
from SiEPIC.utils import get_layout_variables
import numpy as np
TECHNOLOGY, lv, ly, cell = get_layout_variables()

layout = layout_cdc(ly, TECHNOLOGY)
layout.cell_name = "cdc_strip_c_te_uni"
layout.cell = cell
layout.io = "GC_TE_1550_8degOxide_BB"
layout.io_lib = "EBeam"
layout.cdc = "contra_directional_coupler"
layout.cdc_lib = "EBeam"
layout.num_sweep = 20
layout.wavl = 1550
layout.pol = "TE"
layout.label = "device_cdc_strip"
layout.wg_type = "Strip TE 1550 nm, w=500 nm"
layout.label = "device_cdc_GAPsweep"
layout.layer_floorplan = 'FloorPlan'
layout.wg_spacing = 1

layout.number_of_periods = 1400
layout.grating_period = 0.322  # µm
layout.wg1_width = 0.56  # µm
layout.wg2_width = 0.44  # µm
layout.corrugation1_width = 0.048  # µm
layout.corrugation2_width = 0.024  # µm
layout.gap = 0.1  # µm
layout.sinusoidal = False  # sinusoidal corrugations option
layout.a = 2.8  # gaussian apodization index
layout.sbend = True
layout.sbend_r = 15  # µm
layout.sbend_length = 11  # µm
layout.port_w = 0.5  # µm

layout.make()
layout.add_to_layout(cell)