FROM arm32v6/alpine
RUN apk add build-base git jack-dev alsa-lib-dev
RUN cd /root && git clone https://github.com/libpd/libpd
RUN cd /root/libpd && git submodule init && git submodule update
RUN cd /root/libpd && make && make install
RUN cd /root/libpd/samples/cpp/pdtest_rtaudio && make  


