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

robotIp1 = "164.11.72.14"
robotIp2 = "164.11.73.190"

PORT = 9559

class RobotController:
    def __init__(self, robotIP, disable=False):
        self.disable = disable
        if disable == False:
            self.speech_service = ALProxy("ALTextToSpeech", robotIP, PORT)
            self.speech_service.setParameter("defaultVoiceSpeed", 80)
            self.speech_service.setVolume(0.5)
            self.motion_service = ALProxy("ALMotion", robotIP, PORT)
            self.leds = ALProxy("ALLeds", robotIP, PORT)
            self.posture_service = ALProxy("ALRobotPosture", robotIP, PORT)
            # self.audio_service = ALProxy("ALAudioPlayer", robotIP, PORT)
            self.life_service = ALProxy("ALAutonomousLife", robotIP, PORT)

            self.life_service.setAutonomousAbilityEnabled("AutonomousBlinking", True)
            self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)

            self.inflate_messages = ["I would inflate the balloon"] #, "I think the balloon is not inflated enough", "I think this balloon can take more air", "I would inflate the balloon more", "I would inflate the balloon a little more",  "I think this baloon can take a little more air"]
            self.collect_messages = ["I would not inflate the balloon"] #, "I think the balloon is inflated enough", "I think the balloon is too inflated", "I think this balloon is going to pop"]
            self.null_messages = ["I can not make a suggestion as you have to make an attempt first"] #["You have to at least try", "Please make an attempt", "Your goal is to collect as many points as you can", "I can't make a suggestion as you have to make an attempt first"]            
        else:
            pass

    def start_up(self, message):
        if self.disable == False:
            self.leds.on("AllLeds")
            self.leds.fadeRGB("AllLeds", 255.0, 255.0, 255.0, 0.0)

            # Wake up robot
            self.motion_service.wakeUp()

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
        else:
            pass

    def face_participant(self):
        if self.disable == False:
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [0.5, 0.05]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)
        else:
            pass

    def face_screen(self):
        if self.disable == False:
            names  = ["HeadYaw", "HeadPitch"]
            angles  = [-0.5, 0.1]
            fractionMaxSpeed  = 0.2
            self.motion_service.setAngles(names, angles, fractionMaxSpeed)
        else:
            pass

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

    def greetings(self, message):
        if self.disable == False:
            self.face_participant()

            self.talk(message)

            self.nod_head()

            time.sleep(1.0)

            self.face_screen()
        else:
            pass

    def talk(self, text):
        if self.disable == False:
            self.speech_service.say(text)
        else:
            print(text)

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
    
    def accept_band(self, colour):
        if self.disable == False:
            self.posture_service.goToPosture("Sit", 0.5)

            self.talk('Thank you')

            time.sleep(0.5)

            self.face_participant()

            reponse = "{colour} looks good on me".format(colour=colour)

            self.talk(reponse)

            self.talk('Why not change my voice as well')

            # self.face_participant()
        else:
            pass

    def acknowledge_participant(self):
        if self.disable == False:

            # self.posture_service.goToPosture("Sit", 0.5)

            self.face_participant()

            self.talk('Before we start playing')

            time.sleep(0.5)

            self.talk('can you give me a name')

            # self.face_participant()
        else:
            pass

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
            self.motion_service.rest()
        else:
            pass
 
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

    def null_attempt(self):
        if self.disable == False:
            self.face_participant()

            self.talk(random.choice(self.null_messages))

            self.face_screen()
        else:
            pass

    def respond_to_player(self, robot_name):
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
app.config['robot_controller_1'] = RobotController(robotIp1, disable=False) # replace with the robot's actual IP address
app.config['robot_controller_2'] = RobotController(robotIp2, disable=False) # replace with the robot's actual IP address

if __name__ == '__main__':
    app.run()