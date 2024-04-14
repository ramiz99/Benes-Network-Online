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
                break
            if debug: print ('#input demand 1:', ind, '\tstage=', stage, 'pe=', cur_pe, 'come_from=', \
                             come_from, 'state=', new_state)
        ####################################################
        # not last stage
        ####################################################
        elif pe[cur_pe][stage].state >-1 and pe[cur_pe][stage].state != bit^come_from:
                bad = 1
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
    return changes, bad

########################################################################################################################

##############################################
# Main
##############################################

#N           = 32      # must be 8 or greater for the recursion
#Row         = N//2
#Column      = int(2*math.log(N,2)-1)
#Load = N//4
Samples     = 100000
MODE        = 0      # 0: random, 1: LLA, 2: TTA
debug       = 0
#random.seed(12344)

print('Sample\t', Samples)
if MODE==0: print('RANDOM')
elif MODE==1: print('LLA')
elif MODE==2: print('TTA')
else: 
    print('Unknown mode', MODE)
    exit(0)
print('N\t   Load\t   succ%\t#perm\trouted')

for NN in range(5,11):
    N = 2 ** NN
    for ld in range(1,8):
        Load  = ld * (N//8)
        Row = N//2
        Column = int(2*math.log(N,2)-1)

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
        perm_cnt = 0

        for i in range(Samples):
            ####################################################
            # clear PEs
            ####################################################
            for k in range (Row):
                for j in range (Column):
                    pe[k][j].state = -1

            ####################################################
            # generate permutation
            ####################################################
            i_vec = [x for x in range (N)]
            o_vec = [x for x in range (N)]

            ####################################################
            # fill network with connections
            ####################################################

            for con in range(Load):
                port_num = random.choice (i_vec)
                i_vec.remove(port_num)
                cur_pe = port_num//2
                input_from = port_num%2
                #print('***', port_num)
                for stage in range(int(2*math.log(N,2))-1):
                    if pe[cur_pe][stage].state==-1:
                        pe[cur_pe][stage].state = random.randint(0,1)
                    #print('**', 'stage', stage, '\tpe', cur_pe, '\tin port', input_from, '\tstate', pe[cur_pe][stage].state)
                    if stage<int(2*math.log(N,2))-2:
                        if pe[cur_pe][stage].state==0 and input_from==0 or pe[cur_pe][stage].state==1 and input_from==1:
                             [cur_pe, input_from] = pe[cur_pe][stage].conn0
                        else: [cur_pe, input_from] = pe[cur_pe][stage].conn1

                if pe[cur_pe][stage].state==0 and input_from==0 or pe[cur_pe][stage].state==1 and input_from==1:
                    port_dem = cur_pe*2
                else: port_dem = cur_pe*2+1
                #print('***', port_dem)
                o_vec.remove(port_dem)
            success_cnt = Load
            
            
            '''
            success_cnt = 0
            for ind in range(6*N):
                port_num = random.choice (i_vec)
                port_dem = random.choice (o_vec)
                changes, bad = find_path(port_num, port_dem)    # find path
                if bad==0:                                      # if path is found, set the new states
                    success_cnt += 1
                    if len(changes)!=0:
                        for c in changes:
                            pe[c[1]][c[0]].state = c[2]
                    i_vec.remove(port_num)
                    o_vec.remove(port_dem)
                if success_cnt==Load: break
            '''

            ####################################################
            # try 1 demand
            ####################################################
            if success_cnt==Load:
                perm_cnt += 1
                add_cnt = 0
                for ind in range(1):
                    port_num = random.choice(i_vec)
                    port_dem = random.choice(o_vec)
                    changes, bad = find_path (port_num, port_dem)
                    if bad==0:
                        add_cnt += 1
                        #i_vec.remove (port_num)
                        #o_vec.remove (port_dem)
                #print(i, perm_cnt, add_cnt)

            # End of loop on samples

            routed += add_cnt
            if debug: print_states()

        ####################################################
        # Statistics
        ####################################################
        print(N, '  \t', Load, '  \t', round(100*routed/Samples,2), '\t', perm_cnt, '\t', routed)

# end of loop on N


#input('press any key to complete')
