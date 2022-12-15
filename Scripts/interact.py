import bpy
from bge import logic

cont = logic.getCurrentController()
own = cont.owner

ray = cont.sensors["InteractRay"]
e = cont.sensors["InteractKey"]

def every_1_seconds():
    obj = ray.hitObject
    if "Locked" in obj:
        if obj["Locked"] == True:
            if own["Key"]:
                obj["Locked"] = False
                own["Key"] = False
            else:
                return

    if "Key" in obj:
        own["Key"] = True

    if "Disabled" in obj:
        print("has atrribute")
        if obj["Disabled"]:
            return

    if obj["Interact"]:
        obj["Interact"] = False
    else:
        obj["Interact"] = True

if ray.positive:
    if e.positive:
       every_1_seconds()


bpy.app.timers.register(every_1_seconds)