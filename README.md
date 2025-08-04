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

<pre>  docker run -it --rm -e RUNTIME_NAME="KKK" -p 55555:55555 --name sdv-runtime ghcr.io/eclipse-autowrx/sdv-runtime:latest  </pre>


### Step 2: Configure Pi 5 status

#### Enable SPI

1. Open terminal and run:

<pre> sudo raspi-config </pre>

Choose **interface option** -> **SPI** -> **enable**.
Then, reopen terminal then execute

<pre> sudo nano /boot/config.txt </pre>

sudo raspi-config

Choose interface option -> SPI -> enable.
Then, reopen terminal then execute

<pre> sudo nano /boot/config.txt </pre>
 
Add **dtparam=spi=on** then press **ctrl + s** to save and **ctrl + x** to leave.
Make sure to reboot to save all the changes.

### Step 3: create a virtual environment by executing.

<pre>  
#create virtual enviroment         
python3 -m venv venv               

#activate the virtual environment  
source ./venv/bin/activate         
</pre>

Then install all the dependencies:

<pre>
# Upgrade pip first 
pip3 install --upgrade pip 

# Install kuksa_client (may require git or custom installation if not on PyPI) 
pip3 install kuksa-client 
  
# Install Adafruit Blinka to get 'board' module 
pip3 install adafruit-blinka 

# Install neopixel_spi driver
pip3 install adafruit-circuitpython-neopixel 
  
</pre>

**After that:** open thonny then choose **Tools**, scroll down and click on **Options…** . Then go to **Interpreter** and choose you **Python executable** which is your newly create virtual environment. When finish click **OK** to save.


## Step 4: run file **rgb_led.py**

<pre> 
from kuksa_client.grpc.aio import VSSClient  # Async gRPC client for KUKSA.val vehicle server
import asyncio                                # Async IO event loop

import board                                  # Hardware SPI interface on Raspberry Pi
import neopixel_spi as neopixel               # NeoPixel SPI driver

NUM_PIXELS = 60                              # Number of LEDs in the NeoPixel strip
PIXEL_ORDER = neopixel.GRB                   # Pixel color byte order (Green-Red-Blue)

last_state = None                            # Track last known ambient light state (on/off)
base_colour = 0xFF0000                       # Default base color (red) as 24-bit integer
base_inten = 100                             # Default intensity value (percentage)

spi = board.SPI()                            # Initialize SPI bus

pixels = neopixel.NeoPixel_SPI(
    spi,
    NUM_PIXELS,
    pixel_order=PIXEL_ORDER,
    auto_write=False                         # Update LEDs only when show() is called
)

def apply_intensity(color, intensity):
    intensity = max(0.0, min(1.0, intensity))  # Clamp intensity between 0.0 and 1.0
    r = int(((color >> 16) & 0xFF) * intensity)  # Scale red channel by intensity
    g = int(((color >> 8) & 0xFF) * intensity)   # Scale green channel by intensity
    b = int((color & 0xFF) * intensity)          # Scale blue channel by intensity
    return (r << 16) | (g << 8) | b              # Recombine channels into 24-bit color int

async def main():
    while True: 
        async with VSSClient('localhost', 55555) as client:  # Connect to KUKSA server
            ambient = await client.get_current_values([      # Request multiple datapoints
                'Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.IsLightOn',
                'Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Color',
                'Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Intensity'
            ])
            state_detect = ambient.get('Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.IsLightOn')  # Get on/off state
            
            color_detect = ambient.get('Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Color')      # Get color value
            inten_detect = ambient.get('Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Intensity')  # Get intensity value
        
            asyncio.create_task(display(state_detect, color_detect, inten_detect))  # Run display update asynchronously
           
            
async def display(stateD, colorD, intenD):
    global last_state, base_colour, base_inten
    colour = getattr(colorD, 'value')                  # Extract color hex string (e.g. '#FF0000')
    colour = int(colour.lstrip('#'), 16)               # Convert hex string to integer
    inten = getattr(intenD, 'value') / 100             # Normalize intensity to 0.0-1.0
    if stateD is not None or colorD is not None:       # Check datapoints are valid
        state = getattr(stateD, 'value')                # Extract boolean on/off state
        if last_state != state:                          # Only update if state changed
            print(f"Ambient Light is {'On' if state else 'Off'}")
            base_colour = colour
            if state:
                pixels.fill(apply_intensity(base_colour, base_inten))  # Fill LEDs with adjusted color
                #pixels.fill(base_colour)  # (Commented out alternative: fill without intensity)
            else:
                pixels.fill(0)  # Turn off LEDs
            pixels.show()
            last_state = state
        elif last_state:  # If still on, check for color or intensity changes
            if base_colour != colour:
                #print(f"Ambient Lights change from {base_colour} to {colour}")
                base_colour = colour
                pixels.fill(base_colour)  # Update color without intensity adjustment
                pixels.show()
            elif base_inten != inten:
                #print(f"Ambient Lights intensity is set from {base_inten} to {inten}")
                base_inten = inten
                pixels.fill(apply_intensity(base_colour, base_inten))  # Update color with new intensity
                pixels.show()
    else:
        print("Error: datapoint is None")  # Handle missing datapoints gracefully


asyncio.run(main())  # Start async main event loop


</pre>
