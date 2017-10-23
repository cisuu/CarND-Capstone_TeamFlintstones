
GAS_DENSITY = 2.858
ONE_MPH = 0.44704


import rospy
from pid import PID

class TwistController(object):
    def __init__(self, pid_velocity_params,pid_steer_params,vehicle_mass,decel_limit,wheel_radius):

        # TODO: Implement
        self.pid_velocity_params = pid_velocity_params
        self.pid_steer_params    = pid_steer_params
        self.vehicle_mass = vehicle_mass
        self.decel_limit = decel_limit
        self.wheel_radius = wheel_radius

        # Create a pid controller of the velocity control
        self.velocity_controller = PID(self.pid_velocity_params, mn = -1.0, mx = 1.0)

        # Create a pid controller of the steer control
            # Max steer @ steeringwheel = 90 degrees
        self.steermax = 90 * 3.14/180 # in radians
        self.steering_controller = PID(self.pid_steer_params, mn = -1.0*self.steermax, mx = self.steermax)

        # Timers for the two controllers
        self.prev_vel_msg_time = 0.0
        self.prev_steer_msg_time = 0.0

    # def control(self, *args, **kwargs):
    def control(self, velocity_error_mps, yawrate_error_radps,
                      dbw_enabled,  loop_rate):

        # TODO: Change the arg, kwarg list to suit your needs
        throttle = brake = steering = 0.0

        if dbw_enabled:

            # Velocity controller
            # Call the step function of the velocity controller to get new control value
            sample_time = 1.0/loop_rate
            throttle = self.velocity_controller.step(velocity_error_mps, sample_time)
            rospy.loginfo('in twist_controller, throttle = %s'% throttle)
            # rospy.loginfo('in twist_controller: time, pid params: %s, %s, %s, %s'% (sample_time,
            #                                                     self.velocity_controller.kp,
            #                                                     self.velocity_controller.ki,
            #                                                     self.velocity_controller.kd))

            # If the throttle value is negative, that means we need to brake
            if (throttle<0.0):
                # TODO : Need to convert brake signal value into torque
                brake = -1.0*throttle

                # Convert brake value from 0 to 1  --> 0 to Max torque
                brake  = brake *  self.decel_limit * self.vehicle_mass * self.wheel_radius

                # Set the throttle to 0, since we are braking.
                throttle = 0.0
            else:
                # Don't apply brakes when we are accelerating. You are not Ken Block
                brake = 0.0

            # Steering controller
            # Call the step function of the velocity controller to get new control value
            steering = self.steering_controller.step(yawrate_error_radps,1.0/loop_rate)

        else:
            self.velocity_controller.reset()
            self.steering_controller.reset()

        # Return throttle, brake, steer
        # return 1., 0., 0.
        return throttle, brake, steering

