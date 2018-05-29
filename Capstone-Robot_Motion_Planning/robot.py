import numpy as np
import random
import sys

class Robot(object):
    def __init__(self, maze_dim):
        '''
        Use the initialization function to set up attributes that your robot
        will use to learn and navigate the maze. Some initial attributes are
        provided based on common information, including the size of the maze
        the robot is placed in.
        
        On the following n lines, there will be n comma-delimited numbers describing which edges of the square are open to movement. Each number represents a four-bit number that has a bit value of 0 if an edge is closed (walled) and 1 if an edge is open (no wall); the 1s register corresponds with the upwards-facing side, the 2s register the right side, the 4s register the bottom side, and the 8s register the left side. For example, the number 10 means that a square is open on the left and right, with walls on top and bottom (0*1 + 1*2 + 0*4 + 1*8 = 10). Note that, due to array indexing, the first data row in the text file corresponds with the leftmost column in the maze, its first element being the starting square (bottom-left) corner of the maze.
        L,B,R,U
        '''

        self.location = [0, 0]
        self.heading = 'up'
        self.maze_dim = maze_dim  #Minimum 12x12, max 16x16, n even, defined by first line of text file
        self.center = self.maze_dim/2
        self.goal = [self.center, self.center]#designate goal as 6,6
        path = 0
        self.steps = 0
        print "Maze Dimensions: ",self.maze_dim
        print "Goal Coordinates: ", self.goal
        
        #initialize matrix for distance to goal, calculates distance to goal cell for each location
        self.distance = [[0 for i in range(self.maze_dim)] for j in range(self.maze_dim)]
       
        for i in range(len(self.distance)):
            for j in range(len(self.distance[0])):
                self.distance[i][j] = abs(self.center-i)+abs(self.center-j)
                
        #print the distance map
        #print('\n'.join('entry {0}: {1}'.format(*k) for k in enumerate(self.distance, 1)))
       
        #initilize matrix for mapping maze
        self.mapping = [[np.array([1,1,1,1]) for i in range(self.maze_dim)] for j in range(self.maze_dim)]
        self.mapping = np.array(self.mapping)
        #Explore each to each corner before going to goal
        corners = [[self.maze_dim-1,0],[self.maze_dim-1,self.maze_dim-1],[0,self.maze_dim-1],[0,0],self.goal]
        #Explore to midpoints of boundaries before goal
        midpoints=[[self.maze_dim/2,0],[self.maze_dim-1, self.maze_dim/2],[self.maze_dim/2,self.maze_dim-1],[0,self.maze_dim/2],[0,0],self.goal]
        self.goals=midpoints
        self.checkpoint = self.goals[0]
        self.explore = 1
        print "Checkpoints: ", self.goals
        raw_input("Continue?")
        #Goal is a 2x2 square in the middle of the maze e.g. coordinates (5,5),(6,5),(5,6),(6,6)
        self.sensefile = open('sensor_data.txt','w')

    def next_move(self, sensors):
        '''
        Use this function to determine the next move the robot should make,
        based on the input from the sensors after its previous move. Sensor
        inputs are a list of three distances from the robot's left, front, and
        right-facing sensors, in that order.

        Outputs should be a tuple of two values. The first value indicates
        robot rotation (if any), as a number: 0 for no rotation, +90 for a
        90-degree rotation clockwise, and -90 for a 90-degree rotation
        counterclockwise. Other values will result in no rotation. The second
        value indicates robot movement, and the robot will attempt to move the
        number of indicated squares: a positive number indicates forwards
        movement, while a negative number indicates backwards movement. The
        robot may move a maximum of three units per turn. Any excess movement
        is ignored.

        If the robot wants to end a run (e.g. during the first training run in
        the maze) then returing the tuple ('Reset', 'Reset') will indicate to
        the tester to end the run and return the robot to the start.
        '''
        
        self.sensors = sensors
        headings = ["left", "down", "right", "up"]
        rotate = [90, 0, -90]
        self.steps = self.steps +1
        print "Next Checkpoint: ", self.checkpoint
        print "Location: ", self.location
        if self.location == self.goal:
            print "Goal Reached!"
            print "Required Steps: ", self.steps
            self.explore = 0
            rotation = 'Reset' 
            movement = 'Reset'
            self.steps = 0
            self.location = [0, 0]
            self.heading = 'up'
            print "Saving robot map..."
            thefile = open('robot_map.txt', 'w')
            thefile.write("%s"%self.maze_dim)
            for i in self.mapping:
                thefile.write("\n")
                for cell in i:
                    thefile.write("%s,"% sum(cell*[8,4,2,1]))
            raw_input("Reset for test run?")
            return rotation, movement
            #sys.exit()
        
        if ((self.location == self.checkpoint) & self.explore):
            self.checkpoint = self.goals[self.goals.index(self.checkpoint)+1]
        print "Heading: ", self.heading
        print "Steps taken: ", self.steps
        print "Sensor Readings: ", self.sensors
        
        self.sensefile.write("%s,\n"%self.sensors)
        
        #Add information gained from sensors to map
        #What sides of location are navigable [Left, Bottom, Right, Up]?
        
        
        sensed = []
        for i in self.sensors:
            if i > 0:
                sensed.append(1)
            else:
                sensed.append(0)
        
        sensed = np.array(sensed)
        print("Sensed: ", sensed)
        '''
        Sensor reading directions for each heading
        U-L,U,R
        R-U,R,D
        D-R,D,L
        L-D,L,U
        '''
        #update value array to indicate which directions are navigable from that cell for cell based on sensor readings, unknown areas assumed navigable (value = 1 in that direction)
        if self.heading=="up":
            value = np.array([sensed[0], 1, sensed[2], sensed[1]])
        elif self.heading=="right":
            value = np.array([1, sensed[2], sensed[1], sensed[0]])
        elif self.heading=="down":
            value = np.array([sensed[2], sensed[1], sensed[0], 1])
        elif self.heading=="left":
            value = np.array([sensed[1], sensed[0], 1, sensed[2]])
        
        #value represents current navigable directions (L, B, R, U)
        #print("Value: ", value)
        #update the map value for the cell based on the information gained
        self.mapping[self.location[0],self.location[1]] = value*self.mapping[self.location[0],self.location[1]] 
        #print "Assigning value to map: ", value*self.mapping[self.location[0],self.location[1]]
        #raw_input("Continue?\n")
        #Print map for debugging
        #print self.mapping
        
        #Update mapping for all cells based on current data
        for i in range(len(self.mapping[0])):
            for j in range(len(self.mapping[1])):
                #print "Updating map based on cell: ", [i, j]
                #print "Cell value: ", self.mapping[i][j]
                #Determine adjacent cells
                adjacent = [[i, j-1], [i-1,j], [i,j+1], [i+1,j]]
                #print "Adjacent cells are: ", adjacent
                for cell in adjacent:
                    #print "Updating cell: ", cell
                    if (0 <= cell[0] < self.maze_dim) and (0 <= cell[1] < self.maze_dim):#verify cell within maze 
                        #print "Cell within maze"
                        #if cell has wall in direction adjacent, update adjacent cell to show wall as well
                        if self.mapping[i][j][adjacent.index(cell)] == 0:#if current cell has wall between adjacent cell
                            #print "Wall adjacent to: ", cell
                            #print "Current cell value: ", self.mapping[cell[0]][cell[1]]
                            self.mapping[cell[0]][cell[1]][(adjacent.index(cell)+2)%4] = 0
                            #print "Updated cell value: ", self.mapping[cell[0]][cell[1]]
            #raw_input("Continue?")
        print "Updated maze map"
        #print self.mapping
        #print('\n'.join('entry {0}: {1}'.format(*k) for k in enumerate(self.mapping, 1)))
    
        #Update distance map using information gained
        #Based on discussion from http://www.societyofrobots.com/member_tutorials/book/export/html/94
        #starting at goal cell
        #print "Flooding from goal"
        flood = [self.checkpoint]
        #print flood
        flooded = [self.checkpoint]
        while len(flooded)<(self.maze_dim*self.maze_dim):
            #print "# Cells updated: ", len(flooded)
            #print "# Cells remaining: ", self.maze_dim*self.maze_dim - len(flooded)
            #Reset current flooded to cells
            cur_flood = []
            #Determine which cells to flood into
            #print "Cells to flood from", flood
            current = flood[0]
            flood.remove(current)
            #print "Flooding from cell: ", current
            possible = [[current[0], current[1]-1], [current[0]-1,current[1]], [current[0],current[1]+1], [current[0]+1,current[1]]]
            #print "Possible cells are: ", possible
            #check which directions are blocked
            for cell in possible:
                #print "Checking destination: ", cell
                #Check for valid location within maze
                if (0 <= cell[0] < self.maze_dim) and (0 <= cell[1] < self.maze_dim):
                    #print "Cell within maze"
                    #Check if destination is reachable
                    if self.mapping[current[0]][current[1]][possible.index(cell)] == 1:
                        #print "Cell not blocked by wall"
                        #Check if cell already assigned dist
                        if cell not in flooded:
                            #print "Cell not previously flooded"
                            cur_flood.append(cell)
            #print "Current flooded cells: ", cur_flood
            #print "Distance to current cell", self.distance[current[0]][current[1]]
            for cell in cur_flood:
                self.distance[cell[0]][cell[1]] = self.distance[current[0]][current[1]] + 1 
                #print "Assigning distance to cell",self.distance[current[0]][current[1]] + 1 , cell 
                flood.append(cell) #Queue of cells to flood from
                flooded.append(cell)#tracks cells that have updated distance
            #print "All flooded cells", flooded
        #raw_input("Continue?\n")
            
        print "Updated distance map" 
        #print('\n'.join('entry {0}: {1}'.format(*k) for k in enumerate(self.distance, 1)))
        #Determine next move by determing navigable directions and moving closer to goal
        #Find possible move from nearest cells
        options = [[self.location[0], self.location[1]-1], [self.location[0]-1,self.location[1]], [self.location[0],self.location[1]+1], [self.location[0]+1,self.location[1]]]
        #print("Options: ", options)
        
        
        #Remove invalid moves e.g. outside the boundaries, obstacles
        valid = []
        for cell in options:
            #print("Testing cell: ", cell)
            if ((cell[0] < 0) or (cell[1] < 0)):
                #print("Destination cell below min")
                #print("Removing: ", cell)
                print ""
            elif ((cell[0] > self.maze_dim) or (cell[1] > self.maze_dim)):
                #print("Destination cell above max")
                #print("Removing: ", cell)
                print ""
            elif ((self.mapping[self.location[0],self.location[1]][options.index(cell)] == 0)):
                #print("Destination blocked by obstacle")
                #print("Removing: ", cell)
                print ""
            else:
                #print("Destination Valid")
                valid.append(cell)
        
        
        #print valid options
        #print("Valid options: ", valid)
    
        
        moves = []
        for cell in valid:
            #print("Cell: ", cell)
            #print("Distance value: ", self.distance[cell[0]][cell[1]])
            moves.append(self.distance[cell[0]][cell[1]])
            
             
        #print("moves array: ", moves)    
            
        next_wp = valid[moves.index(min(moves))]
       
        print("Next WP: ", next_wp)
        
        #raw_input("Continue?")
        
        #Determine heading needed to reach next waypoint cell
        heading = headings[options.index(next_wp)]
        #print("Required Heading: ", heading)
        
        #default no heading change
        rotation = 0
        
        #Determine if heading change needed
        if self.heading != heading:
            #determine turns available
            turns = [headings[(headings.index(self.heading)-1)%4],self.heading,headings[(headings.index(self.heading)+1)%4]]
            #print("Possible Turns: ", turns)
            #if heading is possible
            if heading in turns:
                rotation=rotate[turns.index(heading)]
            else:
                rotation = 90
                
        
        #calculate heading after turn
        # headings = ["left", "down", "right", "up"]
        #rotate = [90, 0, 90]
        self.heading = headings[(headings.index(self.heading) + (rotate.index(rotation)-1))%4]
        
        #determine if heading is correct
        if self.heading == heading:
            movement = 1
        else:
            movement = 0
            
        #print("New Heading: ", self.heading)
        
        #Update location LBRU
        changes = [[0,-1],[-1,0],[0,1],[1,0]]
        if movement:
            change = changes[headings.index(self.heading)]
            #print("Change: ", change)
        else:
             change = [0,0]
        self.location[0] = self.location[0] + change[0]
        self.location[1] = self.location[1] + change[1]
        
        #print("New location: ", self.location)
        
        #raw_input("Continue?\n")
        return rotation, movement