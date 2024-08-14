import argparse
import os
import asyncio
import ugradio
import queue
from functions_test import send

# arguments for when observing
parser = argparse.ArgumentParser()
parser.add_argument('--prefix', '-p', default='data')
parser.add_argument('--len_obs', '-l', default='60')
parser.add_argument('--folder', '-f', default='output')
args = parser.parse_args()

prefix = args.prefix
len_obs = int(args.len_obs)
folder = args.folder

LAPTOP_IP = "10.10.10.30"
PORT = 6373
num_samples = 2048

if not os.path.exists(folder):
    os.makedirs(folder)

# sets up SDR
sdr = ugradio.sdr.SDR(sample_rate=2.2e6, center_freq=145.2e6, direct=False, gain=20)

# sets up network connection
UDP = send(LAPTOP_IP, PORT)

data_queue = queue.Queue(maxsize=0)  # infinite size queue to prevent data loss

async def data_sender():
    try:
        cnt = 0
        while True:
            d = await asyncio.to_thread(data_queue.get)
            if d is None:
                break
            await asyncio.to_thread(UDP.send_data, d)
            cnt += 1
            print(f"Sent Data! cnt={cnt}")
    except Exception as e:
        print(f"Error in data_sender: {e}")
    finally:
        UDP.stop()
        print("Data transfer stopped.")

async def main():
    # Start sender threads as asyncio tasks
    sender_tasks = [asyncio.create_task(data_sender()) for _ in range(3)]
    
    try:
        while True:
            d = await asyncio.to_thread(sdr.capture_data, num_samples)
            data_queue.put(d)
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        pass
    finally:
        # Stop sender tasks
        for _ in range(3):
            data_queue.put(None)
        await asyncio.gather(*sender_tasks)
        print("Main task done.")

# Run the event loop
asyncio.run(main())
