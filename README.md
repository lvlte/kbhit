# kbhit
A Python class implementing KBHIT, the standard keyboard-interrupt poller.

Works transparently on Windows and Posix (Linux, Mac OS X) - except for CTRL keys.  
Doesn't work from REPL nor with IDLE.


### Usage

```python
from kbhit import KBHit

kb = KBHit()

print('Hit any key, or ESC to exit')

while True:

    if kb.kbhit():
        c = kb.getch()
        if ord(c) == 27:  # ESC
            print('exiting...')
            break
        print(c, ord(c))
```

### Non-ASCII characters

Unicode charset is supported provided that your system use the proper encoding (eg. utf-8).  
See [`PYTHONIOENCODING`](https://docs.python.org/3/using/cmdline.html#envvar-PYTHONIOENCODING)

### CTRL Keys

You can use `getarrow()` to get arrow-key codes. The drawback is that you can't `getch()` regular characters when your program is already expecting CTRL keys.
In other words, you can't use both functions in the same script.

### SIG Keys

You can still use `signal` along with `KBHit` to handle SIG keys. For example :
```python
kb = KBHit()

import signal
import sys

def interrupt(sig, _):
    print('SIGINT (Signal Interrupt) (2) : Interrupt from keyboard')
    sys.exit(2)

# Register handler for interruption (CTRL + C).
# Alternatively you can catch KeyboardInterrupt exception in the while loop.
signal.signal(signal.SIGINT, interrupt)

print('Hit any key, or ESC to exit')

while True:

    if kb.kbhit():
        c = kb.getch()
        if ord(c) == 27:  # ESC
            print('exiting...')
            break
        print(c, ord(c))
```

### Credits

- Simon D. Levy ([@simondlevy](https://github.com/simondlevy))
- Eric Lavault ([@lvlte](https://github.com/lvlte))
