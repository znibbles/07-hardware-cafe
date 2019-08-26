So finally the opportunity has come to talk about one of my favorite languages and environments on this show, and this is the Elixir language, and the Nerves framework specifically. 

Nerves is a way to create and maintain applications for embedded computers such as the Raspberry Pi in a particularly easygoing way - think: an Arduino IDE for Raspberry Pi, only supercharged with IoT-centric libraries and tools. We are going to look at how to install all the prerequisites for it and code a simple time lapse video using the Cloudinary image cloud storage. The Hardware I use is a Raspberry Pi Zero with a Camera Module v2. Let’s jump right in. 

## Cloudinary

Before we get to actual coding, we’re going to set up a Cloudinary account. We will use Cloudinary’s advanced image processing capabilities to transform uploaded images and concatenate them into a time lapse.

I'm going to [https://cloudinary.com](https://cloudinary.com) and set up an account. This is pretty straightforward, just follow along here and fill in some values. You are assigned an API key and an API secret, which we will need later on. You can always access them on your dashboard.

The free plan gives you 25 cloudinary credits, which is a compound value of your storage and transfer rate in GB, as well as  applied transformations. You can read more about that [here](https://cloudinary.com/pricing#faq-5).

Next we're going to set up a so-called upload preset. Click on the settings icon, then `Upload`. Scroll down to the presets section and click `Add upload preset`. We are going to name it `timelapse_pi` and specify that images be uploaded into the folder `timelapse_pi`.

Now, click on `Upload Manipulations`. We are going to resize our image to 640x480 on upload, but there's a wealth of transformations you can apply here, including intelligent face detection algorithms, applying gravity etc. Click `Save`, that's it.



## Setting up Elixir and Nerves for Development

We're going to follow the [Nerves installation guidelines](https://hexdocs.pm/nerves/installation.html#content), just note that depending on your operating system, you will need some additional packages, usually to be installed via your package manager. Please refer to the docs for  that.

Nerves recommends installing the Elixir language and the Erlang/OTP runtime via the `asdf` version manager, so we need to install that beforehand. Next we need to add the `elixir` and `erlang` plugins to `asdf`, to have access to the packages.

## Creating a Nerves Project and Installing Dependencies

Let's create a new Nerves project with

`$ mix nerves.new timelapse_picam_nerves --init-gadget`

We confirm that we'd like to fetch the project dependencies as well. Next, we need to set the `MIX_TARGET` environment variable to `rpi0` so our firmware will be cross compiled to the correct device. Note that probably you're going to have to use a different command here, since I'm not using `bash` but the `fish` shell. You'll likely want to run

`$ export MIX_TARGET=rpi0` 

instead. Let's look at the `mix.exs` file, and add three more dependencies. The first is `picam` itself, the second is `httpoison`, a lightweight http client we're going to use to communicate with Cloudinary. The third and last is `nerves_time`, which is necessary to sync the Nerves system clock with an NTP server.

Alright, let's run

`$ mix deps.get` 

again to fetch the updated dependencies list.

## Configuring our Project

Let's see what we have to do in terms of configuration. We head over to `config/config.exs` and skim through what has been bootstrapped for us. At the bottom we find an import statement pointing to `target.exs`, which we enter.

The keys section is important because it sets up the public SSH keys of our host system to be used to ssh into the Nerves device later. If you don't know what that is or how to create one, [Github has some excellent guides](https://help.github.com/en/articles/connecting-to-github-with-ssh) on this.

In the `nerves_init_gadget` section, we go straight to configuring our local WiFi instead of the USB port. Change the `ifname` to `"wlan0"` and `address_method` to `:dhcp`, then edit the `mdns_domain` to something more telling, `"timelapse_picam_nerves.local"`

Next, we're going to actually configure the WiFi settings. I'm going to copy-paste in some code here, to set the `key_mgmt` either to the one provided by an environment variable, or `"WPA-PSK"` as the default. 

Then, we configure the network adapter, `wlan0` with the `ssid`, `psk`, which are going to be set from outside, via environment variables, and the `key_mgmt`.

Last but not least, we need some app specific configuration: We need a `cloudinary_base_url`, `cloudinary_api_key` and `cloudinary_secret`, which will all be obtained from Cloudinary and set as environment variables, too.

## Preparing the Environment

Before we can actually start hacking, we need to set those environment variables. First the wifi network credentials, then we define the base URL for all interactions with the Cloudinary API. Next, we head over to Cloudinary and grab our API key and secret. 

## Drawing the Rest of the Owl (TM)

Do you know this image? Now we're going to draw the rest of the owl. Let's create a file for our `ImageUploader` first. Next we'll create some module attributes to hold our constants. First `@tags` and `@upload_preset`, we name both `timelapse_pi` like we specified before. Then we fetch `@key` and `@secret` from the application environment like this.

Now let's create our `take_picture_and_upload` function. This is pretty straightforward - you could split it up into different functions, but I'll leave that to future refactorings.

We start by taking a picture with `Picam.next_frame` and apply base64 encoding. We then construct the data URI by specifying that it's of type `image/png` and that it's `base64` encoded, and concatenate it with the actual image data. Because we are going to submit it as a form-data POST request, we need to URL-encode it, too.

Let's think of some `public_id` to reference our image later. I call it `timelapse_pi` followed by a timestamp - that function doesn't exist yet, we have to write it ourselves later, it's just a placeholder for now.

And then, Cloudinary expects us to supply a signature in a certain, specific format. Here, too, I write a call to a `make_signature` function that doesn't exist yet, but we'll deal with that afterwards.

Alright, let's next construct the actual URL we are going to send our request to. We take the `base_url` we specified as an environment variable before, followed by `/image/upload`, that's Cloudinary's endpoint for uploading image data. 

Finally we get to concatenating the actual request body, consisting of the `file`, where we supply the `file_data_uri` form above, the `api_key`, a `public_id`, the `tags`, the `timestamp`, the `upload_preset`, and the `signature`.

When that is all set and done, we finally send off our request by a call to `HTTPoison.post`, supplying `url`, `body`, a set of headers represented as tuples (here we only specify the `Content-Type`), and finally some options. For some reason this particular request only worked when explicitly setting the `TLS` version to 1.2. 

Okay, that was the hard part, let's look at the helper functions now.

## Helping Out

For one, we need that `timestamp`, that's pretty easy. We fetch the `utc_now` and convert it to a Unix timestamp with `to_unix`.

For the `signature` required by Cloudinary, we first need to construct a string out of some params that are key/value pairs. We do this by a call to `Enum.map_join`. The mapper function interpolates key and value into a string joined by an equals sign. The whole list is then joined together with the `"&"` character.

Afterwards we take this string, append the `secret`, hash this with the `sha` algorithm apply `base16` encoding and `downcase` it. This might seem contrived, but it's the exact data structure the Cloudinary API expects.

## Wrapping Up

Okay, now we need to actually complete the call to `make_signature`. Cloudinary expects us to supply all parameters that are also present in the body, except for `file` and `api_key`, so here we go. There's another twist though: Those params have to be passed in alphabetical order.

Alright, that was (almost) it. As a last step, we only have to make sure the application supervisor starts the `Picam.Camera` process.

We trigger the firmware generation with

		$ mix firmware
		
insert a micro SD card and then run

		$ mix firmware.burn
		
We only have to do this the first time though, as Nerves supports hot reloading of the code via SSH. Yay!

Now we plug the micro SD card into the Pi Zero, start it up and connect to it via `ssh`. And here's what's really neat: We're instantly greeted by an `iex` console, where we can just go about and try our code in a REPL!

Call `TimelapsePicamNerves.ImageUploader.take_picture_and_upload` and  observe that we got a `200` response back, which means everything should have worked. We head over to the Cloudinary media library, see that a `timelapse_pi` folder was created, and voilà, an image of yours truly. How cool is that?

Let's conclude this video at this point, we have already covered _a lot_ of ground. We'll leave the actual generation of the timelapse to the second part of this tutorial.