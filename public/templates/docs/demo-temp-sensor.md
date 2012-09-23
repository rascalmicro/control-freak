TMP102 Temperature Sensor
=========================

--

The TMP102 is a tiny digital temperature sensor manufactured by [Texas Instruments][ti].
It has a two-wire serial interface and is capable of reading temperatures between
-25&#176;C and +85&#176;C to an accuracy of 0.5&#176;C.

 A break-out board for the TMP102 is available from [SparkFun Electronics][sf].
 As well as the chip itself, this includes pull-up resistors and a filtering
 capacitor, with the result that it can be directly connected to a Rascal:

![Diagram](/static/images/docs/TMP102-Rascal.png)

Note that the address pin ADD0 should be zero (i.e. connected to GND) for the TMP102
to appear at its default address 0x48.

With the break-out board connected as above, clicking the **Read temperature** button
should display the reading from the TMP102 in the blue panel:

![Result](/static/images/docs/demo-temp.png)

--

#### Example Code
The Rascal communicates with the TMP102 via a two-wire serial interface (also known as I2C)
where the clock line is SCL and the data sent or received on SDA. Reading the temperature
from the TMP102 with Pytronics library functions is straightforward.

If you are new to this, the [test-i2c][i2c] page is a good place to start:

1. The bus scan should show `48` indicating that the TMP102 has been detected at I2C address 0x48.
2. Click `48` to enter it as the **Chip address**
3. With the transfer size set to Byte, click **Read**

    _The Read result (decimal) is the temperature in whole degrees (e.g. 19)_

4. Change the transfer size to Word and click **Read** again

    _The Read result is now a 16-bit number (e.g. 0xb013 in hexadecimal),
    where the lower byte is whole degrees and the top four bits of the upper
    byte the fractional part in sixteenths of a degree_

The demo program reads the temperature data via a JavaScript call to the Pytronics `/i2cget/` URL:

    $.get('/i2cget/0x48/0/W', function (data) {
        ...
    }

This returns a 16-bit value as described above in `data`
which is converted into a decimal fraction as follows:

    var degrees, fraction, strTemp;
    // Whole degrees are returned in the low byte
    degrees = data & 0xff;
    // The fraction is in the top four bits
    fraction = (data >> 12) / 16.0;
    // Round the fraction to one decimal place
    fraction = Math.round(fraction * 10) / 10;
    // Compose string for display
    strTemp = (degrees + fraction).toString();


See the [TMP102 Data Sheet][tids] for more information.

[ti]: http://www.ti.com/product/tmp102
[tids]: http://www.ti.com/lit/ds/symlink/tmp102.pdf
[sf]: https://www.sparkfun.com/products/9418
[i2c]: /test-i2c.html
