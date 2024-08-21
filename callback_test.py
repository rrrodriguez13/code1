#import ugradio
import os
import numpy as np
import sdr_stream
import networking

#cnt = 0
#
#def file_writer(dev_id, shape, data):
#    global cnt
#    folder = 'output'
#    if not os.path.exists(folder):
#        os.makedirs(folder)
#    filename = os.path.join(folder, f'sdr_data{cnt:03d}.npz')
#    print(f'Saving data to {filename}')
#    np.savez(filename, data=data)
#    cnt += 1

IP = '10.10.10.30'

UDP = networking.UdpSend(IP)

def udp_sender(dev_id, shape, data):
    UDP.send_data(data)
    print('Sent a packet')
    
sdr = sdr_stream.SDR(sample_rate=2.2e6, center_freq=145.2e6, direct=False, gain=10)
sdr_stream.capture_data(sdr, nblocks=128, callback=udp_sender)
