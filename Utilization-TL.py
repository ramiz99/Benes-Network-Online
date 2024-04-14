##############################################
# adaptive routing testing
##############################################

import random
import math

##############################################
##############################################

class PE:
    def __init__(self, index):
        self.index = index
        self.state = -1
        self.conn0 =  [-1, -1]  # number of next PE, inp0/1
        self.conn1 =  [-1, -1]  # number of next PE, inp0/1

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
    print ('\t\t\t', end='')
    for i in range (2 * int (math.log (N, 2)) - 1):
        print (i, '\t\t\t\t', end='')
    print ()
    for i in range (Row):
        for j in range (Column):
            print (i, ':  state', pe[i][j].state, end='\t')
        print ()
        if i == Row // 2 - 1: print ()


##############################################
# find path
##############################################
def find_path(port_num, port_dem, success):
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
            if MODE==0:         # RANDOM
                new_state = random.randint(0,1)
            elif MODE==1:       # LLA
                new_state = 1
            else:                # TAA
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

            if debug: print ('#input demand 0:', ind, '\tstage=', stage, 'pe=', cur_pe, 'come_from=', come_from,\
                             'state=', new_state, 'next pe=', end=' ')
        # state is known
        else:
            new_state = pe[cur_pe][stage].state
        # set for next stage
        if new_state==0 and come_from==0 or new_state==1 and come_from==1:
            next_pe = pe[cur_pe][stage].conn0[0]
            next_come_from = pe[cur_pe][stage].conn0[1]
        else:
            next_pe = pe[cur_pe][stage].conn1[0]
            next_come_from = pe[cur_pe][stage].conn1[1]

        if debug: print (next_pe, 'to input', next_come_from)

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

            elif not (pe[cur_pe][stage].state==0 and (come_from==0 and port_dem%2==0 or come_from==1 and port_dem%2==1) or \
                 pe[cur_pe][stage].state==1 and (come_from==1 and port_dem%2==0 or come_from==0 and port_dem%2==1)):
                bad = 1
                if debug: print('failed 1')
                success -= 1
                break
            if debug: print ('#input demand 1:', ind, '\tstage=', stage, 'pe=', cur_pe, 'come_from=', \
                             come_from, 'state=', new_state)
        ####################################################
        # not last stage
        ####################################################
        elif pe[cur_pe][stage].state >-1 and pe[cur_pe][stage].state != bit^come_from:
                bad = 1
                success -= 1
                if debug: print ('#input demand 1:', ind, '\tstage=', stage, 'pe=', cur_pe, 'come_from=',come_from, \
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
            if debug: print ('#input demand 1:', ind, '\tstage=', stage, 'pe=', cur_pe, 'come_from=', come_from, \
                             'state=', new_state, 'next pe=', end=' ')
            if debug: print (next_pe, 'to input', next_come_from)
            cur_pe = next_pe
            come_from = next_come_from
    return changes, bad, success

########################################################################################################################

##############################################
# Main
##############################################

#N           = 32      # must be 8 or greater for the recursion
#Row         = N//2
#Column      = int(2*math.log(N,2)-1)
Samples     = 100000
MODE        = 1       # 0: random, 1: LLA, 2: TTA
#in_load     = 100    # percentage out of 100
debug       = 0

print('Sample\t', Samples)
#print('In load\t', in_load)
if MODE==0: print('RANDOM')
elif MODE==1: print('LLA')
elif MODE==2: print('TTA')
else: 
    print('Unknown mode', MODE)
    exit(0)
print('N \t InLoad \t % \tHistogram')

for N in (16, 32, 64, 128, 256, 512, 1024):
    for in_load in range(100, 101, 10):
        Row = N//2
        Column = int(2*math.log(N,2)-1)
        success_hist = [0 for x in range(N+1)]
        cnt_input_load = 0

        # build matrix of PEs
        pe = [[0 for j in range(Column)] for k in range(Row)]
        for k in range(Row):
            for j in range(Column):
                pe[k][j] = PE ([k, j])

        ####################################################
        # build connectivity into the matrix
        ####################################################
        Build_conn(N)

        ####################################################
        # run multiple input permutations
        ####################################################
        routed = 0
        for i in range(Samples):

            # clear PEs
            for k in range (Row):
                for j in range (Column):
                    pe[k][j].state = -1

            ####################################################
            # generate permutation
            ####################################################
            i_vec = random.sample ([x for x in range (N)], N)
            o_vec = random.sample ([x for x in range (N)], N)

            # reduce demands based on in_load
            if in_load<100:
                cnt_input_load += N-N*in_load/100
                while cnt_input_load>0:
                    x = random.randint(0,N-1)
                    while(o_vec[x]==-1):
                        x = random.randint (0, N - 1)
                    o_vec[x] = -1
                    cnt_input_load -= 1

            if debug: print(i_vec, o_vec)
            list_of_paths = []
            failures = 0

            ####################################################
            # loop over demands of current permutation
            ####################################################
            success = N
            for ind in range(N):
                port_num = i_vec[ind]
                port_dem = o_vec[ind]
                # find path
                if port_dem==-1:
                    success -= 1
                else:
                    changes, bad, success = find_path(port_num, port_dem, success)
                    # if path is found, set the new states
                    if len(changes)!=0 and bad == 0:
                        for c in changes:
                            pe[c[1]][c[0]].state = c[2]
            # End of loop on samples
            routed += success
            success_hist[success] += 1
            if debug: print_states()

        ####################################################
        # Statistics
        ####################################################
        print(N, '\t', in_load, '\t', round(100*routed/Samples/N,2), end='\t')


        for i in range(len(success_hist)):
            print(round(100*success_hist[i]/Samples/N, 3), end='\t')

        print()
# end of loop on N

#input('press any key to complete')
