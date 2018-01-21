import random
from environment import Agent, Environment
from planner import RoutePlanner
from simulator import Simulator

class LearningAgent(Agent):
    """An agent that learns to drive in the smartcab world."""

    def __init__(self, env):
        super(LearningAgent, self).__init__(env)  # sets self.env = env, state = None, next_waypoint = None, and a default color
        self.color = 'red'  # override color
        self.planner = RoutePlanner(self.env, self)  # simple route planner to get next_waypoint
        # TODO: Initialize any additional variables here
	self.trials = 0
        self.success = 0
        states = []
        light = ['green','red']
        oncoming = [None,'left','right','forward']
        right = [None,'left','right','forward']
        left = [None,'left','right','forward']
        waypoints = ['forward','left','right']
        for i in light:
            for j in oncoming:
                for k in right:
                    for l in left:
                        for m in waypoints:
                            states.append(tuple([i,j,k,l,m]))  #individual states entered as tuples so they can be used as dictionary keys
        states=tuple(states)#transform the whole state space to a tuple to use as dictionary keys
        self.Q = {key:[0,0,0,0] for key in states}
        #initialize q values dictionary from http://stackoverflow.com/questions/2241891/how-to-initialize-a-dict-with-keys-from-a-list-and-empty-value-in-python  each value represents value of action [forward, left, right, None] at that state
        self.A= 0.6 #alpha learning rate
        self.G= 0.5 #gamma discount rate
        self.E= 0.8 #epsilon initial probability that we choose a random value
        
        action = None

    def reset(self, destination=None):
        self.planner.route_to(destination)
        # TODO: Prepare for a new trip; reset any variables here, if required
        self.trials += 1
        self.mistakes = 0
        
		

    def update(self, t):
        # Gather inputs
        self.next_waypoint = self.planner.next_waypoint()  # from route planner, also displayed by simulator
        inputs = self.env.sense(self)
        deadline = self.env.get_deadline(self)
        Max_Q = []
        
        

        # TODO: Update state
        self.state = [inputs['light'],inputs['oncoming'],inputs['left'],inputs['right'], self.next_waypoint]
        s= tuple(self.state) #remember previous state
        
        # TODO: Select action according to your policy
        actions = ['forward', 'left', 'right',None]
        if self.E > random.random():
            action = random.choice(actions) #choose random action with epsilon probability
        else:
            Max_Q = self.Q[tuple(self.state)] #store values of all actions at this state
            action = actions[Max_Q.index(max(Max_Q))]#identify action with highest value
            
        self.E -= 0.001
        print('action',action)
        print('state',self.state)
        
        #implement epsilon in action choice https://discussions.udacity.com/t/using-epsilon-in-q-learning/190012/2 /// https://junedmunshi.wordpress.com/2012/03/30/how-to-implement-epsilon-greedy-strategy-policy/
        
        a = actions.index(action) #remember previous action

        # Execute action and get reward
        reward = self.env.act(self, action)
        
        #track number of mistakes
        if reward < 0:
            self.mistakes += reward
     
        
        #Calculate Max_Q for new state
        Max_Q=[]
        Max_Q = self.Q[tuple([inputs['light'],inputs['oncoming'],inputs['left'],inputs['right'], self.next_waypoint])] #store values of all actions at this state
        Max_Q = max(Max_Q)

        # TODO: Learn policy based on state, action, reward
        self.Q[s][a]= (1-self.A)*self.Q[s][a]+self.A*(reward+self.G*Max_Q-self.Q[s][a]) 
		
        #print('self.Q[s][a]',self.Q[s][a])
        #print ('Trials:',self.trials)
        print "Mistakes:", self.mistakes

        

        print "LearningAgent.update(): deadline = {}, inputs = {}, action = {}, reward = {}".format(deadline, inputs, action, reward)  # [debug]


def run():
    """Run the agent for a finite number of trials."""

    # Set up environment and agent
    e = Environment()  # create environment (also adds some dummy traffic)
    a = e.create_agent(LearningAgent)  # create agent
    e.set_primary_agent(a, enforce_deadline=True)  # specify agent to track
    # NOTE: You can set enforce_deadline=False while debugging to allow longer trials

    # Now simulate it
    sim = Simulator(e, update_delay= 0.01, display=False)  # create simulator (uses pygame when display=True, if available)
    # NOTE: To speed up simulation, reduce update_delay and/or set display=False

    sim.run(n_trials=100)  # run for a specified number of trials
    # NOTE: To quit midway, press Esc or close pygame window, or hit Ctrl+C on the command-line


if __name__ == '__main__':
    run()
