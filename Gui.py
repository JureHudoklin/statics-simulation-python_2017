import sys
import numpy as np
from tkinter import *
import bg
from PIL import ImageTk, Image
#import numericne_metode
from scipy.interpolate import *

main_height = 150
selected = ["red", "blue"]

class Gui():
    """
    class--> kreira grafični vmesnik
    """
    def __init__(self, master):
        self.vkljucena = 0  #definira vključeno funkcijo
        self.lokacije_konzol = [0,0]
        self.lokacije_nosilca =[0,0]
        self.kontinuerana_narjena = 0
        self.kreiran = 0 #rabim za izris. Če enako nič objekta za izris še nisem kreiral. Če enako 1 je že kreiran
        self.postavljen = 0 #rabim ko postavim podporo. Če == 0 še ni postavljena

        frame_top = Frame(master)  #glavni frame za gumbe
        self.canvas = Canvas(master, width=600, height=300)  #glavni frame za grafiko
        self.frame_NTM = Frame(master,width=300, height=800)
        self.frame_NTM.pack(side = RIGHT)

        """
        Spodaj so definirani bindi gumbov na funkcije
        """
        self.canvas.bind("<Motion>", self.motion)  #premikanje miške premika izris konzole--> glej funkcijo motion
        self.canvas.bind("<Button-1>", self.postavi_podporo)


        """
        V canvasu naredi pike kjer je možno postavljati stvari
        """
        for x in range(0,1000,10):
            self.canvas.create_oval(x-1, main_height-1, x+1, main_height+1, fill="black")

        frame_top.pack(side=BOTTOM)
        self.canvas.pack(side=TOP)

        """
        Spodaj so definirani vsi gumbi, označbe ,polja, ...
        """
        self.button_stat_podpora = Button(frame_top, command=lambda: self.spremeni_funkcijo("stat"), text="Statična podpora")
        self.button_din_podpora = Button(frame_top, command=lambda: self.spremeni_funkcijo("din"), text="Drsna podpora")
        self.button_konzola = Button(frame_top, command=lambda: self.spremeni_funkcijo("konzola"), text="Konzola")
        self.button_nova_sila = Button(frame_top, command=self.nova_sila, text="Dodaj silo")
        self.button_nosilec = Button(frame_top, command=self.dodaj_nosilec, text="Dodaj nosilec")
        self.button_izvedi_nosilec = Button(frame_top, command=self.izvedi_nosilec, text="Izvedi nosilec", bg="lightblue")
        self.button_izracun = Button(self.frame_NTM, command=self.izracun, text="Izračun", bg="red", fg="yellow")
        self.button_kontinuerana_tocke = Button(frame_top, command=lambda: self.spremeni_funkcijo("kontinuerana_tocke"), text="tocke za kont. obremenitev")
        self.button_kontinuerana_naredi = Button(frame_top, command=self.kontinuerana_naredi, text="Naredi kont. obremenitev")

        self.label_podpore = Label(frame_top, text="Izberi podporo:")
        self.label_xy = Label(frame_top, text="0,0")
        self.label_xkoord = Label(frame_top, text="X koordinata")
        self.label_velikost = Label(frame_top, text="Velikost sile")
        self.label_kot = Label(frame_top, text="Kot delovanja sile")
        self.label_nos_x = Label(frame_top, text="zač. nosilca")
        self.label_nos_x2 = Label(frame_top, text="kon. nosilca")
        self.label_določi_nosilec = Label(frame_top, text="Določi nosilec:")
        self.label_dodaj_silo = Label(frame_top, text="Dodaj silo:")


        self.entry_sila_x = Entry(frame_top, text="x koordinata")
        self.entry_sila_kot = Entry(frame_top, text="kot sile")
        self.entry_sila_velikost = Entry(frame_top, text="velikost sile")
        self.entry_nosilec_x1 = Entry(frame_top)
        self.entry_nosilec_x2 = Entry(frame_top)

        self.entry_nosilec_x1.insert(0,"10")
        self.entry_nosilec_x2.insert(0,"40")
        self.entry_sila_velikost.insert(0,"50")
        self.entry_sila_kot.insert(0,"90")
        self.entry_sila_x.insert(0,"20")

        """
        Spodaj vse gumbe, labele ter ostala polja dodam na top frame
        """
        self.label_xy.grid(row = 0, column = 0, sticky=NW)
        self.button_izvedi_nosilec.grid(row = 3, column = 4, pady = [0,20])

        self.label_podpore.grid(row = 3, column = 0, pady = [0,20])
        self.button_stat_podpora.grid(row=3, column=1, pady = [0,20])
        self.button_din_podpora.grid(row=3, column=2, pady = [0,20])
        self.button_konzola.grid(row=3, column=3, pady = [0,20])


        self.label_xkoord.grid(row=5,column=1)
        self.label_kot.grid(row=5,column=2)
        self.label_velikost.grid(row=5,column=3)
        self.button_nova_sila.grid(row=5, column=4, rowspan=2)
        self.label_dodaj_silo.grid(row=5, rowspan=2, column = 0)
        self.entry_sila_x.grid(row=6, column=1, pady = [0,20])
        self.entry_sila_kot.grid(row=6, column=2, pady = [0,20])
        self.entry_sila_velikost.grid(row=6, column=3, pady = [0,20])
        self.button_izracun.grid(row=0, rowspan=3, column = 0)

        self.label_nos_x.grid(row=1, column=1)
        self.label_nos_x2.grid(row=1, column=2)
        self.label_določi_nosilec.grid(row = 1, rowspan = 2, column = 0)
        self.button_nosilec.grid(row=1,column=3, rowspan=2)
        self.entry_nosilec_x1.grid(row=2,column=1, pady = [0,20])
        self.entry_nosilec_x2.grid(row=2,column=2, pady = [0,20])

        self.button_kontinuerana_tocke.grid(row=9,column = 1)
        self.button_kontinuerana_naredi.grid(row=9,column = 3)

        self.label_kontpt_x = Label(frame_top, text="X-koordinata")
        self.label_kontpt_y = Label(frame_top, text="Velikost")
        self.label_kont_obrem = Label(frame_top, text="Kontunerana obremenitev:")
        self.entry_kontx = Entry(frame_top)
        self.entry_konty = Entry(frame_top)
        self.button_kont_dodaj = Button(frame_top, command=self.kont_kot_tocke, text="Kontinuerana po tockah")
        self.label_kont_obrem.grid(row = 7, rowspan = 2, column = 0)
        self.label_kontpt_x.grid(row=7, column=1)
        self.label_kontpt_y.grid(row=7, column=2)
        self.entry_kontx.grid(row=8, column=1)
        self.entry_konty.grid(row=8, column=2)
        self.button_kont_dodaj.grid(row = 8, column =3)

        self.label_max_moment = Label(self.frame_NTM, text="Maksimalen moment:")
        self.label_tocke_ekstremov = Label(self.frame_NTM, text="Tocke ekstremnov")
        self.label_reakcije = Label(self.frame_NTM, text="Reakcijeske sile:")

        self.button_poves = Button(self.frame_NTM, command = self.klicipoves, text="Izračun povesa ")




        self.button_poves.grid(row = 5,columnspan= 2, pady = [20,0])
        self.label_max_moment.grid(row=6,column=0, sticky=W, pady = [20,0])
        self.label_tocke_ekstremov.grid(row=7, column=0,sticky=W)
        self.label_reakcije.grid(row=8, column=0, sticky=W)
        """
        Spodaj sta definirana linija in poligon za statično ter dinamično podporo
        """
        #self.izris_podpore = self.canvas.create_polygon(0,0,0,0,0,0, fill="white")  #izrise bel trikotnik katerega lahko kasneje spreminjamo ko izrisujemo lokacijo podpore
        #self.izris_konzole = self.canvas.create_line(0,0,0,0, fill="white")  #isto kot izris podpore le da za statično konzolo
    def klicipoves(self):
        """
        Klice funkcijo za izracun povesa
        :return:
        """
        self.postavljen_nosilec.diferencialna()

    def kont_kot_tocke(self):
        """
        Omogoča dodajanje eksaktnih točk za kontinuerano obremenitev in ne s klikanjem
        :return:
        """
        x = float(self.entry_kontx.get())+1
        y = float(self.entry_konty.get())
        #Če nismo naredili še nobene točke za to kontinuerano obremenitev ponastavim/ustvarim tabeli
        if self.kontinuerana_narjena == 0:
            self.kontinuerana_ena = [] #Točke
            self.kontinuerana_narjena += 1 #koliko točk je v kontinuerani obremenitvi

        #Če je že kakšna točka narejena
        if self.kontinuerana_narjena < 6:
            self.kontinuerana_ena.append((x, y))
           #pripnem točko glede na lokacijo klika

            self.canvas.create_oval(x*10-2, -y-2+150, x*10+2,-y+2+150, fill="red") #izrišem točko #!!!!
            self.kontinuerana_narjena += 1

        #Ne pustim funkcije več kot petega reda
        else:
            print("prevec tock")

    def kontinuerana_naredi(self):
        """
        Iz tock,ki so zapisane kot lastnosti nosilca interpolira polinom. Ta polinom na danem območju tudi izriše
        :return:  Ponastavi self.kontinuerana_ena in self.kontinuerana_narjena
        """

        x_izris, y_izris = self.postavljen_nosilec.nova_kontinuerana(self.kontinuerana_ena)
        zipped = np.array([x_izris,-y_izris+150]).T #transponira (da dobimo (x,y)) DODAL
        #odg = np.round(zipped,-1)

        odg = np.ravel(np.round(zipped,0)) #izravna/razvije tabelo ter jo zaokroži
        _ = []
        for x in odg: #naredi preurejeno tabelo zipped, da lahko naredimo linijo
            x = int(x)
            _.append(x)
        self.canvas.create_line(_, smooth=True) #izriše polinom (verjetno izriše z zlepki)

        self.kontinuerana_ena = []
        self.kontinuerana_narjena = 0


    def kontinuerana_tocke(self):
        """
        Izriše ter naredi tabelo točk za kontinuerane obremenitve.
        :return:
        """
        #Če nismo naredili še nobene točke za to kontinuerano obremenitev ponastavim/ustvarim tabeli
        print(self.y)
        if self.kontinuerana_narjena == 0:
            self.kontinuerana_ena = [] #Točke
            self.kontinuerana_narjena += 1 #koliko točk je v kontinuerani obremenitvi

        #Če je že kakšna točka narejena
        if self.kontinuerana_narjena < 6:
            self.kontinuerana_ena.append((round(self.x/10,1), round(-self.y+main_height,1)))
           #pripnem točko glede na lokacijo klika

            self.canvas.create_oval(self.x-2, self.y-2, self.x+2,self.y+2, fill="red") #izrišem točko
            self.kontinuerana_narjena += 1

        #Ne pustim funkcije več kot petega reda
        else:
            print("prevec tock")


    def izracun(self):
        """
        Ob pritisku na gumb izračun se pokliče ta funkcija. Ta funkcija le pokliče dodatne funkcije
        , ki izračunajo T in M diagrame, reakcije, ...
        :return:
        """
        self.postavljen_nosilec.izracun_reakcij()
        self.postavljen_nosilec.izracun_T()
        self.postavljen_nosilec.izracun_M()
        self.postavljen_nosilec.izris_NTM()

        #Koda spodaj nam izpise kaksni so maksimalni momenti, kje so, ...
        if self.postavljen_nosilec.konzola:
            self.label_reakcije.config(text=f"Reakcije: Ax:{round(self.postavljen_nosilec.reakcije[0],2)},"
                                             f"   Ay:{round(self.postavljen_nosilec.reakcije[1], 2)},"
                                             f"   M:{round(self.postavljen_nosilec.reakcije[2],2)}")
        else:
            self.label_reakcije.config(text=f"Reakcije: Ax:{round(self.postavljen_nosilec.reakcije[0],2)},"
                                            f"   Ay:{round(self.postavljen_nosilec.reakcije[1],2)},"
                                            f"   By:{round(self.postavljen_nosilec.reakcije[2],2)}")
        self.label_tocke_ekstremov.config(text=f"Ekstremene tocke: "
                                               f"{np.round(self.postavljen_nosilec.m_max_x - 1, decimals=2)}")
        self.label_max_moment.config(text=f"Maksimalen moment: {round(self.postavljen_nosilec.m_max_y,2)}")


    def izvedi_nosilec(self):
        """
        Ko postavimo konzole ter definiramo nosilec se pokliče ta funkcija. Naredi objekt nosilca na katerega lahko
        potem dodajamo kontinuerane obremenitve ter sile.
        :return:
        """
        if self.lokacije_konzol[1] == 0:
            param_1 = (self.lokacije_konzol[0], False)
            param_2 = ((0,0), False)
        else:
            param_1 = (self.lokacije_konzol[0], True)
            param_2 = (self.lokacije_konzol[1], True)
        self.postavljen_nosilec = bg.Nosilec(zacetek=(self.lokacije_nosilca[0], 0), konec=(self.lokacije_nosilca[1], 0),
                                             stat_podpora=param_1, din_podpora=param_2)
        print(self.postavljen_nosilec.neznane)

    def dodaj_nosilec(self):
        """
        Izrise nosilec ter doda njegovo lokacijo kot self.lokacija nosilca
        :return:
        """
        x1 = int(self.entry_nosilec_x1.get())+1
        x2 = int(self.entry_nosilec_x2.get())+1
        self.lokacije_nosilca = [x1,x2]
        self.nosilec = self.canvas.create_line(x1*10, main_height, x2*10, main_height, fill="red")

    def nova_sila(self):
        """
        Postavljenemu nosilcu definera novo silo z parametri, ki jih prebere iz vhodnih polj
        Silo tudi izriše.
        :return:
        """
        x_koordinata = float(self.entry_sila_x.get())+1
        kot = float(self.entry_sila_kot.get())
        param_velikost = float(self.entry_sila_velikost.get())
        param_lokacija = (x_koordinata,0)
        param_kot = np.pi*kot/180
        self.canvas.create_line(x_koordinata*10, main_height, x_koordinata*10, main_height-param_velikost, arrow=FIRST)


        self.postavljen_nosilec.nova_sila(lokacija=param_lokacija, kot=param_kot, velikost=param_velikost)
        print(x_koordinata,kot, param_velikost)

    def motion(self, event):
        """
        Funkcija nastavi classu gui x in y vrednosti kurzoraja vendar le na območju kanvasa. Event = motion
        :param event:
        :return:
        """
        self.x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
        self.y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
        self.label_xy.config(text=f"{self.x/10},{round(-self.y/10+main_height/10,1)}")
        self.izris(self.vkljucena)
        #print(self.x,self.y)
    def prvi_izris(self):
        """
        Glede na to katera funkcija je vključena ustvari oziroma izbriše ustrezne objekte.
        To objekte lahko kasneje spreminjam z funkcijo izris. Če so objekti že ustavrjeni jih izbriše
        ter nato ustvari na novo. Sami objekti se tu še ne prikažejo na zaslonu ampak so le ustvarjeni.
        :return:
        """
        print("mogoce")
        if self.kreiran == 0:
            if self.vkljucena == 1 or self.vkljucena == 2:
                self.izris_podpore = self.canvas.create_polygon(0,10, 0, 5, 0, 2, fill="black")
                #print("neki")
            elif self.vkljucena == 3:
                self.izris_podpore = self.canvas.create_line(0, 0, 0, 0, fill="black")
            self.kreiran = 1
        else:
            self.canvas.delete(self.izris_podpore)
            if self.vkljucena == 1 or self.vkljucena == 2:
                self.izris_podpore = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="black")
                #print("neki")
            elif self.vkljucena == 3:
                self.izris_podpore = self.canvas.create_line(0, 0, 0, 0, fill="black")
            self.kreiran = 1

    def spremeni_funkcijo(self, vrsta_pod):
        """
        Funkcija spremeni izbrano funkcijo: stevilka izbrane funkcije zapisana v slovarju.
        :param vrsta_pod:
        :return: spremeni "vkljucena"
        """
        mozne_funkcije = {"stat":1, "din":2, "konzola":3, "kontinuerana_tocke":4}
        self.vkljucena = mozne_funkcije[vrsta_pod]

        if self.vkljucena == 1 or self.vkljucena==2 or self.vkljucena==3:
            self.prvi_izris()
            print("neki")


        print(self.vkljucena)


    def izris(self, vklj):
        """
        Na kanvas izrisuje kam želimo postaviti katerokoli od konzol. Odvisna od vključene funkcije
        :param vklj: Vstavimo vključeno fukncijo
        :return:
        """
        zaokrozena_x = round(self.x, -1)
        if vklj == 0:
            pass
        elif vklj == 3:
            linija = (zaokrozena_x, main_height-40, zaokrozena_x, main_height+40)
            self.canvas.coords(self.izris_podpore, linija)
            self.canvas.itemconfig(self.izris_podpore, fill="black")
            #self.canvas.itemconfig(self.izris_podpore, fill="white")
            #self.canvas.coords(self.izris_podpore, 0,0,0,0,0,0)

        elif vklj == 1 or vklj == 2:
            trikotnik = (zaokrozena_x-10, main_height+20, zaokrozena_x+10, main_height+20, zaokrozena_x, main_height)
            self.canvas.coords(self.izris_podpore, trikotnik)
            self.canvas.itemconfig(self.izris_podpore, fill=selected[self.vkljucena-1])

            #self.canvas.itemconfig(self.izris_konzole, fill="white")
            #self.canvas.coords(self.izris_konzole, 0,0,0,0)


    def postavi_podporo(self, event):
        """
        Ta funkcija ob izbrani vrsti konozle ob kliku na levi gumb miške postavi izbrano konzolo na to mesto oziroma
        prestavi že postavljeno,
        :param event:
        :return:
        """
        zaokrozena_x = round(self.x, -1)
        trikotnik = (
        zaokrozena_x - 10, main_height + 20, zaokrozena_x + 10, main_height + 20, zaokrozena_x, main_height)
        linija = (zaokrozena_x, main_height - 40, zaokrozena_x, main_height + 40)
        #Zgoraj so postavljene spremenljivke, da lahko izrišem trikotnik oziroma linijo za podporo


        """
        S spremenljivko self.postavljen preverjam ali je bila funkcija že zagnana ali se je to za program zgodilo prvic.
        Če se to še ni zgodilo moraj najprej ustvariti objekte za podpore.
        Glede na to kera funkcija je bila izbrana ko smo pritisnili ta objekt še postavim na pravo mesto.
        Na koncu spremenim parameter self.postavljen na 1 ker so vse instance objekta že ustvarjene.
        """
        if self.vkljucena == 4:
            self.kontinuerana_tocke()
            return

        if self.postavljen == 0:
            self.stat_podpora = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="red")
            self.din_podpora = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, fill="blue")
            self.konzola = self.canvas.create_line(0,0,0,0, fill="black")

            if self.vkljucena == 1:
                self.canvas.coords(self.stat_podpora, trikotnik)
            elif self.vkljucena == 2:
                self.canvas.coords(self.din_podpora, trikotnik)
            elif self.vkljucena == 3:
                self.canvas.coords(self.konzola, linija)

            self.postavljen = 1


        """
        Ta del funkcije se izvaja že so objekti že ustvarjeni. Najpre izbrišem objekt ter ga nato na novo narišem na
        na pravem mestu. 
        """
        if self.postavljen == 1:

            if self.vkljucena == 1:
                self.canvas.delete(self.stat_podpora)
                self.canvas.delete(self.konzola)
                self.stat_podpora = self.canvas.create_polygon(trikotnik, fill="red")

            elif self.vkljucena == 2:
                self.canvas.delete(self.din_podpora)
                self.canvas.delete(self.konzola)
                self.din_podpora = self.canvas.create_polygon(trikotnik, fill="blue")

            elif self.vkljucena == 3:
                self.canvas.delete(self.konzola)
                self.canvas.delete(self.din_podpora)
                self.canvas.delete(self.stat_podpora)
                self.konzola = self.canvas.create_line(linija, fill="black")


        """
        Ob kliku v tabelo lokacije_konzol dodam še x koordinato kamer sem kliknil. Na prvem mestu je stavična podpora na
        drugem dinamična. Če je podpora konzola je na prvem mestu lokacija konzole na drugem pa 0.
        """
        if self.vkljucena == 3:
            self.lokacije_konzol[0] = (zaokrozena_x/10, 0)
            self.lokacije_konzol[1] = 0
        elif self.vkljucena == 2:
            self.lokacije_konzol[1] = (zaokrozena_x/10, 0)
        elif self.vkljucena == 1:
            self.lokacije_konzol[0] = (zaokrozena_x/10, 0)


        print(self.lokacije_konzol)
        self.vkljucena = 0


# Tukaj zdaj ustvarim okno ter ga podam v class.
# Poženem tudi mainloop
root = Tk()
okno = Gui(root)
root.mainloop()

