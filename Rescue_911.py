import pygame, sys
from pygame import gfxdraw
from pygame.math import Vector2
from pygame.math import Vector3
import time
from djitellopy import tello

# Wichtig Drohne wird benötigt!!!

# class Basic_Shapes():
def draw_polygon(surface, points, color, color_fill):
    gfxdraw.filled_polygon(surface, points, color_fill)
    gfxdraw.aapolygon(surface, points, color)

def draw_trigon(surface, x1, y1, x2, y2, x3, y3, color=(255, 0, 0)):
    gfxdraw.aatrigon(surface, x1, y1, x2, y2, x3, y3, color)
    gfxdraw.filled_trigon(surface, x1, y1, x2, y2, x3, y3, color)

def draw_line(surface, color, start_pos, end_pos):
    pygame.draw.aaline(surface, color, start_pos, end_pos)

def draw_circle(surface, x, y, r, color):
    gfxdraw.circle(surface, x, y, r, color)
    gfxdraw.filled_circle(surface, x, y, r, color)


class Drone():
    def __init__(self, drone_name='Tello', drone_length=10, drone_width=10, cell_size=10,
                 drone_color=pygame.Color(255, 0, 0), drone_start_pos=Vector3(0, 0, 0)):
        self.name = drone_name
        self.cell_size = cell_size
        self.length = drone_length
        self.width = drone_width
        self.drone_color = drone_color
        self.drone_start_pos = drone_start_pos
        self.position = [drone_start_pos, drone_start_pos]  # .body aus dem Beispiel ist ein Vektor3
        self.direction = Vector2(0, 0)  # A unit vector pointing rightward.
        self.next_direction = Vector2(0, 0)
        self.last_direction = Vector2(0, 0)
        self.speed = 2
        self.angle_speed = 0
        self.angle = 0
        self.fly_hight = drone_start_pos.z
        self.search_flight = False
        self.search_flight_finished = False

        self.collision_free_hight = False
        self.home_flight = False
        self.home_flight_finished = False
        self.get_first_step = True

        # Überprüfung der Rasterung
        self.box_check = [True, True, True, False, False, False, True, True]

        # Koordinaten für die Boxen in abhängigkeit zu der Position der Drohne!!!
        self.box1 = Vector2(drone_start_pos.x - 1, drone_start_pos.y - 1)
        self.box2 = Vector2(drone_start_pos.x, drone_start_pos.y - 1)

        # Für immer bewegung richtung Box3 bei begin!!!
        self.box3 = Vector2(drone_start_pos.x + 1, drone_start_pos.y - 1)
        self.box4 = Vector2(self.position[0].x + 1, self.position[0].y)
        self.box5 = Vector2(self.position[0].x + 1, self.position[0].y + 1)
        self.box6 = Vector2(self.position[0].x, self.position[0].y + 1)
        self.box7 = Vector2(self.position[0].x - 1, self.position[0].y + 1)
        self.box8 = Vector2(self.position[0].x - 1, self.position[0].y)

        self.fly_path = Fly_Path(drone_start_pos, self.length, self.width, self.angle, cell_size)

        self.creat_drone()
        self.draw_drone()


    def creat_drone(self):

        self.drone_points_indi = [[0, 0], [self.length, int(self.width / 2)], [0, self.width]]
        self.dpi = self.drone_points_indi
        self.image = pygame.Surface((self.length, self.width))  # ,pygame.SRCALPHA
        draw_trigon(self.image, self.dpi[0][0], self.dpi[0][1], self.dpi[1][0], self.dpi[1][1], self.dpi[2][0],
                    self.dpi[2][1], self.drone_color)
        self.image.set_colorkey((0, 0, 0))
        self.original_image = self.image

    def draw_drone(self):
        for index, block in enumerate(self.position):
            x_pos = int(block.x * self.cell_size)
            y_pos = int(block.y * self.cell_size)
            middle_of_cell = self.cell_size / 2
            self.rect = self.image.get_rect(center=(x_pos + middle_of_cell, y_pos + middle_of_cell))
            self.image = pygame.transform.rotate(self.original_image, -self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)


    def move_drone(self):
        # Unklar ob nötig, da nur ein objekt bewegt wird
        position_copy = self.position[:-1]
        position_copy.insert(0, position_copy[0] + Vector3(self.direction.x, self.direction.y, self.fly_hight))
        self.position = position_copy[:]

        # Info Flugweg (Flight_path):
        if self.search_flight == True:
            self.fly_path.fly_path.insert(0, self.position[1])




    def update_drone(self):
        if self.search_flight == True:

            self.box1 = Vector2(self.position[0].x - 1, self.position[0].y - 1)
            self.box2 = Vector2(self.position[0].x, self.position[0].y - 1)

            # Für immer bewegung richtung Box3 bei begin!!!
            self.box3 = Vector2(self.position[0].x + 1, self.position[0].y - 1)
            self.box4 = Vector2(self.position[0].x + 1, self.position[0].y)
            self.box5 = Vector2(self.position[0].x + 1, self.position[0].y + 1)
            self.box6 = Vector2(self.position[0].x, self.position[0].y + 1)
            self.box7 = Vector2(self.position[0].x - 1, self.position[0].y + 1)
            self.box8 = Vector2(self.position[0].x - 1, self.position[0].y)


    def print(self):
        print(self.name, self.length, self.width)

class Fly_Path():
    def __init__(self, drone_start_pos, length, width, angle, cell_size):
        self.fly_path = [drone_start_pos]
        self.fly_path_color = pygame.Color(0, 100, 0, 255)
        self.length = length
        self.width = width
        self.angle = angle
        self.cell_size = cell_size
        self.creat_fly_path()

    def creat_fly_path(self):
        self.points_indi = [[0, 0], [self.length, 0], [self.length, self.width], [0, self.width]]
        self.dpi = self.points_indi
        self.image = pygame.Surface((self.length, self.width))
        draw_circle(self.image, int(self.length / 2), int(self.width / 2), int(self.cell_size / 2.5),
                    self.fly_path_color)  # surface, x, y, r, color
        self.image.set_colorkey((0, 0, 0))
        self.original_image = self.image

