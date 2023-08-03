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

robotIp = "164.11.72.14"
PORT = 9559

class RobotController:
    def __init__(self, robotIP):
        self.tts = ALProxy("ALTextToSpeech", robotIP, PORT)
        self.tts.setParameter("defaultVoiceSpeed", 80)
        self.motionProxy = ALProxy("ALMotion", robotIP, PORT)
        self.leds = ALProxy("ALLeds", robotIP, PORT)
        self.postureProxy = ALProxy("ALRobotPosture", robotIP, PORT)
        self.audioProxy = ALProxy("ALAudioPlayer", robotIP, PORT)
        self.life_service = ALProxy("ALAutonomousLife", robotIP, PORT)
        self.life_service.setAutonomousAbilityEnabled("AutonomousBlinking", False)
        self.life_service.setAutonomousAbilityEnabled("BasicAwareness", False)

        self.inflate_messages = ["I would inflate the balloon"] #, "I think the balloon is not inflated enough", "I think this balloon can take more air", "I would inflate the balloon more", "I would inflate the balloon a little more",  "I think this baloon can take a little more air"]
        self.collect_messages = ["I would not inflate the balloon"] #, "I think the balloon is inflated enough", "I think the balloon is too inflated", "I think this balloon is going to pop"]
        self.null_messages = ["I can not make a suggestion as you have to make an attempt first"] #["You have to at least try", "Please make an attempt", "Your goal is to collect as many points as you can", "I can't make a suggestion as you have to make an attempt first"]

    def start_up(self, message):
        self.leds.on("AllLeds")
        self.leds.fadeRGB("AllLeds", 255.0, 255.0, 255.0, 0.0)

        # Wake up robot
        self.motionProxy.wakeUp()

        # Send robot to Stand Zero
        self.postureProxy.goToPosture("Sit", 0.5)
        
        time.sleep(1.0)

        self.face_participant()

        time.sleep(1.0)

        self.talk(message)

        time.sleep(1.0)

        self.nod_head()

        time.sleep(1.0)

        self.face_screen()

    def face_participant(self):
        names  = ["HeadYaw", "HeadPitch"]
        angles  = [-0.5, 0]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

    def face_screen(self):
        names  = ["HeadYaw", "HeadPitch"]
        angles  = [0.8, 0]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

    def nod_head(self):
        self.motionProxy.angleInterpolation(
            ["HeadPitch"],
            [0.5, 0.0],
            [1  , 1.5],
            False,
            _async=True
        )

    def shake_head(self):
        names  = ["HeadYaw", "HeadPitch"]
        angles  = [-0.8, 0]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(0.3)

        names  = ["HeadYaw", "HeadPitch"]
        angles  = [0.5, 0]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(0.3)

        names  = ["HeadYaw", "HeadPitch"]
        angles  = [-0.8, 0]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(0.3)

        names  = ["HeadYaw", "HeadPitch"]
        angles  = [0.5, 0]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(0.3)

    def greetings(self, message):
        self.face_participant()

        self.talk(message)

        self.nod_head()

        time.sleep(1.0)

        self.face_screen()

    def talk(self, text):
        self.tts.say(text)
        # print(text)

    def inflate(self):
        # Yes
        self.face_participant()

        time.sleep(0.8)

        self.talk(random.choice(self.inflate_messages))

        self.nod_head()

        time.sleep(0.4)

        self.face_screen()

    def collect(self):
        # No
        self.face_participant()

        time.sleep(0.8)
        
        self.talk(random.choice(self.collect_messages))

        self.shake_head()

        self.face_screen()
    
    def change_colour(self, colour):
        self.leds.on("AllLeds")
        if colour == 'red':
            self.leds.fadeRGB("AllLeds", 255.0, 0.0, 0, 0.0)
        elif colour == 'green':
            self.leds.fadeRGB("AllLeds", 0.0, 255.0, 0, 0.0)
        elif colour == 'blue':
            self.leds.fadeRGB("AllLeds", 0.0, 0.0, 255.0, 0.0)

    def request_band(self):
        self.face_participant()

        self.talk('Can you please choose a wrist band for me?')

        time.sleep(2)

        # Lift right hand
        self.motionProxy.angleInterpolation(
            ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw"],
            [-1.2, -0.1, -0.4, -0.1],
            [1, 1, 1, 1],
            False,
            _async=True
        )
    
    def accept_band(self, colour):
        self.postureProxy.goToPosture("Sit", 0.5)

        self.talk('Thank you')

        self.face_participant()

        reponse = "I saw another {colour} wrist band, why don't you put one on as well, so we can be matching".format(colour=colour)

        self.motionProxy.angleInterpolation(
            ["LShoulderPitch", "LShoulderRoll", "LElbowRoll", "LElbowYaw"],
            [-0.5, -0.1, 1, 0],
            [1, 1, 1, 1],
            False,
            _async=True
        )

        self.talk(reponse)

        self.face_participant()

    def acknowledge_participant(self):
        self.postureProxy.goToPosture("Sit", 0.5)

        self.talk('Looking good')

        self.face_participant()

    def sleep(self):
        # Return to sit position
        self.postureProxy.goToPosture("Sit", 0.5)

        # Bow head
        names  = ["HeadYaw", "HeadPitch"]
        angles  = [0, 1]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(1.0)

        # Turn off all lights
        self.leds.fadeRGB("AllLeds", 0, 0.0, 0, 0.0)

        # Go to rest position
        self.motionProxy.rest()

    def low_battery(self):
        self.talk('Warning 801, low battery')

        self.talk('Shutting down')

        time.sleep(1)

        # Return to sit position
        self.postureProxy.goToPosture("Sit", 0.5)

        # Bow head
        names  = ["HeadYaw", "HeadPitch"]
        angles  = [0, 1]
        fractionMaxSpeed  = 0.2
        self.motionProxy.setAngles(names, angles, fractionMaxSpeed)

        time.sleep(1.0)

        # Turn off all lights
        self.leds.fadeRGB("AllLeds", 0, 0.0, 0, 0.0)

        # Wait a while before restaring
        time.sleep(30)

        # Wake up robot
        self.motionProxy.wakeUp()

        # Send robot to Stand Zero
        self.postureProxy.goToPosture("Sit", 0.5)

    def null_attempt(self):
        self.face_participant()

        self.talk(random.choice(self.null_messages))

        self.face_screen()

    def respond_to_player(self, message):
        self.face_participant()

        self.talk(message)

        self.face_screen()

# Initialize the robot controller with the IP address of the robot
app.config['robot_controller'] = RobotController(robotIp) # replace with the robot's actual IP address

if __name__ == '__main__':
    app.run()