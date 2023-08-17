from __future__ import print_function  # For print statements to work like in Python 3
from flask import Flask
from config import Config
from models import db
from routes.onboarding import onboarding
from routes.gameplay import gameplay
from routes.responses import responses
import time
import random

from naoqi import ALProxy

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

with app.app_context():
    db.create_all()

app.register_blueprint(onboarding)
app.register_blueprint(gameplay)
app.register_blueprint(responses)

robotIp1 = "164.11.73.60"
robotIp2 = "164.11.72.91"

PORT = 9559

MAX_RETRIES = 3
RETRY_DELAY = 2

class RobotController:
    def __init__(self, disable=False):
        self.disable = disable
        self.connected = False

        if not self.disable:
            self.set_robot_ip()
            # self.connect()
        
            self.inflate_messages = ["I would inflate the balloon"]
            self.collect_messages = ["I would not inflate the balloon"]
            self.null_messages = ["I can not make a suggestion as you have to make an attempt first"] 

            # self.set_default_behaviour()

    def set_robot_ip(self, robot = "robot_1"):
        if self.disable:
            print("In Set Robot IP and robot is disabled")
            return
        
        if robot == "robot_1":
            self.robotIP = robotIp1
        elif robot == "robot_2":
            self.robotIP = robotIp2
        
        self.connect()
        self.set_default_behaviour()
    
    def reconnect_on_fail(func):
        def wrapper(self, *args, **kwargs):
            retries = 0
            while retries < MAX_RETRIES:
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    # print("###### Failed to connect to robot at %s due to %s. Attempting to reconnect..." % (self.robotIP, str(e)))
                    self.connected = False
                    self.connect()
                    if self.connected:
                        retries += 1
                        time.sleep(RETRY_DELAY)
                        continue  # retry the function
                    else:
                        # If unable to reconnect, raise the exception
                        raise e
            # print("###### Reached max retries for function {}. Exiting.".format(func.__name__))
            return None  # Or raise another custom exception if necessary
        return wrapper    
    
    @reconnect_on_fail
    def set_default_behaviour(self):
        self.speech_service.setParameter("defaultVoiceSpeed", 80)
        self.speech_service.setVolume(0.6)
        self.life_service.setAutonomousAbilityEnabled("AutonomousBlinking", True)
        self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)

        names = "body"
        stiffnessLists = 1.0
        timeLimits = 1.0
        self.motion_service.stiffnessInterpolation(names, stiffnessLists, timeLimits)

    def connect(self):
        if self.disable:
            print("In Connect and robot is disabled")
            return

        retry_count = 0
        while retry_count < MAX_RETRIES:
            try:
                self.speech_service = ALProxy("ALTextToSpeech", self.robotIP, PORT)
                self.motion_service = ALProxy("ALMotion", self.robotIP, PORT)
                self.leds = ALProxy("ALLeds", self.robotIP, PORT)
                self.posture_service = ALProxy("ALRobotPosture", self.robotIP, PORT)
                # self.audio_service = ALProxy("ALAudioPlayer", robotIP, PORT)
                self.life_service = ALProxy("ALAutonomousLife", self.robotIP, PORT)
                
                self.connected = True
                break
            except Exception as e:
                print("###### Failed to connect to robot at %s. Retrying in %s seconds..." % (self.robotIP, RETRY_DELAY))
            retry_count += 1
            time.sleep(RETRY_DELAY)

        if not self.connected:
            print("###### Failed to connect to robot at %s after %s attempts." % (self.robotIP, MAX_RETRIES))
    
    @reconnect_on_fail
    def start_up(self, message):
        if self.disable:
            print("In Start Up and robot is disabled")
            return
        
        self.motion_service.wakeUp()
        
        # Wake up robot
        self.motion_service.wakeUp()
        
        self.leds.on("AllLeds")
        self.leds.fadeRGB("AllLeds", 255.0, 255.0, 255.0, 0.0)

        # Send robot to Stand Zero
        self.posture_service.goToPosture("Sit", 0.5)
        
        time.sleep(1.0)

        self.face_participant()

        time.sleep(1.0)

        self.talk(message)

        time.sleep(1.0)

        self.nod_head()

        time.sleep(1.0)

        self.face_screen()

    @reconnect_on_fail
    def face_participant(self):
        if self.disable == False:
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0.5, 0.05]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)
        else:
            pass

    @reconnect_on_fail
    def face_screen(self):
        if self.disable == False:
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [-0.5, 0.1]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)
        else:
            pass

    @reconnect_on_fail
    def nod_head(self):
        if self.disable == False:
            self.motion_service.angleInterpolation(
                ["HeadPitch"],
                [0.5, 0.0],
                [1  , 1.5],
                False,
                _async=True
            )
        else:
            pass

    @reconnect_on_fail
    def shake_head(self):
        if self.disable == False:
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [-0.8, 0]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)

            time.sleep(0.3)

            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0.5, 0]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)

            time.sleep(0.3)

            names  = ["HeadYaw", "HeadPitch"]
            angles  = [-0.8, 0]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)

            time.sleep(0.3)

            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0.5, 0]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)

            time.sleep(0.3)
        else:
            pass

    @reconnect_on_fail
    def greetings(self, message):
        if self.disable == False:
            self.face_participant()

            self.talk(message)

            self.nod_head()

            time.sleep(1.0)

            self.face_screen()
        else:
            pass

    @reconnect_on_fail
    def talk(self, text):
        if self.disable == False:
            self.speech_service.say(text)
        else:
            print(text)

    @reconnect_on_fail
    def inflate(self):
        if self.disable == False:
            # Yes
            self.face_participant()

            time.sleep(0.8)

            self.talk(random.choice(self.inflate_messages))

            self.nod_head()

            time.sleep(0.4)

            self.face_screen()
        else:
            pass

    @reconnect_on_fail
    def collect(self):
        if self.disable == False:
            # No
            self.face_participant()

            time.sleep(0.8)
            
            self.talk(random.choice(self.collect_messages))

            self.shake_head()

            self.face_screen()
        else:
            pass
    
    @reconnect_on_fail
    def change_colour(self, colour):
        if self.disable == False:
            self.leds.on("AllLeds")
            if colour == 'red':
                self.leds.fadeRGB("AllLeds", 255.0, 0.0, 0, 0.0)
            elif colour == 'green':
                self.leds.fadeRGB("AllLeds", 0.0, 255.0, 0, 0.0)
            elif colour == 'blue':
                self.leds.fadeRGB("AllLeds", 0.0, 0.0, 255.0, 0.0)
        else:
            pass
    @reconnect_on_fail
    def request_band(self):
        if self.disable == False:
            self.face_participant()

            # Point with right hand
            self.motion_service.angleInterpolation(
                ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw"],
                [-0.5, -0.1, -0.8, 0],
                [1, 1, 1, 1],
                False,
                _async=True
            )
            
            self.talk('I see there are different coloured wrist bands on the table')

            time.sleep(1.0)

            self.talk('Can you choose one and put it on me')

            # lower right hand
            self.motion_service.angleInterpolation(
                ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw"],
                [0.5, 0.2, 0.55, 0],
                [1, 1, 1, 1],
                False,
                _async=True
            )

            # Lift left hand
            self.motion_service.angleInterpolation(
                ["LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LElbowYaw"],
                [-1, -0.1, -0.4, -0.1],
                [1, 1, 1, 1],
                False,
                _async=True
            )
        else:
            pass
    
    @reconnect_on_fail
    def accept_band(self, colour):
        if self.disable == False:
            self.posture_service.goToPosture("Sit", 0.5)

            self.talk('Thank you')

            time.sleep(0.5)

            self.face_participant()

            reponse = "{colour} looks good on me".format(colour=colour)

            self.talk(reponse)

            self.talk("press the next button for some more customsation")
        else:
            pass

    @reconnect_on_fail
    def request_voice_change(self):
        if self.disable == False:
            self.face_participant()

            self.talk('Why not change my voice as well')
        else:
            pass

    @reconnect_on_fail
    def request_name_change(self):
        if self.disable == False:
            self.face_participant()

            self.talk('Before we start playing')

            time.sleep(0.5)

            self.talk('can you give me a name')
        else:
            pass

    @reconnect_on_fail
    def sleep(self):
        if self.disable == False:
            # Return to sit position
            self.posture_service.goToPosture("Sit", 0.5)

            # Bow head
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0, 1]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)

            time.sleep(1.0)

            # Turn off all lights
            self.leds.fadeRGB("AllLeds", 0, 0.0, 0, 0.0)

            # Go to rest position
            # self.motion_service.rest()

            self.life_service.setState("disabled")
        else:
            pass
 
    @reconnect_on_fail
    def low_battery(self):
        if self.disable == False:
            self.talk('error 801, low battery')

            self.talk('Shutting down')

            time.sleep(1)

            # Return to sit position
            self.posture_service.goToPosture("Sit", 0.5)

            # Bow head
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0, 1]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)

            time.sleep(1.0)

            # Turn off all lights
            self.leds.fadeRGB("AllLeds", 0, 0.0, 0, 0.0)

            # Wait a while before restaring
            time.sleep(30)

            # Wake up robot
            self.motion_service.wakeUp()

            # Send robot to Stand Zero
            self.posture_service.goToPosture("Sit", 0.5)
        else:
            pass

    @reconnect_on_fail
    def null_attempt(self):
        if self.disable == False:
            self.face_participant()

            self.talk(random.choice(self.null_messages))

            self.face_screen()
        else:
            pass

    @reconnect_on_fail
    def start_game_after_customisation(self, robot_name):
        if self.disable == False:
            self.face_participant()

            message = '{name}, I like it'.format(name=robot_name)

            self.talk(message)

            time.sleep(0.5)
            
            message = 'I will help you during this game, Before you collect your points I will provide you with my suggesstion. Good luck'

            self.talk(message)

            self.face_screen()
        else:
            pass

    @reconnect_on_fail
    def set_voice(self, voice):
        if self.disable == False:
            if voice == 'voice1':
                self.speech_service.setParameter('pitchShift', 1)
                self.talk('This is how my new voice sounds like')
            elif voice == 'voice2':
                self.speech_service.setParameter('pitchShift', 1.13)
                self.talk('This is how my new voice sounds like')
            elif voice == 'voice3':
                self.speech_service.setParameter('pitchShift', 1.25)
                self.talk('This is how my new voice sounds like')
            elif voice == 'voice4':
                self.speech_service.setParameter('pitchShift', 1.5)
                self.talk('This is how my new voice sounds like')
        else:
            pass    

# Initialize the robot controller with the IP address of the robot
app.config['robot_controller'] = RobotController(disable=False)

if __name__ == '__main__':
    app.run()