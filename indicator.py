#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- coding: 850 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from pyModbusTCP.client import ModbusClient
from QLed import QLed
from gauge import AnalogGauge
from color_button import ColorButton
from appData import AccessControl
from simple_pid import PID
import hashlib, json


class CommsEngine(QThread):
    error_signals = pyqtSignal(name='er_signals')
    running = pyqtSignal()
    stopped = pyqtSignal()

    def __init__(self):
        QThread.__init__(self)

        self._writeTo = []
        self.on_line = False
        '''self.SERVER_PORT = 502
        self.SERVER_HOST = "192.168.2.5"'''
        self.time_base = 100  # poll time base msec
        self.client = ModbusClient()
        '''self.comm_clock = QTimer()
        self.comm_clock.setInterval(self.time_base)
        self.comm_clock.moveToThread(self)'''

    def set_time_base(self, t):
        self.time_base = t

    def writeTo(self, w):
        self._writeTo = w

    def run(self):
        # TCP auto connect on modbus request, close after it
        # uncomment this line to see debug message
        # c.debug(True)
        # define modbus server host, port
        '''self.client.host(self.SERVER_HOST)
        self.client.port(self.SERVER_PORT)'''
        self.update()
        # print("communication engine running")

        '''self.comm_clock.timeout.connect(self.update)
        self.comm_clock.start()
        loop = QEventLoop()
        loop.exec_()'''

    def update(self):
        # open or reconnect TCP to server
        if not self.client.is_open():
            if not self.client.open():
                #self.comm_clock.timeout.disconnect()
                self.on_line = not self.client.is_open()
                self.error_signals.emit()
                print('cannot connect',self._writeTo)
                self.stop()

        if self.client.is_open():
            self.on_line = self.client.is_open()
            self.client.write_single_coil(self._writeTo['addr'],self._writeTo['state'])
            print(self._writeTo)

        self.client.close()

    def is_online(self):
        return self.on_line

    def stop(self):
        if self.isRunning():
            self.quit()


