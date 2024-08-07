import threading
import queue
import os
import matplotlib.pyplot as plt
import numpy as np
from functions1 import receive, writeto, initialize_plots, update_plot

# Configuration
IP_ADDRESSES = ["10.10.10.40", "10.10.10.50"]
PORTS = [6371, 6372]  # Different ports for each IP
DATA_QUEUE_SIZE = 10

data_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
plot_queues = {ip: queue.Queue(maxsize=DATA_QUEUE_SIZE) for ip in IP_ADDRESSES}
stop_event = threading.Event()

def data_receiver(ip, port):
    UDP = receive(ip, port)
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

def data_processor(ip):
    folder = 'output'
    prefix = 'data'
    track_files = 0  # counter for the number of files saved

    if not os.path.exists(folder):
        os.makedirs(folder)

    try:
        while True:
            data = data_queues[ip].get()
            if data is None:
                break

            spectrum = np.frombuffer(data, dtype=np.uint8)
            spectrum.shape = (-1, 2)
            print(f"Data shape for {ip}: {spectrum.shape}")
            
            # Save the data to a file
            track_files += 1
            writeto(spectrum, prefix, folder, track_files)

            # Put the data in the plot queue
            plot_queues[ip].put((spectrum, track_files))

            data_queues[ip].task_done()
    except KeyboardInterrupt:
        print(f'Data processor for {ip} interrupted.')
    finally:
        plot_queues[ip].put(None)  # Signal to stop plotting
        print(f'Processor for {ip} done.')

def plot_data():
    fig, axs, lines = initialize_plots(IP_ADDRESSES)

    try:
        while True:
            for ip in IP_ADDRESSES:
                item = plot_queues[ip].get()
                if item is None:
                    continue

                spectrum, track_files = item
                update_plot(spectrum, fig, lines[IP_ADDRESSES.index(ip)])

                plot_queues[ip].task_done()
            #plt.pause(0.1)
    except KeyboardInterrupt:
        print('Plotting interrupted.')
    finally:
        plt.ioff()
        plt.show()
        print('Plotting done.')

if __name__ == "__main__":
    receiver_threads = [threading.Thread(target=data_receiver, args=(ip, port)) for ip, port in zip(IP_ADDRESSES, PORTS)]
    processor_threads = [threading.Thread(target=data_processor, args=(ip,)) for ip in IP_ADDRESSES]

    for thread in receiver_threads:
        thread.start()
    for thread in processor_threads:
        thread.start()

    try:
        plot_data()
    except KeyboardInterrupt:
        print('Main thread interrupted.')
    finally:
        stop_event.set()
        for thread in receiver_threads:
            thread.join()
        for thread in processor_threads:
            data_queues[thread.name.split('-')[1]].put(None)  # Signal processor threads to exit
            thread.join()
        print('Main thread done.')
