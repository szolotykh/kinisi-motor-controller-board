EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 2 3
Title "Power"
Date "05/14/2001"
Rev "1"
Comp "VsReality "
Comment1 "TPS54331 breakout"
Comment2 "DC-DC Converter"
Comment3 "Input 5V - 12V"
Comment4 "Output 3.3V"
$EndDescr
$Comp
L VsReality_Symbols:TPS54331DDAR U201
U 1 1 608F85D2
P 4850 3100
F 0 "U201" H 4975 3515 50  0000 C CNN
F 1 "TPS54331DDAR" H 4975 3424 50  0000 C CNN
F 2 "Package_SO:HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm_ThermalVias" H 4750 3150 50  0001 C CNN
F 3 "" H 4750 3150 50  0001 C CNN
F 4 "C90761" H 4850 3100 50  0001 C CNN "LCSC Part #"
	1    4850 3100
	1    0    0    -1  
$EndComp
$Comp
L power:GND #PWR0203
U 1 1 60901F20
P 5700 3750
F 0 "#PWR0203" H 5700 3500 50  0001 C CNN
F 1 "GND" H 5705 3577 50  0000 C CNN
F 2 "" H 5700 3750 50  0001 C CNN
F 3 "" H 5700 3750 50  0001 C CNN
	1    5700 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	5400 3300 5700 3300
Wire Wire Line
	5700 3300 5700 3400
Wire Wire Line
	5400 3400 5700 3400
Connection ~ 5700 3400
Wire Wire Line
	5700 3400 5700 3750
Wire Wire Line
	3150 3350 3150 3750
Connection ~ 5700 3750
$Comp
L power:+3.3V #PWR0201
U 1 1 6090281B
P 7750 2900
F 0 "#PWR0201" H 7750 2750 50  0001 C CNN
F 1 "+3.3V" H 7765 3073 50  0000 C CNN
F 2 "" H 7750 2900 50  0001 C CNN
F 3 "" H 7750 2900 50  0001 C CNN
	1    7750 2900
	1    0    0    -1  
$EndComp
Wire Wire Line
	5400 3050 5700 3050
Wire Wire Line
	7750 3050 7750 2900
$Comp
L Connector:TestPoint_Small 3.3V201
U 1 1 6090A6A0
P 7850 3050
AR Path="/608F63EA/6090A6A0" Ref="3.3V201"  Part="1" 
AR Path="/6090A6A0" Ref="3.3V201"  Part="1" 
F 0 "3.3V201" H 7898 3096 50  0000 L CNN
F 1 "TestPoint_Small" H 7898 3005 50  0000 L CNN
F 2 "TestPoint:TestPoint_Pad_D1.5mm" H 8050 3050 50  0001 C CNN
F 3 "~" H 8050 3050 50  0001 C CNN
	1    7850 3050
	1    0    0    -1  
$EndComp
Wire Wire Line
	7750 3050 7850 3050
Wire Wire Line
	5400 2950 5450 2950
Wire Wire Line
	5450 2950 5450 2650
Wire Wire Line
	5450 2650 5700 2650
Wire Wire Line
	5700 2650 5700 2750
Wire Wire Line
	5700 2950 5700 3050
Connection ~ 5700 3050
$Comp
L Device:C_Small C201
U 1 1 6090DCD2
P 5700 2850
F 0 "C201" H 5792 2896 50  0000 L CNN
F 1 "100nf" H 5792 2805 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 5700 2850 50  0001 C CNN
F 3 "~" H 5700 2850 50  0001 C CNN
F 4 "C1525" H 5700 2850 50  0001 C CNN "LCSC Part #"
	1    5700 2850
	1    0    0    -1  
$EndComp
$Comp
L Device:C_Small C202
U 1 1 6090E47B
P 3150 3250
F 0 "C202" H 3242 3296 50  0000 L CNN
F 1 "10uf" H 3242 3205 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 3150 3250 50  0001 C CNN
F 3 "~" H 3150 3250 50  0001 C CNN
F 4 "C13585" H 3150 3250 50  0001 C CNN "LCSC Part #"
	1    3150 3250
	1    0    0    -1  
$EndComp
NoConn ~ 4550 3050
$Comp
L Device:D_Schottky_Small D201
U 1 1 609140A9
P 6150 3150
F 0 "D201" V 6104 3220 50  0000 L CNN
F 1 "B5819W" V 6195 3220 50  0000 L CNN
F 2 "Diode_SMD:D_SOD-123" V 6150 3150 50  0001 C CNN
F 3 "~" V 6150 3150 50  0001 C CNN
F 4 "C8598" H 6150 3150 50  0001 C CNN "LCSC Part #"
	1    6150 3150
	0    1    1    0   
