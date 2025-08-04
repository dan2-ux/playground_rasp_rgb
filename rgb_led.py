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
