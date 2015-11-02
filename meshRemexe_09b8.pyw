# -*- coding: utf-8 -*-

# 2015 - Joz - http://www.hangarxplane.com.br
# Programa desenvolvido para ajudar na edição do Mesh do X-Plane. Funciona com as versões 9 e 10 do simulador.
# Basicamente converte parte de um arquivo DSF em um objeto 3D (formato do próprio simulador) para 
# ser editado em algum programa de modelagem 3D, como o Sketchup, Blender, AC3D, etc. Desde que tenha instalado
# o respectivo plugin para importar/exportar.
# Depois de editar o modelo, o programa converte de volta para o formato de texto do DSF.
# E por último, insere essas informações de volta no arquivo DSF para então ser utilizado como cenário customizado.
# Para extrair o arquivo DSF para txt é necessário o XGrinder, que faz parte do XPtools.
# http://developer.x-plane.com/tools/xptools/
# Plugin para Sketchup: http://marginal.org.uk/x-planescenery/tools.html

# Default modules
from os import remove
import os
from os.path import getsize, join
from collections import Counter
from struct import unpack
from ttk import Progressbar, Combobox, Button, Entry, Checkbutton, Radiobutton, Notebook, Frame
from Tkinter import Label, Tk, IntVar, StringVar, LEFT, CENTER, N, S, E, W, SW, NW, HORIZONTAL, END, SUNKEN, RAISED, GROOVE, RIDGE  #Button, Entry, Checkbutton
from tkFileDialog import askopenfilename, askopenfilenames
from tkMessageBox import showinfo
from shutil import copyfile
import gzip
#import time

# Third party modules 
from shapely.geometry.polygon import Polygon
from shapely.geometry import Point
from shapely.ops import cascaded_union
import matplotlib.path as mplPath
import numpy as np