$EndComp
$Comp
L power:GND #PWR0202
U 1 1 60914FF6
P 6450 3400
F 0 "#PWR0202" H 6450 3150 50  0001 C CNN
F 1 "GND" H 6455 3227 50  0000 C CNN
F 2 "" H 6450 3400 50  0001 C CNN
F 3 "" H 6450 3400 50  0001 C CNN
	1    6450 3400
	1    0    0    -1  
$EndComp
Wire Wire Line
	5700 3050 6150 3050
$Comp
L Device:L_Small L201
U 1 1 6091955E
P 6600 3050
F 0 "L201" V 6785 3050 50  0000 C CNN
F 1 "10uH" V 6694 3050 50  0000 C CNN
F 2 "Inductor_SMD:L_Sunlord_MWSA0518_5.4x5.2mm" H 6600 3050 50  0001 C CNN
F 3 "~" H 6600 3050 50  0001 C CNN
F 4 "C139506" H 6600 3050 50  0001 C CNN "LCSC Part #"
	1    6600 3050
	0    -1   -1   0   
$EndComp
Connection ~ 7750 3050
$Comp
L Device:R_Small R201
U 1 1 6091B3E4
P 7550 3250
F 0 "R201" H 7609 3296 50  0000 L CNN
F 1 "10K" H 7609 3205 50  0000 L CNN
F 2 "Resistor_SMD:R_0402_1005Metric" H 7550 3250 50  0001 C CNN
F 3 "~" H 7550 3250 50  0001 C CNN
F 4 "C25744" H 7550 3250 50  0001 C CNN "LCSC Part #"
	1    7550 3250
	1    0    0    -1  
$EndComp
$Comp
L Device:R_Small R203
U 1 1 6091B6F7
P 7550 3550
F 0 "R203" H 7609 3596 50  0000 L CNN
F 1 "3.3K" H 7609 3505 50  0000 L CNN
F 2 "Resistor_SMD:R_0402_1005Metric" H 7550 3550 50  0001 C CNN
F 3 "~" H 7550 3550 50  0001 C CNN
F 4 "C25890" H 7550 3550 50  0001 C CNN "LCSC Part #"
	1    7550 3550
	1    0    0    -1  
$EndComp
Wire Wire Line
	7550 3050 7550 3150
Connection ~ 7550 3050
Wire Wire Line
	7550 3050 7750 3050
Wire Wire Line
	5400 3200 5850 3200
Wire Wire Line
	4550 3300 4400 3300
$Comp
L Device:C_Small C203
U 1 1 6091EC9C
P 3600 3600
F 0 "C203" H 3692 3646 50  0000 L CNN
F 1 "10nf" H 3692 3555 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 3600 3600 50  0001 C CNN
F 3 "~" H 3600 3600 50  0001 C CNN
F 4 "C57112" H 3600 3600 50  0001 C CNN "LCSC Part #"
	1    3600 3600
	1    0    0    -1  
$EndComp
Wire Wire Line
	3150 3750 3600 3750
$Comp
L Device:R_Small R202
U 1 1 6092124E
P 4000 3600
F 0 "R202" H 4059 3646 50  0000 L CNN
F 1 "30K" H 4059 3555 50  0000 L CNN
F 2 "Resistor_SMD:R_0603_1608Metric" H 4000 3600 50  0001 C CNN
F 3 "~" H 4000 3600 50  0001 C CNN
F 4 "C22984" H 4000 3600 50  0001 C CNN "LCSC Part #"
	1    4000 3600
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 3700 4000 3750
$Comp
L Device:C_Small C205
U 1 1 6091D5FD
P 4400 3600
F 0 "C205" H 4492 3646 50  0000 L CNN
F 1 "8.2nF" H 4492 3555 50  0000 L CNN
F 2 "Capacitor_SMD:C_0603_1608Metric" H 4400 3600 50  0001 C CNN
F 3 "~" H 4400 3600 50  0001 C CNN
F 4 "C27920" H 4400 3600 50  0001 C CNN "LCSC Part #"
	1    4400 3600
	1    0    0    -1  
$EndComp
Wire Wire Line
	4400 3300 4400 3500
