import numpy as np
import scipy
import matplotlib.pyplot as plt
from scipy.interpolate import *
from scipy.integrate import *
from numpy.polynomial.polynomial import *
from scipy.optimize import curve_fit, root

def najdi_nicle(x, y):
    """
    Funkcija nam posice ničle za tabelarično podane vrednosti.
    Ničle se iščejo po inkementani metidu. Pogledamo kje funkcija spremeni predznak.
    :param x: x vredosti funkcije
    :param y: y vrednosti funkcije
    :return: Vrednosti x kjer y doseže ekstrem.
    """
    #y = y-0.000001

    znak_x = np.sign(y)
    sprememba_znaka = ((np.roll(znak_x, 1) - znak_x) != 0).astype(int)
    sprememba_znaka[0] = 0
    i_sprememba = np.nonzero(sprememba_znaka)
    b = x[i_sprememba]
    return b

def lagrangev_interpolacijski_polinom(x_i, y_i, x_inp):
    """
    S pomočjo lagrangeve metode interpolira funkcijo stopnje n-1 skozi točke.
    :param x_i: x koxrdinate intepolacijskih tock
    :param y_i: y koordinate interpolacijskih tock
    :param x_inp: tocke katere intepoliramo
    :return: vrne vrednosti y_inp
    """
    if np.max(x_inp) > np.max(x_i) or np.min(x_inp) < np.min(x_i):
        raise Exception("X out of range!!!")

    else:
        y_inp = np.zeros(len(x_inp))  # naredimo prazen seznam enake velikosti kot x_inp --> ta seznam vrnemo
        for i in range(len(x_i)):
            Lp = 1
            for j in range(len(x_i)):  # v tej for zanki racunamo lagrangev polinom za vsak i posebej
                if j != i:
                    Lp *= (x_inp - x_i[j]) / (x_i[i] - x_i[j])
            y_inp += y_i[i] * Lp  # vsota vseh lagrangevih polinomov
        return y_inp  # vrne vrednosti y_inp (tock, ki smo jih interpolirali)

def integral(polinom, zac, konec):
    """
    Izračuna integral po trapezni metodi. Vrne površino polinoma med mejama a in b.
    :param polinom: funkcija
    :param zac: zacetek integralnega obmocja
    :param konec: Konec integralnega obmocja
    :return:
    """
    korak = 1000
    povrsina = 0
    napaka = 1
    stevilo_ciklov = 0
    cikel = [0,0]


    while napaka > 0.01:
         #integriranje izvajamo dokler ne bo napaka manjša od 0.01
        if stevilo_ciklov > 4:
            #print("Natancnost ni dosezena")
            break
        cikel[0] = povrsina
        #integriramo funkcijo po trapeznem pravilu pri dveh različnih korakih
        d_x = (konec - zac) / korak
        x_g = np.linspace(zac, konec, korak)
        f_x = polinom(x_g)
        delta = f_x[1:] - f_x[0:-1]
        f_x2 = f_x[0:-1] + delta / 2
        povrsina = sum(d_x * f_x2)
        cikel[1] = povrsina
        napaka = (abs(cikel[1] - cikel[0])) / 3

        korak = korak * 2
        stevilo_ciklov += 1
    richardson = (4/3)*cikel[0]-(1/3)*cikel[1] #boljš približek. Na koncu rezultat izboljšamo z Richardsonovo ekstrapolacijo.
    return richardson

def intergral_tabel(polinom,zac,konec):

    """
    Izračuna integral in nam vrne tabelo prispevkov posameznih segmentov integriranja.
    :param polinom: FUnkcija
    :param zac: a
    :param konec: b
    :return: [(x, prispevek_y), ...]
    """
    korak = 1000
    povrsina = 0
    napaka = 1
    stevilo_ciklov = 0
    cikel = [0,0]


    while napaka > 0.1:
        #Enaka funkija kot zgoraj le da vrnemo posamezne segmente in ne njihov seštevek.
        if stevilo_ciklov > 3:
            #print("natancnost ni dosezena")
            break
        cikel[0] = povrsina

        d_x = (konec - zac) / korak
        x_g = np.linspace(zac, konec, korak)
        f_x = polinom(x_g)
        delta = f_x[1:] - f_x[0:-1]
        f_x2 = f_x[0:-1] + delta / 2
        y_g = d_x*f_x2
        povrsina = sum(d_x * f_x2)
        cikel[1]= povrsina
        napaka = (abs(cikel[1] - cikel[0])) / 3
        stevilo_ciklov += 1
        korak = korak * 2
    vrni = []

    d = np.stack((x_g[0:-1], -y_g), axis = 1)
    vrni = list(map(tuple, d))
    return vrni


def integral_tabelaricno(x, f_x):
    """
    Vzma tabelarično podano vunkcijo ter nam vrne tabelo vseh neničelnih ploščin integrala
    :param x: x točke
    :param f_x: funkcijske točke
    :return: Tabela vrednosti posameznih prispevkov tabelarično podane funkcije
    """
    d_x = x[1:]-x[:-1]
    f_x2 = (f_x[0:-1]+f_x[1:])/2
    tabela_vrednosti = d_x * f_x2

    indeksi_0 = np.nonzero(tabela_vrednosti==0) #izbrišemo vse ničelne prispevke (olajša obdelavo pri drugih fn.
    tabela_vrednosti = np.delete(tabela_vrednosti, indeksi_0)

    x_m = np.copy(x[1:])
    x_m = np.delete(x_m, indeksi_0)
    return x_m,tabela_vrednosti

