### Analog graph demo ###
This demo reads the voltage on pin A0 once per second and graphs the voltage as a function of time. The graph data is just stored in your browser's memory; when the browser window is closed, the data is thrown out.

The [thermostat demo][1] is based on this demo, but it uses graphs 3 data series instead of 1. The [datalogger demo][2] is also similar, but it pulls its data from a SQLite database. 

The graph is created using a jQuery plugin called [jqPlot][3].

#### Warning ####

If your readings appear stuck at 3.3 V, it's probably because you haven't connected the ADREF pin to a reference. Try connecting it to 3.3 V or lower. Never connect it to anything above 3.3 V. It will burn out around 3.6 V.

[1]: /thermostat.html
[2]: /datalogger.html
[3]: http://www.jqplot.com/