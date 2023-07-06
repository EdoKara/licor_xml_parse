# licor_xml_parse
Reads the XML datastream of a LI-840A CO2 analyzer and outputs it to CSVs through pandas. Likely works with any LI-COR which has similar XML output scheme. 

This is a basic script that's meant to help read LI-COR data without relying on the application, if there's some issue with dependencies or concern
about reliability (like there was in my case). 

## Operation

**make sure you plug in the li-cor first before operating so that pyserial has a USB port to look for.**

In the code, modify 
```
portpath = "YOUR_PORT_PATH"
```
to the correct portpath. Linux-likes are usually `\dev\ttyUSB#` format while windows uses form `COM#`. 
Ensure that your serial refresh rates & baud rates are all correct (default is 9600 and a 1s timeout but depending on your data 
frequency you'll need to do a faster/slower timeout on the port). 

`export_interval` controls the length (in s) between data exports from the monitor. 
`filepath` controls the path to the folder that will contain exported CSVs from this program. 

the program will run indefinitely in terminal and provides a timestamped "successful export" message each time it outputs data.
`ctrl+c` stops the program and exports the remaining buffer of data to the specified folder. 
