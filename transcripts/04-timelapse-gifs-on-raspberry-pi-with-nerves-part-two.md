Okay, back to the point where I left you. Before we go on though, I'd like to try a little refactoring first. 

That part where we build a parameter string from this keyword list will be of use in other parts of the application. So I define a new private function `param_string_from_keyword_list` which takes a keyword list, and perform the exact same `map_join` operation from above. Now we can simply call this from the `make_signature` function.

Back above in the main function, we attempt to do the same with the request body. I duplicate everything from above into a keyword list and pipe it into our newly defined utility function. Let's delete the old body, though, and take a look if everything still works.

For that we call

		$ mix firmware
		
and afterwards

		$ mix firmware.gen.script

which will in turn generate a script called `upload.sh`, which we can call with the target host, like so:

		$ ./upload.sh timelapse_picam_nerves.local
		
And this is what makes nerves so ingenious: hot code replacement via ssh. I don't know of any other embedded computing framework with the same level of comfort :-)

After it's done, we are disconnected from the ssh port, because the device is rebooting. Few seconds later, we can connect again:

		$ ssh timelapse_picam_nerves.local

From the iEx console, let's try if our upload still works. It does seem so.

## Coding the Actual Timelapse

By now you're probably thinking that something is missing from this tutorial of making a timelapse... ah yes, the actual timelapse. Let's tackle that now.

Let's start out by defining a new function, `create_gif_animation`. The interface Cloudinary gives us consists of calling another URL (ending in `/multi`) with a `tag` to make a running animation from. You guessed it, that's why I introduced the `@tags` attribute in the first place.

Again we need a signature, so we provide it. We include `tag` and `timestamp`, that's all we need for this call.

The request body then consists of these parameters plus `api_key` and `signature`. We use our utility function again, and formulate the request.

## Tasking the Module

To generate a recurring sequence of calls to our uploader and converter functions, we convert our module into a `Task` that can be started by a supervisor by calling `use Task`. Before we go about initializing it, we will code two polling functions.

To make this work, we will employ a little trick: The `receive` special form in Elixir provides an `after` clause which will fire if no matching message is received. In our case, we just leave the `receive` block empty and call `take_picture_and_upload` and `poll_picture` recursively. Next, we do the same for `poll_gif`.

To initialize our Task, we call `start_link` on those two functions when starting the task.

Back in `application.ex`, we need to make this new task part of the supervision tree, so that it will be kicked off upon application start. If you're new to Elixir, you'll likely want to catch up on supervision trees, because it's the most prominent feature of the Elixir/Erlang ecosystem.

Alright, back in our console we'll do another firmware update, and wait for the device to come online again. Using the built-in `Toolshed` module, we can print out the running processes, and see our `ImageUploader` has been started. Magnificent!

Back in the Cloudinary media library, we see a lot of images have already been taken, and if we navigate back out of this folder, we see that also our little GIF is ready.