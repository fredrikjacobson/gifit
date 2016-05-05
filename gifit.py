#!/usr/bin/env python3

import sys, getopt
from moviepy.editor import *
import re



def time_symetrize(clip):
    """ Returns the clip played forwards then backwards. In case
    you are wondering, vfx (short for Video FX) is loaded by
    >>> from moviepy.editor import * """
    return concatenate([clip, clip.fx( vfx.time_mirror )])

def main(argv):

   HELP_STRING = 'gifit.py -i <inputfile> -o <outputfile> -t mm:ss-mm:ss'
   OPTIONS = '''Usage: gifit.py -i <inputfile> -o <outputfile> -t mm:ss-mm:ss [OPTIONS]

   Options:
   -h          Print this help and exit
   --subtitles Subtitles in the form "{mm:ss-mm:ss <subtitle string>}
   --crop      Crops video by parameters. Available parameters:
                  x1 and x2 to crop horizontally
                  y1 and y2 to crop vertically
                  (x1, y1) and (x2, y2) to crop an arbitrary rectangle
                  width or height in pixels
   --cuts      replaces -t by specifying several times in {mm:ss-mm:ss} format which are concatenated

   Flags:
   --preview   Opens a PyGame windows where presses are printed to terminal, facilitating cropping
   --fx        Time symetrization, looping the gif back and forth'''


   inputfile = ''
   outputfile = ''
   try:
      opts, args = getopt.getopt(argv,"hi:t:o:",["subtitles=", "crop=", "cuts=", "preview", "fx"])
   except getopt.GetoptError:
      print (HELP_STRING)
      sys.exit(2)

   arguments = set(list(zip(*opts))[0])

   if arguments == set(['-h']):
      print (OPTIONS)
      sys.exit(2)


   # Required inputs
   if not arguments.issuperset(set(['-i','-t', '-o'])) and not arguments.issuperset(set(['-i','--cuts', '-o'])): 
      print (HELP_STRING)
      sys.exit(2)
      
         

   captions = []
   sub_clips = []
   list_of_subclips = []
   list_of_composite_videos = []
   preview = False
   crop = False
   fx_opt = False

   for opt, arg in opts:
      if opt in ("-i", "--ifile"):
         inputfile = arg
      elif opt in ("-o", "--ofile"):
         outputfile = arg
      elif opt == '-t':
         sub_clips.append(arg)
      elif opt == '--cuts':
         sub_clips = re.findall('\{([^\}]*)\}', arg)
      elif opt == '--subtitles':
         captions = re.findall('\{([^\}]*)\}', arg)
      elif opt == '--crop':
         crop = True
         crops = re.findall('(\w\d)=\ ?(\d*)', arg)
         crop_args = {'x1':None, 'y1':None, 'x2':None, 'y2':None, 'width':None, 'height':None, 'x_center':None, 'y_center':None}
         for parameter in crops: crop_args[parameter[0]] = int(parameter[1])
      elif opt == '--preview': preview = True
      elif opt == '--fx': fx_opt = True
      

   for section in sub_clips:

      cut_time = [x.split(':') for x in section.split('-')]
      t1 = float(cut_time[0][0]) * 60 + float(cut_time[0][1])
      t2 = float(cut_time[1][0]) * 60 + float(cut_time[1][1])



      video_clip = (VideoFileClip(inputfile, audio=False)
                  .subclip(t1, t2)
                  .resize(.5)
                  .speedx(0.5)
                  )
      list_of_subclips.append(video_clip)
   print(list_of_subclips)
   video_clip = concatenate( list_of_subclips )


   # Possible options to crop, time_symetrize or preview clip before subtitles are added
   if crop: 
      video_clip = video_clip.crop(x1=crop_args['x1'], y1=crop_args['y1'], x2=crop_args['x2'], y2=crop_args['y2'], width=crop_args['width'], height=crop_args['height'], x_center=crop_args['x_center'], y_center=crop_args['y_center'])   
   if fx_opt:
      video_clip = video_clip.fx( time_symetrize )
   if preview: video_clip.preview()

   #Final video is added to list
   list_of_composite_videos.append(video_clip)

   for cap in captions:
      time, subtitle = cap.split(' ',1)
      time = [x.split(':') for x in time.split('-')]
      start = float(time[0][0]) * 60 + float(time[0][1])
      duration = float(time[1][0]) * 60 + float(time[1][1]) - start
      
      subtitle = (subtitle+'\n').encode('latin1')


      text = (TextClip(subtitle,
                        fontsize=20, color='white',
                        font='Georgia', interline=0,)
               .set_duration(duration))

      list_of_composite_videos.append(text.set_start(start).set_pos(("center","bottom")))

   composition = CompositeVideoClip( list_of_composite_videos )
   composition.write_gif(outputfile, fps=10, fuzz=2)




if __name__ == "__main__":
   main(sys.argv[1:])