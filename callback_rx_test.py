import threading
import queue
import os
import numpy as np
from functions_test import writeto
from networking import UdpReceive, NUM_SAMPLES

# Configuration
IP_ADDRESSES = ["10.10.10.60", "10.10.10.50"]
PORTS = [6373, 6372] # using different ports for easy identification
DATA_QUEUE_SIZE = 100

BLOCKS_PER_FILE = 128

data_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
stop_event = threading.Event()

def receive_data(ip, port):
    UDP = UdpReceive(ip, port)
    UDP.eth0()
    print(f'Listening on {ip}:{port} ...')

    try:
        while not stop_event.is_set():
            data = UDP.set_up()
            if data: 
                data_queues[ip].put(data)
    except KeyboardInterrupt:
        print(f'Data receiver for {ip} interrupted.')
    finally:
        UDP.stop()
        data_queues[ip].put(None)  # Signal to stop processing
        print(f'Receiver for {ip} done.')

def process_data(ip, verbose=True):
    folder1 = 'num_output' # creates output folder for numbered list
    folder2 = 'data_output' # creates output folder for actual data
    prefix1 = 'num' # prefix for numbered list
    prefix2 = 'data' # prefix for data
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder1):
        os.makedirs(folder1)

    if not os.path.exists(folder2):
        os.makedirs(folder2)

    try:
        data = np.empty((BLOCKS_PER_FILE, NUM_SAMPLES, 2), dtype='int8')
        cnt = 0
        while True:
            d = data_queues[ip].get()
            if data is None:
                print("No data received.")
                break

            signal = np.frombuffer(d, dtype=np.int8)
            signal.shape = (-1, 2)
            data[cnt] = signal
            cnt += 1

            # Save the data to a file
            if cnt >= BLOCKS_PER_FILE:
                if verbose:
                    print(f"Writing file {track_files}")
                track_files += 1
                writeto(data, prefix1, folder1, track_files)
                cnt = 0

            data_queues[ip].task_done()
    except Exception as e:
        print(f'Error in data processor for {ip}: {e}')
    finally:
        print(f'Processor for {ip} done.')


if __name__ == "__main__":
    receiver_threads = [threading.Thread(target=receive_data, args=(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_threads = [threading.Thread(target=process_data, args=(ip,)) for ip in IP_ADDRESSES]

    for thread in receiver_threads:
        thread.start()
    for thread in processor_threads:
        thread.start()

    for thread in receiver_threads:
        thread.join()
    for thread in processor_threads:
        data_queues[thread.name.split('-')[1]].put(None)  # Signal processor threads to exit
        thread.join()

    print('Main thread done.')
