'''
Real time HRTF renderer.

Multiple SOFA files can be loaded and arbitrarily switched using UDP messages
Authors: Davi Rocha Carvalho
'''

# %% Import libs
import sofar
import pyaudio
import warnings
import threading
import numpy as np
import soundfile as sf
from copy import deepcopy
from FIRconv import FIRfilter
from geometry import GeomtryFunctions
from EACheadtracker import HeadTracker
from positionReceiver import PositionReceiver
from datasetIndexReceiver import DatasetIndexReceiver


# %% Global configs ##################################################################
# head tracker data receiver config
isHeadTracker = True
HT_IP = '127.0.0.1'
HT_PORT = 5555
CAM_ID = 0  # select index of camera feed

# dataset remote receiver config
DS_IP = '0.0.0.0'
DS_PORT = 5556

# audio rendering config
buffer_sz = 512
method = 'upols'  # FIR method

# List the files you wanna load
SOFAfiles = ['SOFA/HRTF_individualizada_44.1kHz.sofa']

# Audio path'
audioPath = 'Audio/drums.wav'
# audioPath = 'Audio/sabine.wav'


# Source position
''' NOTE os angulos são em coordenadas "navigacionais"
    -180 < azimute < 180
    -90 < elevação < 90
    tal que 0° é diretamente a frente,
    elevação=90: topo
    azimute negativo: direita
'''
src_azim = 0  # azimute
src_elev = 0   # elevação

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
sofaIDXmanager = DatasetIndexReceiver(IP_rcv=DS_IP, PORT_rcv=DS_PORT,
                                      IP_snd=HT_IP, PORT_snd=HT_PORT)


# %% Audio Input
# Audio input
audio_in, _ = sf.read(audioPath,
                      samplerate=None,
                      always_2d=True,
                      dtype=np.float32)  # input signal
audio_in = np.mean(audio_in, axis=1, keepdims=True)
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

# initialize position index manager
PosManager = []
for Obj in Objs:
    PosManager.append(GeomtryFunctions(Obj.SourcePosition, src_azim, src_elev))


# %% Initialize FIR filter
idxSOFA = 0
idxPos = PosManager[idxSOFA].closestPosIdx(yaw=0, pitch=0, roll=0)
FIRfilt = FIRfilter(method, buffer_sz, h=Objs[idxSOFA].Data_IR[idxPos, :, :].T)


# %% Stream audio
# instantiate PyAudio (1)
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paFloat32,
                channels=2,
                rate=fs,
                output=True,
                frames_per_buffer=buffer_sz)

# play stream (3)
sigLen = audio_in.shape[0]

data_out = np.zeros((buffer_sz, 2))
frame_start = 0
frame_end = frame_start + buffer_sz

while True:
    # check if dataset has changed
    idxSOFA_tmp = sofaIDXmanager.latest
    if idxSOFA_tmp < len(SOFAfiles): # only update if index is within range
        idxSOFA = deepcopy(idxSOFA_tmp)

    # get head tracker position
    if isHeadTracker:
        idxPos = PosManager[idxSOFA].closestPosIdx(HTreceiver.yaw, HTreceiver.pitch, -1*HTreceiver.roll)

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
