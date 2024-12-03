from scipy.signal import resample
from sklearn.cross_decomposition import CCA
import numpy as np

def pro_cca(ref_sin, eeg_signals):
    cca_sklearn = CCA(n_components=1)
    cca_sklearn.fit(ref_sin, eeg_signals)
    X_c, Y_c = cca_sklearn.transform(ref_sin, eeg_signals)
    rho = np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1]
    return rho

def cca_no_downsample(window_data, list_freqs, original_fs):
    num_points = window_data.shape[1]
    t = np.arange(1, num_points + 1) / original_fs

    N_harmonic = 4

    Reference = np.zeros((N_harmonic * 2, num_points, len(list_freqs)))
    for targ_i in range(len(list_freqs)):
        reference_signals = []
        for i in range(1, N_harmonic + 1):
            reference_signals.append(np.sin(np.pi * 2 * i * list_freqs[targ_i] * t))
            reference_signals.append(np.cos(np.pi * 2 * i * list_freqs[targ_i] * t))
        reference_signals = np.array(reference_signals)
        Reference[:, :, targ_i] = reference_signals

    output = [0] * len(list_freqs)
    for i in range(len(list_freqs)):
        corr_coeffs = pro_cca(Reference[:, :, i].T, window_data.T)
        output[i] = corr_coeffs

    index = np.argmax(output)
    cor = output[index]

    return round(list_freqs[index], 2), round(cor, 2), output