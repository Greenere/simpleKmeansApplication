import math
import random
import threading
import tkinter
import os
from tkinter import ttk
from tkinter import messagebox
from matplotlib.pyplot import figure, plot, scatter, legend, show
from numpy import asarray

#读取待聚类的数据
def readSamples(path='fkmeansData.txt',dsp=',',ssp='\r\n'):
    samples=[]
    sampledict={}
    with open(path,'rb') as f:
        data=f.read()
        data=data.decode('utf-8')
    smps=data.split(ssp)
    i=0
    for smp in smps:
        samples.append(smp.split(dsp))
        sampledict[i]=smp.split(dsp)
        i+=1

    #格式检查
    smpdim=len(samples[0])
    for sample in samples:
        if smpdim!=len(sample):
            raise ImportError
    return samples,sampledict

#求两个数据点之间的距离
def distance(sma,smb,dimension,dstmode='euclidean'):
    dst=0
    #euclidean距离是几何距离，即日常认知的距离
    if dstmode=='euclidean':
        for i in range(dimension):
            dst += (float(sma[i]) - float(smb[i])) ** 2
        dst = math.sqrt(dst)
    #棋盘距离是规定只能横走或者竖走后的距离
    elif dstmode=='chessdst':
        for i in range(dimension):
            dst += math.fabs(float(sma[i]) - float(smb[i]))
    return dst

#根据簇内样本更新中心点
def meanCenter(samples,dimension,cmode='mean'):
    sumsmp=[]
    for i in range(dimension):
        sumsmp.append(0.)
    #求中心点
    if cmode=='mean':
        for i in range(dimension):
            for smp in samples:
                sumsmp[i] += float(smp[i])
        for i in range(dimension):
            sumsmp[i] /= (len(samples) + 1e-5)
    return sumsmp

#K-均值聚类
def kmeansCluster(samples,dimension,k,epochs=10,dsmode='euclidean'):
    num=len(samples)
    center={}#保存中心点
    cluserDict={}#保存聚类结果（标签）
    sampleClus={}#保存聚类结果（数据点）
    for i in range(k):
        #随机选择初始簇中心
        center[i]=samples[random.randint(0,num-1)]
        cluserDict[i]=[]
        sampleClus[i]=[]

    for epoch in range(epochs):
        cluserDict = {}
        sampleClus = {}
        for i in range(k):
            cluserDict[i] = []
            sampleClus[i] = []
        for j in range(num):
            #将数据归类给距离最近的簇
            clus = 0
            dst = distance(samples[j], samples[clus],dimension)
            for i in range(k):
                ndst = distance(samples[j], center[i],dimension,dstmode=dsmode)
                if ndst < dst:
                    clus = i
                    dst = ndst
            sampleClus[clus].append(samples[j])
            cluserDict[clus].append(j)
        #更新簇中心
        for i in range(k):
            center[i]=meanCenter(sampleClus[i],dimension)
    return sampleClus,cluserDict,center

#绘制聚类结果
def viewCluster(sampleClus,center,k,dim1=0,dim2=1):

    #随机颜色生成，用于给簇涂色
    def randomcolor():
        colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
        color = ""
        for i in range(6):
            color += colorArr[random.randint(0, len(colorArr)-1)]
        return "#" + color

    emptyClus={}
    cls=[]
    for i in range(k):
        if sampleClus[i]== []:
            emptyClus[i]=1
            continue
        emptyClus[i]=0
        #由于原始数据是字符串，因此需要转成float
        for m in range(len(sampleClus[i])):
            for n in range(len(sampleClus[i][m])):
                sampleClus[i][m][n]=float(sampleClus[i][m][n])
        cls.append(asarray(sampleClus[i]))

    figure()
    clist=[]
    for i in range(min([k,len(cls)])):
        clist.append(randomcolor())
    for i in range(min([k,len(cls)])):
        if emptyClus[i]==1:
            continue
        scatter(cls[i][:,dim1],cls[i][:,dim2],label='C'+str(i),c=clist[i])
        scatter(center[i][dim1],center[i][dim2],marker='*',c=clist[i])
        for j in range(len(cls[i][:,dim1])):
            plot([center[i][dim1],cls[i][j,dim1]],[center[i][dim2],cls[i][j,dim2]],c=clist[i],alpha=0.4)
    legend()
    show()

