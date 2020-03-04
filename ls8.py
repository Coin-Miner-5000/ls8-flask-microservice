#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

def ls8():
    cpu = CPU()

    cpu.load()
    return cpu.run()

if "name" == "__main__":
    ls8()


