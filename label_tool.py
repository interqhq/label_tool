#!/usr/bin  python

'''
Read images
label with left button, and correct it with right button
a for previous image
d for next image
detect the skin region,rectangle the regioin
save the region info

@kst_lable_tool1

@gdk
@2014-05-07
'''

import os
import cv2
import numpy as np
import string

extl = ['.jpg', '.jpeg', '.png']


'''
def kst_draw_img(src_img, pt_list):
    for pt0 in pt_list:
        cv2.circle(src_img,pt0, 2,blue,1) 
    cv2.imshow('src', src_img)
'''   

class CLabel:
    def __init__(self):
        self.pt = [-1,-1]
        self.chg_pt = [-1,-1]
        self.imgdict = {}
        self.imglist = []
        self.infolist = []
        self.infoname = ''
        self.cur_index = 0
        self.num       = 0
        self.pos       = []
        self.blue      = (255, 0, 0)
        self.red       = (0,0,255)
        self.fs        = None

    def cmp_near_pt(self, m_pt, pts):
        if len(pts) < 1:
            return (-1,-1)
        index = 0
        i     = 0
        l_pt = pts[0]
        min_d    = 200
        for i,pt in enumerate(pts):
            d = abs(pt[0] - m_pt[0]) + abs(pt[1] - m_pt[1])
            if d < min_d:
                index = i
                min_d = d
                
        return l_pt, index

    def onmouse(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            self.chg_pt = [-1,-1]
            self.pt = [-1,-1]
            x, y = np.int16([x,y])
            self.pt = [x,y]
        if event == cv2.EVENT_RBUTTONDOWN:
            self.chg_pt = [-1,-1]
            self.pt = [-1,-1]
            x, y = np.int16([x,y])
            self.chg_pt = [x,y]

    def draw_rect(self, pts):
        minx = 0
        maxx = 0
        miny = 0
        maxy = 0
        if len(pts) > 2:
            nparr = np.array(pts)
            npx   = nparr[:,0]
            npy   = nparr[:,1]
            minx  = np.min(npx)
            maxx  = np.max(npx)
            miny  = np.min(npy)
            maxy  = np.max(npy)
        return (minx, miny), (maxx, maxy)

    def run(self):
        cur_index = 0
        log = open('log.txt', 'a+')
        while len(self.imglist) > 0:
            log.write('cur_idx %d\t' % (cur_index))
            log.fflush()
            pts = []
            nn = self.imglist[cur_index]
            p,n = os.path.split(nn)
            title,ext = n.split('.')

            log.write('name: %s\t, title: %s\n' % (nn, title))
            lgo.fflush()
            
            img = cv2.imread(nn, 1)

            # if title not in keys ,then push
            if title not in self.imgdict.keys():
                self.imgdict.setdefault(title)
            else:
                pts = self.imgdict[title]
            
            for pt0 in pts:
                cv2.circle(img, tuple(pt0), 2,self.blue,1) 
            cv2.imshow('src', img)

            cv2.setMouseCallback('src', self.onmouse)

            if self.pt[0] > 0 and self.pt[1] > 0:
                pts.append(self.pt)
                cv2.circle(img, tuple(self.pt), 2, self.blue,1) 
                log.write('pt: (%d,%d)\t' % (self.pt))
                log.fflush()

            if self.chg_pt[0] > 0 and self.chg_pt[1] > 0:
                self.pt,idx = self.cmp_near_pt(self.chg_pt, pts)
                cv2.circle(img, tuple(self.chg_pt), 2, self.red,1) 
                pts[idx] = self.chg_pt
                log.write('pt: (%d,%d)\t' % (self.pt))
                log.fflush()

            if len(pts) > 2:
                pt1,pt2 = self.draw_rect(pts)
                cv2.rectangle(img, pt1,pt2, self.blue) 

            cv2.imshow('src', img)
            log.write('show img1\n')
            log.fflush()
            
            self.imgdict[title] = pts
            
            self.pt = [-1,-1]
            self.chg_pt = [-1,-1]

            ch = cv2.waitKey(10)
            #print ch
            if ch == ord('a'):
                cur_index -= 1
                if cur_index < 0:
                    cur_index = len(self.imglist) - 1
            if ch == ord('d'):
                cur_index += 1
                if cur_index == len(self.imglist):
                    cur_index = 0
            if ch == ord('c'):
                pts = []
                self.imgdict[title] = pts
            if ch == 27:
                #for key in self.imgdict.keys() if key != 'ext':
                self.fs.seek(0)
                a = self.fs.tell()
                a = self.fs.truncate(0)
                for key in self.imgdict.keys():
                    if key == 'ext':
                        continue
                    if len(self.imgdict[key]) == 0:
                        continue
                    self.fs.write('%s.%s' % (key, self.imgdict['ext']))
                    for ii in self.imgdict[key]:
                        for i in ii:
                            self.fs.write(' %s' % str(i))
                    self.fs.write('\n')
                #self.fs.flush()
                self.fs.close()
                break

        cv2.destroyAllWindows()

    def dict_from_file(self):
        self.fs.seek(0)
        for ln in self.fs:
            nm,nu = ln.split('g')
            title, ext = nm.split('.')
            strnu = nu.split()
            cord = []
            pts= []

            for n in strnu:
                nu = string.atoi(n)
                cord.append(nu)
            i = 0
            while i < len(cord):
                pt = []
                pt.append(cord[i])
                pt.append(cord[i+1])
                i += 2
                pts.append(pt)

            self.imgdict.setdefault(title, pts)



    def pre_process(self, dir_name):
        objs = os.listdir(dir_name) 

        if len(objs) < 1:
            print 'No imgs'

        for obj in objs:
            nn = os.path.join(dir_name, obj)
            ret,ext = os.path.splitext(nn)
            if ext in extl:
                self.imglist.append(nn)

        # create info.txt
        # extend push into dict
        if len(self.imglist):
            infoname = dir_name + '/info.txt'
            self.fs = open(infoname, 'a+')
            nn = self.imglist[0]
            ret,ext = os.path.splitext(nn)
            ret     = ext.split('.')
            self.imgdict.update(ext=ret[1])
            self.dict_from_file()
        
        cv2.namedWindow('src', cv2.WINDOW_NORMAL)
        #cv2.resizeWindow('src', 100, 100)

if __name__ == '__main__':

    dir_name = os.getcwd()

    app = CLabel()
    app.pre_process(dir_name)
    app.run()

