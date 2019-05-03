import numpy as np

# routine returning principal axes for data clouds...
def principal_axes(data): # data in Nx2 format...
    mu = np.mean(data,axis=0)
    data = data - mu
    eigenvectors, eigenvalues, _ = np.linalg.svd(data.T, full_matrices=False)
    projected_data = np.dot(data, eigenvectors)
    sigma = projected_data.std(axis=0)
    return mu, sigma, eigenvectors

from scipy import signal

def calc_periodogram ( data, zSamplingFreq):
    WaveNo, Pxx = signal.periodogram(data, zSamplingFreq,scaling='density')
    Pxx=Pxx/trapz(Pxx,WaveNo)
    indWaveNo = ~(WaveNo==0)&(WaveNo<=6)
    Pxx=Pxx[np.where(indWaveNo)]
    WaveNo=WaveNo[np.where(indWaveNo)]
    return WaveNo, np.log10(Pxx)
