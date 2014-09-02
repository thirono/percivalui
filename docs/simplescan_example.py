'''
A simple PercivalUI scan demo

This demonstrates how to do a synchronous scan of a DAC 
parameter while acquiring samples off the detector.
'''

from percivalui import PercivalUI
import datetime

pcvl = PercivalUI()

# Do a rough scan (steps of 8) through a 12 bit DAC subrange
DAC_scan_values = range(128, 512, 8)

nframes_per_step = 10
nframes_total = nframes_per_step * len(DAC_scan_values)

# Prepare to record the acquired data into a file with a timestamp in the name
start_time = datetime.datetime.now() 
data_filename = 'simplescan_demo_%s.h5'%start_time.isoformat()
pcvl.data.start_capture(data_filename, nframes=nframes_total)

# Scan through the desired DAC values
for DAC_value in DAC_scan_values:
    
    # Set the desired control DAC parameter. In this example "some_gain"
    pcvl.control.dacs.some_gain = DAC_value
    
    # Acquire 10 frames for each step with a 0.1s exposure per frame
    # With wait=True, this function will block until aquisition completes
    pcvl.acquire(0.1, nframes_per_step, wait=True)
    
# Now wait for the data to be stored to disk. This function
# blocks until data capture is complete or stopped.
pcvl.data.wait_complete(timeout = None)

# Collect the information about where the data is stored
data_filename = pcvl.data.get_filename()
dataset_name = pcvl.data.get_datasetname()

# Access the real data through h5py
import h5py
h5file = h5py.open(data_filename, 'rw')
dset = h5file[dataset_name]

print "Acquire dataset dimensions: ", dset.shape 