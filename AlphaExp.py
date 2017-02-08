
# Alphabet Expert


__author__ = 'Robert'
import sys
sys.path.append('/Users/robertwest/CCMSuite')
#sys.path.append('C:/Users/Robert/Documents/Development/SGOMS/CCMSuite')
import ccm
from random import randrange, uniform
log = ccm.log()
log=ccm.log(html=True)
from ccm.lib.actr import *




# Create Environment

class MyEnvironment(ccm.Model):

    response = ccm.Model(isa='response', state='none', salience=0.99)
    display = ccm.Model(isa='display', state='structura', salience=0.99)
    response_entered = ccm.Model(isa='response_entered', state='no', salience=0.99)

    blue_wire = ccm.Model(isa='wire', state='uncut', salience=0.99)
    green_wire = ccm.Model(isa='wire', state='uncut', salience=0.99)
    warning_light = ccm.Model(isa='warning_light', state='off', salience=0.99)

    motor_finst = ccm.Model(isa='motor_finst', state='re_set')




# Create a Motor Module 

class MotorModule(ccm.Model):  ### defines actions on the environment

# change_state is a generic action that changes the state slot of any object
# disadvantages (1) yield #time is always the same (2) cannot use for parallel actions

    def change_state_slow(self, env_object, slot_value):
        yield 1
        x = eval('self.parent.parent.' + env_object)
        x.state = slot_value
        print env_object
        print slot_value
        self.parent.parent.motor_finst.state = 'change_state_slow'

    def change_state_fast(self, env_object, slot_value):
        yield 3
        x = eval('self.parent.parent.' + env_object)
        x.state = slot_value
        print env_object
        print slot_value
        self.parent.parent.motor_finst.state = 'change_state_fast'

    def vision_slow(self):
        yield 5
        print 'target identified'
        self.parent.parent.motor_finst.state = 'vision_slow'
        self.parent.visual_buffer = 'spotted'
        
    def vision_fast(self):
        yield 2
        print 'target spotted'
        self.parent.parent.motor_finst.state = 'vision_fast'
 

    def motor_finst_reset(self):
        self.parent.parent.motor_finst.state = 're_set'


##    def change_state_referee(self, env_object, slot_value):
##        # yield 2
##        x = eval('self.parent.parent.' + env_object)
##        x.state = slot_value
##        print env_object
##        print slot_value
##        self.parent.parent.motor_finst.state = 'finished'

        



# Create An Agent

##class Referee(ACTR):
##    production_time = 0
##
##    focus = Buffer()
##    motor = MotorModule()
##
##    focus.set('go')
##
##    def change_display_zzz(focus='go', display='state:zzz', response_entered='state:yes'):
##        motor.change_state_referee('display', "yyy")
##        motor.change_state_referee('response_entered', "no")
##        print 'display changed to yyy '
##        
##    def change_display_yyy(focus='go', display='state:yyy', response_entered='state:yes'):
##        target = 'display'
##        motor.change_state_referee(target, "zzz")
##        print 'display changed to xxx '
##


    

# Create An Agent

class MyAgent(ACTR):



# BUFFERS (create buffers and add initial content
    
    # goal system buffers
    b_context = Buffer()
    b_plan_unit = Buffer()
    b_unit_task = Buffer()
    b_method = Buffer()
    b_operator = Buffer()
    
    b_emotion = Buffer()
    
    # module buffers
    b_DM = Buffer()
    b_motor = Buffer()
    visual_buffer=Buffer()
    b_image = Buffer()
    b_focus = Buffer()

    # initial buffer contents
    b_context.set('status:unoccupied')
    b_emotion.set('threat:ok')
    b_plan_unit.set('planning_unit:P cuelag:P cue:P unit_task:P state:P ptype:P')
    



# MODULES (import modules into agent, connect to buffers, and add initial content)
    
    # vision module - from CCM suite
    vision_module=SOSVision(visual_buffer,delay=.085)
    
    # motor module - defined above
    motor = MotorModule(b_motor)

    # declarative memory module - from CCM suite
    DM = Memory(b_DM)

    # initial memory contents
    DM.add('planning_unit:structura         cuelag:none          cue:start          unit_task:primus')
    DM.add('planning_unit:structura         cuelag:start         cue:primus          unit_task:lectus')
    DM.add('planning_unit:structura         cuelag:primus        cue:lectus            unit_task:finished')


    ########### create productions for choosing planning units ###########

    ## these productions are the highest level of SGOMS and fire off the context buffer
    ## they can take any ACT-R form (one production or more) but must eventually call a planning unit and update the context buffer

    def dominus_planning_unit(b_context='status:unoccupied'): 
        b_plan_unit.modify(planning_unit='dominus',state='begin_situated', ptype='unordered')
        b_context.set('status:occupied, next_planning_unit:unkown')# update context status to occupied
        print 'dominus planning unit is chosen'

    def next_planning_unit_structura(b_context='status:unoccupied next_planning_unit:structura'): 
        b_plan_unit.modify(planning_unit='structura',state='begin_sequence', ptype='ordered')
        b_context.set('status:occupied, next_planning_unit:unkown')# update context status to occupied
        print 'structura planning unit is chosen'


