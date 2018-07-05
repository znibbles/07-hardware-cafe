

https://www.raspberrypi.org/documentation/installation/installing-images/README.md
https://etcher.io/
https://www.raspberrypi.org/documentation/remote-access/ssh/

apt-get install build-essential swig
//apt-get install python-pyaudio

https://github.com/libpd/libpd/wiki/Python-API

pip install pygame

I'm not a master python programmer at all, and using `pyaudio` always gave me glitchy results, so I just basically copy/pasted the `pygame` examples from libpd, which worked reasonably well.


For those of you unfamiliar with puredata and libpd, it is important that you take the vanilla distribution of PD, because some externals aren't included in libpd.