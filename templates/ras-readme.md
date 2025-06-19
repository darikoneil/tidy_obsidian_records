# {{ subject_name }}
Processed data for {{ subject_name }}'s Startle & PPI experiments.

## At a Glance
- **Subject**: {{ subject_name }}
- **Tasks**: Startle, PPI
- **Date**: {{ date }}
- **Time**: {{ time }}

## Contents

### General
- `{{ subject_name }}_readme.md`: This file
- `{{ subject_name }}_records.md`: Exported laboratory notebook
- `ras_example_open_data.ipynb`: Jupyter notebook with example code for loading and plotting the data.
- `ras-requirements.txt`: Python package requirements for running the code in `ras_example_open_data.ipynb`
- `files/`: Directory containing all files references by the laboratory notebook document

{% set tasks = ['Startle', 'PPI'] %}
{% set steps = ["preparation", "processing"] %}
{% set ext = ["pdf", "ipynb"] %}
{% for task in tasks %}
### {{ task }}
- `{{ task }}/`: Directory containing all contents for the {{ task }} task
- `{{ subject_name }}_{{ task }}_behavior_data.parquet`: Behavioral features x time tabular data
- `{{ subject_name }}_{{ task }}_neural_data.parquet`: Denoised neural activity x time tabular data
- `{{ subject_name }}_{{ task }}_rois.npz`: Centroid, Contours, Coordinates, & Footprint for each ROI
- `{{ subject_name }}_{{ task }}_{{ task }}.pdf`: exported jupyter notebooks used to conduct behavioral analysis
{% for channel in range(channels) %}
{% for plane in range(planes) %}
{% for step in steps %}
{% for ext in ext %}
- `{{ subject_name }}_{{ task }}_channel_{{ channel }}_plane_{{ plane }}_{{ step }}.{{ ext }}`: exported jupyter notebooks used to conduct imaging analysis for each step, channel, & plane combination.
{% endfor %}
{% endfor %}
- `{{ subject_name }}_{{ task }}_channel_{{ channel }}_plane_{{ plane }}_prepped_preview.tif`: <=10,000 frames of imaging data
{% endfor %}
{% endfor %}
{% endfor %}

### Methodology

#### Behavior Data
1. **Loading Data**: The analog data, event log, video, imaging metadata, and 
voltage recording were loaded into DataFrames. 
2. **Synchronization** The neurobeam data (analog data, event log, and video) were 
aligned using their respective timestamps. The timestamps were converted from absolute 
to relative time, where the initiation of habituation was set to t=0. The locomotion 
signal was split to both the PrairieView DAQ and neurobeam DAQ. Given this relationship, 
the voltage recording and analog data were aligned by maximizing their 
cross-correlation. The imaging data could then be aligned to the voltage recording using
its recorded metadata. With all the data aligned, a merged dataframe was formed in 
containing the locomotion signal, event_log, and indices of the camera 
and imaging frames.
3. **Feature Encoding**: The merged dataframe was then used to one-hot encode the 
features of the behavioral experiment (e.g., trial #, stimulus type, etc.).

#### Imaging Data

##### Pre-Processing
1. **Deinterlacing**: The raw data was deinterlaced to remove insufficient alignment of
forward and backward-scanned lines. To achieve sub-pixel alignment, the fourier 
of the two sets of lines was computed to calculate the cross-power spectral density.
Taking the inverse fourier transform of the cross-power spectral density yields
a matrix whose peak corresponds to the sub-pixel offset between the two sets of lines.
This translative offset was then discretized and used to shift the backward-scanned 
lines.
2. 
2. **Median Filtering**: To faciliate appropriate motion-correction, deinterlaced data was 
then denoised using a three-dimensional median filter with an approximate radius of 
100 ms x 1 um x 1 um.
3. **Motion Correction**: The deinterlaced and denoised data was then motion corrected
using Suite2P's rigid registration algorithm.
4. **Spatial Downscaling**: The motion-corrected data was then spatially downscaled by a
factor of 2 to facilitate faster downstream analysis.

##### Processing
1. **Simultaneous Source Extraction and Deconvolution**: Neural activity was extracted from
the imaging data using CaImAn's CNMF algorithm. 
2. **Component Evaluation** Identified components were required to 
possess a signal-to-noise ratio of >= 1.0 to be included in subsequent analysis. 
Pairs of components with a correlation >= 0.7 were merged.
