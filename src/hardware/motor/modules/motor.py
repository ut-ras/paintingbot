import pigpio
import threading
import conf
from time import sleep

class Motor:
    '''
        Class for controlling a DC motor with PWM,
        requires two pins per motor to function.
        Meant to be interfaced with a motor controller
    '''

    ## Pin numbers for the two IO pins in use
    forward = None
    direction = None
    reset = None
    currentSense = None
    fault1 = None
    fault2 = None
    pi = None

    currentSpeed = None
    currentDirection = None

    lock = None

    def __init__(self, fwd, pDir, res, CS, FF1, FF2, rate=20000):
        '''
            Starts PWM on the fwd pin and
            back pin, with a rate of [rate]
            hertz. Initializes to 0 duty cycle.
            Needs access to the pigpio daemon,
            achieved by passing the pi parameter
            through
        '''

        ## Exporting them to class variables so that
        ## they can be used by other functions
        self.forward  = fwd
        self.direction = pDir
        self.reset = res
        self.currentSense = CS
        self.fault1 = FF1
        self.fault2 = FF2
        self.pi = pigpio.pi()
        self.currentSpeed = 0
        self.currentDirection=0
        self.lock = threading.Lock()
        ## Turn fwd and direction into output pins
        self.pi.set_mode(fwd, pigpio.OUTPUT)
        self.pi.set_mode(pDir, pigpio.OUTPUT)
        self.pi.set_mode(res, pigpio.OUTPUT)

        ## Turn current sense and fault pins into input pins
        self.pi.set_mode(FF1, pigpio.INPUT)
        self.pi.set_mode(FF2, pigpio.INPUT)
        self.pi.set_mode(CS, pigpio.INPUT)

        ## Initializing fault interrupts
        self.pi.callback(FF1, pigpio.RISING_EDGE, self.fault)
        self.pi.callback(FF2, pigpio.RISING_EDGE, self.fault)

        ## Initializing pins to operate at [rate] frequency
        self.pi.set_PWM_frequency(fwd, rate)

        ## Initializing the motor to the equivalent of no speed
        self.pi.set_PWM_dutycycle(fwd, 0)

        ## Change scale of speed from 0-512 to 0-180
        self.pi.set_PWM_range(fwd, 100)

    def set_speed(self, speed):
        '''
        Changes speed without smoothing
        '''
        if speed < 0 or speed > 100:
            raise ValueError('Speed must be between 0 and 100 inclusive')
        self.pi.set_PWM_dutycycle(self.forward, speed)
        self.currentSpeed = speed

    def lerp_speed(self, speed):
        '''
	     Smoothly changes speed from one to another by
	     using linear interpolation
	     '''
        currentSpeed = self.currentSpeed
        for i in range(currentSpeed, speed, -1 if currentSpeed > speed else 1):
            self.set_speed(speed)
            sleep(0.01)

    def increment_speed(self, inc):
        self.set_speed(self.currentSpeed + inc)
        return self.currentSpeed

    def decrement_speed(self, inc):
        self.set_speed(self.currentSpeed + inc)
        return self.currentSpeed

    def changeSpeedAndDir(self, speed, mDir):
        '''
            Changes the speed and direction of a motor. [speed] is a
            float between 0 and 100. [pDir] is the direction of power
            flow on the motor making it go forward or backward
        '''
        ## Adjusting PWM to match calculated duty cycles
        self.lock.acquire()

        ## Setting the direction of the motor
        if self.currentDirection != mDir:
                self.lerp_speed(0)
                self.pi.write(self.direction, mDir)
                self.currentDirection = mDir
        self.lerp_speed(speed)

        self.lock.release()

    def stop(self):
        '''Stops PWM at the pins but leaves the daemon running'''
        self.pi.changeSpeed(0);

        ## Changes motor driver to low energy mode
        ## TODO: INSPECT THIS
        self.pi.write(self.reset, 0)

    def fault(self):
        ## detects fault, stops motor, and notes which fault occurred
        fault1 = self.pi.read(fault1)
        fault2 = self.pi.read(fault2)
        '''Detected fault '''
        if fault1 and fault2:
                print("Detected fault under voltage")
        elif fault1:
                print("Detected fault overtemp")
        elif fault2:
                print("Detected fault short circuit")
        stop(self)

