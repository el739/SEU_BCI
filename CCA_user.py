from scipy.signal import resample
from sklearn.cross_decomposition import CCA
import numpy as np


def pro_cca(ref_sin, eeg_signals):
    cca_sklearn = CCA(n_components=1)
    cca_sklearn.fit(ref_sin, eeg_signals)
    X_c, Y_c = cca_sklearn.transform(ref_sin, eeg_signals)
    rho = np.corrcoef(X_c[:, 0], Y_c[:, 0])[0, 1]
    return rho


def cca_user(window_data, list_freqs, original_fs, target_fs):
    # 确保降采样频率不超过原始频率的一半，以避免混叠
    assert target_fs <= original_fs / 2, "目标频率应小于原始频率的一半以避免混叠。"

    # 降采样
    num_points_downsampled = int(window_data.shape[1] * (target_fs / original_fs))
    window_data_downsampled = resample(window_data, num_points_downsampled, axis=1)

    t_downsampled = np.arange(1, num_points_downsampled + 1) / target_fs

    N_harmonic = 4

    Reference = np.zeros((N_harmonic * 2, num_points_downsampled, len(list_freqs)))
    for targ_i in range(len(list_freqs)):
        reference_signals = []
        for i in range(1, N_harmonic + 1):
            reference_signals.append(np.sin(np.pi * 2 * i * list_freqs[targ_i] * t_downsampled))
            reference_signals.append(np.cos(np.pi * 2 * i * list_freqs[targ_i] * t_downsampled))
        reference_signals = np.array(reference_signals)
        Reference[:, :, targ_i] = reference_signals

    output = [0] * len(list_freqs)
    for i in range(len(list_freqs)):
        corr_coeffs = pro_cca(Reference[:, :, i].T, window_data_downsampled.T)
        output[i] = corr_coeffs

    index = np.argmax(output)
    cor = output[index]


    return round(list_freqs[index], 2), round(cor, 2),output