Wire Wire Line
	4400 3700 4400 3750
Connection ~ 4400 3750
Wire Wire Line
	4400 3750 5700 3750
Connection ~ 4000 3750
Wire Wire Line
	4000 3750 4400 3750
Wire Wire Line
	4000 3250 4000 3200
Wire Wire Line
	4000 3200 4550 3200
Wire Wire Line
	3600 3500 3600 3200
Wire Wire Line
	3600 3200 4000 3200
Connection ~ 4000 3200
Wire Wire Line
	3600 3700 3600 3750
Connection ~ 3600 3750
Wire Wire Line
	3600 3750 4000 3750
Text Notes 7100 2700 0    50   ~ 0
POWER INDUCTORS should be 6.8uH
Wire Wire Line
	7550 3750 7550 3650
$Comp
L Device:C_Small C206
U 1 1 60A121EF
P 6800 3250
F 0 "C206" H 6892 3296 50  0000 L CNN
F 1 "47uF" H 6892 3205 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 6800 3250 50  0001 C CNN
F 3 "~" H 6800 3250 50  0001 C CNN
F 4 "C96123" H 6800 3250 50  0001 C CNN "LCSC Part #"
	1    6800 3250
	1    0    0    -1  
$EndComp
Wire Wire Line
	7550 3350 7550 3400
Wire Wire Line
	7550 3400 7400 3400
Connection ~ 7550 3400
Wire Wire Line
	7550 3400 7550 3450
Wire Wire Line
	6150 3050 6500 3050
Connection ~ 6150 3050
Wire Wire Line
	6700 3050 6800 3050
$Comp
L Device:C_Small C207
U 1 1 60A19378
P 7150 3250
F 0 "C207" H 7242 3296 50  0000 L CNN
F 1 "47uF" H 7242 3205 50  0000 L CNN
F 2 "Capacitor_SMD:C_1206_3216Metric" H 7150 3250 50  0001 C CNN
F 3 "~" H 7150 3250 50  0001 C CNN
F 4 "C96123" H 7150 3250 50  0001 C CNN "LCSC Part #"
	1    7150 3250
	1    0    0    -1  
$EndComp
Wire Wire Line
	6800 3050 6800 3150
Connection ~ 6800 3050
Wire Wire Line
	6800 3050 7150 3050
Wire Wire Line
	7150 3050 7150 3150
Connection ~ 7150 3050
Wire Wire Line
	7150 3050 7550 3050
Wire Wire Line
	6150 3250 6150 3400
Wire Wire Line
	6150 3400 6450 3400
Wire Wire Line
	7150 3400 7150 3350
Connection ~ 6450 3400
Wire Wire Line
	6450 3400 6800 3400
Wire Wire Line
	6800 3350 6800 3400
Connection ~ 6800 3400
Wire Wire Line
	6800 3400 7150 3400
$Comp
L power:GND #PWR0204
U 1 1 60A1CAD5
P 7550 3750
F 0 "#PWR0204" H 7550 3500 50  0001 C CNN
F 1 "GND" H 7555 3577 50  0000 C CNN
F 2 "" H 7550 3750 50  0001 C CNN
F 3 "" H 7550 3750 50  0001 C CNN
	1    7550 3750
	1    0    0    -1  
$EndComp
Wire Wire Line
	5850 3700 7400 3700
Wire Wire Line
	5850 3200 5850 3700
Wire Wire Line
	7400 3400 7400 3700
Text Notes 3600 3900 0    50   ~ 0
10nF=>4ms slow start
Wire Wire Line
	3150 2950 4550 2950
Wire Wire Line
	3150 2950 3100 2950
Connection ~ 3150 2950
Wire Wire Line
	3150 2950 3150 3150
Text GLabel 3100 2950 0    50   Input ~ 0
BACK_IN
$Comp
L Device:C_Small C204
U 1 1 6091E757
P 4000 3350
F 0 "C204" H 4092 3396 50  0000 L CNN
F 1 "1nF" H 4092 3305 50  0000 L CNN
F 2 "Capacitor_SMD:C_0402_1005Metric" H 4000 3350 50  0001 C CNN
F 3 "~" H 4000 3350 50  0001 C CNN
F 4 "C1523" H 4000 3350 50  0001 C CNN "LCSC Part #"
	1    4000 3350
	1    0    0    -1  
$EndComp
Wire Wire Line
	4000 3450 4000 3500
$EndSCHEMATC
