import argparse

try:
    from gpiozero import LED
except ImportError:
    raise SystemExit('gpiozero is required. Install it with: pip install gpiozero')


def main():
    parser = argparse.ArgumentParser(description='Control an LED on a Raspberry Pi GPIO pin.')
    parser.add_argument('action', choices=['on', 'off', 'toggle', 'status'], help='Action to perform')
    parser.add_argument('--pin', type=int, default=17, help='GPIO pin number for the LED (default: 17)')
    args = parser.parse_args()

    led = LED(args.pin)

    if args.action == 'on':
        led.on()
        print(f'LED on GPIO {args.pin} is now ON')
    elif args.action == 'off':
        led.off()
        print(f'LED on GPIO {args.pin} is now OFF')
    elif args.action == 'toggle':
        if led.is_lit:
            led.off()
            print(f'LED on GPIO {args.pin} was ON, now OFF')
        else:
            led.on()
            print(f'LED on GPIO {args.pin} was OFF, now ON')
    elif args.action == 'status':
        state = 'ON' if led.is_lit else 'OFF'
        print(f'LED on GPIO {args.pin} is {state}')


if __name__ == '__main__':
    main()
