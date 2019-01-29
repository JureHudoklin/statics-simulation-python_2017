import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import lagrange
import numericne_metode as nm
from scipy.integrate import odeint
from PIL import Image

class Nosilec(object):
    """
    Vhodni podatki: zacetna in koncna tocka nosilca(trenutno le linearno),
                    tip in lokacija prve in druge poodpore(druge ni, če je konzola) --> ((x,y), True) false ce konzola
    """

    def __init__(self, zacetek=(0, 0), konec=(0, 10), stat_podpora=((0, 0), True), din_podpora=((10, 0), True)):
        self.sile = []  # se zapisujejo vse sile, ki delujejo na nosilec v obliki [(lokacija), kot, velikost = (x,y)]
        self.neznane = []   #se shranijo reakcije v obliki: [[ime, lokacija], ...
        self.momenti = []   #se zapisujejo momenti kot float
        self.kontinuerane = []

        self.zacetek = zacetek
        self.konec = konec

        self.podpore(stat_podpora, din_podpora)

    def podpore(self, stat, din):
        """
        Določi ali imamo konzolo ali ne. Glede na to spremeni self.konzola na True ali False
        Spremenljivki self.neznane doda ime reakcije ter lokacije teh reakcij po x.
        :param stat: tuple z ((x,y), True/False)
        :param din: tuple z ((x,y), True/False)
        :return:
        """
        if stat[1]:  # ce imamo "normalno" konfiguracijo: 1x tockovna premicna + 1x tockovna nepremicna
            self.neznane = [["A_x", stat[0]], ["A_y", stat[0]], ["B_y", din[0]]]
            self.konzola = False

        elif stat[1] == False:  # ce imamo konzolo
            self.neznane = ["A_x", stat[0]], ["A_y", stat[0]], ["A_m", stat[0]]
            self.konzola = True

    def nova_kontinuerana(self, tocke):
        """
        S pomočjo lagrangevih polinomov čez vnesene točke definiramo interpolacijsko krivuljo.
        To krivuljo nato integriramo, da določimo velikost obremenitve.
        S pomočjo integrala nato izračunamo še težišče obremenitve (absolutno ne glede na začetek nosilca)
        :param tocke: Točke čez katere poteka kontinuerana obremenitev
        :return: Vrne x in y koordinate glede na canvas (uporabim za izris krivuje)
        """
        x_i = []
        y_i = []
        zacetek = tocke[0][0]
        konec = tocke[-1][0]
        x_inp = np.linspace(zacetek, konec, 20)

        for i in tocke:
            x_i.append(i[0])
            y_i.append(i[1])
        x_i = np.array(x_i)
        y_i = np.array(y_i)
        polinom = lagrange(x_i, y_i)  #S pomočjo scipy interpoliram čez točke lagrangevo interpolacijsko krivuljo
        x_t = nm.najdi_tezisce(polinom ,zacetek, konec) #Poiščem težišče funkcijske ploščine po x osi
        velikost = -nm.integral(polinom ,zacetek, konec) #poščem velikost obremenitve
        print(x_t, velikost, "x_tezisca", "velikostkontinuerane obremenitve")
        self.kontinuerane.append(((zacetek,konec), polinom, x_t, velikost)) #Pripnem astnosti za nadaljno uporabo

        return x_inp*10, polinom(x_inp) #Vrnem točke za izris

    def nova_sila(self, lokacija, kot, velikost):
        """
        Ko dodamo novo silo  na nosilec jo dolocimo z lokacijo = (x,y), kot = pozitiven za -x sile, velikost.
        Dobimo: seznamu sil se pripne seznam z vrednostmi (lokacija, kot ,(velikostx, velikosty))
        seznamo momentov se pripne moment, ki ga povzroča sila.
        :param lokacija: (x,y)
        :param kot: kot v stopinjah od x+ osi
        :param velikost: Velikost sile v N
        :return:
        """

        self.sile.append([lokacija, kot, (-np.cos(kot) * velikost, -np.sin(kot) * velikost)])

        razdalja = lokacija[0] - self.neznane[0][1][0]
        print(self.sile[0][2][1], "velikost sile v y")
        print(razdalja, "razdalja sile od prve podpore")
        moment = -np.sin(kot) * velikost * razdalja
        self.momenti.append(moment)

    def izracun_reakcij(self):
        """
        Na podlagi lastnosti nosilca ter sil, ki delujejo na nosilec izracuna reakcije v podporah.
        Ne potrebuje vhodnih parametriv oziroma gleda že predhodno določene lastnosti nosilca

        :return: (doda lastnosim nosilca) Vrne listo z Ax,Ay,By oziroma Ax,Ay,Am v primeru konzole
        """

        if self.konzola == False:
            razdalja2 = -self.neznane[0][1][0] + self.neznane[2][1][0]
            # self.neznane[2][1][0] je x koordinata
            # dinamicne podpore, self.neznane[0][1][0]
            # je x koordinata stat podpore. Razdalja2 je razdalja med podporami  -self.zacetek[0]
            matrika_koef = np.array([[1, 0, 0], [0, 1, 1], [0, 0, razdalja2]])
            # prva v x smeri, druga v y smeri, tretja momenti: Ax Ay By

            vsota_x = 0
            vsota_y = 0
            vsota_m = 0
            for x in self.sile:              #izracun vrednosti za dolocitev matrike koeficientov. Sešteje vse sile
                vsota_x = vsota_x + x[2][0]  #ter posledične momente, ki jih povzročajo naše vnesene sile.
                vsota_y = vsota_y + x[2][1]

            for x in self.kontinuerane:      #prišteje še prispevke, ki jih povzročijo kontinuerane obremenitve
                vsota_y += x[-1]
                vsota_m += (x[-2]-self.neznane[0][1][0]) * x[-1]

            for x in self.momenti:           #Zračuna vsoto momentov, ki jih povzročajo sile oziroma kont.obremenitve
                vsota_m = vsota_m + x

            matrika_vrednosti = np.array([-vsota_x, -vsota_y, -vsota_m])
            rezultat = np.linalg.solve(matrika_koef, matrika_vrednosti)  # resi sistem linearnih enacb
            self.reakcije = rezultat


        else:
            #Stori isto kot če ni konzola dugačna je le matrika koeficientov
            matrika_koef = np.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])   #Ax,Ay,M

            vsota_x = 0
            vsota_y = 0
            vsota_m = 0
            for x in self.sile:   # izracun vrednosti za dolocitev matrike koeficientov
                vsota_x = vsota_x + x[2][0]
                vsota_y = vsota_y + x[2][1]
            for x in self.kontinuerane:
                vsota_y += x[-1]
                vsota_m += (x[-2]-self.neznane[0][1][0])*x[-1]

            for x in self.momenti:
                vsota_m = vsota_m + x
            matrika_vrednosti = np.array([-vsota_x, -vsota_y, -vsota_m])
            rezultat = np.linalg.solve(matrika_koef, matrika_vrednosti)

            self.reakcije = rezultat
        print(self.reakcije, "reakcijske sile v konzoli")
    def izracun_T(self):
        """
        Izračuna T digram ter ga prirdi tako, da je izris pravi.
        :return:
        """

        #To je table z prispevki sil v posazenimi točkah (tudi z prispevki delov kontinueranih sil
        t_tabela = [(self.zacetek[0],0), (self.konec[0], 0)]



        for element in self.sile: #dodamo vse sile
            t_tabela.append((element[0][0], element[-1][1]))
        for element in self.kontinuerane: #izračunam prispevek kontinuerane obremenitve ter dodam vse majhne prispevke
            #print(element[1], element[0][0], element[0][1])
            neki = nm.intergral_tabel(element[1], element[0][0], element[0][1])
            #print(neki)
            t_tabela.extend(neki)

        if self.konzola == True: #Dodam še reakcije
            a_y = self.reakcije[1]
            x_a = self.neznane[0][1][0]
            t_tabela.append((x_a, a_y))

        else:
            x_b = self.neznane[2][1][0]
            x_a = self.neznane[0][1][0]
            a_y = self.reakcije[1]
            b_y = self.reakcije[2]
            t_tabela.extend([(x_a,a_y),(x_b, b_y)])
        t_tabela.sort(key = lambda x: x[0]) #sortiram tabelo glede na lokacijo x posameznega prispevka

        vsota = 0
        delovna = np.array(t_tabela)
        #print(delovna)
        y_t = []
        x_t = []
        #x_t = np.copy(delovna[:,0])
        x1 = self.zacetek[0]
        for element in delovna: #Funkcija skrbi za dodajanje točk kjer imamo še dodatne sile
            x2 = element[0]
            if x2-x1 >= 0.1:
                x_t.append(x2)
                x_t.append(x2)
                y_t.append(vsota)
                vsota += element[1]
                y_t.append(vsota)
            else:
                x_t.append(x2)
                vsota += element[1]
                y_t.append(vsota)
            x1 = x2

        #To so je končan diagram, ki ga izračunam
        x_t = np.array(x_t)
        y_t = -np.array(y_t)
        self.t_diag_x = x_t
        self.t_diag_y = y_t


    def izracun_M(self):
        """
        Funkcija iz T diagrama s pomočjo integracije izračuna M diagram
        :return:
        """
        if self.konzola:
            x = np.array([self.neznane[0][1][0]])
            y = np.array([self.reakcije[2]])
            m_x, m_y = nm.integral_tabelaricno(self.t_diag_x, self.t_diag_y) #integriram T diagram
            _ = np.nonzero(self.t_diag_x)
            _ = _[0][0]
            x = np.append(m_x, x) #Točkam pripnem še začetno in končno točko, da dobim pravilen izris
            y = np.append(m_y, y)
            if len(self.kontinuerane) > 0:
                x = np.insert(x, 0, self.t_diag_x[_])
                y = np.insert(y, 0, 0)
            xy = np.array([x,y])
            xy_sortirana = xy[:, np.argsort(xy[0, :], kind = "mergesort")]
            """tabelo sortiram glede na x. Mergesort je zato, da x z istimi vrednostmi ostanejo v istem vrstnem redu"""


            self.m_diag_x = xy_sortirana[0,:]
            self.m_diag_y = np.cumsum(xy_sortirana[1,:]) #Prištevke posameznih delov zdaj zaporedno seštejem


        else:
            #Podobno kot zgoraj vendar mi je treba manj skrbeti glede dodajanja točk
            _ = np.nonzero(self.t_diag_x)
            _ = _[0][0]
            m_x, m_y = nm.integral_tabelaricno(self.t_diag_x, self.t_diag_y)
            self.m_diag_y = np.cumsum(m_y)
            self.m_diag_x = m_x
            self.m_diag_y = np.insert(self.m_diag_y, 0, 0)
            self.m_diag_x = np.insert(self.m_diag_x, 0, self.t_diag_x[_])

        """
        Koda spodaj s pomocjo funkcije najdi nicle poisce x-e v katerih moment doseze maksimalne vrednosti
        Kaksna pa je maksimalna vrednost momenta pa preberemo kar iz tabele self.m_diag_y.
        """

        max_x = nm.najdi_nicle(self.t_diag_x, self.t_diag_y)
        self.m_max_x = max_x
        self.m_max_y = np.max(np.absolute(self.m_diag_y))
        print(self.m_max_y, self.m_max_x,"maksimumi momentov")

    def izris_NTM(self):
        """
        S pomočjo matplotlib izriše T in M diagram ter ga oblikuje. Grafa shrani v datoteko kjer je program
        :return:
        """

        fig = plt.figure(1)
        ax1 = fig.add_subplot(211)
        ax2 = fig.add_subplot(212)
        ax1.set_xlim(self.zacetek[0]-1, self.konec[0]-1)
        ax2.set_xlim(self.zacetek[0]-1, self.konec[0]-1)

        ax1.plot(self.t_diag_x-1, self.t_diag_y, label = "T(x)")
        ax2.plot(self.m_diag_x-1, self.m_diag_y, label = "M(x)")
        ax1.axhline(0, color = "red")
        ax2.axhline(0, color="red")
        for i in self.m_max_x-1:
            ax2.axvline(i, color="red", ymin=-1, ymax=1)

        ax1.set_title("T-diagram")
        ax2.set_title("M-diagram")

        ax1.set_xlabel("x [m]")
        ax1.set_ylabel("T[mm]")

        ax2.set_xlabel("x [m]")
        ax2.set_ylabel("M[Nm]")

        ax1.legend()
        ax2.legend()

        plt.tight_layout()
        plt.savefig("NTM_diagrami")
        plt.show(1)

    def diferencialna(self):
        """
        Izračuna diferencialno enačbo. Na podlagi izračuna nato nariše diagram povesa. Rešuje s pomočjo odeint.
        :return:
        """

        #Kluc funkcij za interpolacijo ter za izračun diferencialne enačbe
        funkcija, x = nm.aproksimacija(self.m_diag_x, self.m_diag_y) #to je interpolacija le ime fn je aproksimacija
        poves = nm.izracun_dif(x, funkcija, self.konzola) #izračuna krivuljo povesa nosilca

        #Izris povesa nosilca ter interpolacije momenta
        fig2 = plt.figure(2)
        ax1 = fig2.add_subplot(211)
        ax2 = fig2.add_subplot(212)
        ax1.plot(x-1, -poves[:,0]*10**3-1, label="poves nosilca v mm/m")
        ax2.plot(x-1, funkcija(x)-1, label="Interpoleran moment z zlepkom")
        ax1.set_title("Diagram povesa")
        ax2.set_title("Mdiagram (interpoleran)")

        ax1.axhline(0, color = "red")
        ax2.axhline(0, color="red")
        ax1.axvline(x[0]-1,color="red")
        ax2.axvline(x[0]-1, color="red")

        ax1.set_xlabel("x [m]")
        ax1.set_ylabel("poves [mm]")

        ax2.set_xlabel("x [m]")
        ax2.set_ylabel("moment[Nm]")

        ax1.legend()
        ax2.legend()
        plt.tight_layout()
        plt.savefig("Poves")
        plt.show()
