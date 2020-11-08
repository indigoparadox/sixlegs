
from machine import ADC
from machine import I2C
from sgp30 import SGP30
from pixy import CMUcam5

DEBUG = False

def wheel( pos ):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)

from neopixel import NeoPixel
import time

RANGE_MAX = 2000
RANGE_THRESH = 700

np = NeoPixel( Pin( 27 ), 1 )
adc = ADC( Pin( 36 ) )
adc.read()
adc.atten( ADC.ATTN_11DB )
i2c = I2C( scl=Pin( 22 ), sda=Pin( 21 ), freq=100000 )
sgp = SGP30( i2c )
px = CMUcam5( i2c )
#px.set_led( 0, 255, 0 )
counter = 0
while True:
    for rc_index in range( 255 ):
        # Grab front rangefinder distance.
        r = adc.read()

        # Detect visual objects (blocks) from PixyCam.
        try:
            blks = px.get_blocks( 1, 1 )
        except OSError as e:
            # Sometimes we fail for some reason.
            print( e )

        # Figure out what to do with LED.
        if r > RANGE_THRESH:
            # Change LED if obstacle in range.
            if r > RANGE_MAX:
                # Sanity cap so that cross-multiply below works.
                r = RANGE_MAX
            new_col = int( 255 * r / RANGE_MAX )
            np[0] = (255, 255 - new_col, 255 - new_col)

        elif len( blks ) > 0:
            # Blink LED if objects found.
            if counter > 5000:
                counter = 0
                np[0] = (0, 255, 0)
            elif counter > 2500:
                np[0] = (0, 255, 0)
            else:
                np[0] = (255, 255, 255)

            if DEBUG:
                print( '---blk found---' )
                print( 'sig: {}'.format( blks[0].sig ) )
                print( 'x: {}'.format( blks[0].x ) )
                print( 'y: {}'.format( blks[0].y ) )
                print( 'idx: {}'.format( blks[0].idx ) )
                print( '---end blk---' )

        else:
            # Cycle through rainbow if nothing else going on.
            np[0] = wheel( rc_index & 255 )

        #print( sgp.indoor_air_quality )

        # Perform housekeeping for this loop iter (write LED, sleep, etc.)
        np.write()
        counter += 1
        time.sleep_ms( 25 )
