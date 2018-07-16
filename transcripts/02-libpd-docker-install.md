## Feeling a Little Weary?

This episode is a little follow-up to the last one that will make your lives considerably easier. 

If you were uncomfortable watching me download, compile, intialize git submodules and so on, I can tell you there is a pleasant alternative underway. This alternative is called **Docker**.

## Docker to the Rescue

Docker is a tool to bundle and deliver applications in so-called containers. These containers are essentially small, integrated environments that live on top on a standard Linux stack. We'll get to that in a moment.

The good news is the people at Docker are so nice as to provide us with a neat install script, which you can just copy and paste from the transcript, as I've done here.

	$ curl -sSL https://get.docker.com | sh

## Linux in a Nutshell

When the setup process is complete, it's time to talk about what a Docker *image* is. Essentially, that's a snapshot of a small Linux virtual machine in a well-defined state. It is formally described by what is called a *Dockerfile*, which is at the heart of every docker-driven implementation. This is ours:

	FROM arm32v6/alpine
	RUN apk add build-base git jack-dev alsa-lib-dev
	RUN cd /root && git clone https://github.com/libpd/libpd
	RUN cd /root/libpd && git submodule init && git submodule update
	RUN cd /root/libpd && make && make install
	RUN cd /root/libpd/samples/cpp/pdtest_rtaudio && make

Do you recognize it? Basically that's all the steps we've taken in the previous episode to get up and running with LibPD on Raspbian. The `FROM` line just identifies a base Linux image. I've chosen alpine here, because it has a very small footprint and can live entirely in memory.

The good thing is, when you *build* an image, all those steps take place automatically. You can then either just use the image on your machine, or go ahead and push it to a repository, such as https://hub.docker.com, which is exactly what I did.

## Running a Container

And which is the reason why we can do this:

	$ sudo docker run --rm -ti --device /dev/snd znibbles/libpd-raspbian:0.1.3 sh

Now don't be intimidated. We're just telling `docker` to `run` an image provided by me at `znibbles/libpd-raspbian`. The `--rm` flag tells Docker to delete the container once it has stopped, `-ti` tells it to start with an interactive terminal (the `sh` command at the end), and `--device /dev/snd` specifies the host's (your RPi's) sound device to be mapped to the container.

The process of downloading and extracting can take a little time on the RPi, please be patient :)

## Inside the Container

Now we have a different looking prompt, which means we are now *inside* our container. We can go to our `pdtest_rtaudio` directory and run the `pdtest_rtaudio` application, which worked right out of the box, and didn't consume significantly more CPU power, as you can see here.

## Applying a Bind Mount

We again copy our own `test.pd` patch to the home directory on the host with `scp`, then again run the docker container with an additional flag:

`-v ~:/root/test`

which tells Docker to map our home directory on the host (`~`) to a specified directory in the container (`/root/test`) which will be initialized if it doesn't exist yet. This is called a *bind mount*.

Inside the container again, we copy our `test.pd` from the `/root/test` directory to the `pdtest_rtaudio` directory and run again. At least on my machine, this worked instantly.

## Conclusion

In future episodes, I plan to make this process even more automatic. I envision dozens of Raspberry Pis provisioned with Docker to make up a huge installation...

If you'd like to learn more about this awesome tool, I'm considering making a whole course dedicated to Docker for Creators. Let me know if you'd fancy that, just reach out to me in the comments!