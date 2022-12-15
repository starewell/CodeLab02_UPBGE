###############################################################################
#             Character Controller | Template v 1.0 | UPBGE 0.3.0+            #
###############################################################################
#                      Created by: Guilherme Teres Nunes                      #
#                       Access: youtube.com/UnidayStudio                      #
#                               github.com/UnidayStudio                       #
#               github.com/UnidayStudio/UPBGE-CharacterController             #
#                                                                             #
#                           Copyright - July 2018                             #
#                        This work is licensed under                          #
#           the Creative Commons Attribution 4.0 International                #
###############################################################################

## import dictionaries
import bge
from collections import OrderedDict
from mathutils import Vector, Matrix

def clamp(x, a, b):
    return min(max(a, x), b)

# class based components! just like in Unity
# to attach this component to an object, add a game component to it in the game object properties tab and link
# character_controller_complex.CharacterController
class CharacterController(bge.types.KX_PythonComponent):


# "global" variables, serialized dict saved in blender GUI, vars used in start
    args = OrderedDict([
        ("Activate", True),
        ("Walk Speed", 0.1),
        ("Run Speed", 0.2),
        ("Max Jumps", 1),
        ("Avoid Sliding", True),
        ("Static Jump Direction", False),
        ("Static Jump Rotation", False),
        ("Smooth Character Movement", 0.0),
        ("Make Object Invisible", False),
    ])

# local variable declaration happens in start
# create pointers to global vars and initialize blender components
    def start(self, args):

        self.active = args["Activate"]

        self.walkSpeed = args["Walk Speed"]
        self.runSpeed = args["Run Speed"]

        self.avoidSliding = args["Avoid Sliding"]
        self.__lastPosition = self.object.worldPosition.copy()
        self.__lastDirection = Vector([0,0,0])
        self.__smoothSlidingFlag = False

        self.__smoothMov = clamp(args["Smooth Character Movement"], 0, 0.99)
        self.__smoothLast = Vector([0,0,0])

        self.staticJump = args["Static Jump Direction"]
        self.__jumpDirection = [0,0,0]

        self.staticJumpRot = args["Static Jump Rotation"]
        self.__jumpRotation = Matrix.Identity(3)

# get reference to blender character controller, set max jumps
        self.character = bge.constraints.getCharacter(self.object)
        self.character.maxJumps = args["Max Jumps"]

        if self.active:
            if args["Make Object Invisible"]:
                self.object.visible = False

# function that applies force to our character controller
    def characterMovement(self):

#input setup
        keyboard = bge.logic.keyboard.inputs
        keyTAP = bge.logic.KX_INPUT_JUST_ACTIVATED

#speed init
        x = 0
        y = 0
        speed = self.walkSpeed

#if running
        if keyboard[bge.events.LEFTSHIFTKEY].active:
            speed = self.runSpeed

#keyboard inputs
        if keyboard[bge.events.WKEY].active:   y = 1
        elif keyboard[bge.events.SKEY].active: y = -1
        if keyboard[bge.events.AKEY].active:   x = -1
        elif keyboard[bge.events.DKEY].active: x = 1

#translate input to vector
        vec = Vector([x, y, 0])
        self.__smoothSlidingFlag = False
        if vec.length != 0:
            self.__smoothSlidingFlag = True
# normalizing the vector
            vec.normalize()
# multiply by the speed
            vec *= speed

#static jump; lock vector if jumping if this is enabled
        if not self.character.onGround:
            if self.staticJump:
                vec = self.__jumpDirection
            if self.staticJumpRot:
                self.object.worldOrientation = self.__jumpRotation.copy()
        else:
            self.__jumpDirection = vec
            self.__jumpRotation  = self.object.worldOrientation.copy()

#lerp position by input vector
        smooth = 1.0 - self.__smoothMov
        vec = self.__smoothLast.lerp(vec, smooth)
        self.__smoothLast = vec
        test = self.object.worldPosition.copy()
        self.character.walkDirection = self.object.worldOrientation @ vec
#set position of game object
        if vec.length != 0:
            self.__lastDirection = self.object.worldPosition - self.__lastPosition
            self.__lastPosition = self.object.worldPosition.copy()

# function to trigger jump on space press
    def characterJump(self):

        keyboard = bge.logic.keyboard.inputs
        keyTAP = bge.logic.KX_INPUT_JUST_ACTIVATED

        if keyTAP in keyboard[bge.events.SPACEKEY].queue:
            self.character.jump()

    def avoidSlide(self):

        self.object.worldPosition.xy = self.__lastPosition.xy

        other = self.object.worldOrientation @ self.__smoothLast

        if self.__lastDirection.length != 0 and other.length != 0:
            if self.__lastDirection.angle(other) > 0.5:
                if not self.__smoothSlidingFlag:
                    self.__smoothLast = Vector([0,0,0])

# called every logic step interval in UPBGE
    def update(self):
        if self.active:
            self.characterMovement()
            self.characterJump()

            if self.avoidSliding:
                self.avoidSlide()
