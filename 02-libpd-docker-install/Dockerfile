FROM alpine
RUN apk add build-base git jack-dev alsa-lib-dev
RUN cd /home && git clone https://github.com/libpd/libpd
RUN cd /home/libpd && git submodule init && git submodule update
RUN cd /home/libpd && make && make install
RUN cd /home/libpd/samples/cpp/pdtest_rtaudio && make  

CMD /home/libpd/samples/cpp/pdtest_rtaudio