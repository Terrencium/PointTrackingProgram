# PointTrackingProgram
Takes reference points to create a transform a perspective distorted video, undistort it and plot points that translate to real world coordinates.



First enter the path to the .MOV file you are trying to analyze in the terminal.

Next plot at least 4 points as reference points, then enter into the python terminal the real world coordinates to each of the reference points in the order that you clicked them.

Next enter start and end frames of your video, these are not extremely important as you can change frames during the video.

Next plot points using the mouse and confirm them using the space key, each one of those will register as the location set for the frame.

Once it you are done hit the escape key and the points in real world coordinates will be printed out into the terminal in the format: frame #, x, y

The returned coordinates will be localized to the starting frame, which will be set to (0,0)
