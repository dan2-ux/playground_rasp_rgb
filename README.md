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

### Step 1: Run the sdv-runtime natively on Pi 5

## Docker Run Command

To start the SDV runtime, use the following command:

```bash
docker run -it --rm -e RUNTIME_NAME="KKK" -p 55555:55555 --name sdv-runtime ghcr.io/eclipse-autowrx/sdv-runtime:latest ```bash


### Step 2: Configure Pi 5 status

#### Enable SPI

1. Open terminal and run:

| ```bash<br> sudo raspi-config <br>```  |

Choose **interface option** -> **SPI** -> **enable**.
Then, reopen terminal then execute

| sudo nano /boot/config.txt |

sudo raspi-config

Choose interface option -> SPI -> enable.
Then, reopen terminal then execute
sudo nano /boot/config.txt
 
Add **dtparam=spi=on** then press **ctrl + s** to save and **ctrl + x** to leave.
Make sure to reboot to save all the changes.

### Step 3: create a virtual environment by executing.

| #create virtual enviroment         |  
| python3 -m venv venv               |
||
| #activate the virtual environment  |
| source ./venv/bin/activate         |

Then install all the dependencies:


| # Upgrade pip first |
| pip3 install --upgrade pip |
||
| # Install kuksa_client (may require git or custom installation if not on PyPI) |
| pip3 install kuksa-client |
||
| # Install Adafruit Blinka to get 'board' module |
| pip3 install adafruit-blinka |
| |
| # Install neopixel_spi driver|
|pip3 install adafruit-circuitpython-neopixel |



