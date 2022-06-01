from djitellopy import tello
from time import sleep


me = tello.Tello()
me.connect()



print("Battery: " + str(me.get_battery()) +"%")
print("Temperatur: " + str(me.get_temperature()) + "°C")

me.enable_mission_pads()
me.set_mission_pad_detection_direction(0)
me.takeoff()
print("Pause für 2 Sec")
sleep(2)
me.land()
me.disable_mission_pads()
sleep(1)

print("Battery: " + str(me.get_battery()) +"%")
print("Temperatur: " + str(me.get_temperature()) + "°C")

me.end()
exit()