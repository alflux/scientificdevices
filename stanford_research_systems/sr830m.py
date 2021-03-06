#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Manual: http://www.thinksrs.com/downloads/PDFs/Manuals/SR830m.pdf

__author__ = 'Marc Hanefeld, Alfons Schuck'
__version__ = 0.1

import visa


class SR830m(object):
    def __init__(self, GPIBPort: str = 'GPIB0::7::INSTR'):
        rm = visa.ResourceManager('@py')
        self.inst = rm.open_resource(GPIBPort,
                                     write_termination='\r\n',
                                     read_termination=None)

        # Defining the extremal values for the device
        self._vRmsAcMin = 0.004
        self._vRmsAcMax = 5.000
        self._vAuxOutpMax = 10.5

        # Possible integration times for the Lock-In amplifier
        self._integrationTimes = [10E-6, 30E-6, 100E-6, 300E-6, 1E-3, 3E-3, 10E-3, 30E-3, 100E-3, 300E-3, 1, 3, 10, 30,
                                  100, 300, 1E3, 3E3, 10E3, 30E3]
        self._sensitivities = [2E-9, 5E-9, 10E-9, 20E-9, 50E-9, 100E-9, 200E-9, 500E-9, 1E-6, 2E-6, 5E-6, 10E-6, 20E-6,
                               50E-6, 100E-6, 200E-6, 500E-6, 1E-3, 2E-3, 5E-3, 10E-3, 20E-3, 50E-3, 100E-3, 200E-3,
                               500E-3, 1]

        """
        # self.LIA.write('*RST') # Reset the unit to its default configurations. Careful V = 1V!
        self.LIA.clear()  # Clear the local buffer for GPIB communications
        self.LIA.write("OUTX 1")  # Set the LIA to output responses to the GPIB port
        self.LIA.write('REST')  # Reset the scan. All stored data is lost.
        self.LIA.write('IGND 0')  # Set (Query) the Input Shield Grounding to Float (0) or Ground (1)
        self.LIA.write('ISRC 1')  # Set (Query) the Input Configuration to A (0), A-B (1) , I (1 MW) (2) or I (100 MW) (3)
        self.LIA.write('PHAS 0.0')  # Set (Query) the Phase Shift to x degrees.
        self.LIA.write('HARM 1')  # Set (Query) the Detection Harmonic to 1 <= i <= 19999 and i*f <= 102 kHz.
        self.set_sensitivity(1)  # Set the Sensitivity 1 V rms full scale.
        self.set_integration_time(1)  # Set (Query) the Time Constant to 1s.
        time.sleep(1)

        """

    # TODO copy docstrings from user manual

    @property
    def phaseShift(self) -> float:
        """
        The PHAS command sets or queries the reference phase shift. The
        parameter x is the phase (real number of degrees). The PHAS x com-
        mand will set the phase shift to x. The value of x will be rounded to 0.01°.
        The phase may be programmed from -360.00 ≤ x ≤ 729.99 and will be
        wrapped around at ±180°. For example, the PHAS 541.0 command will
        set the phase to -179.00° (541-360=181=-179). The PHAS? queries the
        phase shift.
        :return:
        :rtype:
        """
        return float(self.inst.query('PHAS?'))

    @phaseShift.setter
    def phaseShift(self, value: float):
        assert (value >= -360) and (value <= 729.99), 'Phase shift should be between -360° and +729.99°!'
        self.inst.write('PHAS{:.2f}'.format(value))

    @property
    def fmod(self) -> int:
        return int(self.inst.query('FMOD?'))

    @fmod.setter
    def fmod(self, value: int):
        assert (value == 0) or (value == 1), 'FMOD should be 0 (external) or 1 (internal)!'
        self.inst.write('FMOD{:d}'.format(value))

    @property
    def freq(self) -> float:
        """
        The FREQ command sets or queries the reference frequency. The
        FREQ? query command will return the reference frequency (in internal or
        external mode).
        The FREQ f command sets the frequency of the internal oscillator. This
        command is allowed only if the reference source is internal. The parame-
        ter f is a frequency (real number of Hz). The value of f will be rounded to
        5 digits or 0.0001 Hz, whichever is greater. The value of f is limited to
        0.001 ≤ f ≤ 102000. If the harmonic number is greater than 1, then the
        frequency is limited to nxf ≤ 102 kHz where n is the harmonic number.
        :return: frequency
        :rtype: float
        """
        return float(self.inst.query('FREQ?'))

    @freq.setter
    def freq(self, value: float):
        assert (value >= 0.001) and (value <= 10200), 'Frequency should be between 0.001 Hz and 10200 Hz!'
        self.inst.write('FREQ{:.3f}'.format(value))

    @property
    def rslp(self) -> int:
        return int(self.inst.query('RSLP?'))

    @rslp.setter
    def rslp(self, value: int):
        assert (value >= 0) and (
                value <= 2), 'Reference trigger should be 0 (zero crossing), 1 (rising edge) or 2 (falling edge)!'
        self.inst.write('RSLP{:d}'.format(value))

    @property
    def harm(self) -> int:
        return int(self.inst.query('HARM?'))

    @harm.setter
    def harm(self, value: int):
        assert (value >= 1) and (value <= 19999), 'Detection harmonic should be between 1 and 19999!'
        self.inst.write('HARM{:d}'.format(value))

    @property
    def slvl(self) -> float:
        return float(self.inst.query('SLVL?'))

    @slvl.setter
    def slvl(self, value: float):
        assert (value >= 0) and (value <= 5), 'Amplitude of sine-output should be between 0 (=0.004) V and 5 V'
        if value < 0.004:
            value = 0.004
        self.inst.write('SLVL{:.3f}'.format(value))

    @property
    def isrc(self) -> int:
        return int(self.inst.query('ISRC?'))

    @isrc.setter
    def isrc(self, value: int):
        assert (value >= 0) and (value <= 3), 'Input Configuration should be 0 (A), 1 (A-B), 2 (1 MΩ) or 3 (100 MΩ)!'
        self.inst.write('ISRC{:d}'.format(value))

    @property
    def ignd(self) -> int:
        return int(self.inst.query('IGND?'))

    @ignd.setter
    def ignd(self, value: int):
        assert (value == 0) or (value == 1), 'Shield grounding should be 0 (float) or 1 (ground)!'
        self.inst.write('IGND{:d}'.format(value))

    @property
    def icpl(self) -> int:
        return int(self.inst.query('ICPL?'))

    @icpl.setter
    def icpl(self, value: int):
        assert (value == 0) or (value == 1), 'Input coupling should be 0 (AC) or 1 (DC)!'
        self.inst.write('ICPL{:d}'.format(value))

    @property
    def ilin(self) -> int:
        return int(self.inst.query('ILIN?'))

    @ilin.setter
    def ilin(self, value: int):
        assert (value >= 0) and (
                value <= 3), 'Input line notch filter should be 0 (no filter), 1 (Line filter), 2 (2x line filter) or 3 (both filters)!'
        q = 'ILIN{:d}'.format(value)
        self.inst.write('ILIN{:d}'.format(value))

    @property
    def sens(self) -> int:
        return self.inst.query('SENS?')

    @sens.setter
    def sens(self, value: int):
        assert (value >= 0) and (value <= 26), 'Sensitivity should be integer between 0 and 26! Check user manual.'
        self.inst.write('SENS{:d}'.format(value))

    @property
    def rmod(self) -> int:
        return int(self.inst.query('RMOD?'))

    @rmod.setter
    def rmod(self, value: int):
        assert (value >= 0) and (value <= 2), ' Reserve Mode should be 0 (High Reserve), 1 (Normal) or 2 (Low Noise)!'
        self.inst.write('RMOD{:d}'.format(value))

    @property
    def oflt(self) -> int:
        return int(self.inst.query('OFLT?'))

    @oflt.setter
    def oflt(self, value: int):
        assert (value >= 0) and (value <= 19), 'Time Constant should be integer between 0 and 19! Check user manual.'
        self.inst.write('OFLT{:d}'.format(value))

    @property
    def ofsl(self) -> int:
        return int(self.inst.query('OFSL?'))

    @ofsl.setter
    def ofsl(self, value: int):
        assert (value >= 0) and (value <= 3), 'Low pass filter slope should be 0 (6dB), 1 (12dB), 2 (18dB) or 3 (24dB)!'
        self.inst.write('OFSL{:d}'.format(value))

    @property
    def sync(self) -> int:
        return int(self.inst.query('SYNC?'))

    @sync.setter
    def sync(self, value: int):
        assert (value == 0) or (value == 1), 'Synchronous filter should be 0 (Off) or 1 (filtering below 200Hz)!'
        self.inst.write('SYNC{:d}'.format(value))

    # TODO DDEF
    # TODO FPOP
    # TODO OEXP
    # TODO AOFF

    @property
    def oaux(self) -> dict:
        return {1: self.inst.query('OAUX?1'),
                2: self.inst.query('OAUX?2'),
                3: self.inst.query('OAUX?3'),
                4: self.inst.query('OAUX?4')}

    @property
    def auxv(self) -> dict:
        return {1: self.inst.query('AUXV?1'),
                2: self.inst.query('AUXV?2'),
                3: self.inst.query('AUXV?3'),
                4: self.inst.query('AUXV?4')}

    @auxv.setter
    def auxv(self, value: tuple):
        auxChannel = value[0]
        auxVoltage = value[1]
        assert (auxChannel >= 1) and (auxChannel <= 4), 'Output Channel should be 1, 2, 3 or 4!'
        assert (abs(auxVoltage) <= 10.5), 'Output Voltage should be between -10.5V and 10.5V'
        self.inst.write('AUXV{:d},{:.3f}'.format(auxChannel, auxVoltage))

    # TODO OUTX
    # TODO OVRM
    # TODO KCLK
    # TODO AKRM
    # TODO SSET
    # TODO RSET

    def agan(self):
        self.inst.write('AGAN')

    def arsv(self):
        self.inst.write('ARSV')

    def aphs(self):
        self.inst.write('APHS')

    def aoff(self, value: int):
        self.inst.write('AOFF {:d}'.format(value))

    # TODO Datastorage Commands

    @property
    def outpX(self) -> float:
        return float(self.inst.query('OUTP?1'))

    @property
    def outpY(self) -> float:
        return float(self.inst.query('OUTP?2'))

    @property
    def outpR(self) -> float:
        return float(self.inst.query('OUTP?3'))

    @property
    def outpT(self) -> float:
        return float(self.inst.query('OUTP?4'))

    def snap(self, liste: list) -> list:
        assert (len(liste) >= 2) and (len(liste) <= 6), 'List should contain 2-6 entries.'
        assert (min(liste) >= 1) and (max(liste) <= 11), 'List should contain integer values between 1 and 11.'
        query = 'SNAP?{},'.format(str(liste).strip('[]'))
        answer = str(self.inst.query(query))
        return [float(i) for i in answer.split(',')]

    # TODO SPTS
    # TODO TRCA
    # TODO TRCB
    # TODO TRCL
    # TODO FAST
    # TODO STRD

    @property
    def idn(self) -> str:
        return str(self.inst.query('*IDN?'))

    def rst(self):
        """
        Reset Lock-In
        """
        self.inst.write('*RST')

    # TODO LOCL
    # TODO TRIG
    # TODO CLS
    # TODO ESE
    # TODO ESR
    # TODO SRE
    # TODO STB
    # TODO PSC
    # TODO ERRE
    # TODO ERRS
    # TODO LIAE
    # TODO LIAS


if __name__ == '__main__':
    lia = SR830m()
    a = lia.ilin
    lia.ilin = 0
    print(a)