class Room():
    def __init__(self, room_name='test_area', room_sice_x=300, room_sice_y=200, room_sice_z=100,
                 room_color=pygame.Color(255, 0, 0), thickness=10):
        self.name = room_name
        self.th = thickness
        self.room_sice_x = room_sice_x
        self.room_sice_y = room_sice_y
        self.room_sice_z = room_sice_z
        self.room_color = room_color
        #möglichkeit um nachträglich die größe des Raums einzustellen
        #input()

        self.creat_room()

    def creat_room(self):
        self.points_left = [[0, 0], [self.th, 0], [self.th, self.room_sice_y + self.th * 2],
                            [0, self.room_sice_y + self.th * 2]]
        self.rpi_left = self.points_left
        self.imageside = pygame.Surface((self.th, int(self.room_sice_y + self.th * 2)))
        draw_polygon(self.imageside, self.rpi_left, self.room_color, self.room_color)
        self.left_rect = self.imageside.get_rect(
            midright=(int(self.room_sice_x - self.room_sice_x / 2), self.room_sice_y))
        self.right_rect = self.imageside.get_rect(
            midleft=(int(self.room_sice_x + self.room_sice_x / 2), self.room_sice_y))

        self.points_top = [[0, 0], [self.room_sice_x + self.th * 2, 0], [self.room_sice_x + self.th * 2, self.th],
                           [0, self.th]]
        self.rpi_top = self.points_top
        self.imageup = pygame.Surface((self.room_sice_x + self.th * 2, self.th))
        draw_polygon(self.imageup, self.rpi_top, self.room_color, self.room_color)
        self.top_rect = self.imageup.get_rect(
            midbottom=(self.room_sice_x, int(self.room_sice_y - self.room_sice_y / 2)))
        self.down_rect = self.imageup.get_rect(midtop=(self.room_sice_x, int(self.room_sice_y + self.room_sice_y / 2)))

class Mountain():
    def __init__(self,name,hight,cell_size):
        self.mountain_name = name
        self.mountain_hight = hight
        self.angle = 0
        self.mountain_color = pygame.Color(200, 190, 140)
        self.snow_color = pygame.Color(255,255,255)
        self.cell_size = cell_size
        self.mountain_positions = [] #Unklar hier später eine Externe Liste nur mit Daten des Berges... - Einfügen der Vektoren für die Berge
        self.creat_mountain()

    def creat_mountain(self):
        self.mountain_outline = [[0, self.cell_size], [self.cell_size / 2, 0], [self.cell_size, self.cell_size]]
        self.snow_outline = [[self.cell_size * (1 / 4), self.cell_size / 2], [self.cell_size / 2, 0], [self.cell_size * (3 / 4), self.cell_size / 2]]
        self.image = pygame.Surface((self.cell_size, self.cell_size))
        #Mountainoutline
        draw_polygon(self.image,self.mountain_outline,self.mountain_color,self.mountain_color)
        #Snow
        draw_polygon(self.image, self.snow_outline, self.snow_color, self.snow_color)
        self.image.set_colorkey((0, 0, 0))
        self.original_image = self.image

