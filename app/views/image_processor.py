# core.py - Image processing core
import numpy as np
import tifffile
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from skimage.filters import threshold_otsu

class ImageProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.image = tifffile.imread(file_path)
        self.shape = self.image.shape
        self.ndim = self.image.ndim
        
    def get_slice(self, time=None, z=None, channel=None):
        slice_idx = [slice(None)] * self.ndim
        dims = {0: 'Time', 1: 'Z', 2: 'Channel', 3: 'Y', 4: 'X'}
        
        if time is not None:
            slice_idx[0] = time
        if z is not None:
            slice_idx[1] = z
        if channel is not None:
            slice_idx[2] = channel
            
        return self.image[tuple(slice_idx)]
    
    def calculate_statistics(self):
        stats = []
        for ch in range(self.shape[2]):
            channel_data = self.image[:, :, ch, :, :].ravel()
            stats.append({
                "channel": ch,
                "mean": float(np.mean(channel_data)),
                "std": float(np.std(channel_data)),
                "min": float(np.min(channel_data)),
                "max": float(np.max(channel_data))
            })
        return stats
    
    def perform_pca(self, n_components=3):
        original_shape = self.image.shape
        data = self.image.reshape(-1, original_shape[2])
        pca = PCA(n_components=n_components)
        reduced = pca.fit_transform(data)
        return reduced.reshape(original_shape[0], original_shape[1], n_components, original_shape[3], original_shape[4])
    
    def segment_channel(self, channel, method='otsu'):
        channel_data = self.image[:, :, channel, :, :]
        if method == 'otsu':
            threshold = threshold_otsu(channel_data)
            return (channel_data > threshold).astype(np.uint8)
        elif method == 'kmeans':
            kmeans = KMeans(n_clusters=2)
            flattened = channel_data.reshape(-1, 1)
            return kmeans.fit_predict(flattened).reshape(channel_data.shape)
        return None

    def save_image(self, output_path, image_data):
        """
        Save the processed image data to a file.
        
        Parameters:
        output_path (str): The path where the image will be saved.
        image_data (numpy.ndarray): The image data to be saved.
        """
        tifffile.imwrite(output_path, image_data)