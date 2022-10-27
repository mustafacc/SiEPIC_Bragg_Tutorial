"""
Contra directional coupler DOE layout builder.

@author: Mustafa Hammood
"""
import numpy as np
import pya
from SiEPIC.extend import to_itype
from SiEPIC.scripts import connect_pins_with_waveguide, connect_cell


class layout_cdc:
    def __init__(self, ly, tech):
        # layout parameters
        self.ly = ly
        self.tech = tech
        self.cell = None
        self.cell_name = 'Top_cdc'
        self.io = "GC_TE_1550_8degOxide_BB"
        self.io_lib = "EBeam"
        self.cdc = "contra_directional_coupler"  # or "Contra_DC_chirped" if chirped
        self.cdc_lib = "EBeam"  # or "EBeam_Beta" if "Contra_DC_chirped" is used
        self.num_sweep = 10
        self.wavl = 1550
        self.pol = "TE"
        self.label = "device_cdc"
        self.layer_floorplan = 'FloorPlan'
        self.layer_text = 'Text'

        # pcell parameters
        self.number_of_periods = 1000
        self.grating_period = 0.322  # µm
        self.grating_period_end = None  # if chirped, µm
        self.wg1_width = 0.44  # µm
        self.wg2_width = 0.56  # µm
        self.corrugation1_width = 0.024  # µm
        self.corrugation2_width = 0.048  # µm
        self.gap = 0.1  # µm
        self.sinusoidal = False
        self.a = 2.8
        self.sbend = True  # You need to include tapers in your layout if False!
        self.sbend_r = 15  # µm
        self.sbend_length = 11  # µm
        self.port_w = 0.5  # µm

        # waveguide routing and placement parameters
        self.wg_type = "Strip TE 1550 nm, w=500 nm"
        self.wg_radius = 5  # µm
        self.io_pitch = 127  # µm
        self.wg_spacing = 2  # µm

    def make_dependent_params(self):
        """Define "dependent" waveguide routing variables."""
        self.route_up = self.io_pitch  # µm
        self.device_io_space = self.wg_radius*5  # µm
        self.io_column_space = self.wg_radius*13  # µm
        self.device_column_space = self.wg_radius + 2  # µm
        self.wg_spacing = self.wg_spacing+self.port_w

    def make_cdc(self, number_of_periods, grating_period, grating_period_end, wg1_width, wg2_width,
                 corrugation1_width, corrugation2_width, gap, sinusoidal, a,
                 sbend, sbend_r, sbend_length, port_w):
        """Create the device PCell."""
        pcell_params = {"number_of_periods": number_of_periods, "grating_period": grating_period,
                        "wg1_width": wg1_width, "wg2_width": wg2_width, "corrugation1_width": corrugation1_width,
                        "grating_period_end": grating_period_end, "corrugation2_width": corrugation2_width,
                        "gap": gap, "sinusoidal": sinusoidal, "index": a, "sbend": sbend, "sbend_r": sbend_r,
                        "sbend_length": sbend_length, "port_w": port_w}
        return self.ly.create_cell(self.cdc, self.cdc_lib, pcell_params)

    def make_params(self):
        """Convert the pcell params to list of size self.num_sweep."""
        if type(self.number_of_periods) not in [list, np.ndarray]:
            self.number_of_periods = [self.number_of_periods]*self.num_sweep
        if type(self.grating_period) not in [list, np.ndarray]:
            self.grating_period = [self.grating_period]*self.num_sweep
        if type(self.grating_period_end) not in [list, np.ndarray]:
            self.grating_period_end = [self.grating_period_end]*self.num_sweep
        if type(self.wg1_width) not in [list, np.ndarray]:
            self.wg1_width = [self.wg1_width]*self.num_sweep
        if type(self.wg2_width) not in [list, np.ndarray]:
            self.wg2_width = [self.wg2_width]*self.num_sweep
        if type(self.corrugation1_width) not in [list, np.ndarray]:
            self.corrugation1_width = [self.corrugation1_width]*self.num_sweep
        if type(self.corrugation2_width) not in [list, np.ndarray]:
            self.corrugation2_width = [self.corrugation2_width]*self.num_sweep
        if type(self.gap) not in [list, np.ndarray]:
            self.gap = [self.gap]*self.num_sweep
        if type(self.sinusoidal) not in [list, np.ndarray]:
            self.sinusoidal = [self.sinusoidal]*self.num_sweep
        if type(self.a) not in [list, np.ndarray]:
            self.a = [self.a]*self.num_sweep
        if type(self.sbend) not in [list, np.ndarray]:
            self.sbend = [self.sbend]*self.num_sweep
        if type(self.sbend_r) not in [list, np.ndarray]:
            self.sbend_r = [self.sbend_r]*self.num_sweep
        if type(self.sbend_length) not in [list, np.ndarray]:
            self.sbend_length = [self.sbend_length]*self.num_sweep
        if type(self.port_w) not in [list, np.ndarray]:
            self.port_w = [self.port_w]*self.num_sweep

    def make(self):
        """Make the layout cell."""
        dbu = self.ly.dbu
        top_cell = self.cell
        cell = self.cell.layout().create_cell(self.cell_name)
        cell_io = self.ly.create_cell(self.io, self.io_lib).cell_index()
        self.make_dependent_params()
        self.make_params()  # convert parameters to lists in case they weren't already

        insts_cdc = []
        space_interleave = 0
        for i in range(self.num_sweep):
            insts_io = []
            cell_cdc = self.make_cdc(
                self.number_of_periods[i], self.grating_period[i], self.grating_period_end[i], self.wg1_width[i],
                self.wg2_width[i], self.corrugation1_width[i], self.corrugation2_width[i],
                self.gap[i], self.sinusoidal[i], self.a[i], self.sbend[i], self.sbend_r[i],
                self.sbend_length[i], self.port_w[i])
            # Pcell center is that much away from opt1 label
            cdc_center = self.sbend_length[i]+3
            cdc_length = cell_cdc.dbbox().width()
            x_cdc = cdc_center-cdc_length/2
            y_cdc = i*self.device_column_space + self.device_io_space
            t = pya.Trans(pya.Trans.R0, to_itype(x_cdc, dbu), to_itype(y_cdc, dbu))
            insts_cdc.append(cell.insert(pya.CellInstArray(cell_cdc.cell_index(), t)))

            # measurement labels
            device_label = f"opt_in_{self.pol}_{self.wavl}_{self.label}"
            if not self.grating_period_end[i]:
              device_attributes = f"_{self.number_of_periods[i]}N{int(self.grating_period[i]*1e3)}nmPeriod{int(self.wg1_width[i]*1e3)}nmWA{int(self.wg2_width[i]*1e3)}nmWB{int(self.corrugation1_width[i]*1e3)}nmdW{int(self.corrugation2_width[i]*1e3)}nmdWB{int(self.gap[i]*1e3)}nmGAP{self.a[i]}Apo{int(self.sinusoidal[i])}"
            else:
              device_attributes = f"_{self.number_of_periods[i]}N{int(self.grating_period[i]*1e3)}nmPeriod{int(self.grating_period_end[i]*1e3)}nmPeriodEnd{int(self.wg1_width[i]*1e3)}nmWA{int(self.wg2_width[i]*1e3)}nmWB{int(self.corrugation1_width[i]*1e3)}nmdW{int(self.corrugation2_width[i]*1e3)}nmdWB{int(self.gap[i]*1e3)}nmGAP{self.a[i]}Apo{int(self.sinusoidal[i])}"
            text = device_label + device_attributes
            text_size = 1.5/dbu
            # direct routing devices
            if i % 2 == 0:

                # instantiate IOs (4 IOs per device)
                x = -self.io_pitch*2 + self.io_pitch/2 - self.io_pitch/4
                y = -i*self.io_column_space/2
                t = pya.Trans(pya.Trans.R90, to_itype(x, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))
                t = pya.Trans(pya.Trans.R90, to_itype(
                    x + self.io_pitch, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))
                t = pya.Trans(pya.Trans.R90, to_itype(
                    x + 2*self.io_pitch, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))
                t = pya.Trans(pya.Trans.R90, to_itype(
                    x + 3*self.io_pitch, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))

                # measurement text label on IO
                t = pya.Trans(pya.Trans.R0, to_itype(-self.io_pitch /
                              2-self.io_pitch/4, dbu), to_itype(y, dbu))
                io_text = pya.Text(text.replace('.', 'p')+'_inWA', t)
                TextLayerN = cell.layout().layer(self.tech[self.layer_text])
                shape = cell.shapes(TextLayerN).insert(io_text)
                shape.text_size = text_size

                space_interleave += 2*self.wg_spacing

                # connect IOs to devices
                pt1_1 = self.wg_radius
                if (cdc_length/2-(self.io_pitch*2-self.io_pitch/4)) < 0:
                  space_pt1 = 0
                else:
                  space_pt1 = (cdc_length/2-(self.io_pitch*2-self.io_pitch/4))
                pt1_2 = space_pt1+2*self.wg_radius \
                    + i*self.wg_spacing + self.wg_spacing + space_interleave
                turtle1 = [pt1_1, 90, pt1_2, 90]  # inflection points
                wg_io_device1 = connect_pins_with_waveguide(
                    insts_io[0], 'opt1', insts_cdc[-1], 'opt2', waveguide_type=self.wg_type, turtle_A=turtle1)  # leftmost io

                pt2_1 = self.wg_radius+self.wg_spacing
                pt2_2 = pt1_2+self.io_pitch-self.wg_spacing
                turtle1 = [pt2_1, 90, pt2_2, 90]  # inflection points
                wg_io_device2 = connect_pins_with_waveguide(
                    insts_io[1], 'opt1', insts_cdc[-1], 'opt1', waveguide_type=self.wg_type, turtle_A=turtle1)  # left io

                pt3_1 = pt2_1+self.wg_spacing
                pt3_2 = pt2_2 + self.io_pitch/2
                turtle1 = [pt3_1, -90, pt3_2, 90]  # inflection points
                wg_io_device3 = connect_pins_with_waveguide(
                    insts_io[2], 'opt1', insts_cdc[-1], 'opt3', waveguide_type=self.wg_type, turtle_A=turtle1)  # right io

                pt4_1 = pt1_1+self.wg_spacing
                pt4_2 = pt3_2 - self.io_pitch + self.wg_spacing
                turtle1 = [pt4_1, -90, pt4_2, 90]  # inflection points
                wg_io_device4 = connect_pins_with_waveguide(
                    insts_io[3], 'opt1', insts_cdc[-1], 'opt4', waveguide_type=self.wg_type, turtle_A=turtle1)  # rightmost io
            # backwards routing devices (interdigitated io layout)
            else:
                # instantiate IOs (4 IOs per device)
                x = -self.io_pitch*2 + self.io_pitch - self.io_pitch/4
                y = -(i-1)*self.io_column_space/2
                t = pya.Trans(pya.Trans.R90, to_itype(x, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))
                t = pya.Trans(pya.Trans.R90, to_itype(
                    x + self.io_pitch, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))
                t = pya.Trans(pya.Trans.R90, to_itype(
                    x + 2*self.io_pitch, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))
                t = pya.Trans(pya.Trans.R90, to_itype(
                    x + 3*self.io_pitch, dbu), to_itype(y, dbu))
                insts_io.append(cell.insert(pya.CellInstArray(cell_io, t)))

                # measurement text label on IO
                t = pya.Trans(pya.Trans.R0, to_itype(-self.io_pitch/4, dbu), to_itype(y, dbu))
                io_text = pya.Text(text.replace('.', 'p')+'_inWB', t)
                TextLayerN = cell.layout().layer(self.tech[self.layer_text])
                shape = cell.shapes(TextLayerN).insert(io_text)
                shape.text_size = text_size

                # connect IOs to devices
                if 'space_interleaver' not in locals():
                    space_interleaver = 0
                pt1_1 = self.wg_radius
                pt1_2 = self.io_pitch/4
                pt1_3 = self.io_column_space*3/4
                if (cdc_length/2-(self.io_pitch*2-self.io_pitch/4)) < 0:
                  space_pt1 = 0
                else:
                  space_pt1 = (cdc_length/2-(self.io_pitch*2-self.io_pitch/4))
                pt1_4 = space_pt1+pt1_2+2*self.wg_radius \
                    + 2*i*self.wg_spacing + 2*self.wg_spacing + space_interleaver
                turtle1 = [pt1_1, 90, pt1_2, 90, pt1_3, -90, pt1_4, -90]  # inflection points
                wg_io_device1 = connect_pins_with_waveguide(
                    insts_io[0], 'opt1', insts_cdc[-1], 'opt1', waveguide_type=self.wg_type, turtle_A=turtle1)  # top io

                pt2_1 = pt1_1
                pt2_2 = pt1_2
                pt2_3 = pt1_3 + self.wg_spacing
                pt2_4 = pt1_4 + self.io_pitch + self.wg_spacing
                turtle1 = [pt2_1, 90, pt2_2, 90, pt2_3, -90, pt2_4, -90]  # inflection points
                wg_io_device2 = connect_pins_with_waveguide(
                    insts_io[1], 'opt1', insts_cdc[-1], 'opt2', waveguide_type=self.wg_type, turtle_A=turtle1)  # top io

                pt4_1 = pt1_1
                pt4_2 = pt1_2
                pt4_3 = pt1_3
                pt4_4 = pt1_4
                turtle1 = [pt4_1, 90, pt4_2, 90, pt4_3, 90, pt4_4, -90]  # inflection points
                wg_io_device4 = connect_pins_with_waveguide(
                    insts_io[3], 'opt1', insts_cdc[-1], 'opt3', waveguide_type=self.wg_type, turtle_A=turtle1)  # top io

                pt3_1 = pt4_1
                pt3_2 = pt4_2
                pt3_3 = pt4_3 + 2*self.wg_spacing
                pt3_4 = pt2_4
                turtle1 = [pt3_1, 90, pt3_2, 90, pt3_3, 90, pt3_4, -90]  # inflection points
                wg_io_device3 = connect_pins_with_waveguide(
                    insts_io[2], 'opt1', insts_cdc[-1], 'opt4', waveguide_type=self.wg_type, turtle_A=turtle1)  # top io

        self.cdc_cell = cell

    def add_to_layout(self, cell, x=0, y=0):
        t = pya.Trans(pya.Trans.R270, x, y)
        x = -pya.CellInstArray(self.cdc_cell.cell_index(), t).bbox(self.ly).p1.x
        y = -pya.CellInstArray(self.cdc_cell.cell_index(), t).bbox(self.ly).p1.y
        t = pya.Trans(pya.Trans.R270, x, y)
        cell.insert(pya.CellInstArray(self.cdc_cell.cell_index(), t))
        FloorplanLayer = self.cdc_cell.layout().layer(self.tech[self.layer_floorplan])
        cell.shapes(FloorplanLayer).insert(
            pya.Box(0, 0, self.cdc_cell.bbox().height(), self.cdc_cell.bbox().width()))
