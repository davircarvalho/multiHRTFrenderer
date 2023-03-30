'''
Real time HRTF renderer.

Multiple SOFA files can be loaded and arbitraryly switched using UDP messages
Authors: Davi Rocha Carvalho
'''

# %% Import libs
import sofar
import pyaudio
import warnings
import threading
import numpy as np
import librosa as lb
from copy import deepcopy
from FIRconv import FIRfilter
from EACheadtracker import HeadTracker
from positionReceiver import PositionReceiver
from datasetIndexReceiver import DatasetIndexReceiver


# %% Global configs ##################################################################
# head tracker data receiver config
isHeadTracker = False
HT_IP = '0.0.0.0'
HT_PORT = 5555
CAM_ID = 0  # select index of camera feed

# dataset remote receiver config
DS_IP = '0.0.0.0'
DS_PORT = 5556

# audio rendering config
buffer_sz = 1024
method = 'upols'  # FIR method

# List the files you wanna load
SOFAfiles = ['SOFA/P0138_Windowed_44kHz.sofa',
             'SOFA/pp3_HRIRs_measured.sofa',
             'SOFA/pp3_HRIRs_simulated.sofa',
             'SOFA/subject_011.sofa']

# Audio path
audioPath = 'Audio/01 - My Favorite Things.flac'

# ##################################################################################33
# %% SOFA setup
Objs = []
samplingRate = []
for n, name in enumerate(SOFAfiles):
    Objs.append(sofar.read_sofa(name))
    samplingRate.append(Objs[n].Data_SamplingRate)

if not np.allclose(samplingRate, samplingRate):
    warnings.warn('SOFA Sampling Rates do not match\n >>>>You should NOT continue!<<<<<')
else:
    fs = int(samplingRate[0])


# %% initialize Dataset Index Receiver
sofaIDXmanager = DatasetIndexReceiver(IP=DS_IP, PORT=DS_PORT)


# %% Audio Input
def mono2stereo(audio):
    if np.size(audio.shape) < 2:
        audio = np.expand_dims(audio, 0)
        audio = np.append(audio, audio, axis=0)
    return audio.T


# Audio input
audio_in, _ = lb.load(audioPath,
                      sr=fs,
                      mono=True,
                      duration=None,
                      dtype=np.float32)  # input signal
audio_in = mono2stereo(audio_in)
N_ch = audio_in.shape[-1]


# %% Initialize head tracker and position functions
if isHeadTracker:
    thread = threading.Thread(target=HeadTracker.start, args=(CAM_ID, HT_PORT), daemon=False)  # track listener position
    thread.start()
    HTreceiver = PositionReceiver(IP=HT_IP, PORT=HT_PORT)  # read head tracker position data

    # convert positions to navigational coordinates for ease to use
    def sph2cart(posArray):
        idx = np.where(posArray[:, 0] > 180)[0]
        posArray[idx, 0] = posArray[idx, 0] - 360
        return posArray

    for n in range(len(Objs)):
        Objs[n].SourcePosition = sph2cart(Objs[n].SourcePosition)


def closestPosIdx(posArray, azi, ele):
    pErr = np.sqrt((posArray[:, 0] - azi)**2 + (posArray[:, 1] - ele)**2)
    return np.argmin(pErr)


idxPos = closestPosIdx(Objs[0].SourcePosition, azi=0, ele=0)


# %% Initialize FIR filter
FIRfilt = FIRfilter(method, buffer_sz, h=Objs[0].Data_IR[idxPos, :, :].T)

idxSOFA = 0

# %% Stream audio
# instantiate PyAudio (1)
p = pyaudio.PyAudio()
# open stream (2)
stream = p.open(format=pyaudio.paFloat32,
                channels=N_ch,
                rate=fs,
                output=True,
                frames_per_buffer=buffer_sz)

# play stream (3)
sigLen = audio_in.shape[0]

data_out = np.zeros((buffer_sz, N_ch))
frame_start = 0
frame_end = frame_start + buffer_sz
while True:

    # check if dataset changed
    idxSOFA = sofaIDXmanager.latest

    # get head tracker position
    if isHeadTracker:
        idxPos = closestPosIdx(Objs[idxSOFA].SourcePosition, HTreceiver.yaw, HTreceiver.pitch)

    # process data
    data_out = FIRfilt.process(audio_in[frame_start:frame_end, :],
                               h=Objs[idxSOFA].Data_IR[idxPos, :, :].T)

    # output data
    data_out = np.ascontiguousarray(data_out, dtype=np.float32)
    stream.write(data_out, buffer_sz)

    # # update reading positions
    frame_start = deepcopy(frame_end)
    frame_end = frame_start + buffer_sz
    if frame_end >= sigLen:
        frame_start = 0
        frame_end = frame_start + buffer_sz

# stop stream (4)
stream.stop_stream()
stream.close()
# close PyAudio (5)
p.terminate()

# %%
