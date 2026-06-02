import time
import sys

# Try RPLCD (HD44780 I2C backpack)
try:
    from RPLCD.i2c import CharLCD
    HAS_RPLCD = True
except Exception:
    HAS_RPLCD = False

# Try CircuitPython character LCD
try:
    import board
    import busio
    from adafruit_character_lcd.character_lcd_i2c import Character_LCD_I2C
    HAS_ADA_LCD = True
except Exception:
    HAS_ADA_LCD = False

# DHT
try:
    import adafruit_dht
    HAS_DHT = True
except Exception:
    HAS_DHT = False

# Default config
I2C_ADDR = 0x27
COLS = 16
ROWS = 2
DHT_PIN = 27

SCROLL_TEXT = 'Shooters'


def init_lcd(i2c_addr=I2C_ADDR, cols=COLS, rows=ROWS):
    if HAS_RPLCD:
        lcd = CharLCD(i2c_expander='PCF8574', address=i2c_addr, cols=cols, rows=rows)
        return lcd, 'rplcd'
    if HAS_ADA_LCD:
        i2c = busio.I2C(board.SCL, board.SDA)
        lcd = Character_LCD_I2C(i2c, cols, rows, address=i2c_addr)
        return lcd, 'adafruit'
    raise SystemExit('No supported LCD library found. Install RPLCD or adafruit_character_lcd')


def read_temperature_once(pin=DHT_PIN):
    if not HAS_DHT:
        return None, None, 'adafruit_dht not installed'
    try:
        import board as _board
        pin_attr = getattr(_board, f'D{pin}', None)
        if pin_attr is None:
            return None, None, f'board has no D{pin} attribute'
        sensor = adafruit_dht.DHT11(pin_attr)
        try:
            t = sensor.temperature
            h = sensor.humidity
        finally:
            try:
                sensor.exit()
            except Exception:
                pass
        return t, h, None
    except Exception as e:
        return None, None, str(e)


def scroll_text(lcd, text, row=0, delay=0.3):
    cols = COLS
    if len(text) <= cols:
        lcd.cursor_pos = (row, 0)
        lcd.write_string(text.ljust(cols))
        return
    padding = ' ' * cols
    s = padding + text + padding
    for i in range(len(text) + cols + 1):
        segment = s[i:i+cols]
        lcd.cursor_pos = (row, 0)
        lcd.write_string(segment)
        time.sleep(delay)


def main():
    lcd, kind = init_lcd()
    print(f'Initialized LCD with {kind}')
    try:
        while True:
            # Display scrolling title on first row
            scroll_text(lcd, SCROLL_TEXT, row=0, delay=0.25)
            # Read temperature once and show on second row
            t, h, err = read_temperature_once()
            if err:
                line2 = f'Err: {err}'[:COLS]
            else:
                if t is None:
                    line2 = 'Temp: N/A'.ljust(COLS)
                else:
                    line2 = f'Temp:{t:.1f}C Hum:{(h if h is not None else "N/A")}'[:COLS]
            lcd.cursor_pos = (1, 0)
            lcd.write_string(line2.ljust(COLS))
            # small pause before next cycle
            time.sleep(1)
    except KeyboardInterrupt:
        try:
            lcd.clear()
        except Exception:
            pass
        print('Exiting')


if __name__ == '__main__':
    main()
