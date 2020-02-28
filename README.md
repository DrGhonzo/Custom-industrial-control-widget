# Custom Industrial Control Widget
Full custom Industrial shape widget for control and visualization process

## Brief
This script encapsulate diferent control widgets with multiple inheritance.
get_data will retrieve the collected data of each custom widget.
set_data(data) will fill the information on data.
  ### Note: 
  data is a dict, so is imperative to parse a parameter with same shape or in case build it's one.
  
Also this group classes were created with porpose of work in multithreading joined to a Modbus communication engine.
## Todo:
  +Implement threaded modbus communications engine.
  +Implement Save data in a .json file and upload data file and parse to custom widgets.
  +Implement access control slot for advanced settings control access.
  +Implement Bar gauge needle animation.
  +Implement alarms settings and needle visualization.
  
## Features
## Main Tab
+ Radial or Bar shape full colour gauge.
+ Live value of measurement.
+ Colorpicker button (trend).
+ Checkbox control (trend).
## Second Tab (Config)
+ Alias line edit to name the control.
+ Zero edit value for measuring and control porposes.
+ Span edit value for measuring and control porposes.
+ Units line edit for measuring and control porposes.
+ Avanzado button to unlock advanced settings.
## Third Tab (Control)
+ Habilitar checkbox for ENABLE/DISABLE control features.
+ Set point value edit for On/Off or PID control porposes.
+ Type combobox for choose a type On/Off or PID control.
+ Hist value edit for On/Off control porposes.
+ kP, Ki, KD value edit for PID type control setting values.
## Fourth Tab (Comms)
+ Host line edit for network settings.
+ Port value edit for network settings.
+ Read and Write addr, reg respectly for read and wirte communications.
