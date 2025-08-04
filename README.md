# dreamKIT to NeoPixel without CAN

In this part, you will learn how to set up the connection to control NeoPixels.


## Hardware Requirements

- Raspberry Pi 5
- NeoPixel RGB LED WS2812
- Jumper wires

## Software Requirements

- Thonny IDE
- Libraries:
  - `kuksa_client`
  - `board`
  - `neopixel_spi`
  - `docker`


## Workflow

To enable control of NeoPixels through Playground, the Raspberry Pi 5 needs to run Docker for `sdv-runtime`, which acts as a bridge between the Pi 5 and Playground.  
If the connection is successful, the Python script will be able to receive Playground values and change the NeoPixels' status accordingly.


## Wiring

| Raspberry Pi 5   | NeoPixels        |
| ---------------- | ---------------- |
| 5V               | 5V               |
| GND              | GND              |
| GPIO 11 / GPIO 10| Din              |


## Step-by-Step Guide

### Step 2: Configure Pi 5 status

#### Enable SPI

1. Open terminal and run:

    

### Step 1: Run the sdv-runtime natively on Pi 5

