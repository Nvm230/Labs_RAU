#!/usr/bin/env python3
import sys
import math
import time
import moteus
import asyncio
import numpy as np

async def main():

  rate = 50 

  # Connection with the mjbot brushless motor driver
  transport = moteus.Fdcanusb()
  c1 = moteus.Controller(id = 1)
  c2 = moteus.Controller(id = 2)
  await transport.cycle([c1.make_stop(), c2.make_stop()])
  print("Hdsa")
  i=0

  try:
    while (i<10000000):
      print("Hola")
      result = await transport.cycle([c1.make_position(position=math.nan,velocity=0.5,query=True), c2.make_position(position=math.nan,velocity=0.5,query=True)])
      await asyncio.sleep(1/rate)
      i=i+1
            
  except KeyboardInterrupt:
    await transport.cycle([c1.make_stop()])
    await transport.cycle([c2.make_stop()])
    print("The mjbots node is close!")
    sys.exit()

if __name__ == '__main__':
    asyncio.run(main())