def najdi_tezisce(polinom ,zac, konec):
    """
    S pomočjo integriranja vhodne funkcije poišče težišče po x med vrednostima a in b.
    :param polinom: Funkcija
    :param zac: a
    :param konec: b
    :return: Koordinata težišča
    """

    korak = 1000
    napaka = 1
    stevilo_ciklov = 0
    povrsina = 0
    cikel = [0,0]


    while napaka > 0.1:
        if stevilo_ciklov > 5:
            #print("natancost ni dosezena2")
            break
        cikel[0] = povrsina


        d_x = (konec - zac) / korak
        x_g = np.linspace(zac, konec, korak)
        f_x = polinom(x_g)
        delta = f_x[1:] - f_x[0:-1]
        f_x2 = f_x[0:-1] + delta / 2
        povrsina = sum(d_x * f_x2 * (x_g[0:-1] + x_g[1:]) / 2) #podobno kot prejšne fn. le da še množimo z x
        cikel[1] = povrsina                                 # posamezen seagment
        napaka = (abs(cikel[1] - cikel[0])) / 3
        korak = korak * 2
        stevilo_ciklov += 1

    moment = cikel[1]
    povrsina = integral(polinom, zac, konec)
    tezisce = moment / povrsina
    return tezisce



def euler_sistem(f, t,moment, y0, *args, **kwargs):
    """
    Eulerjeva metoda za reševanje sistema navadnih diferencialnih enačb prvega reda : y' = f(t, y)

    :param f:  funkcija, ki jo kličemo s parametroma t in y in vrne seznam
               funkcij desnih strani
    :param t:  ekvidistantni (časovni) vektor neodvisne spremenljivke
    :param y0: seznam začetnih vrednosti
    :param args: dodatni argumenti funkcije f (brezimenski)
    :param kwargs: dodatni argumenti funkcije f (poimenovani)
    :return y: vrne np.array ``y`` funkcijskih vrednosti.
    """
    y = np.zeros((t.shape[0], len(y0)))
    y[0] = np.copy(y0)
    h = t[1] - t[0]
    indeks = 0
    for i, ti in enumerate(t[:-1]):
        # tukaj je bistvo Eulerjeve metode
        y[i + 1] = y[i] + f(ti, y[i],moment, indeks, *args, **kwargs) * h
        indeks += 1
    return y

def aproksimacija(x,my):
    """
    Interpolacija funkcije skozi dane z zlepkom.
    :param x: x vrednosti
    :param my: y vrednosti
    :return: Interpoleran zlepek
    """

    if x[0]==x[1]:
        vektor = np.linspace(x[1], x[-1], 1000)
        return InterpolatedUnivariateSpline(x[1:],my[1:]), x
    else:
        vektor = np.linspace(x[0], x[-1], 1000)
        return InterpolatedUnivariateSpline(x[:],my[:]), vektor

def izracun_dif(t, funkcija, konzola):
    """
    Numerično reševanje diferencialne enačbe z odeint.
    :param t: Časovne točke (x točke)
    :param funkcija: funkcija momenta po nosilcu
    :return: moment in njegov prvi odvod (rezultat odeint)
    """
    if konzola == True: #rešujem začetni problem
        neki = odeint(dif_konzola, y0=[0, 0], t=t, args=(funkcija, 210*10**9, 171*10**-8))
        return neki
    else: #S strelsko metodo rešujem robni problem
        rešitev = root(r, 1, args=(0, t, funkcija))
        return odeint(dif_konzola, y0=[0, rešitev.x], t=t, args=(funkcija, 210*10**9, 171*10**-8))

def r(v0=1, ciljna_lega=0., t=None, funkcija=None, E=210*10**9, I= 171*10**-8):
    """
    Funkcija mejnega preostanka
    :param v0: Odvod v točko nič (predpostavka)
    :param ciljna_lega: Kakšen y želimo v zadnji točki
    :param t: Časovni vektor
    :param funkcija: Funkcija momenta po nosilcu
    :param E: Elastični modul jekla
    :param I: Vztrajnostni prerez nosilca (privzeto je za I nosilec)
    :return:
    """
    y_ode = odeint(dif_konzola, y0=np.array([0., v0]), t=t, args=(funkcija,E,I))
    r = y_ode[-1,0] - ciljna_lega
    return r

def dif_konzola(y,t,funkcija, E,I):
    """
    Diferencialna enačba za poves
    :param y: y
    :param t: x
    :param funkcija: funkcija momenta po nosilcu
    :param E: Elastični modul
    :param I: Vztrajnostni moment prereza nosilca
    :return: prvi odvoda sistema diferencialnih enačb 2. reda
    """
    z0, z1 = y
    return [z1,funkcija(t)/(E*I)]

