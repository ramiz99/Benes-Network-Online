##############################################
# adaptive routing testing
##############################################

import random
import math
import time

##############################################
##############################################

class PE:
    def __init__(self, index):
        self.index = index
        self.state = -1
        self.conn0 =  [-1, -1]  # number of next PE, inp0/1
        self.conn1 =  [-1, -1]  # number of next PE, inp0/1
        self.count =  0         # number of connection through the SE

##############################################
##############################################

def Build_Conn_1st_rec(stage, max_stage, N, ind):
    for i in range(N//2):
        if i%2==0:
            pe[i+ind][stage].conn0 = [(i//2)+ind, 0]
            pe[i+ind][stage].conn1 = [(i//2)+ind+N//4, 0]
        else:
            pe[i+ind][stage].conn0 = [(i//2)+ind, 1]
            pe[i+ind][stage].conn1 = [(i//2)+ind+N//4, 1]
    if stage == max_stage: return
    Build_Conn_1st_rec(stage+1, max_stage, N//2, ind+0)
    Build_Conn_1st_rec(stage+1, max_stage, N//2, ind+N//4)

##############################################

def Build_Conn_2nd_rec(stage, max_stage, N, ind):
    for i in range(0, N, 2):
        if i<N//2:
            pe[i//2+ind][stage].conn0 = [ind+i, 0]
            pe[i//2+ind][stage].conn1 = [ind+i+1, 0]
        else:
            pe[i//2+ind][stage].conn0 = [ind+i-N//2, 1]
            pe[i//2+ind][stage].conn1 = [ind+i+1-N//2, 1]
    if stage == max_stage+1: return
    Build_Conn_2nd_rec(stage-1, max_stage, N//2, ind+0)
    Build_Conn_2nd_rec(stage-1, max_stage, N//2, ind+N//4)

##############################################

def Build_conn(N):
    # connectivity 1st half
    Build_Conn_1st_rec(0, int(math.log(N,2))-2, N, 0)  # start stage, end stage, N, index of starting
    # connectivity middle
    for i in range (Row):
        pe[i][int(math.log(N,2))-1].conn0 = pe[i][int(math.log(N,2))-2].conn0
        pe[i][int(math.log(N,2))-1].conn1 = pe[i][int(math.log(N,2))-2].conn1
    # connectivity 2nd half
    Build_Conn_2nd_rec(2*int(math.log(N,2))-3, int(math.log(N,2))-1, N, 0)  # start stage, end stage, N, index of starting
    # print connectivity
    if debug:
        print ('N=', N, 'row (i)', Row, 'col (j)', Column)
        print('\t\t\t', end='')
        for i in range(2*int(math.log(N,2))-1):
            print(i, '\t\t\t\t\t\t\t\t', end='')
        print()
        for i in range (Row):
            for j in range (Column):
                print (i, ':  con0', pe[i][j].conn0, 'con1', pe[i][j].conn1, end='\t')
            print ()
            if i == Row//2-1: print ()

##############################################
def print_states():
    print ()
    print ('N=', N, 'row (i)', Row, 'col (j)', Column)
    print ('\t\t\t', end='|')
    for i in range (2 * int (math.log (N, 2)) - 1):
        print (i, '\t\t\t\t', end='| ')
    print ()
    for i in range (Row):
        for j in range (Column):
            if pe[i][j].count>2 or pe[i][j].count<0: print('ERROR on count', i, j, pe[i][j].count)
            print (i, ':  stt cnt', pe[i][j].state, pe[i][j].count, end='|\t')
        print ()
        if i == Row // 2 - 1: print ()

##############################################
# find path
##############################################
def find_path(port_num, port_dem):
    changes = []
    cur_pe = port_num//2
    come_from = port_num%2
    if debug: print('\nfrom', port_num, 'to', port_dem)
    ####################################################
    # first logN-1 stages
    ####################################################
    for stage in range(int(math.log(N,2))-1):
        new_state = -1
        next_pe = -1
        # state is unknown
        if pe[cur_pe][stage].state == -1:
            if mode==0:     # Random
                new_state = random.randint(0,1)
            elif mode==1:    # LAA
                new_state = 1
            elif mode==2:   # TAA
                # check connectivity first
                up = pe[cur_pe][stage].conn0
                down = pe[cur_pe][stage].conn1
                state_up = pe[up[0]][stage+1].state
                state_down = pe[down[0]][stage+1].state
                #print('----', stage, pe[cur_pe][stage].index, 'up', up, state_up, 'down', down, state_down)
                if state_up==-1: new_state = 0
                elif state_down==-1: new_state = 1
                else: new_state = random.randint(0,1)

            changes.append([stage, cur_pe, new_state])

            if debug: print ('#input demand 0:', '\tstage=', stage, 'pe=', cur_pe, 'come_from=', come_from,\
                             'state=', new_state, 'next pe=', end=' ')
        # state is known
        else:
            new_state = pe[cur_pe][stage].state
            changes.append ([stage, cur_pe, new_state]) # RAMI---
            if debug: print('#INPUT demand 0:', '\tstage=', stage, 'pe=', cur_pe, \
                          'state=', new_state, end=' ')
        # set for next stage
        if new_state==0 and come_from==0 or new_state==1 and come_from==1:
            next_pe = pe[cur_pe][stage].conn0[0]
            next_come_from = pe[cur_pe][stage].conn0[1]
        else:
            next_pe = pe[cur_pe][stage].conn1[0]
            next_come_from = pe[cur_pe][stage].conn1[1]

        if debug: print ('next_pe', next_pe, 'to input', next_come_from)

        cur_pe = next_pe
        come_from = next_come_from

    ####################################################
    # next logN stages
    ####################################################
    demand_out = port_dem
    NN = N
    for stage in range(int(math.log(N,2))-1, Column):
        bad = 0
        if demand_out >= NN//2:
            bit = 1
            demand_out = demand_out - NN//2
        else: bit = 0
        NN = NN//2

        ####################################################
        # last stage
        ####################################################
        if stage == Column-1:
            if pe[cur_pe][stage].state == -1:
                if come_from==0 and port_dem%2==0 or come_from==1 and port_dem%2==1: new_state = 0
                else: new_state = 1
                changes.append ([stage, cur_pe, new_state])

                #a = pe[cur_pe][stage].state==1 and (come_from^port_dem%2) or \
                #    pe[cur_pe][stage].state==1 and not(come_from^port_dem%2)

            elif (pe[cur_pe][stage].state==0 and (come_from==0 and port_dem%2==0 or come_from==1 and port_dem%2==1) or \
                 pe[cur_pe][stage].state==1 and (come_from==1 and port_dem%2==0 or come_from==0 and port_dem%2==1)):
                changes.append ([stage, cur_pe, new_state])

            elif not (pe[cur_pe][stage].state==0 and (come_from==0 and port_dem%2==0 or come_from==1 and port_dem%2==1) or \
                 pe[cur_pe][stage].state==1 and (come_from==1 and port_dem%2==0 or come_from==0 and port_dem%2==1)):
                bad = 1
                if debug: print('failed 1')
                break
            if debug: print ('#input demand 1:', '\tstage=', stage, 'pe=', cur_pe, 'come_from=', \
                             come_from, 'state=', new_state)
        ####################################################
        # not last stage
        ####################################################
        elif pe[cur_pe][stage].state >-1 and pe[cur_pe][stage].state == bit^come_from:
            new_state = pe[cur_pe][stage].state
            changes.append ([stage, cur_pe, pe[cur_pe][stage].state])   # RAMI---

        elif pe[cur_pe][stage].state >-1 and pe[cur_pe][stage].state != bit^come_from:
                bad = 1
                if debug: print ('#input demand 1:', '\tstage=', stage, 'pe=', cur_pe, 'come_from=',come_from, \
                                 'state=', pe[cur_pe][stage].state, 'need to be inverted')
                if debug: print('failed 2')
                break

        elif pe[cur_pe][stage].state == -1 or pe[cur_pe][stage].state == bit^come_from:
            if pe[cur_pe][stage].state == -1:
                new_state = bit^come_from
                changes.append ([stage, cur_pe, new_state])
            else:
                new_state = pe[cur_pe][stage].state

        if new_state == 0 and come_from == 0 or new_state == 1 and come_from == 1:
            next_pe = pe[cur_pe][stage].conn0[0]
            next_come_from = pe[cur_pe][stage].conn0[1]
        else:
            next_pe = pe[cur_pe][stage].conn1[0]
            next_come_from = pe[cur_pe][stage].conn1[1]
        if debug: print ('#input demand 1:', '\tstage=', stage, 'pe=', cur_pe, 'come_from=', come_from, \
                         'state=', new_state, 'next pe=', end=' ')
        if debug: print (next_pe, 'to input', next_come_from)
        cur_pe = next_pe
        come_from = next_come_from
    return changes, bad


####################################################
# Add path
####################################################
def ADD_PATH(port_num, port_dem):
    # search for path
    if debug1: print('Add   :', port_num, 'to', port_dem, end='\t')
    changes, bad = find_path(port_num, port_dem)
    if debug1: print('Add   :', 'changes', changes, 'bad=', bad)
    # if path is found, set the new states
    if len(changes)!=0 and bad == 0:
        #i_vec.remove(port_num)
        #o_vec.remove(port_dem)
        for c in changes:
            if pe[c[1]][c[0]].state==-1: pe[c[1]][c[0]].state = c[2]
            pe[c[1]][c[0]].count += 1
    if bad==0: return 1
    else: return 0

##############################################
# Remove path
##############################################
def REMOVE_PATH(in_p, out_p):
    # detect path
    if debug1: print ('Remove:', in_p, 'to', out_p, end='\t')
    changes, bad = find_path (in_p, out_p)
    if debug1: print ('Remove:', 'changes', changes, 'bad=', bad)
    if bad==0:
        # remove path
        for c in changes:
            if pe[c[1]][c[0]].state == -1:
                print (t, 'ERROR-2 removing path with state=-1', in_p, out_p)
                break
            pe[c[1]][c[0]].count -= 1
            if pe[c[1]][c[0]].count == 0: pe[c[1]][c[0]].state = -1
    if bad==0: return 1
    else: return 0

########################################################################################################################
########################################################################################################################

##############################################
# Main
##############################################
StartTime = time.time()

#random.seed(10)

Samples     = 100000      # number of time units
warmup      = 10         # percentage of time for warmup
mode        = 0         # 0: Random, 1: LLA, 2: TTA, 3: NEW
debug       = 0
debug1      = 0
debug2      = 0
f = open("data.txt", "w")
results = 'Mod\tN\tLoad\tUtil\tLatency\n'

setup = []
for m in range(3):
    for N in range(5, 11,1):
        for INLoad in range(10, 101, 10):
            setup.append([2**N, INLoad, m])

for s in setup:
    mode = s[2]
    N = s[0]                # network size
    in_load = s[1]          # input load 0-100
    Max_Size = 3*N
    Min_Size = 1*N
    sigma = N//8
    mu = N

    print ('N   \t', N)
    print ('Sample\t', Samples)
    print ('in load\t', in_load, '\t<---')
    print ('Warm t\t', warmup * Samples // 100)
    if   mode==0: print ('Random')
    elif mode==1: print ('LLA')
    elif mode==2: print ('TTA')
    #elif mode==3: print ('NEW')
    else:
        print ('Unknown mode', mode)
        exit(0)

    ####################################################
    # Setup variables
    ####################################################
    Row = N//2
    Column = int(2*math.log(N,2)-1)

    ####################################################
    # build matrix of PEs
    ####################################################
    pe = [[0 for j in range(Column)] for k in range(Row)]
    for k in range(Row):
        for j in range(Column):
            pe[k][j] = PE ([k, j])

    ####################################################
    # build connectivity into the matrix
    ####################################################
    Build_conn(N)

    ####################################################
    # Initialize variables
    ####################################################
    i_vec = random.sample ([x for x in range (N)], N)
    o_vec = random.sample ([x for x in range (N)], N)
    connection_hist = [0 for r in range(N+1)]         # histogram of number of connected paths

    cnt_input_load = 0              # count the input load
    count_connected = 0             # current number of connections
    total_count_connected = 0       # sum of current number of connections over all cycles
    max_connected = 0               # max current number of connections
    min_connected = N               # max current number of connections
    total_latency = 0
    total_con = 0
    remove_list = []

    out_timingwheel = [[] for x in range (42*N)]
    in_timingwheel = [[] for x in range (42*N)]
    add_vec = []
    rem_vec = []
    iport_time = [0 for x in range (N)]      # global time per input port, related to rate
    iport_insert_time = [0 for x in range (N)]

    ####################################################
    # Pre-load
    ####################################################
    for ind in range(N):
        duration = random.randint(Min_Size, Max_Size)
        #duration = int(random.normalvariate (mu, sigma))
        #if duration <= 1: duration = 2
        in_timingwheel[duration].append([i_vec[ind], -1, duration])
        iport_time[i_vec[ind]] = duration           # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
    if debug2: print('in_timingwheel\t', in_timingwheel)
    i_vec = []

    ####################################################
    # Run loop over 'Samples' time units
    ####################################################
    for tunit in range(Samples):

        ####################################################
        # reset counters after warm-up cycles
        ####################################################
        if tunit==Samples*warmup//100:
            total_count_connected = 0
            connection_hist = [0 for r in range(N + 1)]
            total_latency = 0
            total_con = 0
            if debug: print('------------ warm up completed ---------------')

        ####################################################
        # Add new add/remove events
        ####################################################
        add_arr = in_timingwheel.pop(0)
        in_timingwheel.append([])
        for item in add_arr:
            add_vec.append(item)
            if iport_time[item[0]]==0: iport_time[item[0]] = tunit
            iport_insert_time[item[0]] = tunit
        rem_arr = out_timingwheel.pop(0)
        out_timingwheel.append([])
        for item in rem_arr:
            rem_vec.append(item)

        ####################################################
        # Add per event
        ####################################################
        adding = []
        if add_vec!=[]:
            adding = add_vec[0]
            in_p = adding[0]
            out_p = adding[1]
            if out_p==(-1): out_p=o_vec.pop(random.randrange(len(o_vec)))
            dur = adding[2]
            able = ADD_PATH (in_p, out_p)
            if able == 1:
                count_connected += 1
                add_vec.pop(0)
                out_timingwheel[dur-1].append([in_p, out_p, dur])
            else:
                add_vec[0][1] = out_p
                next_entry = add_vec.pop(0)        # <<<<<<<<<<<<<<<< RAMI IMPROVEMENT
                add_vec.insert(1,next_entry)       # <<<<<<<<<<<<<<<< RAMI IMPROVEMENT
            if debug2: print(tunit, '\tAdd\t', in_p, '-->', out_p, 'able=', able, '\tdur', dur, '\t#connected', count_connected, 'latency', latency, 't', tunit, iport_time[in_p])

        ####################################################
        # Remove per event
        ####################################################
        removing = []
        if rem_vec!=[]:
            removing = rem_vec.pop(0)
            in_p = removing[0]
            out_p = removing[1]
            dur = removing[2]
            latency = tunit - iport_insert_time[in_p] - dur
            if REMOVE_PATH(in_p, out_p) == 1:
                o_vec.append(out_p)
                count_connected -= 1
                if debug2: print (tunit, '\tRem\t', in_p, '-->', out_p, '\t#connected', count_connected, 'latency', latency, end='\t')#o_vec, 'iportTime', iport_time[in_p], end='\t')
            else: print ('cycle', tunit, 'ERROR: can not remove path', a)
            total_latency += latency
            total_con += 1

            ####################################################
            # Generate new event
            ####################################################
            wait_time = dur + dur*(100//in_load)
            iport_time[in_p] += wait_time
            #duration = random.randint(Min_Size, Max_Size)
            duration = int(random.normalvariate(mu, sigma))
            if duration <= 1: duration = 2
            out_p = -1

            if wait_time>len(in_timingwheel): print('ERROR: small timing wheel', tunit, '\t', wait_time, len(in_timingwheel))
            if wait_time == 0: wait_time = 1
            if iport_time[in_p]<=tunit:
                in_timingwheel[0].append([in_p, out_p, duration])
                if debug2: print('\tFuture\t', in_p, '-->', out_p, 'wait', 'NOW', 'new dur', duration, '\t', 'port glb time', iport_time[in_p])
            else:
                in_timingwheel[wait_time-1].append([in_p, out_p, duration])
                if debug2: print('\tFuture\t', in_p, '-->', out_p, 'wait', wait_time, 'new dur', duration, '\t', 'port glb time', iport_time[in_p])

        ####################################################
        # Update count remove and add
        ####################################################
        if count_connected>max_connected: max_connected = count_connected
        if count_connected<min_connected: min_connected = count_connected
        total_count_connected += count_connected
        connection_hist[count_connected] += 1

    # end of loop over time

    ####################################################
    # Statistics
    ####################################################
    #for x in range (N): print (x, ':', input_queues[x])
    print('maximum connected\t', max_connected)
    print('minimum connected\t', min_connected)
    print('average utilization\t', round(100*total_count_connected/N/(Samples-Samples*warmup//100),2))
    if total_con==0: total_con = 1
    print('total latency', round(total_latency/total_con,2), total_con, total_latency)
    print('connection hist', end = '\t')
    for a in range(N+1):
        print(connection_hist[a], end='\t')
    print()

    # End of loop on samples
    if debug1: print_states()

    results += str(mode) + '\t' + str(N) + '\t' + str(in_load) + '\t' + str(round(100*total_count_connected/N/(Samples-Samples*warmup//100),2)) + '\t' + str(round(total_latency/total_con,2)) + '\n'

# end of loop over N
###################################################
print('exec time', round(time.time()-StartTime,3))
print(results)
f.write(results)
f.close()
######################################################################################

#a = input()