#######################################################
########## unit task management productions ###########
#######################################################

######################## these set up whether it will be an ordered or a situated planning unit

    def setup_situated_planning_unit(b_plan_unit='planning_unit:?planning_unit state:begin_situated ptype:unordered'):
        b_unit_task.set('state:start type:unordered')
        b_plan_unit.modify(state='running')
        print 'begin situated planning unit = ', planning_unit

    def setup_ordered_planning_unit(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:begin_sequence ptype:ordered'):
        b_unit_task.set('unit_task:?unit_task state:start type:ordered')
        b_plan_unit.modify(state='running')
        print 'begin orderdered planning unit = ', planning_unit

######################### these manage the sequence if it is an ordered planning unit

    def request_next_unit_task(b_plan_unit='planning_unit:?planning_unit cuelag:?cuelag cue:?cue unit_task:?unit_task state:running',
                               b_unit_task='unit_task:?unit_task state:finished type:ordered'):
        DM.request('planning_unit:?planning_unit cue:?unit_task unit_task:? cuelag:?cue')
        b_plan_unit.modify(state='retrieve')
        print 'finished unit task = ', unit_task

    def retrieve_next_unit_task(b_plan_unit='state:retrieve',
                                b_DM='planning_unit:?planning_unit cuelag:?cuelag cue:?cue!finished unit_task:?unit_task'):
        b_plan_unit.modify(planning_unit=planning_unit,cuelag=cuelag,cue=cue,unit_task=unit_task,state='running')
        b_unit_task.set('unit_task:?unit_task state:start type:ordered')
        print 'unit_task = ', unit_task
       
########################## these manage unit tasks that are finished ################### PROBLEM HERE, WANT TO DO DOMINUS

    def last_unit_task_ordered(b_plan_unit='planning_unit:?planning_unit',
                               b_unit_task='unit_task:finished state:start type:ordered'):
        print 'finished planning unit=',planning_unit
        b_unit_task.set('stop')
        b_context.modify(status='unoccupied')

    def interupted_unit_task(b_plan_unit='planning_unit:?planning_unit',
                             b_unit_task='unit_task:interupted state:interupted type:?type'):
        print 'interupting planning unit=',planning_unit
        print planning_unit
        b_unit_task.set('state:end')
        b_context.modify(status='interupted')



#######################################################
##################### unit task productions ###########
#######################################################

## unit task dominus

 ## add condition to fire to this production
    def dominus_unordered(b_unit_task='unit_task:? state:start type:unordered',
                          b_plan_unit='planning_unit:dominus'):
        b_unit_task.set('unit_task:lectus state:begin type:unordered')                   #### competes with other unit tasks to fire
        print 'start unit task dominus unordered'

    def dominus_ordered(b_unit_task='unit_task:lectus state:start type:ordered'):    ### this unit task is chosen to fire by planning unit
        b_unit_task.modify(state='begin')
        print 'start unit task dominus ordered'

    ## the first production in the unit task must begin in this way
    def dominus_start(b_unit_task='unit_task:lectus state:begin type:?type'):
        b_unit_task.set('unit_task:lectus state:running type:?type')
        b_focus.set('start')
        print 'starting unit task dominus now'

    ## body of the unit task
    def dominus_get_code(b_unit_task='unit_task:lectus state:running type:?type',
                         b_focus='start'): 
        b_method.set('method:get_code target:response content:lectus_1 state:start')
        b_focus.set('get_code')
        print 'getting the code'

# response 1 and 2 are chosen randomly here but they would really be chosen based on the percieved code

    def dominus_response1(b_unit_task='unit_task:lectus state:running type:?type',
                          b_focus='code:identified'):
        b_method.set('method:response target:response content:dominus_1a state:start')
        b_focus.set('done')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print 'entering the code'
        b_context.modify(next_planning_unit='structura')

    def dominus_response2(b_unit_task='unit_task:lectus state:running type:?type',
                         b_focus='code:identified'):
        b_method.set('method:response target:response content:dominus_1b state:start')
        b_focus.set('done')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print 'entering the code'
        b_context.modify(next_planning_unit='fortuitus')

    ## finishing the unit task
    def dominus_finished_ordered(b_method='state:finished',  ## this line assumes waiting for the last method to finish
                                 b_unit_task='unit_task:lectus state:end type:ordered',
                                 b_emotion='threat:ok'):
        print 'finished unit task dominus - ordered'
        b_unit_task.set('unit_task:lectus state:finished type:ordered')

    def dominus_finished_unordered(b_method='state:finished',
                                   b_unit_task='unit_task:lectus state:end type:unordered',
                                   b_plan_unit='ptype:unordered',
                                   b_emotion='threat:ok'):
        print 'finished unit task dominus - unordered'
        b_unit_task.set('unit_task:lectus state:start type:unordered')

    def dominus_interupt_planning_unit(b_method='state:finished',
                                       b_unit_task='unit_task:X state:end type:?type',
                                       b_emotion='threat:high'):
        print 'finished unit task dominus - interupting planning unit'
        b_unit_task.set('unit_task:interupted state:interupted type:?type')




## unit task primus

 ## add condition to fire to this production
    def primus_unordered(b_unit_task='unit_task:? state:start type:unordered',
                    display='state:zzz'):
        b_unit_task.set('unit_task:primus state:begin type:unordered')                   #### competes with other unit tasks to fire
        print 'start unit task primus unordered'

    def primus_ordered(b_unit_task='unit_task:primus state:start type:ordered'): ### this unit task is chosen to fire by planning unit
        b_unit_task.modify(state='begin')
        print 'start unit task primus ordered'

    ## the first production in the unit task must begin in this way
    def primus_start(b_unit_task='unit_task:primus state:begin type:?type'):
        b_unit_task.set('unit_task:primus state:running type:?type')
        b_focus.set('start')
        print 'starting unit task primus now'

    ## body of the unit task
    def primus_known_response(b_unit_task='unit_task:primus state:running type:?type',
                   b_focus='start'):
        b_method.set('method:known_response target:response content:primus1 state:start')############## here
        b_focus.set('done')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print 'I known_response'

    ## finishing the unit task
    def primus_finished_ordered(b_method='state:finished',  ## this line assumes waiting for the last method to finish
                           b_unit_task='unit_task:primus state:end type:ordered',
                           b_emotion='threat:ok'):
        print 'finished unit task primus - ordered'
        b_unit_task.set('unit_task:primus state:finished type:ordered')

    def primus_finished_unordered(b_method='state:finished',
                             b_unit_task='unit_task:X state:end type:unordered',
                             b_plan_unit='ptype:unordered',
                             b_emotion='threat:ok'):
        print 'finished unit task primus - unordered'
        b_unit_task.set('unit_task:primus state:start type:unordered')

    def primus_interupt_planning_unit(b_method='state:finished',
                                 b_unit_task='unit_task:primus state:end type:?type',
                                 b_emotion='threat:high'):
        print 'finished unit task primus - interupting planning unit'
        b_unit_task.set('unit_task:interupted state:interupted type:?type')


## unit task lectus

        ## lectus deals with the case when there are two possible responses
        ## depending on the code, so it uses two methods, the first gets the code
        ## then a production fires based off the code to pass the correct response
        ## to the method that enters it

 ## add condition to fire to this production
    def lectus_unordered(b_unit_task='unit_task:? state:start type:unordered',
                         display='state:zzz'):
        b_unit_task.set('unit_task:lectus state:begin type:unordered')                   #### competes with other unit tasks to fire
        print 'start unit task lectus unordered'

    def lectus_ordered(b_unit_task='unit_task:lectus state:start type:ordered'): ### this unit task is chosen to fire by planning unit
        b_unit_task.modify(state='begin')
        print 'start unit task lectus ordered'

    ## the first production in the unit task must begin in this way
    def lectus_start(b_unit_task='unit_task:lectus state:begin type:?type'):
        b_unit_task.set('unit_task:lectus state:running type:?type')
        b_focus.set('start')
        print 'starting unit task lectus now'

    ## body of the unit task
    def lectus_get_code(b_unit_task='unit_task:lectus state:running type:?type',
                        b_focus='start'): 
        b_method.set('method:get_code target:response content:lectus_1 state:start')
        b_focus.set('get_code')
        print 'getting the code'

# response 1 and 2 are chosen randomly here but they would really be chosen based on the percieved code

    def lectus_response1(b_unit_task='unit_task:lectus state:running type:?type',
                        b_focus='code:identified'):
        b_method.set('method:response target:response content:lectus_1a state:start')
        b_focus.set('done')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print 'entering the code'

    def lectus_response2(b_unit_task='unit_task:lectus state:running type:?type',
                        b_focus='code:identified'):
        b_method.set('method:response target:response content:lectus_1b state:start')
        b_focus.set('done')
        b_unit_task.modify(state='end')  ## this line ends the unit task
        print 'entering the code'


    ## finishing the unit task
    def lectus_finished_ordered(b_method='state:finished',  ## this line assumes waiting for the last method to finish
                                b_unit_task='unit_task:lectus state:end type:ordered',
                                b_emotion='threat:ok'):
        print 'finished unit task lectus - ordered'
        b_unit_task.set('unit_task:lectus state:finished type:ordered')

    def lectus_finished_unordered(b_method='state:finished',
                                  b_unit_task='unit_task:lectus state:end type:unordered',
                                  b_plan_unit='ptype:unordered',
                                  b_emotion='threat:ok'):
        print 'finished unit task lectus - unordered'
        b_unit_task.set('unit_task:lectus state:start type:unordered')

    def lectus_interupt_planning_unit(b_method='state:finished',
                                      b_unit_task='unit_task:X state:end type:?type',
                                      b_emotion='threat:high'):
        print 'finished unit task lectus - interupting planning unit'
        b_unit_task.set('unit_task:interupted state:interupted type:?type')






################ methods #######################

### known response method #########################

# the response is assumed to be passed down by the production that called this method
# there is a quick visual check that the code has changed then there is a response
# possibly someone could train themselves to ignore the visual altogether
# here it is assumed that seeing the code change still plays a role as subjects were trained initially to wait for it to change

    def known_response_vision(b_method='method:known_response target:?target content:?content state:start'):  # target is the chunk to be altered
        motor.vision_fast()
        b_method.modify(state='running')
        b_focus.set('target:looking')
        print 'known_responding' 

    def vision_fast_finished(motor_finst='state:vision_fast',
                             b_method='method:known_response',
                             b_focus='target:looking'):
        motor.motor_finst_reset()
        b_focus.set('target:spotted')
        print 'I have spotted the target, the new code is there'

    def enter_response_fast(b_focus='target:spotted',  
                            b_method='method:known_response target:?target content:?content state:running'):
        motor.change_state_fast(target, content)
        b_method.modify(state='running')
        b_focus.set('response_entered')
        print 'entering response'
        print 'target object = ', target

    def response_entered(b_method='method:?method target:?target state:running',
                         motor_finst='state:change_state_fast',
                         b_focus='response_entered'):
        b_method.modify(state='finished')
        motor.motor_finst_reset()
        print 'I have altered', target


### get_code method ################################

# in the case where the next response depends on the code the agent must first read the code

    def get_code_vision(b_method='method:get_code target:?target content:?content state:start'):  # target is the chunk to be altered
        motor.vision_slow()
        b_method.modify(state='running')
        print 'getting code'

    def vision_slow_finished(motor_finst='state:vision_slow'):
        motor.motor_finst_reset()
        b_method.modify(state='finished')
        b_focus.set('code:identified')
        print 'I have spotted the target, I have the new code'

### reponse method #################################

# in this case the vision component took place already using the get_code method so this is only motor

    def response(b_method='method:response target:?target content:?content state:start'):  # target is the chunk to be altered
        motor.change_state_fast(target, content)
        b_method.modify(state='running')
        b_focus.set('response_entered')
        print 'entering response'
        print 'target object = ', target

    def response_entered2(b_method='method:?method target:?target state:running',
                          motor_finst='state:change_state_fast',
                          b_focus='response_entered'):
        b_method.modify(state='finished')
        motor.motor_finst_reset()
        print 'I have altered', target


            

############## run model #############
#tom = Referee()
tim = MyAgent()  # name the agent
subway = MyEnvironment()  # name the environment
#subway.agent = tom  # put the agent in the environment
subway.agent = tim  # put the agent in the environment
ccm.log_everything(subway)  # print out what happens in the environment
subway.run()  # run the environment
ccm.finished()  # stop the environment
