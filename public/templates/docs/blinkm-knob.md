BlinkM Knob Demo
================

--

BlinkM is a smart LED manufactured by [ThingM][tm].
It has a two-wire serial (I2C) interface and is capable of displaying any 24-bit RGB
or HSB color, fading between colors and running built-in light scripts.
This demo allows you to set RGB levels and brightness using the
[jQuery Knob][jqk] plugin and controls the BlinkM via I2C commands
sent from JavaScript using JSON to Pytronics.

The BlinkM can be directly connected to a Rascal:

![Diagram](/static/images/docs/BlinkM-Rascal.png)

#### Example Code
This program communicates with the BlinkM via the two-wire I2C interface using
JavaScript POST requests to Pytronics. For example, to set a new color, the function
`fadeToRGB` is called with new settings from the RGB knobs:

    function fadeToRGB(r, g, b) {
        "use strict";
        var params = {
            addr: BLINKM,
            reg: 0x63,
            value: [r, g, b],
            size: 'I'
        };
        writeToBlinkM(params);
    }

This function sets up a `params` object with the following properties:

<table class="table table-condensed">
<tr><th>Name</th><th>Value</th></tr>
<tr><td>addr</td><td>The I2C address of the BlinkM (0x09)</td></tr>
<tr><td>reg</td><td>The BlinkM command "Fade to RGB Color" ('c' or 0x63)</td></tr>
<tr><td>value</td><td>An array containing the RGB arguments</td></tr>
<tr><td>size</td><td>'I' tells Pytronics to transmit the values using an I2C block transfer</td></tr>
</table>

The params object is passed to the function `writeToBlinkM` which encodes it as JSON and sends
it to Pytronics with jQuery $.post:

    function writeToBlinkM(params) {
        "use strict";
        $.post('/i2c_write', { params: JSON.stringify(params) }, function (response) {
            var result = JSON.parse(response);
            if (result.success) {
                console.log('i2c_write: success');
            } else {
                console.log('i2c_write: [' + result.errorCode + '] ' + result.errorMessage);
            }
        }).error(function (jqXHR, textStatus, errorThrown) {
            console.log('i2c_write: ' + textStatus + ': ' + errorThrown);
        });
    }

Pytronics parses the JSON params argument into a Python dictionary and sends the "Fade to RGB Color"
command to the BlinkM.

#### Error Handling
I2C errors are passed back to the caller and the above example demonstrates how to handle them.
The $.post command has a completion function with parameter `response` which
receives a JSON encoded value when the Pytronics `i2c_write` function completes. After parsing this value into
JavaScript object `result`, you can test property `result.success`. If true, the I2C write completed successfully.
If false, the properties `result.errorCode` and `result.errorMessage` provide the details of the error. For example,
if a BlinkM isn't connected, the response will be:

    {"errorCode": "ENXIO", "errorMessage": "No such device or address", "success": false} 

An unexpected error results in the $.post().error method being called, the values of arguments `textStatus`
and `errorThrown` being received from the Flask framework by jQuery. For example:

    i2c_write: error: INTERNAL SERVER ERROR

where the value of `errorThrown` depends on the numeric error code returned by the Flask function `i2c_write` in server.py.

<div><small>Last update Oct 30 2012</small></div>

[tm]: http://thingm.com/products/blinkm.html
[jqk]: https://github.com/aterrien/jQuery-Knob