class Programm(object):
    def __init__(self, room_name='test_area', room_sice_x=120, room_sice_y=60, room_sice_z=120, drone_name='Tello',
                 drone_length=20, drone_width=20,drone_vision=20):
        pygame.init()
        self.room_data = Vector3(room_sice_x, room_sice_y, room_sice_z)

        # create main screen
        self.window_x = self.room_data.x * 2
        self.window_y = self.room_data.y * 2
        self.window_mid_pos = [self.window_x / 2, self.window_y / 2]
        self.window = pygame.display.set_mode((self.window_x, self.window_y))

        # create Fly_screen
        self.fly_screen = pygame.Surface((self.room_data.x, self.room_data.y))
        self.fly_screen_rect = self.fly_screen.get_rect(center=self.window_mid_pos)

        # seperate the Fly_screen is cells
        self.drohn_vision = drone_vision              #Relevant für die Erkennung der PAT's
        self.drohn_PAT_detection = self.drohn_vision * 2 #/2 #=40
        self.cell_size = self.drohn_vision
        self.middle_of_cell = self.cell_size / 2
        self.cell_number_x = room_sice_x / self.cell_size
        self.cell_number_y = room_sice_y / self.cell_size

        if self.cell_number_x == float or self.cell_number_y == float:
            # Muss noch auf die Funktion getestet werden, soll Einsetzen wenn der Raum eine Kommazahl ausspukt
            print(
                'Der Flugraum muss ein ganzes Vielfaches der Drohne sein, da Sie sonnst das Gebiet nicht komplett erfassen kann.')
            exit()
            sys.exit()

        self.clock = pygame.time.Clock()

        # creat classes (Hier Room & Drohn)
        self.room_name = room_name
        self.room_name = Room(room_name, room_sice_x, room_sice_y, room_sice_z)
        self.drone_name = drone_name
        self.drone_name = Drone(drone_name, drone_length, drone_width, self.cell_size)
        self.mountain_name = "alpen"
        self.mountain_name = Mountain(self.mountain_name,20,self.cell_size)


        # Sehr sehr wichtig, wenn veränderung, dann unten auch bei send_rc_controles die Entvernungen etc anpassen!!!!


        #Extra Variablen für die Ausführung der Drohnen bewegungen bei Updates
        self.move = False
        self.rotate = 0         #-1 = Links; 0=nichts; 1=Rechts
        self.mountain = False
        self.over_mountain = False
        self.mountain_infront = False
        self.indexed_mountain = True
        self.forward_counter = 0

        #Pat ID Variablen
        self.newpat = 0
        self.lastpat = 0
        #Special Pat's
        self.targetpat = 1

        #Data PAD Coordanates
        self.newpat_x = 0
        self.newpat_y = 0
        self.newpat_z = 0

        self.correct_height = True
        self.pat_command = 0    #0= Kein Pat (nichts machen); 1=Tagetpat (Landen); 2=Berg überfliegen (höhe nach oben); 3=Berg höhe anpassen (nach unten nach Berg)

        self.return_flight = []
        self.return_flight_created = False
        self.return_old_old_movement_num = 0
        self.return_old_movement_num = 0
        self.return_new_movement_num = -1

        #Ecken Laufzeit anpassen
        self.corner_rechts = False
        self.corner_links = False
        self.corner_num = 1

        #Parameter für Rescue
        self.rescue_on_board = False
        self.saved_pause_start_land = 1
        self.pause_start_land = self.saved_pause_start_land     #Sicherheitspause bis am Boden / Wieder gestartet
        self.rescue_land_start = 0      #0=nichts 1=Landen 2=Starten
        self.on_ground = False
        self.saved_ground_time = 4 #rescue_time*timer_time = Warte zeit bis zum Takeoff
        self.ground_time = self.saved_ground_time


        #Allgemeine Flugparameter
        self.normal_fly_hight = 70
        self.current_fly_hight = 0

        # Infos und Verbindung zur Drohne
        self.me = tello.Tello()
        self.me.connect()
        print("\nBattery: "+str(self.me.get_battery())+"%\n")
        self.me.enable_mission_pads()
        self.me.set_mission_pad_detection_direction(0)
        self.me.takeoff()
        self.me.send_rc_control(0,0,0,0)
        time.sleep(3)
        self.check_fly_hight()
        # self.current_fly_hight = self.me.get_height()
        # if self.current_fly_hight != self.normal_fly_hight:
        #     correct_fly_hight = self.normal_fly_hight - self.current_fly_hight
        #     if correct_fly_hight <= -1:
        #         self.me.move("down",correct_fly_hight)
        #     else:
        #         self.me.move("up", correct_fly_hight)
        time.sleep(2)
        print("Angepasste Flughöhe: " + str(self.me.get_height()) + " cm")

        # Drohn Update speed
        self.SCREEN_UPDATE = pygame.USEREVENT+0
        #Timer wird abhier gestellt!!!
        self.timer_time = 2000  #1000=1Sec

        #self.PAD_CHECK = pygame.USEREVENT+1
        #self.pad_check_timer = int(self.timer_time/4)

        print("\nBattery: " + str(self.me.get_battery()) + "%")
        print("Timer Time: "+str(self.timer_time))
        #print("Pad Check Timer"+str(self.pad_check_timer)+"\n")
        pygame.time.set_timer(self.SCREEN_UPDATE, self.timer_time) #1000=1Sec
        #pygame.time.set_timer(self.PAD_CHECK, self.pad_check_timer)



        self.game_loop()

    def game_loop(self):
        while True:
            self.input()

            # window background
            self.window.fill((0, 0, 0))

            # draw elements on the main screen
            self.window.blit(self.room_name.imageside, self.room_name.left_rect)
            self.window.blit(self.room_name.imageside, self.room_name.right_rect)
            self.window.blit(self.room_name.imageup, self.room_name.top_rect)
            self.window.blit(self.room_name.imageup, self.room_name.down_rect)

            # drawing on the fly screen
            self.fly_screen.fill((0, 255, 0))
            self.draw_elements()

            if self.drone_name.search_flight == True:  # Erweiterbar für den Rückflug!!!
                self.draw_fly_path()

            self.draw_all_Mountains()

            self.fly_screen.blit(self.drone_name.image, self.drone_name.rect)

            # draw das innere Feld auf das window
            self.window.blit(self.fly_screen, self.fly_screen_rect)

            #self.missionpad_question()

            pygame.display.update()
            self.clock.tick(60)

    def input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.me.disable_mission_pads()
                self.me.land()
                self.me.end()
                exit()
                sys.exit()

            # wichtig, Drohne bewegt sich nur wenn Zeit oben eintrifft!!!
            # Wenn Taste gedrückt wird wird folgendes geupdatet.
            if event.type == pygame.KEYDOWN:
                #if pygame.key.get_pressed()[pygame.K_q]:
                #    self.drone_name.direction = Vector2(0, 0)
                #    self.drone_name.search_flight = False
                #    print('Landen der Drohne')
                    #self.me.disable_mission_pads()
                    #self.me.land()
                    #self.me.end()
                #    exit()
                #    sys.exit()

                # Hier eigentlich nur Butten für Start der Suche!!!
                if pygame.key.get_pressed()[pygame.K_s]:  # Gedacht zum Starten der Suche

                    if self.drone_name.search_flight != True:
                        self.drone_name.search_flight = True
                        self.drone_name.direction = Vector2(+1, 0)
                        self.move = True


                    else:
                        self.drone_name.direction = Vector2(0, 0)
                        self.drone_name.search_flight = False
                        print('Suche unterbrochen')

            # if event.type == self.PAD_CHECK:
            #     if self.on_ground == False:
            #         if self.drone_name.search_flight == False:
            #             self.check_pat() #Checkt nach möglichen Pat's
            #             print("Timer 2 geht!!!!")

            if event.type == self.SCREEN_UPDATE:
                #Simbolisiert das Auslösen des Screen_UPdates
                print("\n\n###########################################################################################")
                print("###########################################################################################\n\n")
                # print("\nVor dem Test\nDrohnen Richtung" + str(self.drone_name.direction))
                # print("Alte Drohnen Richtung" + str(self.drone_name.last_direction)+"\n")

                #Macht das beim Start nach dem einsammeln nichts überschrieben wird bis flughöhe erreicht wurde
                if self.on_ground == False:
                    self.check_collisions()             #Checkt die Blox um die Drohne

                    #Pat's werden nur solange gechacked bis search flight finished, danach übernimmt Home flight
                    if self.drone_name.search_flight_finished == False:
                        self.check_pat()  #Checkt nach möglichen Pat's

                    #Befehle für den Suchflug
                        if self.drone_name.search_flight == True:


                            if self.correct_height == True:

                                #Soll im Falle eines gemachten Höhenausgleichs den Vector davor wieder übernehmen!!!
                                if self.drone_name.direction == Vector2(0,0) and self.rotate == 0 and self.move == True:
                                    self.drone_name.direction = self.drone_name.last_direction

                                if self.corner_links != True and self.corner_rechts != True:
                                    self.deteckt_corner()
                                self.auto_fly()

                            else:
                                #Soll bei einem Höhenausgleich den Vector Speichern und alles andere Stoppen
                                self.drone_name.last_direction = self.drone_name.direction
                                self.drone_name.direction = Vector2(0, 0)
                                self.rotate = 0
                                self.move = False

                    #Befehle für den Homeflug (für alte Befehle, jedoch neue Befehle machen es leichter)
                    elif self.drone_name.home_flight == True and self.return_flight_created == True and self.drone_name.home_flight_finished == False and self.drone_name.collision_free_hight == True:
                        if self.drone_name.get_first_step == True:
                            self.drone_name.direction = self.drone_name.last_direction
                            self.drone_name.get_first_step = False
                        self.return_flight_movements()
                        print("Auf dem Rückweg")
                    ####
                        # if self.correct_height == True:
                        #     print("Auf dem Rückweg")
                        #     print("Drohnen Richtung"+str(self.drone_name.direction))
                        #     print("Alte Drohnen Richtung"+str(self.drone_name.last_direction))
                        #
                        #     # Soll im Falle eines gemachten Höhenausgleichs den Vector davor wieder übernehmen!!!
                        #     #if self.drone_name.direction == Vector2(0, 0) and self.rotate == 0 and self.move == True:
                        #     #    print("Auf dem Rückweg")
                        #
                        #
                        # else:
                        #     #Soll bei einem Höhenausgleich den Vector Speichern und alles andere Stoppen
                        #     print("Daten werden Überschrieben")
                        #     self.drone_name.last_direction = self.drone_name.direction
                        #     self.drone_name.direction = Vector2(0, 0)
                        #     self.rotate = 0
                        #     self.move = False

                self.update()

    def update(self):
        self.print_direction_questions()

        # Bewegt / ändert den Ort der Drohne (Virtuell)
        self.drone_name.move_drone()
        self.drone_name.update_drone()

        # Info Mountain
        if self.mountain_infront == True:
            self.mountain_name.mountain_positions.insert(0,self.drone_name.position[0] + Vector3(self.drone_name.last_direction.x,self.drone_name.last_direction.y,self.mountain_name.mountain_hight))
            print("Berg wird eingefügt")
            print("Bergkoordinaten: "+str(self.mountain_name.mountain_positions)+"\n")
            self.indexed_mountain = True

        #Übergagbe der realen Drohnen Befehle
        if self.drone_name.search_flight == True:

            if self.move == True:
                self.move_forward()

            elif self.rotate == -1:
                self.rotate_left()

            elif self.rotate == 1:
                self.rotate_right()

            #Immer wenn Pat Command nicht 0 muss die Höhe angepasst werden!!!
            elif self.pat_command !=0:
                print("Höhe wird korregiert")
                self.adjust_height()

            print("Drohne soll sich bewegen!!!")

        elif self.drone_name.home_flight == True:
            if self.move == True:
                self.move_forward()

            elif self.rotate == -1:
                self.rotate_left()

            elif self.rotate == 1:
                self.rotate_right()

            # Immer wenn Pat Command nicht 0 muss die Höhe angepasst werden!!!
            elif self.pat_command != 0:
                print("Höhe wird korregiert")
                self.adjust_height()

            print("Drohne soll sich bewegen!!!")

        elif self.drone_name.home_flight_finished == True:
            print("\nDrohne ist erfolgreich zurückgekehrt")
            print("Das Programm kann jetzt geschlossen werden!!!\n")

        #Sicherheits Pause beim Landen / Starten (Quasi extra Timer)
        elif self.rescue_land_start != 0:
            if self.pause_start_land >= 1:
                self.pause_start_land -= 1

            else: #self.pause_start_land == 0:
                if self.rescue_land_start == 1:
                    print("\nGelandet\n")
                    self.on_ground = True
                    self.creat_return_flight()
                    self.drone_name.search_flight_finished = True  # Abhier nur noch Rückflug
                    self.pause_start_land = self.saved_pause_start_land
                    self.rescue_land_start = 0  # Landung / Start abgeschlossen

                elif self.rescue_land_start==2:
                    print("\nGestartet")
                    self.on_ground = False
                    self.rescue_on_board = True
                    self.pause_start_land = self.saved_pause_start_land
                    self.check_fly_hight()
                    self.rescue_land_start = 3

                else:
                    print("Angepasste Flughöhe: " + str(self.me.get_height()) + " cm")
                    print("Bereit für den Rückweg\n")
                    self.correct_height = True
                    self.pat_command = 0
                    self.drone_name.home_flight = True
                    self.drone_name.collision_free_hight = True
                    self.rescue_land_start = 0  # Landung / Start abgeschlossen


        #Pause am Boden
        elif self.on_ground == True:
            print("\nPerson wird eingeladen")
            print("Noch " +str(self.ground_time*(self.timer_time/1000)) +" sec bis zum Start\n")
            if self.ground_time != 1:
                self.ground_time -= 1
            else:
                self.drone_name.home_flight = True
                self.pat_command = 4
                self.ground_time = self.saved_ground_time

        else:
            print("Drohne stoppt!!!")
            self.me.send_rc_control(0, 0, 0, 0)

    def check_pat(self):
        #Speicher der neuen Sensor Pat Werten
        self.newpat = self.me.get_mission_pad_id()
        self.newpat_x = self.me.get_mission_pad_distance_x()
        self.newpat_y = self.me.get_mission_pad_distance_y()
        self.newpat_z = self.me.get_mission_pad_distance_z()

        #Ausgabe von Prüfungswerten
        self.missionpad_question()

        self.forward_counter -= 1

        #Allgemeine Pat Auslösekriterien für den Abstand (-40<x<60) (-20<y<20)
        if self.newpat_x <= ((self.drohn_PAT_detection/2)*3) and self.newpat_x >= -((self.drohn_PAT_detection/2)*2) and self.newpat_y <= (self.drohn_PAT_detection/2) and  self.newpat_y >= -(self.drohn_PAT_detection/2):

            #Feinere Einstellung für Targetpat
            if self.lastpat != self.newpat and self.newpat == self.targetpat:
                #Abstand(-20<x<20) (-20<y<20)
                if self.newpat_x <= self.drohn_PAT_detection/2 and self.newpat_x >= -self.drohn_PAT_detection/2 and self.newpat_y <= self.drohn_PAT_detection/4 and  self.newpat_y >= -self.drohn_PAT_detection/4:
                #Targetpat = Landen!!! (Geht!!!) "and self.newpat_x <= self.cell_size and self.newpat_y <= self.cell_size"
                    print("Target Pat detected")
                    self.me.send_rc_control(0, 0, 0, 0)
                    self.mountain_infront = False
                    self.pat_print_infos()
                    self.pat_command = 1
                    self.lastpat = self.newpat
                    self.correct_height = False

            #Mountain Pat
            elif self.lastpat != self.newpat and self.newpat != -1 and self.newpat != self.targetpat:
                print("Mountain detected")
                self.me.send_rc_control(0,0,0,0)
                self.mountain_infront = True
                self.pat_print_infos()
                self.pat_command = 6
                self.indexed_mountain = False
                self.lastpat = self.newpat
                self.correct_height = False

        if self.pat_command == 6 and self.indexed_mountain == True:
            print("Getting over the Mountain!")
            self.drone_name.direction = self.drone_name.last_direction
            self.mountain_infront = False
            self.pat_command = 2
            self.correct_height = False


        # Gerade Fläche over Mountain
        elif (self.pat_command == 2 and self.indexed_mountain == True):
            print("On Mountain height!")
            self.mountain_infront = False
            self.pat_command = 0
            self.move = True
            self.correct_height = True
            self.over_mountain = True
            self.forward_counter = 2 #Vorwärtsbefehle hier immer die Zahl +1

        #After Mountain
        elif self.pat_command == 0 and self.over_mountain == True and self.forward_counter == 0:
            print("Past Mountain")
            self.pat_print_infos()
            self.pat_command = 3
            #self.lastpat = self.newpat
            self.correct_height = False
            self.over_mountain = False
            self.mountain_infront = False

        #Gerade Fläche
        elif (self.pat_command == 3):
            print("Flachland")
            print("Standart Flughöhe")
            self.pat_command = 0
            self.move = True
            self.correct_height = True
            self.mountain_infront = False

        print("Aktuelles Pat Command: " + str(self.pat_command))

    # Draw Stuff
    def draw_elements(self):
        self.drone_name.draw_drone()
    # Draw the hole Flypath
    def draw_fly_path(self):
        x = self.drone_name.fly_path.fly_path.pop(0) #Da sonnst Greis auf der neuen Drohnen Position
        for index, block in enumerate(self.drone_name.fly_path.fly_path):
            x_pos = int(block.x * self.drone_name.fly_path.cell_size)
            y_pos = int(block.y * self.drone_name.fly_path.cell_size)
            middle_of_cell = self.drone_name.fly_path.cell_size / 2
            self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                center=(x_pos + middle_of_cell, y_pos + middle_of_cell))
            if index == len(self.drone_name.fly_path.fly_path) - 1:
                self.drone_name.fly_path.image = pygame.transform.rotate(self.drone_name.fly_path.original_image, -45)
                self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                    center=self.drone_name.fly_path.rect.center)
                self.drone_name.fly_path.image = pygame.transform.rotate(self.drone_name.fly_path.original_image, +45)
                self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                    center=self.drone_name.fly_path.rect.center)
                self.fly_screen.blit(self.drone_name.fly_path.image, self.drone_name.fly_path.rect)
            else:
                self.drone_name.fly_path.image = pygame.transform.rotate(self.drone_name.fly_path.original_image,
                                                                         -self.drone_name.fly_path.angle)
                self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                    center=self.drone_name.fly_path.rect.center)
                previous_block = self.drone_name.fly_path.fly_path[index + 1] - block
                next_block = self.drone_name.fly_path.fly_path[index - 1] - block
                if previous_block.x == next_block.x:
                    self.drone_name.fly_path.image = pygame.transform.rotate(self.drone_name.fly_path.original_image,
                                                                             -self.drone_name.fly_path.angle)
                    self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                        center=self.drone_name.fly_path.rect.center)

                elif previous_block.y == next_block.y:
                    self.drone_name.fly_path.image = pygame.transform.rotate(self.drone_name.fly_path.original_image,
                                                                             -self.drone_name.fly_path.angle)
                    self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                        center=self.drone_name.fly_path.rect.center)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        self.drone_name.fly_path.image = pygame.transform.rotate(
                            self.drone_name.fly_path.original_image, -self.drone_name.fly_path.angle)
                        self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                            center=self.drone_name.fly_path.rect.center)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        self.drone_name.fly_path.image = pygame.transform.rotate(
                            self.drone_name.fly_path.original_image, -self.drone_name.fly_path.angle)
                        self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                            center=self.drone_name.fly_path.rect.center)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        self.drone_name.fly_path.image = pygame.transform.rotate(
                            self.drone_name.fly_path.original_image, -self.drone_name.fly_path.angle)
                        self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                            center=self.drone_name.fly_path.rect.center)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        self.drone_name.fly_path.image = pygame.transform.rotate(
                            self.drone_name.fly_path.original_image, -self.drone_name.fly_path.angle)
                        self.drone_name.fly_path.rect = self.drone_name.fly_path.image.get_rect(
                            center=self.drone_name.fly_path.rect.center)
                self.fly_screen.blit(self.drone_name.fly_path.image, self.drone_name.fly_path.rect)
        self.drone_name.fly_path.fly_path.insert(0,x) #Drohnen Wert wird nach dem zeichnen neu eingefügt!!!
    # Draw all Mountains
    def draw_all_Mountains(self):
        for index, block in enumerate(self.mountain_name.mountain_positions):
            x_pos = int(block.x * self.mountain_name.cell_size)
            y_pos = int(block.y * self.mountain_name.cell_size)
            middle_of_cell = self.mountain_name.cell_size / 2
            self.mountain_name.rect = self.mountain_name.image.get_rect(center=(x_pos + middle_of_cell, y_pos + middle_of_cell))

            if index == len(self.mountain_name.mountain_positions) - 1:
                self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, -0)
                self.mountain_name.rect = self.mountain_name.image.get_rect(center=self.mountain_name.rect.center)
                self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, +0)
                self.mountain_name.rect = self.mountain_name.image.get_rect(center=self.mountain_name.rect.center)
                self.fly_screen.blit(self.mountain_name.image, self.mountain_name.rect)
            else:
                self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, -self.mountain_name.angle)
                self.mountain_name.rect = self.mountain_name.image.get_rect(center=self.mountain_name.rect.center)
                previous_block = self.mountain_name.mountain_positions[index + 1] - block
                next_block = self.mountain_name.mountain_positions[index - 1] - block
                if previous_block.x == next_block.x:
                    self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, -self.mountain_name.angle)
                    self.mountain_name.rect = self.mountain_name.image.get_rect(center=self.mountain_name.rect.center)
                ####
                elif previous_block.y == next_block.y:
                    self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, -self.mountain_name.angle)
                    self.mountain_name.rect = self.mountain_name.image.get_rect(
                        center=self.mountain_name.rect.center)
                else:
                    if previous_block.x == -1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == -1:
                        self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, -self.mountain_name.angle)
                        self.mountain_name.rect = self.mountain_name.image.get_rect(center=self.mountain_name.rect.center)
                    elif previous_block.x == -1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == -1:
                        self.mountain_name.image = pygame.mountain_name.transform.rotate(self.mountain_name.original_image, -self.mountain_name.angle)
                        self.mountain_name.rect = self.mountain_name.image.get_rect(
                            center=self.mountain_name.rect.center)
                    elif previous_block.x == 1 and next_block.y == -1 or previous_block.y == -1 and next_block.x == 1:
                        self.mountain_name.image = pygame.transform.rotate(self.mountain_name.original_image, -self.mountain_name.angle)
                        self.mountain_name.rect = self.mountain_name.image.get_rect(center=self.mountain_name.rect.center)
                    elif previous_block.x == 1 and next_block.y == 1 or previous_block.y == 1 and next_block.x == 1:
                        self.mountain_name.image = pygame.transform.rotate(
                            self.mountain_name.original_image, -self.mountain_name.angle)
                        self.mountain_name.rect = self.mountain_name.image.get_rect(
                            center=self.mountain_name.rect.center)
                self.fly_screen.blit(self.mountain_name.image, self.mountain_name.rect)


    # Corner Funktionen
    def deteckt_corner(self):
        if self.drone_name.box_check == [True,True,True,True,True,False,False,True] and self.drone_name.direction == Vector2(+1, 0):
            self.corner_rechts = True

        elif self.drone_name.box_check == [True, True, True, True, False, False, True,True] and self.drone_name.direction == Vector2(-1, 0):
            self.corner_links = True

    def reset_corners(self):
        self.corner_rechts = False
        self.corner_links = False
        self.corner_num = 1

    #Automatisiete Flüge
    def auto_fly(self):
        self.drone_name.last_direction = self.drone_name.direction
        # Scan von oben nach unten!!!

        #Einfügen von besserer Laufzeit

        #Erkennung Ecke Rechts
        if self.corner_rechts == True:

            if self.corner_num == 1:
            #Fall 1 Erkennung Rotation nach Rechts
            #if self.drone_name.box_check == [True,True,True,True,True,False,False,True] and self.drone_name.direction == Vector2(+1, 0):
                self.drone_name.angle += 90
                self.rotate = 1
                self.move = False
                self.drone_name.direction = Vector2(0,0)

            if self.corner_num == 2:
            #Fall 2 Erkennung Bewegung nach Vorne nach Rotation
            #elif self.drone_name.box_check == [True, True, True, True, True, False, False,True] and self.drone_name.direction == Vector2(0, 0) and self.drone_name.angle == 90:
                self.rotate = 0
                self.move = True
                self.drone_name.direction = Vector2(0, 1)

            if self.corner_num == 3:
                #Fall 3a Erkennung neue Flugreihe nach Rotation, Bewegung
                if self.drone_name.box_check == [True, True, True, True, True, False, False,False] and self.drone_name.direction == Vector2(0, 1):
                    self.drone_name.angle += 90
                    self.rotate = 1
                    self.move = False
                    self.drone_name.direction = Vector2(0, 0)

                #Fall 3b Ausnahme Erkennung neue Flugreihe = Unterste Reihe nach Rotation,Bewegung,Rotation
                elif self.drone_name.box_check == [True, True, True, True, True, True, True,False] and self.drone_name.direction == Vector2(0, 1):
                    self.drone_name.angle += 90
                    self.rotate = 1
                    self.move = False
                    self.drone_name.direction = Vector2(0, 0)

            if self.corner_num == 4:
                #Fall 4a Erkennung neue Flugreihe nach Rotation,Bewegung,Rotation
                # if self.drone_name.box_check == [True, True, True, True, True, False, False,False] and self.drone_name.direction == Vector2(0, 0) and self.drone_name.angle == 180:
                #     self.rotate = 0
                #     self.move = True
                #     self.drone_name.direction = Vector2(-1, 0)
                #
                # # Fall 4b Erkennung neue Flugreihe nach Rotation,Bewegung,Rotation
                # elif self.drone_name.box_check == [True, True, True, True, True, True, True,False] and self.drone_name.direction == Vector2(0, 0) and self.drone_name.angle == 180:
                #     self.rotate = 0
                #     self.move = True
                #     self.drone_name.direction = Vector2(-1, 0)

                self.rotate = 0
                self.move = True
                self.drone_name.direction = Vector2(-1, 0)
                self.corner_rechts = False

            self.corner_num += 1

        #Erkennung Ecke Links
        if self.corner_links == True:

            #Fall 1
            if self.corner_num == 1:
            #if self.drone_name.box_check == [True, True, True, True, False, False, True,True] and self.drone_name.direction == Vector2(-1, 0):
                self.drone_name.angle -= 90
                self.rotate = -1
                self.move = False
                self.drone_name.direction = Vector2(0, 0)

            #Fall 2
            if self.corner_num == 2:
            #elif self.drone_name.box_check == [True,True,True,True,False,False,True,True] and self.drone_name.direction == Vector2(0, 0):
                self.rotate = 0
                self.move = True
                self.drone_name.direction = Vector2(0, 1)

            if self.corner_num == 3:
                self.rotate = 0
                self.move = True
                self.drone_name.direction = Vector2(0, 0)

            #Fälle 3
            if self.corner_num == 4:
                #Fall 3a
                if self.drone_name.box_check == [True, True, True, False, False, False, True,True] and self.drone_name.direction == Vector2(0, 1):
                    self.drone_name.angle -= 90
                    self.rotate = -1
                    self.move = False
                    self.drone_name.direction = Vector2(0, 0)

                #Fall 3b
                elif self.drone_name.box_check == [True, True, True, False, True, True, True,True] and self.drone_name.direction == Vector2(0, 1):
                    self.drone_name.angle -= 90
                    self.rotate = -1
                    self.move = False
                    self.drone_name.direction = Vector2(0, 0)

            #Fälle 4
            if self.corner_num == 5:

                # #Fall 4a
                # if self.drone_name.box_check == [True, True, True, False, False, False, True,True] and self.drone_name.direction == Vector2(0, 0):
                #     self.rotate = 0
                #     self.move = True
                #     self.drone_name.direction = Vector2(1, 0)
                #
                #
                # #Fall 4b
                # elif self.drone_name.box_check == [True, True, True, False, True, True, True, True] and self.drone_name.direction == Vector2(0, 0):
                #     self.rotate = 0
                #     self.move = True
                #     self.drone_name.direction = Vector2(1, 0)

                self.rotate = 0
                self.move = True
                self.drone_name.direction = Vector2(1, 0)
                self.corner_links = False

            self.corner_num += 1

        if self.corner_links == False and self.corner_rechts == False:
            self.reset_corners()

        #Erkennung gesamtes Gebiet durchscannt
        if self.drone_name.box_check == [True, True, True, True, True, True, True, True]:
            print("Drohne stoppt!!!")
            self.me.send_rc_control(0, 0, 0, 0)
            self.drone_name.last_direction = self.drone_name.direction
            self.drone_name.direction = Vector2(0, 0)
            self.move = 0
            self.rotate = 0
            self.drone_name.search_flight = False
            print('Suche im gesamen Gebiet Beendet')
            self.drone_name.search_flight_finished = True  # Abhier nur noch Rückflug
            self.drone_name.home_flight = True
            self.drone_name.collision_free_hight = True
            self.creat_return_flight()

    def return_flight_movements(self):

        self.return_old_movement_num = self.return_new_movement_num
        self.return_old_old_old_movement_num = self.return_new_movement_num -3
        self.return_new_movement_num += 1

        new_movement = self.return_flight[self.return_new_movement_num]
        old_old_old_movement = self.return_flight[self.return_old_old_old_movement_num]

        #Auflistung der Befehle und was passieren muss in der Update Funktion
        if new_movement == "ro_right":
            self.drone_name.angle += 90
            self.rotate = 1
            self.pat_command = 0
            self.move = False

            #Vector Drehung nach rechts
            if self.drone_name.direction != Vector2(0, 0):
                if self.drone_name.direction == Vector2(1,0):
                    self.drone_name.next_direction = Vector2(0,1)
                elif self.drone_name.direction == Vector2(0,1):
                    self.drone_name.next_direction = Vector2(-1,0)
                elif self.drone_name.direction == Vector2(-1,0):
                    self.drone_name.next_direction = Vector2(0,-1)
                elif self.drone_name.direction == Vector2(0-1):
                    self.drone_name.next_direction = Vector2(1,0)
            # Drehung nach Höheneinstellungen
            elif self.drone_name.next_direction != Vector2(0, 0):
                if self.drone_name.next_direction == Vector2(1,0):
                    self.drone_name.next_direction = Vector2(0,1)
                elif self.drone_name.next_direction == Vector2(0,1):
                    self.drone_name.next_direction = Vector2(-1,0)
                elif self.drone_name.next_direction == Vector2(-1,0):
                    self.drone_name.next_direction = Vector2(0,-1)
                elif self.drone_name.next_direction == Vector2(0-1):
                    self.drone_name.next_direction = Vector2(1,0)
            # Drehung wenn nach Drehungsparameter im Suchflug
            elif self.drone_name.last_direction != Vector2(0, 0):
                if self.drone_name.last_direction == Vector2(1,0):
                    self.drone_name.next_direction = Vector2(0,1)
                elif self.drone_name.last_direction == Vector2(0,1):
                    self.drone_name.next_direction = Vector2(-1,0)
                elif self.drone_name.last_direction == Vector2(-1,0):
                    self.drone_name.next_direction = Vector2(0,-1)
                elif self.drone_name.last_direction == Vector2(0-1):
                    self.drone_name.next_direction = Vector2(1,0)
            else:
                print("Achtung Fehler bei der Drehung!!!")
            self.drone_name.direction = self.drone_name.last_direction
            self.drone_name.direction = Vector2(0,0)

        elif new_movement == "ro_left":
            self.drone_name.angle -= 90
            self.rotate = -1
            self.pat_command = 0
            self.move = False
            #Vector Drehung nach links
            if self.drone_name.direction != Vector2(0,0):
                if self.drone_name.direction == Vector2(1,0):
                    self.drone_name.next_direction = Vector2(0,-1)
                elif self.drone_name.direction == Vector2(0,-1):
                    self.drone_name.next_direction = Vector2(-1,0)
                elif self.drone_name.direction == Vector2(-1,0):
                    self.drone_name.next_direction = Vector2(0,1)
                elif self.drone_name.direction == Vector2(0,1):
                    self.drone_name.next_direction = Vector2(1,0)
            # Drehung nach Höheneinstellungen
            elif self.drone_name.next_direction != Vector2(0,0):
                if self.drone_name.next_direction == Vector2(0,-1):
                    self.drone_name.next_direction = Vector2(-1,0)
                elif self.drone_name.next_direction == Vector2(-1,0):
                    self.drone_name.next_direction = Vector2(0,1)
                elif self.drone_name.next_direction == Vector2(0,1):
                    self.drone_name.next_direction = Vector2(1,0)
                elif self.drone_name.next_direction == Vector2(1,0):
                    self.drone_name.next_direction = Vector2(0,-1)
            # Drehung wenn nach Drehungsparameter im Suchflug
            elif self.drone_name.last_direction != Vector2(0,0):
                if self.drone_name.last_direction == Vector2(1,0):
                    self.drone_name.next_direction = Vector2(0,-1)
                elif self.drone_name.last_direction == Vector2(0,-1):
                    self.drone_name.next_direction = Vector2(-1,0)
                elif self.drone_name.last_direction == Vector2(-1,0):
                    self.drone_name.next_direction = Vector2(0,1)
                elif self.drone_name.last_direction == Vector2(0,1):
                    self.drone_name.next_direction = Vector2(1,0)
            else:
                print("Achtung Fehler bei der Drehung!!!")
            self.drone_name.direction = self.drone_name.last_direction
            self.drone_name.direction = Vector2(0,0)


        elif new_movement == "move":
            self.rotate = 0
            self.pat_command = 0
            self.move = True
            if self.drone_name.direction == Vector2(0,0):
                print("Drohnen Richtung wird angepasst")
                self.drone_name.direction = self.drone_name.next_direction

        elif new_movement == "go_up":
            self.move = False
            self.rotate = 0
            self.pat_command = 2
            if self.drone_name.direction == Vector2(0,0):
                self.drone_name.next_direction = self.drone_name.next_direction
            else:
                self.drone_name.next_direction = self.drone_name.direction
            self.drone_name.direction = Vector2(0,0)

        elif new_movement == "go_down":
            self.move = False
            self.rotate = 0
            self.pat_command = 3
            if self.drone_name.direction == Vector2(0, 0):
                self.drone_name.next_direction = self.drone_name.last_direction
            else:
                self.drone_name.next_direction = self.drone_name.direction
            self.drone_name.direction = Vector2(0,0)

        elif new_movement == "Finish":
            self.move = False
            self.rotate = 0
            self.pat_command = 5
            self.drone_name.home_flight_finished = True
            self.drone_name.direction = Vector2(0,0)

    #Erstellung des Rückflugs
    def creat_return_flight(self):
        if self.return_flight_created == False:
            self.me.disable_mission_pads()

            #creat a returnflyght Liste in __init   self.return_flight = []
            double_ro_right = ["ro_right", "ro_right"]

            #Einfügen Max Flughöhe über alle Berge (als erstes da manchmal der Erste Befahl nicht übernommen wird
            self.return_flight.append("go_up")
            self.return_flight.append("go_up")
            self.return_flight.append("go_up")

            #1. Check Rotation to y = 0
            print("Last Driection: "+str(self.drone_name.last_direction))
            if self.drone_name.last_direction != Vector2(0,-1): #4
                print("Drehung muss eingefügt werden!!!")
                if self.drone_name.last_direction == Vector2(1, 0): #1
                    self.return_flight.append("ro_left")
                elif self.drone_name.last_direction == Vector2(-1, 0): #2
                    self.return_flight.append("ro_right")
                elif self.drone_name.last_direction == Vector2(0, 1): #3 #Hier auch 2x ro_left möglich
                    self.return_flight.extend(double_ro_right)



            #2. Einfügen der Schritte nach y=0
            y_steps = self.drone_name.position[0].y-self.drone_name.drone_start_pos.y
            y_steps_Berg = y_steps - 1
            Schleifen_Zaehler = 0
            for i in range(0, int(y_steps)):

                # for index, block in enumerate(self.mountain_name.mountain_positions):
                #     if block.x == self.drone_name.drone_start_pos.x:
                #         if y_steps_Berg == block.y:
                #             self.return_flight.append("go_up")
                #             self.return_flight.append("move")
                #             self.return_flight.append("go_down")
                #             y_steps_Berg -= 1
                #         pass

                self.return_flight.append("move")

            #3. Rotation nach Links
            self.return_flight.append("ro_left")

            #4. Einfügen der Schritte nach x=0
            x_steps = self.drone_name.position[0].x-self.drone_name.drone_start_pos.x
            for i in range(0, int(x_steps)):
                self.return_flight.append("move")

            #5. Rotation in Anfangstellung
            self.return_flight.extend(double_ro_right)

            #6. Landen
            self.return_flight.append("Finish")
            self.return_flight_created = True
            print("\n\n############################################################\n"
                  "Return flight created\n"
                  "############################################################\n\n")
            print(str(self.return_flight)+"\n\n")

    #Check fly hight
    def check_fly_hight(self):
        print("Flughöhe wird eingenommen")
        self.current_fly_hight = self.me.get_height()
        print("Aktuelle Flughöhe: "+str(self.current_fly_hight)+" cm")
        if self.current_fly_hight != self.normal_fly_hight:
            correct_fly_hight = self.normal_fly_hight - self.current_fly_hight
            if correct_fly_hight <= -1:
                if abs(correct_fly_hight) >= 20 and abs(correct_fly_hight) <= 500:
                    self.me.move("down",abs(correct_fly_hight))
            else:
                if correct_fly_hight >= 20 and correct_fly_hight <= 500:
                    self.me.move("up", correct_fly_hight)
            print(correct_fly_hight)



    #Funktionen für die Realenbewegungen
    def move_forward(self):
        if self.drone_name.search_flight_finished == False:
            self.me.send_rc_control(0, 14, 0, 0) #Möglichst genau anpassen!!! #15 ist gut 14 noch näher/ Problem zu wenig bei den Drehungen
        else:
            self.me.send_rc_control(0, 12, 0, 0)
        print("Bewegung Vorwärts")

    def rotate_left(self):
        self.me.send_rc_control(0,0,0,-60)  #Möglichst genau anpassen!!!    / Drehung sieht bei 61 gut aus 59 versuchen
        print("Drehung Links")

    def rotate_right(self):
        self.me.send_rc_control(0,0,0,60)   #Möglichst genau anpassen!!!
        print("Drehung Rechts")

    def adjust_height(self):
        #Zwischenlandung
        if self.pat_command == 1:
            self.me.send_rc_control(0, 0, 0, 0)
            print("Landen")
            self.me.land()
            self.drone_name.search_flight = False
            self.rescue_land_start = 1

        # Nach oben
        elif self.pat_command == 2:
            # self.me.send_rc_control(0, 0, 0, 0)
            print("Ausweichen")
            self.me.send_rc_control(0, 0, 20, 0)

        # Nach unten
        elif self.pat_command == 3:
            # self.me.send_rc_control(0, 0, 0, 0)
            print("Zurück auf Standart Höhe")
            self.me.send_rc_control(0, 0, -20, 0)

        #Start nach Einsammeln
        elif self.pat_command == 4:
            print("Start")
            self.me.takeoff()
            self.rescue_land_start = 2
            self.drone_name.home_flight = False

        #Landen am Anfangspunkt
        elif self.pat_command == 5:
            self.me.send_rc_control(0, 0, 0, 0)
            print("Landen auf dem Start Punkt")
            self.drone_name.home_flight_finished = True
            self.me.land()
            self.me.end()
            exit()
            sys.exit()


    # All about Collisions
    def check_collisions(self):
        self.length = len(self.drone_name.box_check)
        self.box = Vector2(0, 0)
        for x in range(self.length):
            if x == 0:
                self.box = self.drone_name.box1
                # print('Check Box1:')
            elif x == 1:
                self.box = self.drone_name.box2
                # print('Check Box2:')
            elif x == 2:
                self.box = self.drone_name.box3
                # print('Check Box3:')
            elif x == 3:
                self.box = self.drone_name.box4
                # print('Check Box4:')
            elif x == 4:
                self.box = self.drone_name.box5
                # print('Check Box5:')
            elif x == 5:
                self.box = self.drone_name.box6
                # print('Check Box6:')
            elif x == 6:
                self.box = self.drone_name.box7
                # print('Check Box7:')
            elif x == 7:
                self.box = self.drone_name.box8
                # print('Check Box8:')

            if self.drone_room_collisions(self.box) == True:
                self.drone_name.box_check[x] = True
            elif self.fly_path_collisions(self.box) == True:
                self.drone_name.box_check[x] = True
            else:
                self.drone_name.box_check[x] = False

    def drone_room_collisions(self, box):
        if self.drone_left_collision(box) == True:
            return True
        elif self.drone_right_collision(box) == True:
            return True
        elif self.drone_up_collision(box) == True:
            return True
        elif self.drone_down_collision(box) == True:
            return True
        else:
            return False

    def drone_left_collision(self, box):
        if box.x < 0:
            # print('Rand_Links')
            return True

    def drone_right_collision(self, box):
        if box.x > self.cell_number_x - 1:
            # print('Rand_Rechts')
            return True

    def drone_up_collision(self, box):
        if box.y < 0:
            # print('Rand_Oben')
            return True

    def drone_down_collision(self, box):
        if box.y > self.cell_number_y - 1:
            # print('Rand_Unten')
            return True

    def fly_path_collisions(self, box):
        for element in self.drone_name.fly_path.fly_path:
            if element.x == box.x and element.y == box.y:
                # print('Has already been searched!')
                return True

    # Print Funktionen
    def missionpad_question(self):
        print("\n_____________________________________________________________________________________________________")
        print("Allgemeine Ausgabe von Daten")
        print("Ausgabe des neuen Missionpads: " + str(self.newpat))
        print("Ausgabe des letzten Missionpads: " + str(self.lastpat))
        print("Aktuelle Entfernung zum neuen Missionpad (in X-Richtung):" + str(self.me.get_mission_pad_distance_x())+" cm")
        print("letzte Mission Pat Command: " + str(self.pat_command))
        print("_____________________________________________________________________________________________________\n")

    def pat_print_infos(self):
        print("PAT ID: " + str(self.newpat))
        print("Entfernung zum Missionpad in x Richtung:" + str(self.me.get_mission_pad_distance_x()) + "cm")
        print("Entfernung zum Missionpad in y Richtung:" + str(self.me.get_mission_pad_distance_y()) + "cm")
        print("Entfernung zum Missionpad in z Richtung:" + str(self.me.get_mission_pad_distance_z()) + "cm\n")

    def print_direction_questions(self):
        print("\nAusgeführte Drohnen Richtungen\nDrohnen Richtung" + str(self.drone_name.direction))
        print("Alte Drohnen Richtung" + str(self.drone_name.last_direction))
        print("Nächste Drohnen Richtung" + str(self.drone_name.next_direction) + "\n")

#Input Von Daten
#room_name = input("Enter the Name of the room: ")
#room_sice_x = input("Enter the size of the room: ")
#room_sice_y = input("Enter the size of the room: ")
#room_sice_z = input("Enter the size of the room: ")
#drone_name = input("Enter the name of your drone: ")
#drone_length = input("Enter the length of your drone: ")
#drone_width = input("Enter the width of your drone: ")

#mapping = Programm(room_name, room_sice_x, room_sice_y, room_sice_z, drone_name,drone_length, drone_width)

mapping = Programm()
