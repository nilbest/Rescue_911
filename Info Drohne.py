from djitellopy import tello


me = tello.Tello()
me.connect()

print("Battery: " + str(me.get_battery()) +"%")
print("Temperatur: " + str(me.get_temperature()) + "°C")

me.end()
exit()




