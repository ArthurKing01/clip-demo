ffmpeg -i 1.mp4 -r 1 -f image2 image1-%03d.jpg

ffmpeg -i sports.mp4 -vf fps=1 image1-%03d.jpg