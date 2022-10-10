import numpy as np
import matplotlib.pyplot as plt

def txt_to_spectr(name_of_file: str):
  """Function for converting data from txt format to array of measures that representing spectr
  """
  f = open(name_of_file,'r')
  i = -1
  A = []
  new_word = True
  while True:
    x = f.read(1)
    if i==4096*2-1:
      break
    if x!=' ' and x!='\n':
      if new_word:
        i+=1
        A.append(x)
        new_word = False
      else:
       A[i]+=x
    else:
      new_word = True     
  N=[]
  n=[]
  k=0
  for x in A:
    if k%2==0:
      N.append(int(x))
      isN = False
    else:
      n.append(int(x))
    k+=1
  return n

def Draw_spec(n: list, step=200, xlab="$N_i$ (Номер канала)", ylab = "$n$ (Число зарегистрированных импульсов)", start = 0, stop = 4096):
    """Functuion that draw spectr from array
        User can specify (if there's such need) limits of chanels, xlabel and ylabel 
    """
    fig1,ax1 = plt.subplots()
    n1 = []
    N1 = []
    for i in range(start,stop):
        N1.append(i)
        n1.append(n[i])
    ax1.plot(N1, n1)
    xx1 = np.arange(start, stop, step)
    ax1.set_xlabel(xlab)
    ax1.set_ylabel(ylab)
    plt.show()

def Aver_A(n: list, start: int, end: int, doPrint = True):
    """Function for counting average value of amplitude from certain part of spectrum
     Returns average amplitude and its standart deviation
     Also user can chose to print or not to print the results (print by default)
    """

    N_1 = 0
    n_1 = 0
    for i in range(start,end):
        N_1+=i*n[i]
        n_1+=n[i]
    else:
        N_1=float(N_1)/float(n_1)
    N2_1  = 0
    for i in range(start,end):
        N2_1+=i*i*n[i]
    N2_1 = float(N2_1)/float(n_1)#средний квадрат значения 
    D_1 = N2_1-N_1*N_1 #dispersion
    d_1 = np.sqrt(D_1)#standart deviation
    if doPrint:
        print(N_1,"+-",d_1)
    return N_1, d_1

def MNK(x, y):
    """метод наименьших квадратов
    """
    size = len(x)
  # выполним расчет числителя первого элемента вектора   
    numerator_w1 = size*sum(x[i]*y[i] for i in range(0,size)) - sum(x)*sum(y)
    # выполним расчет знаменателя (одинаковый для обоих элементов вектора)
    denominator = size*sum((x[i])**2 for i in range(0,size)) - (sum(x))**2
    # выполним расчет числителя второго элемента вектора
    numerator_w0 = -sum(x)*sum(x[i]*y[i] for i in range(0,size)) + sum((x[i])**2 for i in range(0,size))*sum(y)
    
    # расчет искомых коэффициентов
    w1 = numerator_w1/denominator
    w0 = numerator_w0/denominator
    return w0, w1

def Lin_of_peaks(n: list, starts: list, stops: list, Energy: list ):
    """Function for linearisation of peaks and finding tgAlfa
    """
    N=[]
    N1 = []
    for i in range(len(stops)):
        Av, dev = Aver_A(n,starts[i], stops[i], False)
        N.append(Av)
        N1.append(dev)
  
    w0,w1 = MNK(N,Energy)

    E_predict=[w0+w1*x for x in N]
    plt.figure(figsize=(15,9))
  #ax3 = fig1.add_subplot()
    plt.plot(N, E_predict,label="Проведённая прямая")

    plt.errorbar(N, Energy, xerr=N1,label = "Экспериментально расчитанные значения",linestyle=" ",marker = 'o')
  #ax1.set_xticks(xx1)
    plt.legend()
    plt.show()
    return w1

def Delta_N(nmax,N:list,left_bound, right_bound):
    """Function for counting the width in channels oo the half of maximum"""
    delta = 2000
    N_left = 0
    for i in range(left_bound, (right_bound-left_bound)//2+left_bound):
    #print (abs(Nmax//2-N[i]))
        if delta>abs(nmax//2-i):
            delta=float(nmax)/2-i
            N_left=i
    delta=0
  #print("left ",N_left)
    N_right=0
    for i in range((right_bound-left_bound)//2+left_bound,right_bound):
        if delta<(nmax//2-i):
            delta=nmax//2-i
            N_right=i
  
    return N_right-N_left

def Delta_E(Delta_N, alfa):
    return Delta_N*alfa

def Final_spectr_analysis(name_of_file):
    n = txt_to_spectr(name_of_file)
    Draw_spec(n)
    print("Введите границы для более близкого рассмотрения спектра")
    left = int(input("Левая граница >>"))
    right = int(input ("Правая граница >>"))
    Draw_spec(n, start = left, stop = right)
    print("По данным изображениям определите границы пиков \nВведите информацию о пиках: границы и соответвующие им энергии \nДля завершение ввода значений пиков введите 'e'")
    i = 1
    left =[]
    right =[]
    Energy = []
    #далее можно поставить больше проверок и assert-ов
    while True:
        print("Пик № ",i)
        x = input ("Энергия >>")
        if x=="e":
            break
        Energy.append(float(x))
        x = input("Левая граница >>")
        if x=="e":
            break
        left.append(int(x))
        x = input ("Правая граница >>")
        if x=="e":
            break
        right.append(int(x))
        i+=1
    
    alfa = Lin_of_peaks(n, left, right, Energy)
    print("Получили следующее значение для альфа: ",alfa)
    print("Энергетическое разрешение:")
    DeltaN = []
    DeltaE = []
    for i in range(len(right)):
        n_max = max([n[i] for i in range(left[i],right[i])])
        DeltaN.append (Delta_N(n_max,n,left[i], right[i]))
        DeltaE.append(DeltaN[i]*alfa)
        print ("Для ",i+1,"-го пика равно ",DeltaE[i]," (ширина в количестве каналов - ",DeltaN[i],")")
        
Final_spectr_analysis("1_Spektr55(2).txt")    






    
  
