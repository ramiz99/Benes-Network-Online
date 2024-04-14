##############################################
# adaptive routing testing
# find all paths
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
        self.fc0 = [-1, -1]  # number of next PE, inp0/1
        self.fc1 = [-1, -1]  # number of next PE, inp0/1
        self.bc0 = [-1, -1]
        self.bc1 = [-1, -1]
        self.forward = 0
        self.backward = 0
        self.count = 0

##############################################
##############################################

def Build_Conn_1st_rec(stage, max_stage, N, ind):
    for i in range(N//2):
        if i%2==0:
            pe[i+ind][stage].fc0 = [(i//2)+ind, 0]
            pe[i+ind][stage].fc1 = [(i//2)+ind+N//4, 0]
        else:
            pe[i+ind][stage].fc0 = [(i//2)+ind, 1]
            pe[i+ind][stage].fc1 = [(i//2)+ind+N//4, 1]
    if stage == max_stage: return
    Build_Conn_1st_rec(stage+1, max_stage, N//2, ind+0)
    Build_Conn_1st_rec(stage+1, max_stage, N//2, ind+N//4)

##############################################

def Build_Conn_2nd_rec(stage, max_stage, N, ind):
    for i in range(0, N, 2):
        if i<N//2:
            pe[i//2+ind][stage].fc0 = [ind+i, 0]
            pe[i//2+ind][stage].fc1 = [ind+i+1, 0]
        else:
            pe[i//2+ind][stage].fc0 = [ind+i-N//2, 1]
            pe[i//2+ind][stage].fc1 = [ind+i+1-N//2, 1]
    if stage == max_stage+1: return
    Build_Conn_2nd_rec(stage-1, max_stage, N//2, ind+0)
    Build_Conn_2nd_rec(stage-1, max_stage, N//2, ind+N//4)


##############################################
# Build connectivity
##############################################
def Build_conn(N):
    # connectivity 1st half
    Build_Conn_1st_rec(0, int(math.log(N,2))-2, N, 0)  # start stage, end stage, N, index of starting
    # connectivity middle
    for i in range (Row):
        pe[i][int(math.log(N,2))-1].fc0 = pe[i][int(math.log(N,2))-2].fc0
        pe[i][int(math.log(N,2))-1].fc1 = pe[i][int(math.log(N,2))-2].fc1
    # connectivity 2nd half
    Build_Conn_2nd_rec(2*int(math.log(N,2))-3, int(math.log(N,2))-1, N, 0)  # start stage, end stage, N, index of starting
    max_stage = 2*int(math.log (N, 2)) - 2
    # last stage to outputs
    for i in range (N//2):
        pe[i][max_stage].fc0 = [2*i, 0]
        pe[i][max_stage].fc1 = [2*i+1, 1]
    # copy backward connectivity
    for i in range (Row):
        for j in range (Column-1,-1,-1):
            pe[i][j].bc0 = pe[i][Column-j-1].fc0
            pe[i][j].bc1 = pe[i][Column-j-1].fc1
    if debug: print_connectivity()

##############################################
# print connectivity
##############################################
def print_connectivity():
    # print connectivity
    print ('N=', N, 'row (i)', Row, 'col (j)', Column)
    print('\t\t\t', end='')
    for i in range(2*int(math.log(N,2))-1):
        print(i, '\t\t\t\t\t\t\t', end='')
    print()
    for i in range (Row):
        for j in range (Column):
            print (i, ':  f0', pe[i][j].fc0, 'f1', pe[i][j].fc1, end='\t')
        print ()
        if i == Row//2-1: print ()
    print()
    print('\t\t\t', end='')
    for i in range(2*int(math.log(N,2))-1):
        print(i, '\t\t\t\t\t\t\t', end='')
    print()
    for i in range (Row):
        for j in range (Column):
            print (i, ':  b0', pe[i][j].bc0, 'b1', pe[i][j].bc1, end='\t')
        print ()
        if i == Row//2-1: print ()

##############################################
# print states and counts
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
# Find path
##############################################
def find_path(port_num, port_dem):
    out_ports = []
    in_ports = []
    ###################################################
    # find forward paths
    ###################################################
    path_exists = 0
    list_of_pes = [[port_num // 2, port_num % 2]]
    for stage in range (2 * int (math.log (N, 2)) - 1):
        new_list_of_pes = []
        for cur_pe in list_of_pes:
            pe[cur_pe[0]][stage].forward = 1
            if pe[cur_pe[0]][stage].state == -1:
                if pe[cur_pe[0]][stage].fc0 not in new_list_of_pes:
                    new_list_of_pes.append (pe[cur_pe[0]][stage].fc0)
                if pe[cur_pe[0]][stage].fc1 not in new_list_of_pes:
                    new_list_of_pes.append (pe[cur_pe[0]][stage].fc1)
            elif pe[cur_pe[0]][stage].state == 0:
                if cur_pe[1] % 2 == 0:
                    if pe[cur_pe[0]][stage].fc0 not in new_list_of_pes:
                        new_list_of_pes.append (pe[cur_pe[0]][stage].fc0)
                else:
                    if pe[cur_pe[0]][stage].fc1 not in new_list_of_pes:
                        new_list_of_pes.append (pe[cur_pe[0]][stage].fc1)
            else:
                if cur_pe[1] % 2 == 0:
                    if pe[cur_pe[0]][stage].fc1 not in new_list_of_pes:
                        new_list_of_pes.append (pe[cur_pe[0]][stage].fc1)
                else:
                    if pe[cur_pe[0]][stage].fc0 not in new_list_of_pes:
                        new_list_of_pes.append (pe[cur_pe[0]][stage].fc0)
        list_of_pes = new_list_of_pes[:]
    for e in list_of_pes:
        out_ports.append (e[0])

    ###################################################
    # find backward paths, if forward path exists
    ###################################################
    if port_dem in out_ports:
        list_of_pes = [[port_dem // 2, port_dem % 2]]
        for stage in range (2 * int (math.log (N, 2)) - 2, -1, -1):
            new_list_of_pes = []
            for cur_pe in list_of_pes:
                pe[cur_pe[0]][stage].backward = 1
                if pe[cur_pe[0]][stage].state == -1:
                    if pe[cur_pe[0]][stage].bc0 not in new_list_of_pes:
                        new_list_of_pes.append (pe[cur_pe[0]][stage].bc0)
                    if pe[cur_pe[0]][stage].bc1 not in new_list_of_pes:
                        new_list_of_pes.append (pe[cur_pe[0]][stage].bc1)
                elif pe[cur_pe[0]][stage].state == 0:
                    if cur_pe[1] % 2 == 0:  # odd
                        if pe[cur_pe[0]][stage].bc0 not in new_list_of_pes:
                            new_list_of_pes.append (pe[cur_pe[0]][stage].bc0)
                    else:
                        if pe[cur_pe[0]][stage].bc1 not in new_list_of_pes:
                            new_list_of_pes.append (pe[cur_pe[0]][stage].bc1)
                else:
                    if cur_pe[1] % 2 == 0:
                        if pe[cur_pe[0]][stage].bc1 not in new_list_of_pes:
                            new_list_of_pes.append (pe[cur_pe[0]][stage].bc1)
                    else:
                        if pe[cur_pe[0]][stage].bc0 not in new_list_of_pes:
                            new_list_of_pes.append (pe[cur_pe[0]][stage].bc0)
            list_of_pes = new_list_of_pes[:]
        for e in list_of_pes:
            in_ports.append (e[0])

        if port_dem in out_ports and port_num in in_ports:
            path_exists = 1
        else:
            path_exists = 0

        if debug:
            print ('out ports  ', out_ports)
            print ('in ports ', in_ports)
            print (port_num, '-->', port_dem, 'path exist=', path_exists)
            print ('\tout ports', out_ports, 'in ports', in_ports)
    return path_exists

##############################################
# Set path
##############################################
def set_path(port_num, port_dem):
    changes = []
    cur_pe = [port_num // 2, port_num % 2]
    for stage in range (2 * int (math.log (N, 2)) - 1):
        changes.append([stage, cur_pe[0]])
        pe[cur_pe[0]][stage].count += 1
        # last stage
        if stage == 2 * int (math.log (N, 2)) - 2:
            if pe[cur_pe[0]][stage].state == -1:
                if cur_pe[1] == 0 and port_dem % 2 == 0 or cur_pe[1] == 1 and port_dem % 2 == 1:
                    pe[cur_pe[0]][stage].state = 0
                else:
                    pe[cur_pe[0]][stage].state = 1
            if debug: print ('\t-->', 'stage:', stage, 'cur pe:', cur_pe, 'state', pe[cur_pe[0]][stage].state)
        else:
            # set up/down options
            up = pe[cur_pe[0]][stage].fc0
            down = pe[cur_pe[0]][stage].fc1
            up_ok = pe[up[0]][stage + 1].forward == 1 and pe[up[0]][stage + 1].backward == 1
            down_ok = pe[down[0]][stage + 1].forward == 1 and pe[down[0]][stage + 1].backward == 1
            if debug: print ('\t-->', 'stage:', stage, 'cur pe:', cur_pe, 'up:', up_ok, ', down:', down_ok)
            # set state of current PE
            if pe[cur_pe[0]][stage].state == -1:

                ''' SLIGHT IMPROVEMENT
                if up_ok and pe[up[0]][stage + 1].state != -1:
                    pe[cur_pe[0]][stage].state = cur_pe[1]
                    cur_pe = up
                elif down_ok and pe[down[0]][stage + 1].state != -1:
                    pe[cur_pe[0]][stage].state = (1 + cur_pe[1]) % 2
                    cur_pe = down
                elif up_ok:
                '''
                if up_ok:
                    pe[cur_pe[0]][stage].state = cur_pe[1]
                    cur_pe = up
                elif down_ok:
                    pe[cur_pe[0]][stage].state = (1 + cur_pe[1]) % 2
                    cur_pe = down
                else:
                    print ('ERROR1', port_num, port_dem)
            elif pe[cur_pe[0]][stage].state == 0:
                if cur_pe[1] == 0 and up_ok:
                    cur_pe = up
                elif cur_pe[1] == 1 and down_ok:
                    cur_pe = down
                else:
                    print ('ERROR2', port_num, port_dem)
            elif pe[cur_pe[0]][stage].state == 1:
                if cur_pe[1] == 1 and up_ok:
                    cur_pe = up
                elif cur_pe[1] == 0 and down_ok:
                    cur_pe = down
                else:
                    print ('ERROR3', port_num, port_dem)
            else:
                print ('ERROR4', port_num, port_dem)
            if debug: print ('\t\t\t', 'up:', up, 'down', down, 'selected:', stage + 1, cur_pe)
    if debug:
        for i in range (Row):
            for j in range (Column):
                print (i, ':  stt', pe[i][j].state, 'f', pe[i][j].forward, 'b', pe[i][j].backward, \
                       'c', pe[i][j].count, end='|\t')
            print ()
            if i == Row // 2 - 1: print ()
    return changes

##############################################
# Clear path
##############################################
def clear_path(port_num, port_dem):
    changes = []
    cur_pe = [port_num // 2, port_num % 2]
    for stage in range (2*int(math.log(N,2))-1):
        if pe[cur_pe[0]][stage].state == -1:
            print ('ERROR-11 removing path', port_num, port_dem)
            break
        changes.append([stage, cur_pe[0]])
        pe[cur_pe[0]][stage].count -= 1
        if pe[cur_pe[0]][stage].count == 0: pe[cur_pe[0]][stage].state = -1
        up = pe[cur_pe[0]][stage].fc0
        down = pe[cur_pe[0]][stage].fc1
        if stage<2*int(math.log(N,2))-2:
            up_ok = pe[up[0]][stage + 1].forward == 1 and pe[up[0]][stage + 1].backward == 1
            down_ok = pe[down[0]][stage + 1].forward == 1 and pe[down[0]][stage + 1].backward == 1
            if down_ok: cur_pe = down
            elif up_ok: cur_pe = up
            else: print('ERROR-12 removing path', port_num, port_dem)
    if debug:
        for i in range (Row):
            for j in range (Column):
                print (i, ':  stt', pe[i][j].state, 'f', pe[i][j].forward, 'b', pe[i][j].backward, \
                       'c', pe[i][j].count, end='|\t')
            print ()
            if i == Row // 2 - 1: print ()
    return changes

###################################################
# clear forward/backward indications
###################################################
def clear_fb_flags():
    for k in range (Row):
        for j in range (Column):
            pe[k][j].forward = 0
            pe[k][j].backward = 0

####################################################
# Add path
####################################################
def ADD_PATH(port_num, port_dem):
    # search for path
    if debug1: print ('Add   :', port_num, 'to', port_dem, end='\t')
    path_exists = find_path(port_num, port_dem)
    # if path is found, set the new states
    if path_exists:
        changes = set_path(port_num, port_dem)
        if debug1: print (changes, end='\t')
    if debug1: print (path_exists)
    clear_fb_flags()
    return path_exists


####################################################
# Remove path
####################################################
def REMOVE_PATH(in_p, out_p):
    # search for path
    if debug1: print ('Remove:', in_p, 'to', out_p, end='\t')
    path_exists = find_path(in_p, out_p)
    # if path is found, set the new states
    if path_exists:
        changes = clear_path(in_p, out_p)
        if debug1: print (changes, end='\t')
    #else:
    #    print('ERROR-, path does not exist to remove')
    #    break
    if debug1: print (path_exists)
    clear_fb_flags()
    return path_exists

#####################################################################################################

##############################################
# Main
##############################################
StartTime = time.time()

#random.seed(10)

Samples     = 100000      # number of time units
warmup      = 10         # percentage of time for warmup
mode        = 3         # 0: Random, 1: LLA, 2: TTA, 3: NEW
debug       = 0
debug1      = 0
debug2      = 0
f = open("data.txt", "w")
results = 'Mod\tN\tLoad\tUtil\tLatency\n'

setup = []
for N in range(10, 11,1):
    for INLoad in range(90, 101, 10):
        setup.append([2**N, INLoad])

for s in setup:
    mode = 3
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
    elif mode==3: print ('NEW')
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
        in_timingwheel[duration].append([i_vec[ind], -1, duration]) #[inPort, outPort, PacketLength]
    if debug2: print('in_timingwheel\t', in_timingwheel)
    i_vec = []

    ####################################################
    # Run loop over 'Samples' time units
    ####################################################
    for t in range(Samples):

        ####################################################
        # reset counters after warm-up cycles
        ####################################################
        if t==Samples*warmup//100:
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
            if iport_time[item[0]]==0: iport_time[item[0]] = t
            iport_insert_time[item[0]] = t
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
            able = ADD_PATH(in_p, out_p)
            if able == 1:
                count_connected += 1
                add_vec.pop(0)
                out_timingwheel[dur-1].append([in_p, out_p, dur])
            else:
                add_vec[0][1] = out_p
                next_entry = add_vec.pop(0)        # <<<<<<<<<<<<<<<< RAMI IMPROVEMENT
                add_vec.insert(1,next_entry)       # <<<<<<<<<<<<<<<< RAMI IMPROVEMENT
            if debug2: print(t, '\tAdd\t', in_p, '-->', out_p, 'able=', able, '\tdur', dur, '\t#connected', count_connected, iport_time[in_p])

        ####################################################
        # Remove per event
        ####################################################
        removing = []
        if rem_vec!=[]:
            removing = rem_vec.pop(0)
            in_p = removing[0]
            out_p = removing[1]
            dur = removing[2]
            latency = t - iport_insert_time[in_p] - dur
            if REMOVE_PATH(in_p, out_p) == 1:
                o_vec.append(out_p)
                count_connected -= 1
                if debug2: print (t, '\tRem\t', in_p, '-->', out_p, '\t#connected', count_connected, 'latency', latency, end='\t')#o_vec, 'iportTime', iport_time[in_p], end='\t')
            else: print ('cycle', t, 'ERROR: can not remove path', a)
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

            if wait_time>len(in_timingwheel): print('ERROR: small timing wheel', t, '\t', wait_time, len(in_timingwheel))
            if wait_time == 0: wait_time = 1
            if iport_time[in_p]<=t:
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
    f.write(results)
    results = ''
    f.flush()

# end of loop over N
###################################################
print('exec time', round(time.time()-StartTime,3))
print(results)
f.write(results)
f.close()
######################################################################################

