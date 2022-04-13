import pygame
import random
import math

pygame.init()

display_surf=pygame.display.set_mode((1200,600))
display=pygame.Surface((display_surf.get_width(),display_surf.get_height()))
shade=pygame.Surface((display_surf.get_width(),display_surf.get_height()),pygame.SRCALPHA)
# shade.set_alpha(200)
clock=pygame.time.Clock()

main_ground=pygame.Rect(300,500,600,100)

class partical:
    def __init__(self,x,y,px,py,bounce=0.1,gravity=0.4,friction=0.998):
        self.x,self.y=x,y
        self.px,self.py=px,py
        self.bounce=bounce
        self.gravity=gravity
        self.friction=friction
        self.rect=pygame.Rect(self.x,self.y,10,10)
    
    def physics(self):
        self.vx=(self.x-self.px)*self.friction
        self.vy=(self.y-self.py)*self.friction
        self.px,self.py=self.x,self.y
        self.x+=self.vx
        self.y+=self.vy
        self.y+=self.gravity
        self.rect.x,self.rect.y=self.x,self.y

class Light_source:
    def __init__(self,angle,magnitude): 
        self.rays=[]
        self.magnitude=magnitude
        self.angle=angle
        self.polygon=[]
        self.angle_offset=0

    def create_rays(self,pos,walls):
        for a in range(-self.angle//2,self.angle//2):
            ray=(pos,(pos[0]+math.cos(math.radians(a+self.angle_offset))*self.magnitude,pos[1]+math.sin(math.radians(a+self.angle_offset))*self.magnitude))
            self.rays.append(ray)
            collision_points=[]
            for wall in walls:
                d=(wall[0][0]-wall[1][0])*(ray[0][1]-ray[1][1]) - (wall[0][1]-wall[1][1])*(ray[0][0]-ray[1][0])
                if d==0:
                    continue
                t=((wall[0][0]-ray[0][0])*(ray[0][1]-ray[1][1])-(wall[0][1]-ray[0][1])*(ray[0][0]-ray[1][0]))/d
                u=-((wall[0][0]-wall[1][0])*(wall[0][1]-ray[0][1])-(wall[0][1]-wall[1][1])*(wall[0][0]-ray[0][0]))/d
                if 0<t<1 and u>0:
                    Px,Py=wall[0][0]+t*(wall[1][0]-wall[0][0]),wall[0][1]+t*(wall[1][1]-wall[0][1])
                    collision_points.append((Px,Py))

            if len(collision_points)>1:
                distances=[]
                for point in collision_points:
                    distances.append(math.dist(pos,point))
                point_index=distances.index(min(distances))
                #pygame.draw.line(display,(255,200,200),pos,collision_points[point_index],1)
                self.polygon.append(collision_points[point_index])
            elif len(collision_points)==1:
                #pygame.draw.line(display,(255,200,200),pos,collision_points[0],1)
                self.polygon.append(collision_points[0])

        #self.draw_rays()
        self.rays=[]

    def draw_rays(self):
        for ray in self.rays:
            pygame.draw.line(display,(200,200,200),ray[0],ray[1],1)

spark=[]
class Effects:
    def __init__(self, pos, NumOfDrops):
        self.dead=False
        self.pos=pos
        self.d_pxy=[]
        for n in range(NumOfDrops):
            self.d_pxy.append([0,[self.pos[0],self.pos[1]],[self.pos[0]+random.randint(-1,1)*5,self.pos[1]+random.randint(-1,1)*5]])
    
    def splash(self,col,grav,rad,time):
        for p in self.d_pxy:
            p[0]+=1
            pvx=(p[1][0]-p[2][0])*0.998
            pvy=(p[1][1]-p[2][1])*0.998
            p[2][0],p[2][1]=p[1][0],p[1][1]
            p[1][0]+=pvx
            p[1][1]+=pvy
            p[1][1]+=grav
            pygame.draw.circle(display,col,(p[1][0],p[1][1]),rad-p[0]*rad*0.1)
            if p[0]%time==0:
                self.d_pxy.pop(self.d_pxy.index(p))
                self.dead=True

class Collision:
    def __init__(self):
        self.zone_x=None
        self.zone_y=None
        

    def check_collisions(self,plyr,rct_list):
        collide=False
        for rct in rct_list:
            if not collide:
                collide=self.check_collision(plyr,rct)
            else:
                self.check_collision(plyr,rct)
            if rct==rct_list[-1] and collide:
                break
        else:
            plyr.friction=0.998

    def check_collision(self,plyr,rct):
        if plyr.x+plyr.rect.width>=rct.x:
            if rct.x+rct.width>=plyr.x:
                self.zone_x="Green"
            else:
                self.zone_x=None
        else:
            self.zone_x=None
        if plyr.y+plyr.rect.height>=rct.y:
            if rct.y+rct.height>=plyr.y:
                self.zone_y="Green"
            else:
                self.zone_y=None
        else:
            self.zone_y=None
        
        if self.zone_x=="Green" and self.zone_y=="Green":
            try:
                if not plyr.jump:
                    plyr.jump=True
            except:
                pass
            if plyr.friction==0.998:
                plyr.friction=0.89
            if plyr.px+plyr.rect.width>rct.x:
                if rct.x+rct.width<=plyr.px:
                    plyr.x-=plyr.vx
                    plyr.x=rct.x+rct.width
            else:
                plyr.x-=plyr.vx
                plyr.x=rct.x-plyr.rect.width

            if plyr.py+plyr.rect.height>rct.y:
                if rct.y+rct.height<=plyr.py:
                    plyr.y-=plyr.vy
                    plyr.y=rct.y+rct.height
            else:
                plyr.y-=plyr.vy
                plyr.y=rct.y-plyr.rect.height

            
            return True
        

class player:
    def __init__(self,x,y):
        self.x,self.y=x,y
        self.px,self.py=x,y
        self.friction=0.998
        self.rect=pygame.Rect(x,y,10,10)
        self.x_mov=None
        self.jump=True
        self.dead=False
        self.power=2
        self.dash=True
    
    def Dash_tackel_physics(self):
        if self.dist_curr_prev:
            for d in range(0,30,5):
                self.x+=d*self.vx/(self.friction*self.dist_curr_prev)
                self.y+=d*self.vy/(self.friction*self.dist_curr_prev)
                self.px+=d*self.vx/(self.friction*self.dist_curr_prev)
                self.py+=d*self.vy/(self.friction*self.dist_curr_prev)
                pygame.draw.rect(display,(100,100,100),(self.x,self.y,self.rect.width,self.rect.height))
            
        self.dash=False

    def check_for_dead(self):
        if self.y>600 or self.x>1200 or self.x<0:
            self.dead=True

    def velocity(self):
        self.dist_curr_prev=math.dist((self.x,self.y),(self.px,self.py))
        self.vx=(self.x-self.px)*self.friction
        self.vy=(self.y-self.py)*self.friction
        self.px,self.py=self.x,self.y
    
    def add_vel(self):
        self.x+=self.vx
        self.y+=self.vy
        self.y+=0.4
        if self.x_mov==True:
            self.x+=1
        elif self.x_mov==False:
            self.x-=1
        self.check_for_dead()
        self.rect.x,self.rect.y=self.x,self.y
    
    def check_player_collision(self,ply):
        if self.rect.colliderect(ply.rect):
            spark.append(Effects((self.x,self.y),5))
            screenshake.start=True
            screenshake.mag=max([math.fabs(self.vx),math.fabs(self.vx),math.fabs(self.vy),math.fabs(ply.vy)])*0.5
            self.px,ply.px=ply.px,self.px
            self.py,ply.py=ply.py,self.py
            return True
        else:
            return False
    
    def become_monster(self,plyr):
        if plyr.x>self.x:
            self.x_mov=True
        elif plyr.x<self.x:
            self.x_mov=False
        if plyr.y<self.y-plyr.rect.height:
            if self.jump:
                self.y-=10
            self.jump=False

class screen_shake:
    def __init__(self,t):
        self.counter=0
        self.time=t
        self.start=False
        self.mag=1
        self.offset=[0,0]

    def shake(self):
        if self.start:
            self.counter+=1
            self.offset[0]=random.randint(-1,1)*self.mag
            self.offset[1]=random.randint(-1,1)*self.mag
            if self.counter%self.time==0:
                self.counter=0
                self.offset=[0,0]
                self.start=False

class show_txt:
    def __init__(self):
        self.f=pygame.font.Font(None,50)
    def blit(self,txt,val,location):
        text=self.f.render(txt+f"{val}",True,(200,150,150))
        display.blit(text,location)

def u_stick(list):
	# add colapseable stick whick can not expand
	for s in list:
		dx=s[1].x-s[2].x
		dy=s[1].y-s[2].y
		distance=math.dist((s[2].x,s[2].y),(s[1].x,s[1].y))
		if distance==0: #distance=0.0001
			continue
		difference=s[0]-distance
		percent=difference/distance/2
		offsetx=dx*percent
		offsety=dy*percent
		try:
			if s[4]:
				s[2].x-=offsetx
				s[2].y-=offsety
		
		except:
			s[1].x+=offsetx
			s[1].y+=offsety
			s[2].x-=offsetx
			s[2].y-=offsety
		
def stick_connect(stk1,stk2,ratio,rev=False):
	x=(ratio[0]*stk2[1].x+ratio[1]*stk2[2].x)/(ratio[0]+ratio[1])
	y=(ratio[0]*stk2[1].y+ratio[1]*stk2[2].y)/(ratio[0]+ratio[1])
	if not rev:
		dx=stk1[2].x-x
		dy=stk1[2].y-y
	else:
		dx=stk1[1].x-x
		dy=stk1[1].y-y
	distance=math.dist((stk1[2].x,stk1[2].y),(x,y))
	if distance==0:
		distance=0.001
	difference=1-distance
	percent=difference/distance/2
	offsetx=dx*percent
	offsety=dy*percent
	if not rev:
		stk1[2].x+=offsetx
		stk1[2].y+=offsety
	else:
		stk1[1].x+=offsetx
		stk1[1].y+=offsety
	stk2[1].x-=offsetx*ratio[0]
	stk2[2].x-=offsetx*ratio[1]
	stk2[1].y-=offsety*ratio[0]
	stk2[2].y-=offsety*ratio[1]
	
def show_stick(slist,col):
	for s in slist:
		if s[3]:
			pygame.draw.line(display,col,[s[1].x+5,s[1].y+5],[s[2].x+5,s[2].y+5],3)
			
def constrain_points(list):
	for s in list:
		if s.x>=2000:
			s.x=2000
			s.px=2*s.x-s.px
		elif s.x<=0:
			s.x=0
			s.px=2*s.x-s.px
		if s.y>=display.get_height()-50:
			s.y=display.get_height()-50
			s.py=2*s.y-s.py-s.bounce
		#elif s.y<=0:
#			s.y=0
#			s.py=2*s.y-s.py+s.bounce

def stick_interaction(s1,s2):
	d=(s1[1].x-s1[2].x)*(s2[1].y-s2[2].y) - (s1[1].y-s1[2].y)*(s2[1].x-s2[2].x)
	if d==0:
		return False
	t=((s1[1].x-s2[1].x)*(s2[1].y-s2[2].y)-(s1[1].y-s2[1].y)*(s2[1].x-s2[2].x))/d
	u=-((s1[1].x-s1[2].x)*(s1[1].y-s2[1].y)-(s1[1].y-s1[2].y)*(s1[1].x-s2[1].x))/d

	if 0<t<1 and 1>u>0:
		Px,Py=s1[1].x+t*(s1[2].x-s1[1].x),s1[1].y+t*(s1[2].y-s1[1].y)
		
		try:
			k_s1=(s1[2].x-Px)/(Px-s1[1].x)
		except:
			k_s1=(s1[2].x-Px)/0.00001
		
		if k_s1>1:
			s2[2].x,s2[2].y=Px,Py
		else:
			s2[1].x,s2[1].y=Px,Py

		s1[1].x+=(s2[2].x-s2[2].px)
		s1[1].y+=(s2[2].y-s2[2].py)
		s1[2].x+=k_s1*(s2[2].x-s2[2].px)
		s1[2].y+=k_s1*(s2[2].x-s2[2].px)
		return True
	else:
		return False
	


def phy(list):
	for p in list:
		p.physics()
def blit(list):
	for p in list:
		p.blit((255,255,255))
def create_unit_vector(final,initial):
	return ((final[0]-initial[0])/math.dist(final,initial),(final[1]-initial[1])/math.dist(final,initial))


screenshake=screen_shake(5)
score=[0,0]
score_red=show_txt()
score_blue=show_txt()

def Main_game():
    Turn_blue_into_monster=False
    p1=player(400,300)
    p1_collision=Collision()

    p2=player(600,300)
    p2_collision=Collision()
    
    Grounds=[main_ground]
    
    #---random level generator---
    for _ in range(random.randint(10,20)):
        trect=pygame.Rect(random.randint(100,1100),random.randint(200,500),random.randint(15,200),random.randint(25,200))
        Grounds.append(trect)

    while True:
        if Turn_blue_into_monster:
            p2.become_monster(p1)
        
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                quit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_d:
                    p1.x_mov=True
                elif event.key==pygame.K_a:
                    p1.x_mov=False
                elif event.key==pygame.K_w:
                    if p1.jump:
                        p1.y-=10
                    p1.jump=False
                elif event.key==pygame.K_RIGHT:
                    p2.x_mov=True
                elif event.key==pygame.K_LEFT:
                    p2.x_mov=False
                elif event.key==pygame.K_UP:
                    if p2.jump:
                        p2.y-=10
                    p2.jump=False
                
                elif event.key==pygame.K_b:
                    if  Turn_blue_into_monster:
                        Turn_blue_into_monster=False
                    else:
                        Turn_blue_into_monster=True
                elif event.key==pygame.K_f:
                    p1.dash=True
            if event.type==pygame.KEYUP:
                if event.key==pygame.K_d or event.key==pygame.K_a:
                    p1.x_mov=None
                elif event.key==pygame.K_RIGHT or event.key==pygame.K_LEFT:
                    p2.x_mov=None
                elif event.key==pygame.K_f:
                    p1.dash=False
            
        p1.velocity()
        p2.velocity()
        
        p1.add_vel()
        p2.add_vel()

        p1_collision.check_collisions(p1,Grounds)
        p2_collision.check_collisions(p2,Grounds)
        
        p1.check_player_collision(p2)
        
        
        #------------------------------------------------------
        # displaying stuff on the screen

        display_surf.fill((0,0,0))
        display.fill((25,25,25))
        
        score_red.blit("RED:",score[0],(50,50))
        score_blue.blit("BLUE:",score[1],(1000,50))
        
        if p1.dash:
            p1.Dash_tackel_physics()

        pygame.draw.rect(display,(255,55,55),p1.rect)
        pygame.draw.rect(display,(55,55,255),p2.rect)

        for g in Grounds:
            pygame.draw.rect(display,(255,255,255),g)
        
        for s in spark:
            s.splash((255,200,200),0.4,3,10)
            if s.dead:
                spark.pop(spark.index(s))

        screenshake.shake()

        pygame.draw.rect(display,(255,100,0),(0,575,1200,25))
        display_surf.blit(display,(0+screenshake.offset[0],0+screenshake.offset[1]))

        if p1.dead:
            score[1]+=1
            break
        elif p2.dead:
            score[0]+=1
            break

        pygame.display.update()
        clock.tick(35)

while True:
    Main_game()