class CommsGO(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.init()

    def init(self):
        lay = QVBoxLayout()
        self.comms = QGroupBox()
        #self.comms.setTitle('Comms')
        form1 = QFormLayout()
        self.host = QLineEdit()
        hostLbl = QLabel('host')
        form1.addRow(hostLbl,self.host)
        self.port = QSpinBox()
        self.port.setMaximum(1023)
        portLbl = QLabel('port')
        form1.addRow(portLbl,self.port)

        self.reads = QGroupBox()
        self.reads.setTitle('Read')
        form2 = QFormLayout()

        self.addrRead = QSpinBox()
        addrRLbl = QLabel('addr')
        form2.addRow(addrRLbl,self.addrRead)

        self.regRead = QSpinBox()
        regRLbl = QLabel('reg')
        form2.addRow(regRLbl, self.regRead)

        self.writes = QGroupBox()
        self.writes.setTitle('Write')
        form3 = QFormLayout()

        self.addrWrite = QSpinBox()
        addrWLbl = QLabel('addr')
        form3.addRow(addrWLbl, self.addrWrite)

        self.regWrite = QSpinBox()
        regWLbl = QLabel('reg')
        form3.addRow(regWLbl,self.regWrite)

        self.comms.setLayout(form1)
        self.reads.setLayout(form2)
        self.writes.setLayout(form3)
        lay.addWidget(self.comms)
        lay.addWidget(self.reads)
        lay.addWidget(self.writes)
        self.setLayout(lay)


class Comms(CommsGO):
    def __init__(self):
        super(Comms, self).__init__()

    def set_data(self, data):
        self.host.setText(data['host'])
        self.port.setValue(data['port'])
        self.addrRead.setValue(data['read']['addr'])
        self.regRead.setValue(data['read']['reg'])
        self.addrWrite.setValue(data['write']['addr'])
        self.regWrite.setValue(data['write']['reg'])

    def get_data(self):
        '''
        this method create a dict of communication settings
        :return: dict
        '''
        data = {'host': self.host.text(),
                'port': self.port.value(),
                'read':{
                'addr': self.addrRead.value(),
                'reg': self.regRead.value()},
                'write':{
                'addr': self.addrWrite.value(),
                'reg': self.regWrite.value()}}
        return data


class ConfigGO(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.init()

    def init(self):
        lay = QVBoxLayout()
        self.vars = QGroupBox()
        #self.vars.setTitle('Variables')
        form1 = QFormLayout()

        self.alias = QLineEdit()
        self.alias.setMinimumHeight(22)
        aliasLbl = QLabel('alias')
        form1.addRow(aliasLbl,self.alias)

        self.zero = QDoubleSpinBox()
        self.zero.setMinimumHeight(22)
        self.zero.setMaximum(1000)
        self.zero.setMinimum(-1000)
        self.zero.setAlignment(Qt.AlignRight)
        zerolbl = QLabel('zero')
        form1.addRow(zerolbl,self.zero)

        self.span = QDoubleSpinBox()
        self.span.setMinimumHeight(22)
        self.span.setMaximum(1000)
        self.span.setMinimum(-1000)
        self.span.setAlignment(Qt.AlignRight)
        spanLbl = QLabel('span')
        form1.addRow(spanLbl,self.span)

        self.units = QLineEdit()
        self.units.setMinimumHeight(22)
        self.units.setAlignment(Qt.AlignRight)
        unitLbl = QLabel('units')
        form1.addRow(unitLbl,self.units)
        self.advanced = QPushButton('Avanzado...')
        form1.addWidget(self.advanced)

        self.vars.setLayout(form1)

        lay.addWidget(self.vars)

        self.setLayout(lay)


class Config(ConfigGO):
    def __init__(self):
        super(Config, self).__init__()


    def set_data(self, data):
        self.alias.setText(data['alias'])
        self.zero.setValue(data['zerp'])
        self.span.setValue(data['span'])
        self.units.setText(data['units'])

    def get_data(self):
        data = {'alias': self.alias.text(),
                'zero': self.zero.value(),
                'span': self.span.value(),
                'units': self.units.text()}
        return data


class ControlGO(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.init()

    def init(self):
        lay = QVBoxLayout()
        self.control = QGroupBox()
        self.control.setTitle('Habilitar')
        self.control.setCheckable(True)
        form1 = QFormLayout()

        self.setPoint = QDoubleSpinBox()
        self.setPoint.setMinimumHeight(22)
        self.setPoint.setDecimals(1)
        self.setPoint.setMaximum(1000)
        self.setPoint.setAlignment(Qt.AlignRight)
        setPointLbl = QLabel('set point')
        form1.addRow(setPointLbl, self.setPoint)

        self.select = QComboBox()
        self.select.insertItem(0,'On/Off')
        self.select.insertItem(1,'PID')
        self.select.setMinimumHeight(22)
        selectLbl = QLabel('type')
        form1.addRow(selectLbl, self.select)

        self.control.setLayout(form1)

        form2 = QFormLayout()
        self.onOff = QGroupBox()
        self.onOff.setTitle('On/Off')
        self.histeresis = QDoubleSpinBox()
        self.histeresis.setMinimumHeight(22)
        self.histeresis.setDecimals(1)
        self.histeresis.setMaximum(100)
        self.histeresis.setPrefix('+/- ')
        self.histeresis.setSuffix(' %')
        self.histeresis.setAlignment(Qt.AlignRight)

        histeLbl = QLabel('hist')
        form2.addRow(histeLbl,self.histeresis)
        self.onOff.setLayout(form2)
        self.onOff.setEnabled(False)

        self.pid = QGroupBox()
        self.pid.setTitle('PID')
        form3 = QFormLayout()
        self.kP = QDoubleSpinBox()
        self.kP.setMinimumHeight(22)
        self.kP.setDecimals(1)
        self.kP.setAlignment(Qt.AlignRight)
        kpLbl = QLabel('kP')
        form3.addRow(kpLbl,self.kP)

        self.kI = QDoubleSpinBox()
        self.kI.setMinimumHeight(22)
        self.kI.setDecimals(1)
        self.kI.setAlignment(Qt.AlignRight)
        kiLbl = QLabel('kI')
        form3.addRow(kiLbl,self.kI)

        self.kD = QDoubleSpinBox()
        self.kD.setMinimumHeight(22)
        self.kD.setDecimals(1)
        self.kD.setAlignment(Qt.AlignRight)
        kdLbl = QLabel('kD')
        form3.addRow(kdLbl,self.kD)
        self.pid.setLayout(form3)
        self.pid.setEnabled(False)

        lay.addWidget(self.control)
        lay.addWidget(self.onOff)
        lay.addWidget(self.pid)

        self.setLayout(lay)


class Control(ControlGO):
    def __init__(self):
        super(Control, self).__init__()
        self.set_slots()

    def set_slots(self):
        #self.select.currentIndexChanged.connect(self._toggleControl)
        self.select.currentIndexChanged.connect(self._toggleControl)

    def get_data(self):
        data = {}
        if self.onOff.isEnabled():
            _type = {'On/Off':self.histeresis.value()}
        if self.pid.isEnabled():
            _type = {'pid':{'kp':self.kP.value(),
                            'ki':self.kI.value(),
                            'kd':self.kD.value()}}
        data['controlOn'] = {'sp': self.setPoint.value(),
                             'type':{_type}}
        return data

    def set_data(self, data):
        if data:
            self.control.setChecked(True)
            if data['type']['pid']:
                self.select.setCurrentIndex(1)
                self.pid.setEnabled(True)
                self.setPoint.setValue(data['sp'])
                self.kP.setValue(data['type']['pid']['kp'])
                self.kI.setValue(data['type']['pid']['ki'])
                self.kD.setValue(data['type']['pid']['kd'])
            elif data['type']['On/Off']:
                self.select.setCurrentIndex(0)
                self.onOff.setEnabled(True)
                self.setPoint.setValue(data['sp'])
                self.histeresis.setValue(data['type']['On/Off'])

    def _enableControl(self):
        if self.control.control.isChecked():
            self._toggleControl()
        elif not self.control.isChecked():
            self.pid.setEnabled(False)
            self.onOff.setEnabled(False)

    def _toggleControl(self):
        if self.select.currentIndex() == 0:
            self.pid.setEnabled(False)
            self.onOff.setEnabled(True and self.control.isChecked())
        if self.select.currentIndex() == 1:
            self.pid.setEnabled(True and self.control.isChecked())
            self.onOff.setEnabled(False)


class PenComboGO(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.init()

    def init(self):
        self.value = QDoubleSpinBox()
        self.value.setDecimals(1)
        #self.value.setSuffix(self._suffix)
        self.value.setButtonSymbols(QAbstractSpinBox.NoButtons)
        self.value.setReadOnly(True)
        self.value.setAlignment(Qt.AlignRight)

        self.colorPen = ColorButton()
        self.enablePen = QCheckBox()
        self.enablePen.setObjectName('enable')
        self.enablePen.setChecked(True)

        hValueLayout = QHBoxLayout()
        hValueLayout.addWidget(self.colorPen)
        hValueLayout.addSpacing(15)
        hValueLayout.addWidget(self.enablePen)
        hValueLayout.setAlignment(Qt.AlignJustify)

        mainValueLayout = QVBoxLayout()
        mainValueLayout.addWidget(self.value)
        mainValueLayout.addLayout(hValueLayout)

        self.setLayout(mainValueLayout)


class PenCombo(PenComboGO):
    def __init__(self):
        super(PenCombo, self).__init__()

    def get_data(self):
        return self.colorPen.text()

    def set_data(self, data):
        self.value.setSuffix(data['units'])
        self.colorPen.setColor(data['colorPen'])


class ControlComboGO(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent=parent)
        self.init()

    def init(self):
        self.action = QPushButton('Abrir')
        self.action.setObjectName('action')
        self.action.setMinimumSize(70, 27)
        self.stateLed = QLed(self, onColour=QLed.Green, offColour=QLed.Red)
        self.stateLed.setMaximumSize(27, 27)

        vContLayout = QVBoxLayout()
        vContLayout.addWidget(self.action)
        vContLayout.addWidget(self.stateLed)
        vContLayout.setAlignment(Qt.AlignRight)

        self.setLayout(vContLayout)


class ControlCombo(ControlComboGO):
    def __init__(self):
        super(ControlCombo, self).__init__()

    def set_slots(self):
        pass


class IndicatorGO(QTabWidget, Control, Comms, Config, ControlCombo, PenCombo):
    '''Indicator graphics object build the visual representation of the "analog" control.
    Config: at the time host, port of the hardware and the read register address. Write register is for control porpose.  '''
    # TODO: implement an alarm setup & it's popup system and logs.
    def __init__(self, parent=None, shape='Radial'):
        QTabWidget.__init__(self, parent=parent)
        self.setMaximumSize(320, 320)

        self._type = shape
        self.setupUi()

    def setupUi(self):

        self.frame = QGroupBox()

        mainLayout = QVBoxLayout()
        mainHLayout = QHBoxLayout()

        if not self._type == 'Pens':
            if self._type == 'Bar':
                self.gauge = AnalogGauge(typeOf=self._type)
                gaugeLayOut = QHBoxLayout()
                gaugeLayOut.addWidget(self.gauge, Qt.AlignHCenter)
                mainLayout.addLayout(gaugeLayOut)
            elif self._type == 'Radial':
                self.gauge = AnalogGauge(typeOf=self._type)
                mainLayout.addWidget(self.gauge)


            self.penCombo = PenCombo()
            self.controlCombo = ControlCombo()
            #mainHLayout.addLayout(mainValueLayout)
            mainHLayout.addWidget(self.penCombo)
            mainHLayout.addWidget(self.controlCombo)
            mainLayout.addLayout(mainHLayout)
            mainLayout.setAlignment(Qt.AlignRight)
        if self._type == 'Pens':
            self.penCombo1 = PenCombo()
            self.penCombo2 = PenCombo()
            self.penCombo3 = PenCombo()
            mainLayout.addWidget(self.penCombo1)
            mainLayout.addWidget(self.penCombo2)
            mainLayout.addWidget(self.penCombo3)


        self.frame.setLayout(mainLayout)
        self.setTabPosition(QTabWidget.West)
        self.addTab(self.frame, '')
        self.config = Config()
        self.addTab(self.config, 'Config')
        self.control = Control()
        self.addTab(self.control, 'Control')
        self.comms = Comms()
        self.addTab(self.comms, 'Comms')
        self.setTabEnabled(2,False)
        self.setTabEnabled(3,False)

        self.show()


class Indicator(IndicatorGO):
    def __init__(self):
        super(Indicator, self).__init__(shape='Bar')
        self.setMaximumSize(320, 320)
        self._toggle = False
        self.set_slots()
        self.timer = QTimer()
        self.comms_engine = CommsEngine()

    def set_slots(self):
        '''Set slots of indicator object'''
        self.config.alias.textChanged.connect(self._set_alias)
        self.penCombo.enablePen.stateChanged.connect(self.pushAction)
        self.controlCombo.action.pressed.connect(self.pushAction)
        self.config.advanced.pressed.connect(self._dialog)

    def _set_alias(self):
        self.frame.setTitle(self.config.alias.text())

    def update_value(self, value):
        '''
        udpate graphics object layout
        :param value: value to be updated
        :return:
        '''
        self.gauge.update_value(value)
        self.penCombo.value.setValue(value)

    def enableGraph(self):
        # TODO: implement EN/DIS graph control
        pass

    def _dialog(self):
        access_control = AccessControl()
        if access_control.access_request():
            self.timer.singleShot(60000, self._disable_config)
            self.setTabEnabled(2, True)
            self.setTabEnabled(3, True)

    def _disable_config(self):
        '''
        perform a disable action and focus on tab index 0 after self.timer timeout
        :return: nothing
        '''
        self.setCurrentIndex(0)
        self.setTabEnabled(2, False)
        self.setTabEnabled(3, False)

    def pushAction(self):
        _sender = self.sender()
        if _sender.objectName() == 'action' and _sender.text() == 'Abrir':
            _sender.setText('Cerrar')
            self._toggleLed()
            self.modBusAction()
        elif _sender.objectName() == 'action' and _sender.text() == 'Cerrar':
            _sender.setText('Abrir')
            self._toggleLed()
            self.modBusAction()
        elif _sender.objectName() == 'action' and _sender.text() == 'Auto':
            _sender.setText('Man')
            self._toggleLed()
            self._pidAutoMode()
        elif _sender.objectName() == 'action' and _sender.text() == 'Man':
            _sender.setText('Auto')
            self._toggleLed()
            self._pidAutoMode()
        print('action was pressed')
        if _sender.objectName() == 'enable':
            print(self._alias, 'pen enable is ', self.penCombo.enablePen.isChecked())

    def _toggleLed(self):
        self._toggle = not self._toggle
        self.controlCombo.stateLed.setValue(self._toggle)

    def modBusAction(self):
        '''
        performs one shot write action
        :return: nothing
        '''
        data = self.comms.get_data()
        self.comms_engine.client.host(self.comms.host.text())  # config modbus host
        self.comms_engine.client.port(self.comms.port.value())  # config modbus port
        self.comms_engine.writeTo([self.comms.addrWrite.value(), self._toggle])  # one shot value write action
        self.comms_engine.start()  # start task

    def _pidAutoMode(self):
        '''
        sets on pid control thread
        :return:
        '''
        self.pid.set_auto_mode(self._toggle)

    def setPid(self, const, sp):
        '''
        sets pid thread object
        :param const: list of pid constants [kp,ki,kd]
        :param sp: pid set point
        :return: nothing
        '''
        self.pid = PID(const['kp'], const['ki'], const['kd'], sp, 0.01, [0, 1023])

    def setDataConfig(self, _config):
        '''
        upload config file info and show up on the Indicator fields
        :param _config: sliced array of channels configuration
        :return: nothing
        '''
        #self._hashConfig = self.computeMD5hash(json.dumps(_config, sort_keys=True).encode("utf-8"))
        #print(self._hashConfig, _config)
        self.config = _config
        self._alias = self.config['alias']
        self.frame.setTitle(self.config['alias'])
        self.config = self.config['config']

        # check if control is "on"
        # if true fill the control frame with info
        # else show control checkbox frame disable
        if self.config['write']['controlOn']:
            self.controlCombo.action.setText('Auto')
            self._control = self.config['write']['controlOn']
            if self._control['type']['pid']:
                self.setPid(self._control['type']['pid'], self._control['sp'])
            if self._control['type']['On/Off']:
                pass
        else:
            self._control = False
            self.control.control.setChecked(self._control)

        ##################################################################
        # Fill everything with config info
        ##################################################################

        self._host = self.config['host']
        self._port = self.config['port']
        self._writer = [self.config['write']['addr'], self.config['write']['reg']]
        self._reader = [self.config['read']['addr'], self.config['read']['reg']]
        self._zero = self.config['read']['zero']
        self._span = self.config['read']['span']
        self._units = self.config['read']['units']
        self._colorPen = self.config['colorPen']

        self.comms.host.setText(self._host)
        self.comms.port.setValue(self._port)

        self.comms.addrRead.setValue(self._reader[0])
        self.comms.regRead.setValue(self._reader[1])

        self.comms.addrWrite.setValue(self._writer[0])
        self.comms.regWrite.setValue(self._writer[1])

        self.config.alias.setText(self._alias)

        self.config.zero.setValue(self._zero)
        self.gauge.set_MinValue(self._zero)

        self.config.span.setValue(self._span)
        self.gauge.set_MaxValue(self._span)

        self.config.units.setText(self._units)
        self.penCombo.value.setSuffix(self._units)

        self.penCombo.colorPen.setColor(self._colorPen)

        # check wich control type was choosen
        # then fill the info with it
        if self._control:
            self.control.control.setChecked(True)
            if self._control['type']['pid']:
                self.control.select.setCurrentIndex(1)
                self.control.pid.setEnabled(True)
                self.control.setPoint.setValue(self._control['sp'])
                self.control.kP.setValue(self._control['type']['pid']['kp'])
                self.control.kI.setValue(self._control['type']['pid']['ki'])
                self.control.kD.setValue(self._control['type']['pid']['kd'])
            elif self._control['type']['On/Off']:
                self.control.select.setCurrentIndex(0)
                self.control.onOff.setEnabled(True)
                self.control.setPoint.setValue(self._control['sp'])
                self.control.histeresis.setValue(self._control['type']['On/Off'])

    def get_data_config(self):
        '''
        retrieve all data displayed at the moment in GO class
        :param _config: sliced array of channels configuration
        :return: dict
        '''
        pass


if __name__ == '__main__':
    import sys
    app = QApplication([])
    indicator = Indicator()
    indicator.show()
    '''comms = Comms()
    comms.show()
    config = Config()
    config.show()
    control = Control()
    control.show()
    pencombo = PenCombo()
    pencombo.show()'''
    sys.exit(app.exec_())