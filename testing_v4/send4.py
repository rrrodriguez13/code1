import argparse
import os
import threading
import queue
import ugradio
from functions4 import send

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
stop_event = threading.Event()

def data_sender():
    try:
        cnt = 0
        while not stop_event.is_set() or not data_queue.empty():
            d = data_queue.get()
            if d is None:
                break
            UDP.send_data(d)
            cnt += 1
            print(f"Sent Data! cnt={cnt}")
    except Exception as e:
        print(f"Error in data_sender: {e}")
    finally:
        UDP.stop()
        print("Data transfer stopped.")

# increases the number of sender threads to handle data faster
num_sender_threads = 3  # can adjust based on what system can handle
sender_threads = [threading.Thread(target=data_sender) for _ in range(num_sender_threads)]

for thread in sender_threads:
    thread.start()

try:
    while not stop_event.is_set():
        d = sdr.capture_data(num_samples)
        data_queue.put(d)
except KeyboardInterrupt:
    stop_event.set()
finally:
    data_queue.put(None)  # signal sender threads to exit
    for thread in sender_threads:
        thread.join()
    print("Main thread done.")
