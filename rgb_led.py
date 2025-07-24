from kuksa_client.grpc.aio import VSSClient
import asyncio

import board
import neopixel_spi as neopixel

NUM_PIXELS = 60
PIXEL_ORDER = neopixel.GRB

last_state = None
base_colour = 0xFF0000
base_inten = 100


spi = board.SPI()

pixels = neopixel.NeoPixel_SPI(
    spi,
    NUM_PIXELS,
    pixel_order=PIXEL_ORDER,
    auto_write=False
)

def apply_intensity(color, intensity):
    intensity = max(0.0, min(1.0, intensity))
    r = int(((color >> 16) & 0xFF) * intensity)
    g = int(((color >> 8) & 0xFF) * intensity)
    b = int((color & 0xFF) * intensity)
    return (r << 16) | (g << 8) | b

async def main():
    while True: 
        async with VSSClient('localhost', 55555) as client:
            
            ambient = await client.get_current_values([
                'Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.IsLightOn',
                'Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Color',
                'Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Intensity'
            ])
            state_detect = ambient.get('Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.IsLightOn')
            
            color_detect = ambient.get('Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Color')
            inten_detect = ambient.get('Vehicle.Cabin.Light.AmbientLight.Row1.DriverSide.Intensity')
        
            asyncio.create_task(display(state_detect, color_detect, inten_detect))
           
            
async def display(stateD, colorD, intenD):
    global last_state, base_colour, base_inten
    colour = getattr(colorD, 'value')
    colour = int(colour.lstrip('#'), 16)
    inten = getattr(intenD, 'value') / 100
    if stateD is not None or colorD is not None:
        state = getattr(stateD, 'value')
        if last_state != state:
            print(f"Ambient Light is {'On' if state else 'Off'}")
            base_colour = colour
            if state:
                pixels.fill(apply_intensity(base_colour, base_inten))
                #pixels.fill(base_colour)
            else:
                pixels.fill(0)  
            pixels.show()
            last_state = state
        elif last_state:
            if base_colour != colour:
                #print(f"Ambient Lights change from {base_colour} to {colour}")
                base_colour = colour
                pixels.fill(base_colour)
                pixels.show()
            elif base_inten != inten:
                #print(f"Ambient Lights intensity is set from {base_inten} to {inten}")
                base_inten = inten
                pixels.fill(apply_intensity(base_colour, base_inten))
                pixels.show()
    else:
        print("Error: datapoint is None")


asyncio.run(main())