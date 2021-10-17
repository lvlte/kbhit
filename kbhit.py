#!/usr/bin/env python
'''
A Python class implementing KBHIT, the standard keyboard-interrupt poller.
Works transparently on Windows and Posix (Linux, Mac OS X).  Doesn't work
with IDLE.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

'''

import os

# Windows
if os.name == 'nt':
    import msvcrt

# Posix (Linux, OS X)
else:
    import sys
    import termios
    import atexit
    from select import select


class KBHit:

    def __init__(self):
        '''Creates a KBHit object that you can call to do various keyboard things.
        '''

        if os.name == 'nt':
            # On Windows, use this as a flag meaning a char has been pushed into
            # the console buffer using ungetch().
            self.ungetched = False

        else:
            # Save the terminal settings
            self.fd = sys.stdin.fileno()
            self.new_term = termios.tcgetattr(self.fd)
            self.old_term = termios.tcgetattr(self.fd)

            # New terminal setting unbuffered
            self.new_term[3] = (self.new_term[3] & ~termios.ICANON & ~termios.ECHO)
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.new_term)

            # Support normal-terminal reset at exit
            atexit.register(self.set_normal_term)

            # Used for ungetch(), if different than stdin fileno, then a char is
            # waiting to be read from that fd.
            self.ungetched = sys.stdin.fileno()

    def set_normal_term(self):
        ''' Resets to normal terminal. Called on exit.
            On Windows this is a no-op.
        '''

        if os.name != 'nt':
            termios.tcsetattr(self.fd, termios.TCSAFLUSH, self.old_term)

    def getch(self):
        ''' Returns a keyboard character after kbhit() has been called.
            Should not be called in the same program as getarrow().
        '''

        if os.name == 'nt':
            return msvcrt.getch()

        elif self.ungetched != self.fd:
            c = os.fdopen(self.ungetched, 'r').read(1)
            self.ungetched = self.fd
            return c

        else:
            return sys.stdin.read(1)

    def ungetch(self, char):
        ''' Opposite of getch. Cause the character to be “pushed back” into the
            console buffer; it will be the next character read by getch().
            Expect a Unicode value on Windows.
        '''

        if not isinstance(char, str) or len(char) > 1:
            raise TypeError('ungetch() argument must be a unicode character')

        if os.name == 'nt':
            msvcrt.ungetch(char)
            self.ungetched = 1

        else:
            r, w = os.pipe()
            self.ungetched = r
            os.write(w, char.encode('utf-8'))
            os.close(w)

    def getarrow(self):
        ''' Returns an arrow-key code after kbhit() has been called. Codes are
        0 : up
        1 : right
        2 : down
        3 : left
        Should not be called in the same program as getch().
        '''

        if os.name == 'nt':
            msvcrt.getch()  # skip 0xE0
            c = msvcrt.getch()
            vals = [72, 77, 80, 75]

        else:
            c = sys.stdin.read(3)[2]
            vals = [65, 67, 66, 68]

        return vals.index(ord(c.decode('utf-8')))

    def kbhit(self):
        ''' Returns True if keyboard character was hit or pushed with ungetch(),
            False otherwise.
        '''

        if os.name == 'nt':
            if self.ungetched:
                self.ungetched = False
                return True
            return msvcrt.kbhit()

        else:
            dr, dw, de = select([sys.stdin, self.ungetched], [], [], 0)
            return dr != []


# Test
if __name__ == "__main__":

    kb = KBHit()

    # Using signal to handle sig keys
    import signal
    import sys

    def interrupt(sig, _):
        print('SIGINT (Signal Interrupt) (2) : Interrupt from keyboard')
        kb.set_normal_term()
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
