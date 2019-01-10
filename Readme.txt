The purpose of this project is to implement an RC-Car controller, using CNN (Convolution Neural Network), to avoid obstacles and manage throttle.

Requirements:
	+ Two CNN shall be used: one for throttle, and one for steering
	+ Each CNN's output shall be used in the controlLoop.py main loop.
	+ For all modules, the outputs should be correctly mapped to the inputs of the next (connected) module
	+ An Android application should be created for the remote controller (an Application from the Google PlayStore is already taken into account as a candidate)

The input to the CNN shall be as follows:
	
	+ Frames from the PiCamera
	+ Signal from ultrasonic sensor, calculated as Time-to-Impact

The output of the CNN shall be as follows:

	+ Each of the networks shall have several outputs in the form of:
		
		Throttle (9 outputs):
			* +-Max Throttle
			* +-75% Throttle
			* +-50% Throttle
			* +-25% Throttle
			* No Throttle

		Steering (9 outputs):
			* Same as for the Throttle above

	+ Activation function -> To be defined

Training the CNN:

The initial proposal is to have a selectable mode, where we could tell the car to enter a "training" mode, and during this time to manually drive the car on the track, after which the car would then learn to drive itself. (to verify whether it is possible to perform "on-the-go" training)

While manually driving the car, the following inputs must be stored:
	+ video with the track and any obstacle detected
	+ signal from the ultrasonic sensor
	+ wheel angles for every video frame (conforming to the selected outputs above)
	+ throttle control for every video frame (conforming to the selected outputs above)
