# Robotics_ROS_workspace

## Running the Code

The ROS code has a launch file included, which means that to run it you can type " ros2 launch motor_ctl motor_ctl_launch.yaml " into the command line (assuming you have ROS sourced and built the package). The code for the micro controller is also included, called main.py, and this needs to be run simultaniously from the microcontoller to get readings from the sensors. 

The code also utilizes code from the Dynamixel Python repo in order to control the two servo motors in the robot. The repo needs to be pip installed so that the package is available for use. All of the code for getting the motors to run is in the ROS package subscriber, and runs by setting the veolocity of the motor and a timer. This repo is public and can be found on the Dynamixel github owned by msgtn. It has information on how to install the package and write the code, in case modifiactions are needed.

## Assembling the Robot

The track was built using metal rods screwed together, and has a motor holder on the end of the track. The .step file is included in this repo. There are also .step files for mounting the gripper on to the track, holding the motor for the gripper, and a cap to screw on the motor to attach gears for the gripper. The rest of the gripper is built using legos, though this is not reccomended as they can be flimsy. 
