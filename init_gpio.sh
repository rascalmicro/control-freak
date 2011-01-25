for pin in 64 65 66 67 68 69 70 71 72 73 96 97 98 99 100 101 
do
    echo $pin > /sys/class/gpio/export
    echo out > /sys/class/gpio/gpio$pin/direction
done