#图形界面
def interfaceGUI():
    #全局信息
    samples=[]#样本列表
    sampledict={}#样本字典
    dimension=1#样本维数
    clusternum=0#簇数目
    epocs=1#迭代轮数
    dsmode='euclidean'#距离度量
    sampleClus={}#聚类信息字典
    clusterDict={}#聚类标号字典
    center=[]#聚类簇中心
    viewthread=None#可视化线程
    clusthread=None#聚类线程
    #窗口组件颜色
    wbg='#EAEAEA'
    bbg='#EaE0e0'
    tbg='#E0EEEf'
    ebg='#E0EEEa'

    #主窗口
    win = tkinter.Tk()
    win.title("K-Means聚类分析-李皓阳-U201615712")
    win.geometry("770x370+200+50")
    win.resizable(0,0)
    win.config(bg=wbg,borderwidth=0)

    wfont=('黑体',10)#字体

    path=tkinter.Variable()
    path.set(os.getcwd()+'\\fkmeansData.txt')
    pathlabel=tkinter.Label(win,text='数据路径:',font=wfont,bg=wbg)
    pathentry=tkinter.Entry(win,width=50,textvariable=path,
                            font=wfont,bg=ebg,relief='solid')
    pathlabel.pack()
    pathentry.pack()
    pathlabel.place(x=10,y=10)
    pathentry.place(x=12,y=40)

    #导入示例数据
    def exmp():
        nonlocal samples,sampledict,dimension
        try:
            samples,sampledict=readSamples(path='fkmeansData.txt')
        except:
            messagebox.showerror(title='示例数据',message='示例数据<fkmeansData.txt>导入失败')
            return
        dimension=len(samples[0])
        data = datahead + str(sampledict).replace('],', '],\n')
        datatext.delete(0.0, tkinter.END)
        datatext.insert(index=tkinter.INSERT, chars=data)
    exmpbutton = tkinter.Button(win, text="示例数据", command=exmp,
                            width=10,height=1,font=wfont,
                            bg=bbg,activebackground=wbg,
                            borderwidth=1,relief='solid')
    exmpbutton.pack()
    exmpbutton.place(x=220,y=10)

    #导入数据
    def importdata():
        dtpath=path.get()
        if not os.path.exists(dtpath):
            messagebox.showerror(title='导入数据',message='文件不存在')
            return
        nonlocal samples,sampledict,dimension
        try:
            samples,sampledict=readSamples(path=dtpath)
        except:
            messagebox.showerror(title='导入数据',message='数据导入失败,请检查数据格式')
            return
        dimension=len(samples[0])
        #只显示数据字典转成字符后的前10000个字符
        sampledictstr=str(sampledict).replace('],','],\n')
        if len(sampledictstr)<10000:
            data=datahead+sampledictstr
        else:
            data=datahead+sampledictstr[:10000]
        datatext.delete(0.0,tkinter.END)
        datatext.insert(index=tkinter.INSERT,chars=data)
    imbutton = tkinter.Button(win, text="导入", command=importdata,
                            width=8, height=1, font=wfont,
                            bg=bbg, activebackground=wbg,
                            borderwidth=1,relief='solid')
    imbutton.pack()
    imbutton.place(x=300,y=10)

    #数据显示框
    datahead='-数据文件格式-\n导入的数据属性以“,”分隔\n每行一个元组,即元组之间以\\r\\n分隔\n\n-聚类数据-\n' \
             '<标号:[属性0,属性1,...]>\n'
    data=datahead
    datatext=tkinter.Text(win,
                          width=50,height=20,
                          font=wfont,bg=tbg,
                          borderwidth=2,relief='solid')
    datatext.insert(tkinter.INSERT,data)
    datatext.pack()
    datatext.place(x=12,y=70)

    #迭代次数选择
    epochs=tkinter.Variable()
    eplabel=tkinter.Label(win,text='迭代次数:',font=wfont,bg=wbg)
    epentry=tkinter.Entry(win,
                          width=5,borderwidth=0,
                          fon=wfont,textvariable=epochs,
                          takefocus=False,bg=wbg)
    eplabel.pack()
    epentry.pack()
    epentry.place(x=480,y=12)
    eplabel.place(x=400,y=10)
    def getepochs(*args):
        eps=epscale.get()
        epochs.set(eps)
        nonlocal epocs
        epocs=int(eps)
    epscale = tkinter.Scale(win,
                           from_=1, to=1000,
                           orient=tkinter.HORIZONTAL,
                           tickinterval=False, length=180,
                           showvalue=False,command=getepochs,
                           fg=wbg,troughcolor=bbg,relief='solid',
                           sliderrelief='solid',borderwidth=0)
    epscale.pack()
    epscale.place(x=400,y=38)
    epscale.set(1)
    epochs.set(epscale.get())

    #距离度量模式选择
    dstdict={"几何距离":'euclidean', "棋盘距离":'chessdst'}
    dstlabel = tkinter.Label(win, text='距离度量:', font=wfont,bg=wbg)
    dstlabel.pack()
    dstlabel.place(x=600,y=10)
    dstmode = tkinter.StringVar()
    dstmodecom = ttk.Combobox(win,
                              width=18,
                              textvariable=dstmode,
                              background=tbg,takefocus=False)
    dstmodecom.pack()
    dstmodecom.place(x=605,y=38)
    dstmodecom["value"] = ("几何距离", "棋盘距离")
    dstmodecom.current(0)
    def func(event):
        nonlocal dsmode
        dsmode=dstdict[dstmode.get()]
    dstmodecom.bind("<<ComboboxSelected>>", func)

    #聚类结果显示框
    clushead='-聚类分析-\n'
    clus=clushead
    clustext=tkinter.Text(win,
                          width=50,height=20,
                          font=wfont,bg=tbg,
                          borderwidth=2,relief='solid')
    clustext.insert(tkinter.INSERT,clus)
    clustext.pack()
    clustext.place(x=400,y=70)

    clusnum=tkinter.Variable()
    clusnum.set('2')
    clusentry= tkinter.Entry(win,
                              width=4, borderwidth=1,
                              font=('黑体', 12), textvariable=clusnum,
                              bg=ebg,relief='solid')
    clusentry.pack()
    clusentry.place(x=720,y=340)

    #聚类分析
    def startclus():
        nonlocal samples,dimension
        nonlocal clusternum,epocs,dsmode
        nonlocal sampleClus,clusterDict,center
        nonlocal clusthread
        if len(samples)<1:
            messagebox.showerror(title='聚类？',message='请先导入数据')
            return
        try:
            clusternum=int(clusnum.get())
            if clusternum>len(samples):
                messagebox.showerror(title='聚类？',message='簇中心数目大于样本个数')
                return
        except:
            messagebox.showerror(title='聚类？',message='请在<聚类分析>右侧输入簇数目')
            return
        clus='-聚类分析-\n'
        clus+='样本数目:'+str(len(samples))+'\n'
        clus+='样本维数:'+str(dimension)+'\n'
        clus+='\n簇数目:'+str(clusternum)+'\n'
        clus+='迭代次数:'+str(epocs)+'\n'
        clus+='距离度量:'+str(dsmode)+'\n'
        clus+='-正在进行中-\n'
        clustext.delete(0.0,tkinter.END)
        clustext.insert(index=tkinter.INSERT,chars=clus)
        clusthread=ClusThread(samples,dimension,clusternum,epocs,dsmode)
        try:
            clusthread.start()
            clusthread.setDaemon(True)
        except InterruptedError:
            if not clusthread.success:
                messagebox.showerror(title='聚类...',message='聚类失败')
                return
            else:
                sampleClus=clusthread.sampleClus
                clusterDict=clusthread.clusterDict
                center=clusthread.center
        clus='\n聚类结果:\n'
        clus+='中心点:\n<簇标号:[中心点坐标]>\n'+str(center).replace('],','],\n')
        clus+='\n\n簇:\n<簇标号:[样本标号0,样本标号1,...]>\n'
        clus+=str(clusterDict).replace('],','],\n')
        clustext.insert(index=tkinter.INSERT, chars=clus)
    clusbutton = tkinter.Button(win, text="聚类分析", command=startclus,
                            width=10,height=1,font=wfont,
                            bg=bbg,activebackground=wbg,
                            borderwidth=1,relief='solid')
    clusbutton.pack()
    clusbutton.place(x=630,y=340)

    #二维可视化，输入要显示的两个维度，显示聚类结果
    def view():
        nonlocal sampleClus,center
        nonlocal dimension,clusternum,viewthread
        if len(center)<1:
            messagebox.showerror(title='二维可视化',message='请先进行聚类分析')
            return
        try:
            d1=int(dim1.get())
            d2=int(dim2.get())
        except:
            messagebox.showerror(title='二维可视化',message='请在<二维可视化>右侧输入要显示的维度')
            return
        if d1<0 or d1>dimension-1 or d2<0 or d2>dimension-1:
            messagebox.showerror(title='二维可视化',message='维数应在0和'+str(dimension-1)+'之间')
            return
        try:
            viewthread=threading.Thread(target=viewCluster,args=(sampleClus,center,clusternum,d1,d2))
            viewthread.run()
        except ImportError:
            messagebox.showerror(title='二维可视化',message='此功能需要安装matplotlib和numpy包')
            return
    viewbutton = tkinter.Button(win, text="二维可视化", command=view,
                            width=10,height=1,font=wfont,
                            bg=bbg,activebackground=wbg,
                            borderwidth=1,relief='solid')
    viewbutton.pack()
    viewbutton.place(x=400,y=340)

    dim1=tkinter.Variable()
    dim2=tkinter.Variable()
    dim1.set('0')
    dim2.set('1')
    dimemtry1=tkinter.Entry(win,
                          width=3,borderwidth=1,
                          fon=('黑体',12),textvariable=dim1,
                          bg=ebg,relief='solid')
    dimemtry2=tkinter.Entry(win,
                          width=3,borderwidth=1,
                          fon=('黑体',12),textvariable=dim2,
                          bg=ebg,relief='solid')
    dimemtry1.pack()
    dimemtry2.pack()
    dimemtry1.place(x=490,y=340)
    dimemtry2.place(x=520,y=340)

    win.mainloop()


#聚类线程
class ClusThread(threading.Thread):
    def __init__(self,samples, dimension, clusternum, epocs, dsmode='euclidean'):
        super().__init__()
        self.samples=samples
        self.dimension=dimension
        self.clusternum=clusternum
        self.epocs=epocs
        self.dsmode=dsmode

        self.sampleClus=None
        self.clusterDict=None
        self.center=None
        self.success=True

    def start(self):
        try:
            sampleClus, clusterDict, center = kmeansCluster(self.samples,
                                                            self.dimension,
                                                            self.clusternum,
                                                            self.epocs,
                                                            self.dsmode)
            self.sampleClus=sampleClus
            self.clusterDict=clusterDict
            self.center=center
        except:
            self.success=False
        raise InterruptedError

interfaceGUI()

