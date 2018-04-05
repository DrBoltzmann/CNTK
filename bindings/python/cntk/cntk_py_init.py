# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE.md file in the project root
# for full license information.
# ==============================================================================
"""
Check OS requirements before running CNTK for Python.
"""
import sys
import os
import platform
import linecache
import warnings
from subprocess import call

def cntk_check_distro_info():
    __my_distro__ = ''
    __my_distro_ver__ = ''
    __my_system__ = platform.system().lower()
    __my_arch__ = platform.architecture()[0].lower()

    __OS_RELEASE_FILE__ = '/etc/os-release'
    __LSB_RELEASE_FILE__ = '/etc/lsb-release'

    if __my_arch__ != '64bit':
        warnings.warn('Unsupported architecture (%s). CNTK supports 64bit architecture, only.' % __my_arch__)

    if __my_system__ == 'windows':
        __my_distro__ = __my_system__
        __my_distro_ver__ = platform.release().lower()

        if __my_distro_ver__ != '10':
            warnings.warn('Unsupported Windows version (%s). CNTK supports Windows 10 and above, only.' % __my_distro_ver__)
    elif __my_system__ == 'linux':
        # Newer systems have /etc/os-release with relevant distro info
        __my_distro__ = linecache.getline(__OS_RELEASE_FILE__, 3)[3:-1]
        __my_distro_ver__ = linecache.getline(__OS_RELEASE_FILE__, 6)[12:-2]

        # Older systems may have /etc/os-release instead
        if not __my_distro__:
            __my_distro__ = linecache.getline(__LSB_RELEASE_FILE__, 1)[11:-1]
            __my_distro_ver__ = linecache.getline(__LSB_RELEASE_FILE__, 2)[16:-1]

        # Instead of trying to parse distro specific files,
        # warn the user CNTK may not work out of the box
        __my_distro__ = __my_distro__.lower()
        __my_distro_ver__ = __my_distro_ver__.lower()

        if __my_distro__ != 'ubuntu' or __my_distro_ver__ != '16.04':
            warnings.warn('Unsupported Linux distribution (%s-%s). CNTK supports Ubuntu 16.04 and above, only.' % (__my_distro__, __my_distro_ver__))
    else:
        warnings.warn('Unsupported platform (%s). CNTK supports Linux and Windows platforms, only.' % __my_system__)

def cntk_check_libs():
    WARNING_MSG='Missing optional dependency (%s).\n   CNTK may crash if the component that depends on those dependencies is loaded.\n   Visit %s for more information'
    WARNING_MSG_CPU_ONLY='If you intend to use CNTK without GPU support, you can ignore the previous GPU-specific warning!'

    devnull = open(os.devnull, 'w')
    __my_system__ = platform.system().lower()
    if __my_system__ == 'windows':
        if call(['where', 'libiomp5md*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'mklml*.dll'], stdout=devnull, stderr=devnull) != 0:
            warnings.warn(WARNING_MSG % ('MKL', 'https://docs.microsoft.com/en-us/cognitive-toolkit/Setup-Windows-Python#mkl'))
        if call(['where', 'cudnn*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'nvml*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'nvml*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'cublas*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'cudart*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'curand*.dll'], stdout=devnull, stderr=devnull) != 0 or \
          call(['where', 'cusparse*.dll'], stdout=devnull, stderr=devnull) != 0:
            warnings.warn(WARNING_MSG % ('GPU-Specific', 'https://docs.microsoft.com/en-us/cognitive-toolkit/Setup-Windows-Python#optional-gpu-specific-packages'))
            warnings.warn(WARNING_MSG_CPU_ONLY)
        if call(['where', 'opencv_world*.dll'], stdout=devnull, stderr=devnull) != 0:
            warnings.warn(WARNING_MSG % ('OpenCV', 'https://docs.microsoft.com/en-us/cognitive-toolkit/Setup-Windows-Python#optional-opencv'))
    elif __my_system__ == 'linux':
        if call('ldconfig -p | grep libmklml_intel*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libiomp5*.so', shell=True, stdout=devnull, stderr=devnull) != 0:
            warnings.warn(WARNING_MSG % ('MKL', 'https://docs.microsoft.com/en-us/cognitive-toolkit/Setup-Linux-Python#mkl'))
        if call('ldconfig -p | grep libcudart*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libcublas*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libcurand*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libcusparse*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libcuda*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libnvidia-ml*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libcudnn*.so', shell=True, stdout=devnull, stderr=devnull) != 0:
            warnings.warn(WARNING_MSG % ('GPU-Specific', 'https://docs.microsoft.com/en-us/cognitive-toolkit/Setup-Linux-Python#optional-gpu-specific-packages'))
            warnings.warn(WARNING_MSG_CPU_ONLY)
        if call('ldconfig -p | grep libopencv_core*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libopencv_imgproc*.so', shell=True, stdout=devnull, stderr=devnull) != 0 or \
          call('ldconfig -p | grep libopencv_imgcodecs*.so', shell=True, stdout=devnull, stderr=devnull) != 0:
            warnings.warn(WARNING_MSG % ('OpenCV', 'https://docs.microsoft.com/en-us/cognitive-toolkit/Setup-Linux-Python#optional-opencv'))
    devnull.close()