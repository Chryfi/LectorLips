# LectorLips
A cool script that allows to convert Adobe Characte Animator mouth animation data into a sequencer morph.
<br><br>
## Setup
First you need to install Python. You probably need to restart your computer after installing it. Test ouf if the command `python` works. It should look something like this:

![Screenshot_658](https://user-images.githubusercontent.com/71967555/206724791-961cb012-f198-4d24-b31d-5acb22da707b.png)

Now you need to tell the script what filenames the mouth pictures have and which mouth they belong to. The image [visemeMapping.jpg](./visemeMapping.jpg) shows the mouth shapes used by Adobe Character Animator. The numbers indicate the order in which you have to define your image file names.

Type `cmd` into the file explorer in the LectorLips folder like this:

![Screenshot_659](https://user-images.githubusercontent.com/71967555/206726526-122a93c3-4212-41e6-927b-7faf01becd76.png)

This will open the CMD in that folder.
Now you need to enter the command 
```
python __init__.py -create_viseme_mapping 0.png 1.png 2.png 3.png 4.png 5.png 6.png 7.png 8.png 9.png 10.png 11.png 12.png 13.png 14.png
```
You can name those image files however you want.
<br><br>
## Adobe Character Animator
First import your audio file. If you have the transcript of the audio, you can use it to increase the accuracy of the mouth animation. Therefore paste your transcript into the transcript text box in the properties context.![transcript](https://user-images.githubusercontent.com/71967555/207728582-b28859d4-70ac-4269-a2f3-ec6d6a8942f5.png)



Now you need to generate the mouth animation. For this go to `Timeline -> Compute Lip Sync Take from Audio and Transcript` as seen in the image. If you didn't enter a transcript, choose the option without the transcript.

![generatemouthanimation](https://user-images.githubusercontent.com/71967555/207729241-3f082bfd-d09f-4df8-ba54-9e3e4213312e.png)
<br><br>
## Convert Character Animator mouth animation into sequencer morph
To convert your mouth animation, you first need to convert it into After Effects Visemes. To do this, right click on your audio and click `Copy Visemes for After Effects`.


![copyvisemes](https://user-images.githubusercontent.com/71967555/207731794-44059f09-9e81-441c-829c-5f5464af86e8.png)

Now you need to paste the copied data into a text file. Then you can execute the command:
```
python __init__.py -create_sequencer /path/to/AfterEffects_keyframes.txt "b.a:path/to/blockbuster/mouth/textures/"
```

With the argument `/path/to/AfterEffects_keyframes.txt` you define the path to the file where you copied the keyframe data to.

With `"b.a:path/to/blockbuster/mouth/textures/"` you define the texture path that should be used in the Blockbuster mod. The texture files in that folder need to have the same names as the ones you defined in your setup.

The command will create a file with the current date where it writes the generated sequencer morph NBT data into.

You need to copy this NBT data and paste it into the morph menu of metamorph.

That's it!
<br><br>
## List of commands

`-help`

```
-create_sequencer
arguments: <path to After Effects keyframe.txt> <Blockbuster path to the mouth textures folder>
optional: <duration of the last mouth in ticks> <different viseme_mapping_filename>
```

```
-create_viseme_mapping
arguments: <15 image file names according to visemeMapping.jpg>
optional: <new viseme_mapping filename>
```
