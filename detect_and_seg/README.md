# Application for searching and segmenting bags, backpacks and knives on video


## Installation

Install Python version 3.10.6 or higher.

For GPU version:
    Download and install the necessary NVIDIA drivers:
    https://developer.nvidia.com/cuda-11-8-0-download-archive?target_os=Windows&target_arch=x86_64&target_version=10

    Install PyTorch. In the command prompt (cmd), enter:
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

 For CPU version (slower version):
    Install PyTorch. In the command prompt (cmd), enter:
    pip3 install torch torchvision torchaudio

Install other dependencies. In the command prompt (cmd), navigate to the program directory and enter:
```
    pip install -r requirements.txt
```

## Run

```
python main.py
```

If the source is a streaming video, insert the link in the "Address" field and click the "Start" button.
If the source is a video/photo file, click the "Open" button and then click the "Start" button.

## Settings

Window size: the size of the image on the monitor.

Frame rate: choose to check every frame, every other frame, or every fifth frame.
If using CPU, it is optimal to use every fifth or every other frame.

Save: whether to save the processed source or not.

The settings are saved in the config.ini file. You can also modify the text in the program by editing the config file.