class Griding:
    def __init__(self,raiz):
        self.raiz = raiz
        self.raiz.title('MeshRemexe 0.9b8 - www.hangarxplane.com.br')
        # Usar Water mesh
        self.use_water = IntVar()
        self.use_texture = IntVar()
        self.ter_list_offset = IntVar()
        # select language
        self.language_box_index = IntVar()
        # select texture
        self.terrain_box_index = IntVar()
        self.progressText = StringVar()
        # Versão do X-Plane
        self.version_var = IntVar()

        self.trad = {
            'Language':['Language','Selecionar idioma','Язык'],
            'English':['English','Português BR','Русский RU'],
            'Extract Mesh':['Extract Mesh','Extrair Mesh','Извлечение Меша'],
            'X-Plane 9':['X-Plane 9','X-Plane 9','X-Plane 9'],
            'X-Plane 10':['X-Plane 10','X-Plane 10','X-Plane 10'],
            '1 - Extract mesh and conver to OBJ':['1 - Extract mesh and conver to OBJ','1 - Extrair e converter Mesh para OBJ','1 - Извлечение меша и конвертация в OBJ'],
            'Select DSF.txt file:':['Select DSF.txt file:','Selecione o arquivo DSF.txt:','Выбрать файл DSF.txt:'],
            'Select raster (elevation.raw) file:':['Select raster (elevation.raw) file:','Selecione o arquivo raster (elevation.raw):','Выбрать растр (elevation.raw):'],
            'Selection area:':['Selection area:','Área de seleção:','Выбрать область:'],
            'Insert Mesh':['Insert Mesh','Inserir mesh','Вставить Меш'],
            '2 - Converts OBJ to mesh and creates DSF.txt file':['2 - Converts OBJ to mesh and creates DSF.txt file','2 - Converter OBJ para mesh e criar arquivo DSF.txt','2 - Конвертировать OBJ в меш и создать файл DSF.txt'],
            'Select GAP file:':['Select GAP file:','Selecione o arquivo GAP:','Выбрать файл *.GAP:'],
            'Select kml file:':['Select kml file:','Selecione o arquivo kml:','Выбрать файл kml:'],
            'Select OBJ file (water area):':['Select OBJ file (water area):','Selecione o arquivo OBJ (área de água):','Добавить файл OBJ содержащий воду:'],
            'Select terrain:':['Select terrain:','Selecione a textura do terreno:','Выбрать текстуру поверхности:'],
            'Size':['Size','Resolução:','Размер (м)'],
            'Select OBJ file:':['Select OBJ file:','Selecione o arquivo OBJ:','Выбрать файл OBJ:'],
            'Includes water area OBJ file:':['Includes water area OBJ file:','Incluir arquivo OBJ (Área de água):','Добавить файл OBJ содержащий воду:'],
            'Create KML bounding box and texture files.':['Create KML bounding box and texture files.','Criar arquivos de textura e kml','Create KML bounding box and texture files.'],
            'Insert':['Insert','Inserir','Вставить'],
            'Select':['Select','Selecionar','Выбрать'],
            'kml':['kml','kml','kml'],
            'Create':['Create','Gerar','Создать'],
            'Exit':['Exit','Fechar','Выход'],
            '(1/6) Loading file.':['(1/6) Loading file.','(1/6) Carregando arquivo','(1/6) Загрузка файла.'],
            '(2/6) DSF processing.':['(2/6) DSF processing.','(2/6) Processando DSF','(2/6) Работа с файлом DSF.'],
            '(3/6) loading elevation info.':['(3/6) loading elevation info.','(3/6) Lendo informações de elevação.','(3/6) Загрузка данных высот.'],
            '(4/6) Fixing elevations.':['(4/6) Fixing elevations.','(4/6) Corrigindo elevações.','(4/6) Изменение высот.'],
            '(5/6) Vertex writing.':['(5/6) Vertex writing.','(5/6) Escrevendo vértices.','(5/6) Запись вершин.'],
            '(5/6) Indexing.':['(5/6) Indexing.','(5/6) Organizando índices.','(5/6) Организация индексов.'],
            '(6/6) Zipping file.':['(6/6) Zipping file.','(6/6) Compactando arquivo.','(6/6) Сжатие файла.'],
            '(1/6) Unzipping file.':['(1/6) Unzipping file.','(1/6) Descompactando arquivo.','(1/6) Распаковка файла.'],
            '(2/6) Converting OBJ to mesh.':['(2/6) Converting OBJ to mesh.','(2/6) Convertendo OBJ para mesh','(2/6) Конвертация OBJ в Меш.'],
            '(3/6) Merging elevations.':['(3/6) Merging elevations.','(3/6) Combinando elevações','(3/6) Объединение высот.'],
            '(4/6) Indexing triangles strips':['(4/6) Indexing triangles strips','(4/6) Indexando strips de triângulos','(4/6) Indexing triangles strips'],
            '(5/6) Setting water color.':['(5/6) Setting water color.','(5/6) Definindo a cor da água','(5/6) Установка цвета воды.'],
            '(6/6) Inserting mesh.':['(6/6) Inserting mesh.','(6/6) Inserindo mesh.','(6/6) Вставка меша.'],
            'Files created successfully.':['Files created successfully.','Arquivos criados com sucesso.','Файл успешно создан.'],
            'Mesh successfully updated.':['Mesh successfully updated.','Mesh atualizado com sucesso.','Меш обновлен успешно.\nДа прибудет с тобой сила!'],
            'Nothing to insert.':['Nothing to insert.','Não foi possível inserir mesh.','Ошибка! Не удалось вставить меш.']
            }

        # tradução
        self.txt_box = StringVar()
        self.txt_tab1 = StringVar()
        self.txt_label_1_0 = StringVar()
        self.txt_label_1_1 = StringVar()
        self.txt_label_1_2 = StringVar()
        self.txt_label_1_3 = StringVar()
        self.txt_radio1 = StringVar()
        self.txt_radio2 = StringVar()        
        self.txt_bt_0 = StringVar()
        self.txt_bt_1 = StringVar()
        self.txt_bt_2 = StringVar()
        self.txt_bt_3 = StringVar()
        self.txt_bt_4 = StringVar()
        self.txt_tab2 = StringVar()        
        self.txt_label_2_0 = StringVar()
        self.txt_label_2_1 = StringVar()
        self.txt_label_2_2 = StringVar()
        self.txt_label_2_3 = StringVar()
        self.txt_label_2_4 = StringVar()
        self.txt_check = StringVar()
        self.txt_check2 = StringVar()

        # Cria abas
        self.nb = Notebook(self.raiz)
        self.page1 = Frame(self.nb)
        self.page2 = Frame(self.nb)

        ############################## Interface ##############################
        # Texto seleção idioma
        Label(self.raiz,textvariable=self.txt_box).grid(row=0, column=0, padx=5, sticky=E, columnspan=3)

        # ComboBox language
        self.box_value = StringVar()
        self.box = Combobox(self.raiz, width=13, textvariable=self.box_value)
        self.box['values'] = (self.trad['English'][0],self.trad['English'][1], self.trad['English'][2])
        self.box.current(0)
        self.box.grid(column=3, row=0, pady=5, padx=5, sticky=E+W)
        self.box.bind('<<ComboboxSelected>>', self.butTraduzir)

        # ============================================================
        # ========================== PAGE 1 ==========================
        # ============================================================
        
        # Extract Mesh
        self.nb.add(self.page1, text=self.txt_tab1)

        # 1 - Extract mesh and conver to OBJ
        Label(self.page1,textvariable=self.txt_label_1_0, width=54, background="gray87", relief=GROOVE).grid(row=1, column=0, columnspan=4, padx=3, pady=5, sticky=E+W)

        # Select DSF.txt file:
        Label(self.page1,textvariable=self.txt_label_1_1).grid(row=2, column=0, sticky=SW, padx=5, columnspan=2)

        # Radio button: X-Plane 10
        self.rb1 = Radiobutton(self.page1, textvariable=self.txt_radio1, variable=self.version_var, value=10, command=self.disableRaster)
        self.rb1.grid(row=2, column=2, padx=3, sticky=E)
        # Radio button: X-Plane 9
        self.rb2 = Radiobutton(self.page1, textvariable=self.txt_radio2, variable=self.version_var, value=9, command=self.disableRaster)
        self.rb2.grid(row=2, column=3, padx=3, sticky=W)
        # Defino a versão 10 como padrão:
        self.version_var.set(10)

        # campo 1- DSF txt file
        self.dsfPatchEntry=Entry(self.page1, justify=LEFT, width=48)
        self.dsfPatchEntry.grid(row=3,column=0, columnspan=3, sticky=N+E+S+W, padx=5, pady=5)
        # Botao 'Select' DSF
        self.selectDsf1=Button(self.page1, width=11, command=self.selectDSFtxt, textvariable=self.txt_bt_0)
        self.selectDsf1.grid(row=3, column=3)

        # Select raster (elevation.raw) file:
        Label(self.page1,textvariable=self.txt_label_1_2).grid(row=4, column=0, sticky=SW, padx=5, columnspan=3)
        # Campo Raster file
        self.rasterEntry=Entry(self.page1, justify=LEFT)
        self.rasterEntry.grid(row=5, column=0, columnspan=3, sticky=N+E+S+W, padx=5, pady=5)
        # Botao Select Raster file
        self.selectRasterBt=Button(self.page1, width=11, command=self.selectRaster, textvariable=self.txt_bt_0)
        self.selectRasterBt.grid(row=5, column=3)

        # Area selection     
        Label(self.page1,textvariable=self.txt_label_1_3).grid(row=6, column=0, sticky=SW, padx=5, columnspan=3)
        # campo - lista de coordenadas
        self.areaSelEntry=Entry(self.page1, justify=LEFT, width=48)
        self.areaSelEntry.grid(row=7,column=0, columnspan=3, sticky=N+E+S+W, padx=5, pady=5)
        # Botao Select KML file
        self.selectKmlBt=Button(self.page1, width=11, command=self.selectKml, textvariable=self.txt_bt_1)
        self.selectKmlBt.grid(row=7, column=3)

        # Includes water area OBJ file:
        self.textureCheck =Checkbutton(self.page1, textvariable=self.txt_check2, variable=self.use_texture)
        self.textureCheck.grid(row=8, column=0, sticky=SW, padx=5, pady=5, columnspan=4)
        
        # Botao Generate Patch
        self.genPatch=Button(self.page1, width=11, command=self.splitDsf, textvariable=self.txt_bt_2)
        self.genPatch.grid(row=9, column=3)

        # ============================================================
        # ========================== PAGE 2 ==========================
        # ============================================================

        # Insert Mesh
        self.nb.add(self.page2, text=self.txt_tab2)

        # 2 - Converts OBJ to mesh and creates DSF.txt file
        Label(self.page2,textvariable=self.txt_label_2_0, width=54, background="gray87", relief=GROOVE).grid(row=1, column=5, columnspan=4, padx=3, pady=5, sticky=E+W)

        # Select GAP file:
        Label(self.page2,textvariable=self.txt_label_2_1).grid(row=2, column=5, sticky=SW, padx=5, columnspan=4)
        # Campo 2 - DSF txt file 
        self.dsfInsertPatchEntry=Entry(self.page2, justify=LEFT)
        self.dsfInsertPatchEntry.grid(row=3,column=5, columnspan=3, sticky=N+E+S+W, padx=5, pady=5)
        # Botao Select DSF to insert
        self.selectInsertPatchEntry=Button(self.page2, width=11, command=self.insertPatchFile, textvariable=self.txt_bt_0)
        self.selectInsertPatchEntry.grid(row=3, column=8)

        # Texture combobox
        # Select terrain:
        Label(self.page2, textvariable=self.txt_label_2_2).grid(row=4, column=5, padx=5, sticky=SW, columnspan=3)
        # Texture combobox field
        self.box_value2 = StringVar()
        self.box2 = Combobox(self.page2, textvariable=self.box_value2)
        self.box2['values'] = ()
        #self.box2.current(0)
        self.box2.grid(column=5, row=5, pady=5, padx=5, columnspan=3, sticky=N+E+S+W)
        self.box2.bind('<<ComboboxSelected>>', self.chooseTer)

        # Size:
        Label(self.page2,textvariable=self.txt_label_2_3).grid(row=4, column=8, sticky=SW, padx=5)
        # Texture resolution Field
        self.resEntry=Entry(self.page2, justify=CENTER, width=10)
        self.resEntry.grid(row=5,column=8, padx=5, pady=5, sticky=N+E+S+W)

        # Select OBJ file:
        Label(self.page2,textvariable=self.txt_label_2_4).grid(row=6, column=5, sticky=SW, padx=5, columnspan=4)
        # OBJ Field
        self.objEntry=Entry(self.page2, justify=LEFT, width=48)
        self.objEntry.grid(row=7,column=5, columnspan=3, sticky=N+E+S+W, padx=5, pady=5)
        # Select OBJ button
        self.selectObj=Button(self.page2, width=11, command=self.selectObj, textvariable=self.txt_bt_0)
        self.selectObj.grid(row=7, column=8)

        # Includes water area OBJ file:
        self.useWobjCheck =Checkbutton(self.page2, command=self.disableEntry, textvariable=self.txt_check, variable=self.use_water)
        self.useWobjCheck.grid(row=8, column=5, sticky=SW, padx=5, pady=5, columnspan=4)

        # Water OBJ Field
        self.wObjEntry=Entry(self.page2, justify=LEFT, width=48)
        self.wObjEntry.grid(row=9,column=5, columnspan=3, sticky=N+E+S+W, padx=5, pady=5)
        # Select Water OBJ button
        self.selectwObjBt=Button(self.page2, width=11, command=self.selectWobj, textvariable=self.txt_bt_0)
        self.selectwObjBt.grid(row=9, column=8)        

        # Botao generate Mesh
        self.insertPatchBt=Button(self.page2, width=11, command=self.insertPatch, textvariable=self.txt_bt_3)
        self.insertPatchBt.grid(row=10, column=8, pady=5)
        
        #=================================================================================

        # Texto barra progresso
        Label(self.raiz,textvariable = self.progressText, relief=GROOVE, width=53).grid(row=2, column=0, padx=5, pady=5, columnspan=4)
        # Barra de progresso
        self.progress = Progressbar(orient=HORIZONTAL, length=383, mode='determinate')
        self.progress.grid(row=3, column=0, pady=5, columnspan=4)
        # Botao Fechar
        self.genMesh=Button(self.raiz, width=11, command=self.fechar, textvariable=self.txt_bt_4)
        self.genMesh.grid(row=4, column=0, pady=5, sticky=S, columnspan=4)

        # Desmarca a opção de usar Water Mesh
        self.use_water.set(0)
        self.disableEntry()

        # Tab displacement
        self.nb.grid(row=1, column=0, columnspan=4, padx=3)

        # Carrega arquivo com informação do diretório
        self.defaultDir = self.loadDir()
        # Carrega as preferências
        self.loadIni()
        # Traduz o programa
        self.traduzir(self.language_box_index.get())

    def butTraduzir(self, event):
        if self.box.get().encode('utf-8') == self.trad['English'][0]:
            self.language_box_index.set(0)
        elif self.box.get().encode('utf-8') == self.trad['English'][1]:
            self.language_box_index.set(1)
        elif self.box.get().encode('utf-8') == self.trad['English'][2]:
            self.language_box_index.set(2)
        #else:
        #    self.language_box_index.set(3)
        var = self.language_box_index.get()
        self.traduzir(var)

    def traduzir(self, var):

        # Tradução
        self.txt_box.set(self.trad['Language'][var])
        self.txt_tab1.set(self.trad['Extract Mesh'][var])
        self.txt_label_1_0.set(self.trad['1 - Extract mesh and conver to OBJ'][var])
        self.txt_label_1_1.set(self.trad['Select DSF.txt file:'][var])
        self.txt_label_1_2.set(self.trad['Select raster (elevation.raw) file:'][var])
        self.txt_label_1_3.set(self.trad['Selection area:'][var])
        self.txt_radio1.set(self.trad['X-Plane 10'][var])
        self.txt_radio2.set(self.trad['X-Plane 9'][var])  
        self.txt_bt_0.set(self.trad['Select'][var])
        self.txt_bt_1.set(self.trad['kml'][var])
        self.txt_bt_2.set(self.trad['Create'][var])
        self.txt_bt_3.set(self.trad['Insert'][var])
        self.txt_bt_4.set(self.trad['Exit'][var])
        self.txt_tab2.set(self.trad['Insert Mesh'][var]) 
        self.txt_label_2_0.set(self.trad['2 - Converts OBJ to mesh and creates DSF.txt file'][var])
        self.txt_label_2_1.set(self.trad['Select GAP file:'][var])
        self.txt_label_2_2.set(self.trad['Select terrain:'][var])
        self.txt_label_2_3.set(self.trad['Size'][var])
        self.txt_label_2_4.set(self.trad['Select OBJ file:'][var])
        self.txt_check.set(self.trad['Includes water area OBJ file:'][var])
        self.txt_check2.set(self.trad['Create KML bounding box and texture files.'][var])

        # Muda o texto das abas. (ttk.notebook não tem textvariable)
        self.nb.tab(self.page1, text=self.txt_tab1.get())
        self.nb.tab(self.page2, text=self.txt_tab2.get())        

    # save meshRemexe.ini file 
    def saveIni(self):
        try:
            entry = {
                'language': self.box.get().encode('utf-8'),
                'version': self.version_var.get(),
                'dsf_file': self.dsfPatchEntry.get().encode('utf-8'),
                'raw_file': self.rasterEntry.get().encode('utf-8'),
                'area_select': self.areaSelEntry.get().encode('utf-8'),
                'gap_file': self.dsfInsertPatchEntry.get().encode('utf-8'),
                'terrain': self.box2.get().encode('utf-8'),
                'size': self.resEntry.get().encode('utf-8'),
                'obj_file': self.objEntry.get().encode('utf-8'),
                'wtr_select': self.use_water.get(),
                'texture_select': self.use_texture.get(),
                'wobj_file': self.wObjEntry.get().encode('utf-8')
                }
            
            w = open(os.path.join(self.defaultDir,'meshRemexe.ini'),'w')
            for key in entry:
                w.write('%s=%s\n' % (key, entry[key]))
            w.close()
        except ValueError as e:
            print e
        #except:
        #    pass

    # load meshRemexe.ini file     
    def loadIni(self):
        try:
            entry = {
                'language': self.box,
                'version': self.version_var,
                'dsf_file': self.dsfPatchEntry,
                'raw_file': self.rasterEntry,
                'area_select': self.areaSelEntry,
                'gap_file': self.dsfInsertPatchEntry,
                'terrain': self.box2,
                'size': self.resEntry,
                'obj_file': self.objEntry,
                'wtr_select': self.use_water,
                'texture_select': self.use_texture,
                'wobj_file': self.wObjEntry
                }
            
            f = open(os.path.join(self.defaultDir,'meshRemexe.ini'),'r')
            config = f.readlines()
            f.close()
            d = {}
            for linha in config:
                try:
                    linha = linha.replace('\n','')
                    a = linha.split('=')
                    d[a[0]] = a[1]
                except:
                    pass

            for key in d:
                if  d[key] != '':
                    if key == 'version':
                        entry[key].set(int(d[key]))
                        self.disableRaster()
                    elif key == 'wtr_select':
                        entry[key].set(int(d[key]))
                        self.disableEntry()
                        entry['wobj_file'].delete(0, END)
                        entry['wobj_file'].insert(0, d['wobj_file'])
                    elif key == 'texture_select':
                        entry[key].set(int(d[key]))
                    elif key == 'terrain':
                        entry['gap_file'].delete(0, END)
                        entry['gap_file'].insert(0, d['gap_file'])
                        self.textList()
                        entry[key].set(d[key])
                    elif key == 'language':
                        entry[key].set(d[key])
                        self.butTraduzir('event')
                    else:
                        entry[key].delete(0, END)
                        entry[key].insert(0, d[key])
        except:
            pass
        #except ValueError as e:
        #    print e

    def loadDir(self):
        try:
            f = open('exeDir.txt','r')
            a = f.readline()
            defaultDir = os.path.join(a)
            endPath = defaultDir.rfind('\\')
            defaultDir = defaultDir[:endPath]+'/'
            defaultDir = defaultDir.replace('\\','/')
            f.close()
        except:
            defaultDir = os.path.dirname(os.path.abspath('__file__'))
        return(defaultDir)

    def splitDsf(self):
        # Arquivo DSF extraido com o DSFtool
        dsfName = self.dsfPatchEntry.get()
        files_created = ''

        #path = dsfName[:(dsfName.rfind('/'))+1]
        path = dsfName[:dsfName.rfind('/')+1]
        filename = dsfName[dsfName.rfind('/'):-4]+'.gap'
        files_created += filename[1:]

        area_sel = self.areaSelEntry.get()


        f=open(dsfName,'r')     # Arquivo DSF original
        
        dsf = []
        # estimando uma barra de progresso baseado na média de 73bytes/linha
        estLines = int(getsize(dsfName))/73
        estLines1 = estLines/100         
        count = 1
        nLine = 0
        while True:
            linha = f.readline()
            if linha == '':
                break
            dsf.append(linha)
            if nLine >= (estLines1)*count:
                self.progressBarUpdate(self.trad['(1/6) Loading file.'][self.language_box_index.get()], nLine, estLines)
                count += 1
            nLine+=1
        f.close()               # Fecha o arquivo original
        
        #f=open(dsfName,'r')     # Arquivo DSF original
        #dsf = f.readlines()     # Carrega o arquivo em uma lista
        #f.close()               # Fecha o arquivo original

        # Separa a area extraída do arquivo original
        extracted_lst = []
        remain_lst = []

        patch_flag = False
        patch_list = []
        counter = 0
        total = len(dsf)
        cur_progress = 0
        progress = 0
        for linha in dsf:
            # acumula patch
            if linha[:11] == 'BEGIN_PATCH':
                patch_flag = True

            if patch_flag == True:
                patch_list.append(linha)
            else:
                remain_lst.append(linha)
        
            if linha[:9] == 'END_PATCH':
                a, b = self.write_patch(patch_list)
                extracted_lst += a
                remain_lst += b
                patch_list = []
                patch_flag = False
            counter += 1
            progress  = int((float(counter)/total)*100)
            if progress != cur_progress:
                self.progressBarUpdate(self.trad['(2/6) DSF processing.'][self.language_box_index.get()], progress, 100)
                cur_progress = progress

        # Lista com vertices que não sejam -32768
        preserv_lst = self.preservElev(extracted_lst, area_sel)

        # Lista com as texturas da área
        # self.printLog('extracted_lst.txt',extracted_lst)
        
        # Combina os patchs físicos numa única lista
        mesh_phy, mesh_wtr  = self.combinePhyPatch(extracted_lst)

        # Corrige a elevação baseado no arquiv raster
        if self.version_var.get() == 10:
            mesh_fix, water_fix = self.fixElevation([mesh_phy, mesh_wtr])
        # X-Plane 9 não precisa corrigir elevações
        else:
            mesh_fix = mesh_phy
            water_fix = mesh_wtr

        # Lista com os vértices e valores de cor da água em volta do mesh
        if len(mesh_wtr) > 0:
            outlineWtr = self.outline(mesh_wtr)
        else:
            outlineWtr = []

        # Converte para OBJ
        mesh_obj, mesh_sea = self.mesh2Obj([mesh_fix, water_fix])
        f=open(path+filename[:-4]+'.obj','w')
        files_created += '\n'+filename[1:-4]+'.obj'
        
        # Atualiza textura
        texture_box = ''
        mesh_obj, mesh_sea = self.updateTex([mesh_obj, mesh_sea])
        for linha in mesh_obj:
            if linha[:14] == '# bounding box':
                texture_box = linha[linha.find('=')+2:]
            elif self.use_texture.get() == 1 and linha[:7] == 'TEXTURE':
                linha = 'TEXTURE\t'+ filename[1:-4]+'.jpg'+'\n'
                files_created += '\n'+filename[1:-4]+'.jpg'
                copyfile('tex_land.jpg', path+filename[:-4]+'.jpg')
            f.write(linha)
        f.close()

        if texture_box != '':
            f=open(path+filename[:-4]+'_box.kml','w')
            files_created += '\n'+filename[1:-4]+'_box.kml'
            self.kmlTexture(texture_box, f, filename[1:-4])
            f.close()

        texture_box = ''
        # Verifica se o objeto não está vazio
        if len(mesh_sea) > 10:
            # Cria o OBJ sea
            f=open(path+filename[:-4]+'_sea.obj','w')
            files_created += '\n'+filename[1:-4]+'_sea.obj'
            for linha in mesh_sea:
                if linha[:14] == '# bounding box':
                    texture_box = linha[linha.find('=')+2:]
                elif self.use_texture.get() == 1 and linha[:7] == 'TEXTURE': 
                    linha = 'TEXTURE\t'+ filename[1:-4]+'_sea.jpg'+'\n'
                    files_created += '\n'+filename[1:-4]+'_sea.jpg'
                    copyfile('tex_sea.jpg', path+filename[1:-4]+'_sea.jpg')
                f.write(linha)
            f.close()

        if texture_box != '':
            f=open(path+filename[:-4]+'_sea_box.kml','w')
            files_created += '\n'+filename[1:-4]+'_sea_box.kml'
            self.kmlTexture(texture_box, f, (filename[1:-4]+'_sea'))
            f.close()

        # Quantidade de linhas + 3 (número de linhas + area select)
        header = ['%i\n' % (len(remain_lst)+len(preserv_lst)+len(outlineWtr)+5)]
        # Adicione Area_sel no início
        header.append(area_sel+'\n')
        # Adiciona número da versão
        header.append('version= %i\n' % self.version_var.get())
        # Adiciona preserve list
        if len(preserv_lst) > 0:
            for linha in preserv_lst:
                header.append('PR_LIST\t%.9f\t%.9f\t%.9f\n' % (linha[0], linha[1], linha[2]))
            header.append('END_PRESERV_LST\n')
        
        if len(outlineWtr) > 0:
            for linha in outlineWtr:
                header.append('VT_COLOR\t%.9f\t%.9f\t%.9f\n' % (linha[0], linha[1], linha[2]))
            header.append('END_SEA_COLOR\n')
            
        remain_lst = header + remain_lst
            
        
        # compress file
        with gzip.open(path+filename,'wb') as f:
            tamanho = len(remain_lst)
            count = 1
            for i in range(len(remain_lst)):
                f.write(remain_lst[i])
                
                # Barra de progresso
                if i >= (tamanho/100)*count:
                    self.progressBarUpdate(self.trad['(6/6) Zipping file.'][self.language_box_index.get()], i, tamanho)
                    count += 1
        f.close()

        self.concluido(self.trad['Files created successfully.'][self.language_box_index.get()]+'\n'+files_created)


    def updateTex(self, objList):
        objName = []
        for obj in objList:
            # Verifica se o OBJ está vazio
            if len(obj) <= 10:
                objName.append(obj)
            else:
                lista = []
                for linha in obj:
                    if linha[:2] == 'VT':
                        a = linha.split()
                        lista.append([float(a[3])/-100000,float(a[1])/100000])

                # Define os valores Min e Max do OBJ
                xy = zip(*lista)
                latSup, lonRight = map(max, xy)
                latInf, lonLeft = map(min, xy)
        
                # Coordenadas da textura
                dlo = lonRight - lonLeft
                dla = latSup - latInf
                for i in range(len(obj)):
                    if obj[i][:2] == 'VT':
                        linha = obj[i].split()
                        lon = float(linha[1])/100000
                        lat = float(linha[3])/-100000
                        linha[7] = '%.4f' % ((lon - lonLeft)/dlo)
                        linha[8] = '%.4f' % ((lat - latInf)/dla)
                        obj[i] = ''
                        for item in linha:
                            obj[i] += item+' '
                        obj[i] = obj[i][:-1]
                        obj[i] += '\n'
                if self.use_texture.get() == 1:
                    a = '%.9f,%.9f,0 ' % (lonLeft, latSup)
                    b = '%.9f,%.9f,0 ' % (lonRight, latSup)
                    c = '%.9f,%.9f,0 ' % (lonRight, latInf)
                    d = '%.9f,%.9f,0 ' % (lonLeft, latInf)
                    coords = a+b+c+d+a
                    obj.append('\n\n')
                    obj.append('# bounding box = %s' % coords)                
                obj.append('\n\n# object created with MeshRemexe 0.9b8\n')
                objName.append(obj)
        return(objName)

    def kmlTexture(self, coords, filename, description):
        filename.write('<?xml version="1.0" encoding="UTF-8"?>')
        filename.write('<kml xmlns="http://earth.google.com/kml/2.2">')
        filename.write(' <Document>')
        filename.write('   <Placemark>')
        filename.write('     <name>%s</name>' % description)
        filename.write('     <description>%s</description>' % (description+' bounding box'))
        filename.write('     <Style>')
        filename.write('       <LineStyle>')
        filename.write('         <color>ff00ff00</color>')
        filename.write('         <width>1</width>')
        filename.write('       </LineStyle>')
        filename.write('       <PolyStyle>')
        filename.write('         <color>33FFFFFF</color>')
        filename.write('         <fill>0</fill>')
        filename.write('       </PolyStyle>')
        filename.write('     </Style>')
        filename.write('     <Polygon>')
        filename.write('       <extrude>1</extrude>')
        filename.write('       <outerBoundaryIs>')
        filename.write('         <LinearRing>')
        filename.write('           <coordinates>%s</coordinates>' % coords)
        filename.write('         </LinearRing>')
        filename.write('       </outerBoundaryIs>')
        filename.write('     </Polygon>')
        filename.write('   </Placemark>')
        filename.write(' </Document>')
        filename.write('</kml>')

    def outline(self, patchList):
        polygonList = []
        polygons = []
        stripTri = False
        stringTri = False
        stringList = []
        stripList = []

        # Converte a Strip de triangulos em String
        for linha in patchList:
            if linha[:17] == 'BEGIN_PRIMITIVE 1':
                stripList.append(linha)
                stripTri = True
            elif linha[:12] == 'PATCH_VERTEX' and stripTri == True:
                stripList.append(linha)
            elif linha[:13] == 'END_PRIMITIVE' and stripTri == True:
                stripList.append(linha)
                stripTri = False
                newString = self.strip2list(stripList)
                for linha1 in newString:
                    stringList.append(linha1)
                stripList = []
            else:
                stringList.append(linha)

        # Cria uma lista d epolígonos a partir da Lista de Strings
        for linha in stringList:
            if linha[:17] == 'BEGIN_PRIMITIVE 0':
                stringTri = True
            elif linha[:12] == 'PATCH_VERTEX' and stringTri == True:
                a = linha.split()
                polygons.append((float(a[1]),float(a[2])))
                if len(polygons) == 3:
                    polygonList.append(Polygon(polygons))
                    polygons = []
            elif linha[:13] == 'END_PRIMITIVE':
                stringTri = False

        # Combina todos os polpigonos em um só
        mergeList = cascaded_union(polygonList)

        outlineVerts = []

        # Cria uma lista com os vertices externos
        if mergeList.geometryType() == 'MultiPolygon':
            for i in range(len(mergeList)):
                outlineVerts += list(mergeList[i].exterior.coords)
        else:
            outlineVerts += list(mergeList.exterior.coords)

        # Converte as tuplas de coordenadas em listas para
        # poder armazenar as informações de cor
        for i in range(len(outlineVerts)):
            outlineVerts[i] = list(outlineVerts[i])

        # Busca na lista de Patch, as informações de cor
        # baseado nas coordenadas
        for i in range(len(outlineVerts)):
            a = '%.9f' % outlineVerts[i][0]
            b = '%.9f' % outlineVerts[i][1]
            for j in range(len(patchList)):
                if patchList[j][:12] == 'PATCH_VERTEX':
                    c = patchList[j].split()
                    if (a, b) == (c[1], c[2]):
                        outlineVerts[i].append(float(c[6]))
                        break

        return(outlineVerts)

    def write_patch(self, patch_list):
        vert_flag = False
        vert_list = []
        header_Flag = False

        extracted_lst = []
        remain_lst = []
        
        for linha in patch_list:
            if linha[:15] == 'BEGIN_PRIMITIVE':
                vert_flag = True
            
            if vert_flag == True:
                vert_list.append(linha)

            else:
                remain_lst.append(linha)
            
            if linha[:13] == 'END_PRIMITIVE':
                # separa em duas listas
                extracted, remain = self.test_vert(vert_list)
                vert_list = []

                if len(extracted) > 0 and header_Flag == False:
                    extracted_lst.append(patch_list[0])
                    header_Flag = True
                for i in range(len(extracted)):
                    extracted_lst.append(extracted[i])
                for i in range(len(remain)):
                    remain_lst.append(remain[i])
                vert_flag = False
        if header_Flag == True:
            extracted_lst.append(patch_list[-1])
            
        # Verifica se o patch é vazio
        if len(extracted_lst) == 2:
            extracted_lst = []
        if len(remain_lst) == 2:
            remain_lst = []

        # verifica se o patch é vazio e tem primitives dentro.
        verifyPrim = False
        if len(extracted_lst) > 2:
            for i in range(1, len(extracted_lst)-1):
                if extracted_lst[i][:15] == 'BEGIN_PRIMITIVE':
                    verifyPrim = True
            if verifyPrim == False:
                del extracted_lst[0]
                del extracted_lst[-1]
        verifyPrim = False
        if len(remain_lst) > 2:
            for i in range(1, len(remain_lst)-1):
                if remain_lst[i][:15] == 'BEGIN_PRIMITIVE':
                    verifyPrim = True
            if verifyPrim == False:
                del remain_lst[0]
                del remain_lst[-1]
            
        return(extracted_lst, remain_lst)


    def test_vert(self, vert_list):

        # Coordenadas da área
        poly = self.string2poly(self.areaSelEntry.get())
        # Cria o poligono
        bbPath = mplPath.Path(np.array(poly))
        
        point_inside = False
        extracted_vert = []
        remain_vert = []

        # Triangle Fan
        if vert_list[0][:17] == 'BEGIN_PRIMITIVE 2':
            coordinates = vert_list[1].split()
            if len(coordinates) > 3:
                if bbPath.contains_point((float(coordinates[1]), float(coordinates[2]))) == True:
                    extracted_vert = vert_list
                    remain_vert = []
                else:
                    vert_list = self.fan2list(vert_list)
        
        # Triangle strip
        if vert_list[0][:17] == 'BEGIN_PRIMITIVE 1':
            insideCount = 2
            for i in range(1, len(vert_list)-1):
                coordinates = vert_list[i].split()
                if len(coordinates) > 3:
                    if bbPath.contains_point((float(coordinates[1]), float(coordinates[2]))) == True:
                        insideCount += 1
            if insideCount == len(vert_list):
                extracted_vert = vert_list
                remain_vert = []
            elif insideCount == 2:
                extracted_vert = []
                remain_vert = vert_list
            else:
                vert_list = self.strip2list(vert_list)

        # Triangle list               
        if vert_list[0][:17] == 'BEGIN_PRIMITIVE 0':
            extracted_vert.append(vert_list[0])
            remain_vert.append(vert_list[0])
        
            for i in range(1, len(vert_list)-1):
                coordinates = vert_list[i].split()
                if len(coordinates) > 3:
                    if bbPath.contains_point((float(coordinates[1]), float(coordinates[2]))) == True:
                        point_inside = True
                if  point_inside == True and i%3 == 0:
                    try:
                        a = vert_list[i-2]
                        b = vert_list[i-1]
                        c = vert_list[i]
                        extracted_vert.append(a)
                        extracted_vert.append(b)
                        extracted_vert.append(c)
                        point_inside = False
                    except:
                        pass
                elif point_inside == False and i%3 == 0:
                    try:
                        a = vert_list[i-2]
                        b = vert_list[i-1]
                        c = vert_list[i]
                        remain_vert.append(a)
                        remain_vert.append(b)
                        remain_vert.append(c)
                    except:
                        pass
            extracted_vert.append(vert_list[-1])
            remain_vert.append(vert_list[-1])
            # Caso nao insira vertices
            if extracted_vert[0][:5] == 'BEGIN' and extracted_vert[1][:3] == 'END':
                extracted_vert = []
            if remain_vert[0][:5] == 'BEGIN' and remain_vert[1][:3] == 'END':
                remain_vert = []

        return (extracted_vert, remain_vert)


    # funcao para gerar lista de vertices a partir de triangle strip
    # criando triangulos no sentido hoario
    def strip2list(self, primitive):
        lista = primitive[1:-1]
        triList = ['BEGIN_PRIMITIVE 0\n']
        # Os dois primeiros triangulos sao definidos manualmente
        triList.append(lista[0])
        triList.append(lista[1])
        triList.append(lista[2])
        triList.append(lista[1])
        triList.append(lista[3])
        triList.append(lista[2])
        # Do terceiro em diante, o algoritmo consegue resolver
        for i in range(3, len(lista)-1):
            triList.append(lista[i])
            triList.append(lista[(i-1)+(i%2)*2])
            triList.append(lista[(i+1)+(i%2)*-2])
        triList.append(primitive[-1])
        return(triList)

    def fan2list(self, primitive):
        lista = primitive[1:-1]
        triList = ['BEGIN_PRIMITIVE 0\n']
        for i in range(len(lista)-2):
            triList.append(lista[0])
            triList.append(lista[i+1])
            triList.append(lista[i+2])
        triList.append(primitive[-1])
        return(triList)

    def string2poly(self, area_sel):
        poly = area_sel.split(';')
        for i in range(len(poly)):
            poly[i] = poly[i].split(',')
            poly[i][0] = float(poly[i][0])
            poly[i][1] = float(poly[i][1])
        return(poly)

    def blendElev(self, meshNames, area_sel, preservLst):
        blendNames = []
        tamanho = 0
        counter = 0.0
        cur_progress = 0
        progress = 0
        for meshList in meshNames:
            tamanho += len(meshList)

        for meshList in meshNames:
            
            lst = meshList
            lstBlend = []
            # Area de seleção
            poly = self.string2poly(area_sel)

            # Cria nova lista para armazenar o índice do preservLst
            preservIdx = []
            for linha in preservLst:
                preservIdx.append((linha[1], linha[0]))

            # Cria o poligono
            bbPath = mplPath.Path(np.array(poly))

            # Iniciliza contador
            count = 0
            #incCount = 1

            for i in range(len(meshList)):
                # verifica se eh vertice
                if meshList[i][:12] == 'PATCH_VERTEX':
                    # divide a linha do texto em uma lista
                    linha = meshList[i].split()

                    # testa se os vértices estão fora da área de seleção
                    if bbPath.contains_point((float(linha[1]), float(linha[2]))) == False:
                        # Se não tiver o valor padrão:
                        if float(linha[3]) != -32768.0:
                            # testa se faz parte da lista de vértices preservados
                            if (float(linha[2]), float(linha[1])) in preservIdx:
                                pos = preservIdx.index((float(linha[2]), float(linha[1])))
                                linha[3] = '%.9f' % preservLst[pos][2]
                            # Caso contrário, define como valor padrão
                            else:
                                linha[3] = '-32768.0000'
                            count += 1
                    # inicializa variavel
                    novaLinha = ''
                    # preenche a variavel com texto da lista mais um espaco
                    for j in range(len(linha)):
                        novaLinha += linha[j] + ' '
                    # Substitui o ultimo espaco por uma quebra de linha
                    novaLinha = novaLinha[:-1] + '\n'
                    # Substitui a linha do arquivo original
                    meshList[i] = novaLinha
                # Barra de progresso
                #if i >= (len(meshList)/100)*count:
                #    self.progressBarUpdate("(5/5) Merging elevations", i, len(meshList))
                #    incCount += 1

                counter += 1.0
                progress  = int((counter/tamanho)*100)
                if progress != cur_progress:
                    self.progressBarUpdate(self.trad['(3/6) Merging elevations.'][self.language_box_index.get()], progress, 100)
                    cur_progress = progress
            
            # Reescreve o arquivo com as linhas modificadas
            for i in range(len(meshList)):
                lstBlend.append(meshList[i])

            blendNames.append(lstBlend)
        return(blendNames)


    def preservElev(self, extracted_lst, area_sel):

        preserv_lst = []

        #Define área de seleção
        poly = self.string2poly(area_sel)
        bbPath = mplPath.Path(np.array(poly))

        preserveList = []
        count = 0
        for i in range(len(extracted_lst)):
            if extracted_lst[i][:12] == 'PATCH_VERTEX':
                linha = extracted_lst[i].split()
                # verifica se os vértices estão for da área de seleção
                if bbPath.contains_point((float(linha[1]), float(linha[2]))) == False:
                    # Verifica se existe elevações não-padrão
                    if float(linha[3]) != -32768.0:
                        preserveList.append(extracted_lst[i])

        listaELev = []
        for linha in preserveList:
            item = linha.split()
            listaELev.append((float(item[1]),float(item[2]),float(item[3])))
        # Lista com itens sem repetição
        listaELev = list(set(listaELev))

        return(listaELev)

    def selectDSFtxt(self):
        entry = self.dsfPatchEntry
        currentEntry = entry.get()
        objFile = askopenfilename(title=self.trad['Select DSF.txt file:'][self.language_box_index.get()], filetypes= [('text files', '.txt'), ('all files', '.*')], initialdir=self.defaultDir)
        if file != None:
            entry.delete(0, END)
            entry.insert(0, objFile)
        if entry.get() == '':
            entry.delete(0, END)
            entry.insert(0, currentEntry)

    def selectRaster(self):
        entry = self.rasterEntry
        currentEntry = entry.get()
        objFile = askopenfilename(title=self.trad['Select raster (elevation.raw) file:'][self.language_box_index.get()], filetypes= [('raster files', '.raw'), ('all files', '.*')], initialdir=self.defaultDir)
        if file != None:
            entry.delete(0, END)
            entry.insert(0, objFile)
        if entry.get() == '':
            entry.delete(0, END)
            entry.insert(0, currentEntry)

    def selectKml(self):
        kmlFile = askopenfilename(title=self.trad['Select kml file:'][self.language_box_index.get()], filetypes= [('kml files', '.kml'), ('all files', '.*')], initialdir=self.defaultDir)
        if file != None:
            try:
                f = open(kmlFile,'r')
                kml = f.readlines()
                f.close()
                coords = []
                for i in range(len(kml)):
                    # Google Earth
                    if kml[i].split() == ['<coordinates>']:
                        if kml[i+2].split() == ['</coordinates>']:
                            coords = kml[i+1].split()
                            break
                    # SAS Planet
                    elif kml[i].find('<coordinates>') != -1:
                        if kml[i].find('</coordinates>') != -1:
                            a = kml[i].find('<coordinates>') + 13
                            b = kml[i].find('</coordinates>')
                            coords = kml[i][a:b].split()
                            break
                coordStr = ''
                for linha in coords:
                    lonLat = linha.split(',')
                    coordStr += lonLat[0]+','+lonLat[1]+';'
                coordStr = coordStr[:-1]
                self.areaSelEntry.delete(0, END)
                self.areaSelEntry.insert(0, coordStr)
            except:
                pass

    def selectObj(self):
        entry = self.objEntry
        currentEntry = entry.get()
        objFile = askopenfilename(title=self.trad['Select OBJ file:'][self.language_box_index.get()], filetypes= [('object files', '.obj'), ('all files', '.*')], initialdir=self.defaultDir)
        if file != None:
            entry.delete(0, END)
            entry.insert(0, objFile)
        if entry.get() == '':
            entry.delete(0, END)
            entry.insert(0, currentEntry)

    def disableEntry(self):
        if self.use_water.get() == 0:
            self.wObjEntry.configure(state='disabled')
            self.selectwObjBt.configure(state='disabled')
        else:
            self.wObjEntry.configure(state='normal')
            self.selectwObjBt.configure(state='normal')

    def disableRaster(self):
        if self.version_var.get() == 9:
            self.rasterEntry.configure(state='disabled')
            self.selectRasterBt.configure(state='disabled')
        else:
            self.rasterEntry.configure(state='normal')
            self.selectRasterBt.configure(state='normal')        
        

    def selectWobj(self):
        entry = self.wObjEntry
        currentEntry = entry.get()
        objFile = askopenfilename(title=self.trad['Select OBJ file (water area):'][self.language_box_index.get()], filetypes= [('object files', '.obj'), ('all files', '.*')], initialdir=self.defaultDir)
        if file != None:
            entry.delete(0, END)
            entry.insert(0, objFile)
        if entry.get() == '':
            entry.delete(0, END)
            entry.insert(0, currentEntry)            

    def insertPatchFile(self):
        entry = self.dsfInsertPatchEntry
        currentEntry = entry.get()
        objFile = askopenfilename(title=self.trad['Select GAP file:'][self.language_box_index.get()], filetypes= [('gap files', '.gap'), ('all files', '.*')], initialdir=self.defaultDir)
        if file != None:
            entry.delete(0, END)
            entry.insert(0, objFile)
        if entry.get() == '':
            entry.delete(0, END)
            entry.insert(0, currentEntry)
        else:
            self.textList()

    def textList(self):
        # decompress file
        data = gzip.open(self.dsfInsertPatchEntry.get(),'r')
        terList = False
        terListIni = False
        lista = []
        offset = self.ter_list_offset
        offset.set(0)
 
        while terList == False:
            linha = data.readline()
            if linha[:11] == 'TERRAIN_DEF':
                terrain = linha.split()[1]
                try:
                    terrain = terrain.split('/')[-1]
                    terrain = terrain.split('.')[0]
                except:
                    pass
                if terrain == 'terrain_Water':
                    offset.set(1)
                else:
                    lista.append(terrain)
                terListIni = True
            else:
                if terListIni == True:
                    terList = True
        
        self.box2['values'] = tuple(lista)
        self.box2.current(0)
        resolution = '30'
        self.resEntry.delete(0, END)
        self.resEntry.insert(0, resolution)
        self.terrain_box_index.set(offset.get())

    def chooseTer(self, event):
        terrain = self.box2.get()
        offset = self.ter_list_offset.get()
        self.terrain_box_index.set(self.box2['values'].index(terrain)+offset)
        
    def concluido(self, mensagem):
        showinfo("Mesh Remexe", mensagem)
        self.progressText.set('')
        self.progress["value"] = 0

    def fechar(self):
        self.saveIni()
        self.raiz.destroy()

    # Barra de progresso
    def progressBarUpdate(self, texto, valorAtual, valorMaximo):
        self.progressText.set(texto)
        self.progress["maximum"] = valorMaximo
        self.progress["value"] = valorAtual
        #time.sleep(0.05)
        #self.raiz.update_idletasks()
        self.raiz.update()
        
    def coord2Dec(self, texto):
        a = texto.split()
        if len(a) == 3:
            coordDec = abs(float(a[0]))+(float(a[1])/60)+(float(a[2])/3600)
        elif len(a) == 2:
            coordDec = abs(float(a[0]))+(float(a[1])/60)
        else:
            coordDec = abs(float(a[0]))
        if a[0][:1] == '-':
            coordDec *= -1
        return coordDec

    #################################################################################

    def combinePhyPatch(self, extracted_lst):
        mesh_phy = []
        mesh_sea = []
        writeFile = False
        for linha in extracted_lst:
            if linha[:9] == "END_PATCH":
                writeFile = False
            elif writeFile == True:
                if writeTer == True:
                    mesh_phy.append(linha)
                else:
                    mesh_sea.append(linha)
            elif linha[:11] == "BEGIN_PATCH" and linha.split()[4] == '1' and linha.split()[1] != '0':
                writeFile = True
                writeTer = True
            elif linha[:11] == "BEGIN_PATCH" and linha.split()[4] == '1' and linha.split()[1] == '0':
                writeFile = True
                writeTer = False
        return(mesh_phy, mesh_sea)

    def combineWtrPatch(self, extracted_lst):
        mesh_wtr = []
        writeFile = False
        for linha in extracted_lst:
            if linha[:9] == "END_PATCH":
                writeFile = False
            if writeFile == True:
                mesh_wtr.append(linha)
            if linha[:11] == "BEGIN_PATCH 0" and linha.split()[4] == '1':
                writeFile = True
        return(mesh_wtr)    

    # retorna indice do patch, inicio e fim do primitve
    def primVerts(self, indice):
        iniPri = indice
        endPri = indice
        iniPat = indice
        indiceList = []
        while self.arquivo[iniPri][:9] != "BEGIN_PRI":
                iniPri -= 1
        while self.arquivo[endPri][:9] != "END_PRIMI":
                endPri += 1
        while self.arquivo[iniPat][:9] != "BEGIN_PAT":
                iniPat -= 1
        return (iniPat, iniPri, endPri)

    # retorna texto BEGIN/END primitivecom, incluindo patch
    def storeVert(self, a):
        listVert = ""
        listVert += self.arquivo[a[0]]
        for i in range(a[2] - a[1]):
                listVert += self.arquivo[a[1]+i]
        listVert += "END_PRIMITIVE\n"
        listVert += "END_PATCH"
        return listVert

    ############################## Funcao corrigir elevacao ##############################
    def fixElevation(self, mesh_fix_list):

        # Largura e altura do arquivo raster.
        rastHeight = 1201
        rastWidth = 1201

        # Arquivo raster
        rastName = self.rasterEntry.get()

        # Carrega no formato binario
        RASTIN = open(rastName,'rb')

        # Extrai a informaoes de elevacao
        elevRast = [[0 for x in xrange(rastWidth)] for x in xrange(rastHeight)]
        incCount = 1
        for i in range(rastWidth):
            for j in range(rastHeight):
                elevRast[i][j] = unpack('<h', RASTIN.read(2))[0]

            # Barra de progresso
            if i >= (rastWidth/100)*incCount:
                self.progressBarUpdate(self.trad['(3/6) loading elevation info.'][self.language_box_index.get()], i, rastWidth)
                incCount += 1
                
        # Fecha arquivo
        RASTIN.close()

        # Inicializa a lista dos meshs corrigidos
        mesh_fix_names = []

        # Total da barra de progresso
        tamanho  = 0
        for mesh in mesh_fix_list:
            tamanho += len(mesh)

        inc = 0
        incCount = 1
        # Corrige cada item da lista        
        for mesh_fix in mesh_fix_list:
            # Inicializa o offset
            lonRef = 0
            latRef = 0

            # Calcula offset
            sair = 0

            for i in range(len(mesh_fix)):
                a = mesh_fix[i].split()
                if len(a) > 3:
                    if a[0] == "PATCH_VERTEX":
                        # converte de string para float
                        b = float(a[1])
                        # verifica se a coordenada eh negativa e cria um complento
                        if b < 0:
                            hemis = 1
                        else:
                            hemis = -1
                        # verifica se a coordenada estah no limite superior
                        if b % 1 == 0:
                            lonRef = int(b)+hemis
                        else:
                            lonRef = int(b)
                        b = float(a[2])
                        if b % 1 == 0:
                            latRef = int(b)+hemis
                        else:
                            latRef = int(b)
                        sair = 1
                        break
                if sair == 1:
                    break

            # Cria copia do arquivo com as elevaoes corrigidas
            fileFixName = []

            # Contador de linhas substituidas
            count = 0

            # Substitui as informacoes de elevacao
            for i in range(len(mesh_fix)):
                a = mesh_fix[i].split()
                if len(a) > 3:
                    
                    try:
                        elevacao = float(a[3])
                    except:
                        elevacao = 0
                        
                    if elevacao == -32768.0:
                        count += 1
                        lon = float(a[1])
                        lat = float(a[2])
                        if lon < 0:
                            lonIndex = (rastWidth+1.5)+(lon - lonRef)*(rastWidth+1.5)
                        else:
                            lonIndex = (rastWidth+1.5)-(lon - lonRef)*(rastWidth+1.5)
                        if lat < 0:
                            latIndex = (rastHeight+1)+(lat - latRef)*(rastHeight+1)
                        else:
                            latIndex = (lat - latRef)*(rastHeight+1)
                            
                        # Calcula a ponto da elevacao pelo metodo center post
                        if lonIndex%1 < .5:
                            lon1 = int(lonIndex)-.5
                            lon2 = int(lonIndex)+.5
                        else:
                            lon1 = int(lonIndex)+.5
                            lon2 = int(lonIndex)+1.5
                        if latIndex%1 < .5:
                            lat1 = int(latIndex)-.5
                            lat2 = int(latIndex)+.5
                        else:
                            lat1 = int(latIndex)+.5
                            lat2 = int(latIndex)+1.5

                        if lat2 > 1200:
                            lat1 = 1199
                            lat2 = 1200
                        if lon2 > 1200:
                            lon1 = 1199
                            lon2 = 1200

                        # define os 4 pontos para o calculo bilinear
                        fourPoints = [[lat1,lon1,elevRast[int(lat1)][int(lon1)]],
                                  [lat2,lon1,elevRast[int(lat2)][int(lon1)]],
                                  [lat1,lon2,elevRast[int(lat1)][int(lon2)]],
                                  [lat2,lon2,elevRast[int(lat2)][int(lon2)]]]
                        # Calcula a nova elevacao pelo metodo bilinear
                        elev =  self.bilinear_interpolation(latIndex, lonIndex, fourPoints)
                        
                        a[3] = '%.9f' % elev
                        
                        novaLinha = ''
                        for j in range(len(a)):
                            novaLinha = novaLinha + '%s ' % a[j]
                        mesh_fix[i] = novaLinha+'\n'

                
                if inc >= ((tamanho/100)*incCount):
                    self.progressBarUpdate(self.trad['(4/6) Fixing elevations.'][self.language_box_index.get()], inc, tamanho)
                    incCount += 1
                inc += 1

            mesh_fix_names.append(mesh_fix)
        return(mesh_fix_names)
        
    def bilinear_interpolation(self, x, y, points):
        points = sorted(points)               # order points by x, then by y
        (x1, y1, q11), (_x1, y2, q12), (x2, _y1, q21), (_x2, _y2, q22) = points
        return (q11 * (x2 - x) * (y2 - y) +
            q21 * (x - x1) * (y2 - y) +
            q12 * (x2 - x) * (y - y1) +
            q22 * (x - x1) * (y - y1)
           ) / ((x2 - x1) * (y2 - y1) + 0.0)


    ############################## Funcao Mesh 2 Obj ##############################
    def mesh2Obj(self, mesh_fix_list):

        mesh_obj_list = []

        fracao = 100/len(mesh_fix_list)/2
        cur_progress = 0
        progress = 0
        inc = 0        

        for mesh_fix in mesh_fix_list:
            
            mesh_obj = []

            lst = []
            for line in mesh_fix:
                if line[:9] == "BEGIN_PRI" or line[:9] == "PATCH_VER" or line[:9] ==  "END_PRIMI":
                    lst.append(line)

            triangle_sflag = "off"
            triangle_lflag = "off"
            triangle_fflag = "off"

            self.vertices = []
        
            # gerar lista de vertices
            # http://scenery.x-plane.com/library.php?doc=dsfspec.php
            
            # http://wiki.x-plane.com/DSFTool_manual
            # BEGIN_PRIMITIVE <type>
            #0 - Triangles
            #1 - Triangle Strip
            #2 - Triangle Fan
            
            #0 - Triangles must have clockwise rotation.
            #1 - A triangle strip is a series of adjacent triangles that share two common vertices;
            # for a series of points 1,2,3,4,5 as a triangle strip is equivalent to the triangles 123,243,345...
            #2 - A triangle fan is a series of adjacent triangles that share two common vertices;
            # for a series of points 1,2,3,4,5 as a triangle fan is equivalent to the triangles 123,134, 145...
            
            counter = 1.0
            for i in range(len(lst)):
                if lst[i][:-3] == "BEGIN_PRIMITIVE":
                    # verifica se eh lista de triangulos
                    if lst[i][16:17] == "0":
                        triangle_lflag = "on"
                    # verifica se eh fan de triangulos
                    elif lst[i][16:17] == "2":
                        triangle_fflag = "on"
                        triangleFan = []
                    # ou string de triangulos
                    else:
                        triangle_sflag = "on"
                        triangleStrip = []

                if lst[i] == "END_PRIMITIVE\n":
                    if triangle_lflag == "on":
                        triangle_lflag = "off"
                    elif triangle_fflag == "on":
                        self.printTriangleFan(triangleFan)
                        triangle_fflag = "off"
                    else:
                        self.printTriangleStrip(triangleStrip)
                        triangle_sflag = "off"
                if lst[i][:12] == "PATCH_VERTEX":
                    if triangle_lflag == "on":
                        self.gravaLinha(lst[i])
                    elif triangle_fflag == "on":
                        triangleFan.append(lst[i])
                    else:
                        triangleStrip.append(lst[i])

                # Barra de progresso
                counter += 1.0
                progress  = int(((counter/len(lst))*fracao)+(fracao*inc))
                if progress != cur_progress:
                    self.progressBarUpdate(self.trad['(5/6) Indexing.'][self.language_box_index.get()], progress, 100)
                    cur_progress = progress
            inc += 1


            # lista vertices unicos
            counter=Counter(self.vertices)
            b = counter.keys()

            # grava cabecalho
            #mesh_obj.append("""I\n800\nOBJ\n\nTEXTURE\timage_ref.png\nPOINT_COUNTS\t%d 0 0 %d\n\n""" % (len(b), len(self.vertices)))
            mesh_obj.append('I\n800\nOBJ\n\n')
            mesh_obj.append('TEXTURE\t\n')
            mesh_obj.append('POINT_COUNTS\t%d 0 0 %d\n\n' % (len(b), len(self.vertices)))
            # grava lista de vertices
            for i in b:
                mesh_obj.append(i)

            # pula linha
            mesh_obj.append("\n")

            # prepara lista de indices
            indice = []

            # acumula indice
            #incCount = 1
            counter = 1.0
            for i in range(len(self.vertices)):
                # verifica cada vertice onde estah na lista de vertices unicos
                for j in range(len(b)):
                    if self.vertices[i] == b[j]:
                        indice.append(j)
                        break

                # Barra de progresso
                #if i >= (len(self.vertices)/100)*incCount:
                #    step = ((float(i)/len(self.vertices))*(100/2.0))+(100/2)
                    # texto: organizando índices
                #    self.progressBarUpdate('(4/5) '+self.dicionario[self.language_box_index.get()][44], step, 100)
                #    incCount += 1

                counter += 1.0
                progress  = int(((counter/len(self.vertices))*fracao)+(fracao*inc))
                if progress != cur_progress:
                    self.progressBarUpdate(self.trad['(5/6) Indexing.'][self.language_box_index.get()], progress, 100)
                    cur_progress = progress
            inc += 1

                

            # indice com 10 posicoes
            for i in range(len(indice)/10):
                mesh_obj.append("IDX10 ")
                for j in range(10):
                    mesh_obj.append("%d " % (indice[(i*10)+j]))
                mesh_obj.append("\n")

            # complemento do indice
            for i in range(len(indice)%10):
                mesh_obj.append("IDX %d\n" % indice[(len(indice)/10)*10+i])

            # pula mais uma linha
            mesh_obj.append("\n")

            # grava rodapeh
            mesh_obj.append("\nTRIS 0 %d\n" % len(self.vertices))

            mesh_obj_list.append(mesh_obj)
        return(mesh_obj_list)
        
    # funcao para gerar lista de vertices a partir de triangle strip
    # criando triangulos no sentido hoario
    def printTriangleStrip(self, lista):
        # Os dois primeiros triangulos sao definidos manualmente
        self.gravaLinha(lista[0])
        self.gravaLinha(lista[1])
        self.gravaLinha(lista[2])
        self.gravaLinha(lista[1])
        self.gravaLinha(lista[3])
        self.gravaLinha(lista[2])
        # Do terceiro em diante, o algoritmo consegue resolver
        for i in range(3, len(lista)-1):
            self.gravaLinha(lista[i])
            self.gravaLinha(lista[(i-1)+(i%2)*2])
            self.gravaLinha(lista[(i+1)+(i%2)*-2])

    def printTriangleFan(self, lista):
        for i in range(len(lista)-2):
            self.gravaLinha(lista[0])
            self.gravaLinha(lista[i+1])
            self.gravaLinha(lista[i+2])

    # formata e armazena os vertices numa lista
    def gravaLinha(self, linhaDsf):
        a = linhaDsf.split()
        b = float(a[1])*100000
        c = float(a[3])
        d = float(a[2])*-100000
        try:
            e = float(a[6])
        except:
            e = 0
        try:
            f = float(a[7])
        except:
            f = 0            
        self.vertices.append("VT %.4f  %.4f  %.4f  0.0001  0.0001  0.0001  %.4f  %.4f\n" %(b,c,d,e,f))

    ############################## Funcao Obj 2 Mesh ##############################
    def obj2Mesh(self, objList):
        convertList = []
        
        fracao = 100/len(objList)
        cur_progress = 0
        progress = 0
        inc = 0

        for objName in objList:
            meshList = []

            # inicializa lista de vertices
            listaVert = []
            # inicializa indice de vertices
            idx = []

            # Carrega o conteudo para uma lista
            for line in objName:
                # verifica se a linha nao estah em branco
                if len(line) > 1:
                    # divide a informacao e armazena numa lista
                    a = line.split()
                    # Verifica se a linha contem vertices
                    if a[0] == 'VT':
                        listaVert.append(line)
                    # Verifica se tem indice 10
                    if a[0] == 'IDX10':
                        for i in range(1, 11):
                            idx.append(a[i])
                    # verifica indice unico
                    if a[0] == 'IDX':
                        idx.append(a[1])

            # Sintaxe do header dos patchs
            # BEGIN_PATCH <primitive type> <near LOD> <far LOD> <flags> <# point coords>
        
            # Escreve cabecalho
            meshList.append('BEGIN_PRIMITIVE 0\n')
            # Escreve corpo
            counter = 1.0
            for i, indice in enumerate(idx):
                a = listaVert[int(indice)].split()
                lat = (float(a[3])/100000)*-1
                lon = float(a[1])/100000
                alt = float(a[2])
                s = float(a[7])
                t = float(a[8])
                
                if s > 0 or s > 1:
                    s = s%1
                if t > 0 or t > 1:
                    t = t%1

                # escreve linha
                # meshList.append('PATCH_VERTEX %.9f %.9f %.9f -0.000015259 -0.000015259 %.9f %.9f\n' % (lon, lat, alt, s, t%1))
                meshList.append('PATCH_VERTEX %.9f %.9f %.9f -0.000015259 -0.000015259\n' % (lon, lat, alt))


                counter += 1.0
                progress  = int(((counter/len(idx))*fracao)+(fracao*inc))
                if progress != cur_progress:
                    self.progressBarUpdate(self.trad['(2/6) Converting OBJ to mesh.'][self.language_box_index.get()], progress, 100)
                    cur_progress = progress
            inc += 1
                
            # escreve rodape
            meshList.append('END_PRIMITIVE\n')

            convertList.append(meshList)
        return(convertList)

    def insertPatch(self):

        # Carrega OBJ
        f = open(self.objEntry.get(), 'r')
        obj = f.readlines()
        f.close()

        # Carrega sea_OBJ
        if self.use_water.get() == 1:
            f = open(self.wObjEntry.get(), 'r')
            wObj = f.readlines()
            f.close()
            insertWpatch = False
        else:
            insertWpatch = True
            wObj = []

        # decompress file
        #with gzip.open(self.dsfInsertPatchEntry.get(),'rb') as f:
        #    file_with_gap = f.read()
        #f.close()
        #file_with_gap = file_with_gap.split('\n')

        file_with_gap = []

        # decompress file
        data = gzip.open(self.dsfInsertPatchEntry.get(),'r')
        tamanho = int(data.readline())
        incCount = 1
        for i in range(tamanho):
        #while True:
            linha = data.readline()
            if linha == '':
                break
            file_with_gap.append(linha)
            #print linha
            if i >= (tamanho/100)*incCount:
                # texto: escrevendo vértices.
                self.progressBarUpdate(self.trad['(1/6) Unzipping file.'][self.language_box_index.get()], i, tamanho)
                incCount += 1
        
        # Area de seleção
        area_sel = file_with_gap.pop(0)
        # Cabeçalho
        version = file_with_gap.pop(0)
        version = int(version.split('=')[1])
        
        # Lista de elevações a preservar
        preservLst = []        
        self.version_var.set(version)        
        # Lista de vértices a preservar
        for i in range(len(file_with_gap)):
            if file_with_gap[i] == 'END_PRESERV_LST\n':
                del file_with_gap[:i+1]
                break
            elif file_with_gap[i][:7] == 'PR_LIST':
                vt = file_with_gap[i].split()
                preservLst.append([float(vt[1]),float(vt[2]),float(vt[3])])

        # Lista de vértices com cores a preservar
        outlineWtr = []        
        for i in range(len(file_with_gap)):
            if file_with_gap[i] == 'END_SEA_COLOR\n':
                del file_with_gap[:i+1]
                break
            elif file_with_gap[i][:8] == 'VT_COLOR':
                vt = file_with_gap[i].split()
                outlineWtr.append([float(vt[1]),float(vt[2]),float(vt[3])])
        
        # Adiciona terrain Water se estiver inserindo água em uma área que antes não existia.
        if self.use_water.get() == 1:
            found_terrain = 0
            contains_water = 0
            first_terrain = 1000
            for i in range(len(file_with_gap)):
                if file_with_gap[i][:11] == 'TERRAIN_DEF':
                    if i < first_terrain:
                        first_terrain = i
                    found_terrain = 1
                    a = file_with_gap[i].split()
                    if a[1] == 'terrain_Water':
                        contains_water = 1
                        break
                if file_with_gap[i][:11] != 'TERRAIN_DEF' and found_terrain == 1:
                    break
            if contains_water == 0 and found_terrain == 1:
                file_with_gap.insert(first_terrain, 'TERRAIN_DEF terrain_Water\n')
                for i in range(len(file_with_gap)):
                    if file_with_gap[i][:11] == 'BEGIN_PATCH':
                        a = file_with_gap[i].split()
                        a[1] = '%s' % (int(a[1])+1)
                        linha = ''
                        for item in a:
                            linha += item+' '
                        file_with_gap[i] = linha[:-1]+'\n'
                new_index = self.terrain_box_index.get() + 1
                self.terrain_box_index.set(new_index)

        # Converte OBJ em mesh
        meshList, meshWlist = self.obj2Mesh([obj, wObj])
        if self.version_var.get() == 10:
            # combina com o mesh default
            meshList, meshWlist = self.blendElev([meshList, meshWlist], area_sel, preservLst)
        # Otimiza os arquivos convertendo em strip triangles
        meshList, meshWlist = self.writeStripList([meshList, meshWlist])
        # Otimiza a cor da agua copiando os valores dos vérices externos
        if self.version_var.get() == 10:
            meshWlist = self.insertColor(meshWlist, outlineWtr)

        # lista com os arquivos mesclados
        file_inserted = []
        insertedPatch = False
        insertedPatch1 = False
        insertedPatch2 = False

        terIndex = self.terrain_box_index.get()
        terRes = float(self.resEntry.get())

        mesh_inserted = open(self.dsfInsertPatchEntry.get()[:-4]+"_mesh_inserted.txt",'w')

        incCount = 1
        
        lstSize = len(file_with_gap)
        #patchBeginRef2 = patchBeginRef.split()
        
        for i in xrange(lstSize):
            if file_with_gap[i][:11] == 'BEGIN_PATCH':
                patchHeader = file_with_gap[i].split()
                
                # Patch Água
                if int(patchHeader[1]) == (0 or 1) and insertWpatch == False:
                    # X-Plane 10
                    if self.version_var.get() == 10:
                        mesh_inserted.write("BEGIN_PATCH 0 0.000000 -1.000000 1 7\n")
                        for linha in meshWlist:
                            mesh_inserted.write(linha)
                    # X-Plane 9
                    else:
                        mesh_inserted.write("BEGIN_PATCH 0 0.000000 -1.000000 1 6\n")
                        for linha in meshWlist:
                            if linha[:12] == 'PATCH_VERTEX':
                                mesh_inserted.write(linha[:-1]+' 1.000000000\n')
                            else:
                                mesh_inserted.write(linha)
                    insertWpatch = True

                # Patch físico
                elif insertedPatch1 == False and (int(patchHeader[1]) >= terIndex and patchHeader[5] == '5'):
                    mesh_inserted.write("BEGIN_PATCH %s 0.000000 -1.000000 1 5\n" % terIndex)
                    for linha in meshList:
                        mesh_inserted.write(linha)
                    insertedPatch1 = True
                    mesh_inserted.write('END_PATCH\n')
                    mesh_inserted.write(file_with_gap[i])

                # Patch de textura
                elif insertedPatch2 == False and ((int(patchHeader[1]) >= terIndex and patchHeader[5] == '7') \
                                                   or (int(patchHeader[1]) > terIndex+1 and patchHeader[5] == '5')):
                    mesh_inserted.write("BEGIN_PATCH %s 0.000000 40000.000000 2 7\n" % terIndex)
                    # Inserir textura
                    for linha in meshList:
                        if linha[:12] == 'PATCH_VERTEX':
                            terResMod = 1.0/60/1852*terRes
                            linhaTex = linha.split()
                            x = (float(linhaTex[2])%terResMod)/terResMod
                            x = ' %.9f' % x
                            y = (float(linhaTex[1])%terResMod)/terResMod
                            y = ' %.9f' % y
                            mesh_inserted.write(linha[:-1]+x+y+'\n')
                        else:
                            mesh_inserted.write(linha)
                    mesh_inserted.write('END_PATCH\n')
                    mesh_inserted.write(file_with_gap[i])
                    insertedPatch2 = True
                else:
                    mesh_inserted.write(file_with_gap[i])
                    
            else:
                mesh_inserted.write(file_with_gap[i])
            if i >= (lstSize/100)*incCount:
                # texto: escrevendo vértices.
                self.progressBarUpdate(self.trad['(6/6) Inserting mesh.'][self.language_box_index.get()], i, lstSize)
                incCount += 1
                
        mesh_inserted.close()
            
        # mensagem de finalizacao
        if insertedPatch1 == True and insertedPatch2 == True: 
            # texto: patch inserido com sucesso.
            mensagem = self.trad['Mesh successfully updated.'][self.language_box_index.get()]
            self.concluido(mensagem)
        else:
            # texto: nenhum patch foi inserido.
            mensagem = self.trad['Nothing to insert.'][self.language_box_index.get()]
            self.concluido(mensagem)

    def printLog(self, filename, lista):
        f = open(filename, 'w')
        for linha in lista:
            try:
                f.write('%s' % linha)
            except:
                str1 = ''.join(str(e)+',' for e in linha)
                f.write('%s\n' % str1[:-1])   
        f.close()

    def insertColor(self, meshWlist, outlineWtr):

        incCount = 1
        if outlineWtr == []:
            outlineWtr.append([0.0,0.0,0.2]) 
        for i in range(len(meshWlist)):
            if meshWlist[i][:12] == 'PATCH_VERTEX':
                vt = meshWlist[i].split()
                a = Point(float(vt[1]), float(vt[2]))
                nearVt = outlineWtr[0]
                dist = (a.distance(Point(outlineWtr[0][0],outlineWtr[0][1])))
                for j in range(len(outlineWtr)):
                    newDist = a.distance(Point(outlineWtr[j][0],outlineWtr[j][1]))
                    if newDist <= dist:
                        nearVt = outlineWtr[j]
                        dist = newDist
                    if dist == 0:
                        break
                meshWlist[i] = meshWlist[i][:-1]+' %.9f 1.000000000\n' % nearVt[2]
            if i >= (len(meshWlist)/100)*incCount:
                # texto: setting water color.
                self.progressBarUpdate(self.trad['(5/6) Setting water color.'][self.language_box_index.get()], i, len(meshWlist))
                incCount += 1
        return(meshWlist)

    # Recebe duas listas (string e strip), devolve uma lista com os cabeçalhos adequados.
    def createPrimitive(self, stripList, stringList):
        finalList = []
        for strip in stripList:
            finalList.append('BEGIN_PRIMITIVE 1\n')
            for linha in strip:
                if linha[:12] == 'PATCH_VERTEX':
                    finalList.append(linha)
                else:
                    finalList.append('PATCH_VERTEX '+linha[0]+' '+linha[1]+' %.9f' % random.random()+' -0.000015259 -0.000015259\n')
            finalList.append('END_PRIMITIVE\n')
        finalList.append('BEGIN_PRIMITIVE 0\n')
        for triangle in stringList:
            for linha in triangle:
                if linha[:12] == 'PATCH_VERTEX':
                    finalList.append(linha)
                else:
                    finalList.append('PATCH_VERTEX '+linha[0]+' '+linha[1]+' %.9f' % random.random()+' -0.000015259 -0.000015259\n')
        finalList.append('END_PRIMITIVE\n')
        return(finalList)

    # Recebe uma string de triângulos e devolve duas listas,
    # uma com strip e outra com o restante de strings
    def iniStrip1(self, stringList):
        x, y = 0, 0
        vert1 = []
        vert2 = []
        vert3 = []
        vert4 = []
        foundFlag = False
        for i in range(len(stringList)):
            for j in range(len(stringList)):
                tupla_i = self.extLatLon(stringList[i])
                tupla_j = self.extLatLon(stringList[j])
            
                if tupla_i[:2] == ([ tupla_j[0],  tupla_j[2]] or [ tupla_j[2],  tupla_j[0]]) and i != j:
                    vert1 = stringList[i][2]
                    vert2 = stringList[i][0]
                    vert3 = stringList[i][1]
                    vert4 = stringList[j][1]
                    foundFlag = True
                    x, y = i, j
                    break
          
                elif  tupla_i[:2] == ([tupla_j[0],  tupla_j[1]] or [ tupla_j[1],  tupla_j[0]]) and i != j:
                    vert1 = stringList[i][2]
                    vert2 = stringList[i][0]
                    vert3 = stringList[i][1]
                    vert4 = stringList[j][2]
                    foundFlag = True
                    x, y = i, j
                    break            
          
                elif  tupla_i[:2] == ([ tupla_j[1],  tupla_j[2]] or [ tupla_j[2],  tupla_j[1]]) and i != j:
                    vert1 = stringList[i][2]
                    vert2 = stringList[i][0]
                    vert3 = stringList[i][1]
                    vert4 = stringList[j][0]
                    foundFlag = True
                    x, y = i, j
                    break            
            if foundFlag == True:
                break

        if foundFlag == True:
            if y > x:
                del stringList[y]
                del stringList[x]

            else:
                del stringList[x]
                del stringList[y]

            if (vert1 and vert2 and vert3 and vert4) != []:
                stripList = [vert1, vert2, vert3, vert4]
        else:
            stripList = None
        return (stripList, stringList)

    # Recebe uma lista com 3 linhas de texto e
    # devolve uma lista com 3 tuplas de coordenadas
    def extLatLon(self, stringList):
        coordList = []
        for i in range(len(stringList)):
            a, b = stringList[i].split()[1], stringList[i].split()[2]
            coordList.append((a,b))
        return(coordList)

    # Encontra, dentro da lista de strings, o próximo vértice que compõe a strip.
    # Devolve as listas atualizadas
    def findNext(self, stripList, stringList):
        tupStrip = self.extLatLon(stripList)
        for i in range(len(stringList)):
            tupString = self.extLatLon(stringList[i])
            if tupStrip[-2:] == ([tupString[0], tupString[1]] or [tupString[1], tupString[0]]):
                stripList.append(stringList[i][2])
                del stringList[i]
                break
            elif tupStrip[-2:] == ([tupString[1], tupString[2]] or [tupString[2], tupString[1]]):
                stripList.append(stringList[i][0])
                del stringList[i]
                break
            elif tupStrip[-2:] == ([tupString[2], tupString[0]] or [tupString[0], tupString[2]]):
                stripList.append(stringList[i][1])
                del stringList[i]
                break
        return (stripList, stringList)

    # Cria uma lista de tuplas com 3 linhas
    def string2list(self, lista):
        stringList = []
        for linha in lista:
            if linha[:12] == 'PATCH_VERTEX':
                a.append(linha)
            if len(a) == 3:
                stringList.append(a)
                a = []
        return(stringList)

    # Recebe a lista de vertices de uma string list e retorna uma lista com Strips e String lists.
    def writeStripList(self, lista_names):

        fracao = 100/len(lista_names)
        cur_progress = 0
        progress = 0
        inc = 0  

        strip_names = []
        counter = 1.0
        for lista in lista_names:
            polygon = []
            stringList = []
            gap = 0
            for linha in lista:
                if linha[:12] == 'PATCH_VERTEX':
                    polygon.append(linha)
                    if len(polygon) == 3:
                        stringList.append(polygon)
                        polygon = []
            a = []

            counter = 1.0
            while True:
                #=======================
                counter += 1.0
                progress  = int(((counter/10)*fracao)+(fracao*inc))
                if progress != cur_progress:
                    self.progressBarUpdate(self.trad['(4/6) Indexing triangles strips'][self.language_box_index.get()], progress, 100)
                    cur_progress = progress
                #=======================
                size = len(a)
                stripList, stringList = self.iniStrip1(stringList)
                if stripList != None:
                    a.append(stripList)
                    stripListNew = list(a[-1])
                while True:
                    if stripList != None:
                        stripListNew, stringList = self.findNext(stripListNew, stringList)
                        if a[-1] == stripListNew:
                            break
                        else:
                            a[-1] = list(stripListNew)
                            stripList = list(stripListNew)
                    else:
                        break
                if size == len(a):
                    break
            inc += 1
            strip_names.append(self.createPrimitive(a,stringList))
        self.progressBarUpdate(self.trad['(4/6) Indexing triangles strips'][self.language_box_index.get()], 100, 100)
        return(strip_names)

inst1=Tk()
inst1.iconbitmap('mesh.ico')
Griding(inst1)
inst1.mainloop()
