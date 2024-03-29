# coding:utf-8
#! /usr/bin/env python
import rospy
import numpy as np
from config import *
from geometry_msgs.msg import Pose
class Agent:
     def __init__(self,desiredV,actualV,pos,dest):
         # agent parameter
         self.mass=60.0
         self.radius=1.0
         self.desiredV = 0.8
         self.acclTime = 10.0 #遷移時間
         self.pos =pos
         self.dest = dest
         self.actualV =actualV
         self.bodyFactor = 1.0 # 弾性係数
         self.slideFricFactor = 5 #散逸係数
         self.A = 0.2 # interaciton strength
         self.B = 8 #

 # 目的地に向かう力
     def adaptVel(self):
        direction =normalize(self.dest-self.pos)
        deltaV = self.desiredV*direction - self.actualV
         # deltaVが近似的にゼロに近いかどうかを計算
        if np.allclose(deltaV, np.zeros(2)):
            deltaV = np.zeros(2)
        return deltaV*self.mass/self.acclTime

    # 人との相互作用
     def peopleInteraction(self, other):
        rij = self.radius + other.radius
        dij = np.linalg.norm(self.pos - other.pos)  # agent間の距離
        nij = (self.pos - other.pos) / dij  # 正規化
        tij = np.array([-nij[1],nij[0]]) #  法線
        deltaVij = (self.actualV - other.actualV)*tij
        # 後者はある範囲にあるときのみに適用される
        if rij-dij > 0:
            first = (self.A * np.exp((rij - dij) / self.B) + self.bodyFactor * (rij - dij)) * nij
            second = self.slideFricFactor * (rij - dij) * deltaVij * tij
            #import pdb; pdb.set_trace()
            #first = (self.A*np.exp((rij-dij)/self.B) + self.bodyFactor*g(rij-dij))*nij
        else:
            first =(self.A * np.exp((rij - dij) / self.B))*nij
            #first = (self.A * np.exp((rij - dij) / self.B))* nij
            second=0
        return first + second


 #　静的障害物からの力
     def wallInteraction(self, wall):
        ri = self.radius+0.5
        diw = np.linalg.norm(self.pos - wall)
        niw = (self.pos - wall) / diw  # 正規化
        tiw = np.array([-niw[1],niw[0]])
        if ri-diw > 0:
            first = (self.A*np.exp((ri-diw)/self.B) + self.bodyFactor*(ri-diw))*niw
            second = self.slideFricFactor * (ri - diw) * (self.actualV * tiw) * tiw
        else:
            first = (self.A * np.exp((ri - diw) / self.B)) * niw
            second=0
        return first - second

