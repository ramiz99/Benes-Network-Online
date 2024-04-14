##############################################
# adaptive routing testing
##############################################

import random
import math
import time
import copy

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
        self.tmp_state = 0
        self.count =  0         # number of connection through the SE

##############################################
##############################################

class BenesSW:
    def __init__(self, index, Row, Column):
        self.index = index
        self.pe = [[0 for j in range(Column)] for k in range(Row)]
        for r in range(Row):
            for c in range(Column):
                self.pe[r][c] = PE([r, c])

    ##############################################

    def Build_Conn_1st_rec(self, r, c, stage, max_stage, N, ind):
        for i in range(N//2):
            if i%2==0:
                self.pe[i+ind][stage].fc0 = [[r,c], [(i//2)+ind,stage+1], 0] # [(i//2)+ind, 0]
                self.pe[i+ind][stage].fc1 = [[r,c], [(i//2)+ind+N//4,stage+1], 0] # [(i//2)+ind+N//4, 0]
            else:
                self.pe[i+ind][stage].fc0 = [[r,c], [(i//2)+ind,stage+1], 1] # [(i//2)+ind, 1]
                self.pe[i+ind][stage].fc1 = [[r,c], [(i//2)+ind+N//4,stage+1], 1] # [(i//2)+ind+N//4, 1]
        if stage == max_stage: return
        self.Build_Conn_1st_rec(r, c, stage+1, max_stage, N//2, ind+0)
        self.Build_Conn_1st_rec(r, c, stage+1, max_stage, N//2, ind+N//4)

    ##############################################

    def Build_Conn_2nd_rec(self, r, c, stage, max_stage, N, ind):
        for i in range(0, N, 2):
            if i<N//2:
                self.pe[i//2+ind][stage].fc0 = [[r,c], [ind+i,stage+1], 0] # [ind+i, 0]
                self.pe[i//2+ind][stage].fc1 = [[r,c], [ind+i+1,stage+1], 0] # [ind+i+1, 0]
            else:
                self.pe[i//2+ind][stage].fc0 = [[r,c], [ind+i-N//2,stage+1], 1] # [ind+i-N//2, 1]
                self.pe[i//2+ind][stage].fc1 = [[r,c], [ind+i+1-N//2,stage+1], 1] # [ind+i+1-N//2, 1]
        if stage == max_stage+1: return
        self.Build_Conn_2nd_rec(r, c, stage-1, max_stage, N//2, ind+0)
        self.Build_Conn_2nd_rec(r, c, stage-1, max_stage, N//2, ind+N//4)

    ##############################################

    def Build_conn(self, r, c, N):
        if N==4:
            self.pe[0][0].fc0, self.pe[0][0].fc1 = [[r,c], [0, 1], 0], [[r,c], [1, 1], 0]
            self.pe[1][0].fc0, self.pe[1][0].fc1 = [[r,c], [0, 1], 1], [[r,c], [1, 1], 1]
            self.pe[0][1].fc0, self.pe[0][1].fc1 = [[r,c], [0, 2], 0], [[r,c], [1, 2], 0]
            self.pe[1][1].fc0, self.pe[1][1].fc1 = [[r,c], [0, 2], 1], [[r,c], [1, 2], 1]
            self.pe[0][2].fc0, self.pe[0][2].fc1 = [-1, -1], [-1, -1]
            self.pe[1][2].fc0, self.pe[1][2].fc1 = [-1, -1], [-1, -1]

            self.pe[0][0].bc0, self.pe[0][0].bc1 = [-1, -1], [-1, -1]
            self.pe[1][0].bc0, self.pe[1][0].bc1 = [-1, -1], [-1, -1]
            self.pe[0][1].bc0, self.pe[0][1].bc1 = [[r,c], [0, 0], 0], [[r,c], [1, 0], 0]
            self.pe[1][1].bc0, self.pe[1][1].bc1 = [[r,c], [0, 0], 1], [[r,c], [1, 0], 1]
            self.pe[0][2].bc0, self.pe[0][2].bc1 = [[r,c], [0, 1], 0], [[r,c], [1, 1], 0]
            self.pe[1][2].bc0, self.pe[1][2].bc1 = [[r,c], [0, 1], 1], [[r,c], [1, 1], 1]
        else:
            # connectivity 1st half
            self.Build_Conn_1st_rec(r, c, 0, int(math.log(N,2))-2, N, 0)  # start stage, end stage, N, index of starting
            # connectivity middle
            for i in range (Row):
                # self.pe[i][int(math.log(N,2))-1].fc0 = self.pe[i][int(math.log(N,2))-2].fc0
                # self.pe[i][int(math.log(N,2))-1].fc1 = self.pe[i][int(math.log(N,2))-2].fc1
                self.pe[i][int(math.log(N,2))-1].fc0 = copy.deepcopy(self.pe[i][int(math.log(N,2))-2].fc0)
                self.pe[i][int(math.log(N,2))-1].fc0[1][1] = self.pe[i][int(math.log(N,2))-1].fc0[1][1] + 1
                self.pe[i][int(math.log(N,2))-1].fc1 = copy.deepcopy(self.pe[i][int(math.log(N,2))-2].fc1)
                self.pe[i][int(math.log(N,2))-1].fc1[1][1] = self.pe[i][int(math.log(N,2))-1].fc1[1][1] + 1

            # connectivity 2nd half
            self.Build_Conn_2nd_rec(r, c, 2*int(math.log(N,2))-3, int(math.log(N,2))-1, N, 0)  # start stage, end stage, N, index of starting
            max_stage = 2*int(math.log (N, 2)) - 2
            # last stage to outputs
            for i in range (N//2):
                self.pe[i][max_stage].fc0 = [2*i, 0]
                self.pe[i][max_stage].fc1 = [2*i+1, 1]

            # copy backward connectivity
            for i in range (Row):
                for j in range (Column-1,-1,-1):
                    self.pe[i][j].bc0 = copy.deepcopy(self.pe[i][Column-j-1].fc0)
                    self.pe[i][j].bc1 = copy.deepcopy(self.pe[i][Column-j-1].fc1)

            for i in range (Row):
                for j in range (Column-1,0,-1):
                    self.pe[i][j].bc0[1][1] = j-1
                    self.pe[i][j].bc1[1][1] = j-1

    ##############################################

def print_conn(sqrt_N, Row, Column):
    print('\t0\t\t\t\t1\t\t\t\t2')
    for cc in range(3):
        for rr in range(sqrt_N):
            print('forward, sw', cc, rr)
            for q in range (Row):
                for p in range (Column):
                    print (bsw[rr][cc].pe[q][p].fc0, bsw[rr][cc].pe[q][p].fc1, end='\t|\t')
                print ()
            print ('_________________________________________________________________________________')
    print('\n\n')
    for cc in range(3):
        for rr in range(sqrt_N):
            print('backward, sw', cc, rr)
            for q in range (Row):
                for p in range (Column):
                    print (bsw[rr][cc].pe[q][p].bc0, bsw[rr][cc].pe[q][p].bc1, end='\t|\t')
                print ()
            print ('_________________________________________________________________________________')
    print()

def print_state(sqrt_N, Row, Column):
    print('\t0\t\t\t\t1\t\t\t\t2')
    for cc in range(3):
        for rr in range(sqrt_N):
            print('state, sw', cc, rr)
            for q in range (Row):
                for p in range (Column):
                    print (bsw[rr][cc].pe[q][p].fc0, bsw[rr][cc].pe[q][p].state, end='\t|\t')
                print ()
            print ('_________________________________________________________________________________')
    print('\n')

##############################################
##############################################

##############################################
# Find path
##############################################
def find_path(sqrt_N, port_num, port_dem):
    out_ports = []
    in_ports = []
    out_port_found = 0
    in_port_found = 0
    ###################################################
    # find forward paths
    ###################################################
    path_exists = 0
    list_of_pes = [[[port_dem // sqrt_N, 2], [(port_dem % sqrt_N) // 2, Column-1], port_dem % 2]]  # end PE
    for stage in range (3*(2*int(math.log(sqrt_N,2))-1)-1, -1, -1):
        new_list_of_pes = []
        for cur_pe in list_of_pes:
            bsw_r = cur_pe[0][0]
            bsw_c = cur_pe[0][1]
            pe_row = cur_pe[1][0]
            pe_col = cur_pe[1][1]
            pe_in = cur_pe[2]
            bsw[bsw_r][bsw_c].pe[pe_row][pe_col].backward = 1
            if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == -1:
                if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc0 not in new_list_of_pes:
                    new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc0)
                if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc1 not in new_list_of_pes:
                    new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc1)
            elif bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state==0 and pe_in==0 or \
                  bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state==1 and pe_in==1:
                if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc0 not in new_list_of_pes:
                    new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc0)
            else:
                if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc1 not in new_list_of_pes:
                    new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].bc1)
        list_of_pes = new_list_of_pes[:]
    for e in list_of_pes:
        #in_ports.append (e[0])
        if port_num == e[0]:
            in_port_found = 1

    ###################################################
    # find backward paths, if forward path exists
    ###################################################
    '''
    if port_num in in_ports:
        list_of_pes = [[[port_num//sqrt_N, 0], [(port_num%sqrt_N)//2, 0], port_num%2]]    # start PE
        for stage in range (3*(2*int(math.log(sqrt_N,2))-1)):
            new_list_of_pes = []
            for cur_pe in list_of_pes:
                bsw_r = cur_pe[0][0]
                bsw_c = cur_pe[0][1]
                pe_row = cur_pe[1][0]
                pe_col = cur_pe[1][1]
                pe_in = cur_pe[2]
                bsw[bsw_r][bsw_c].pe[pe_row][pe_col].forward = 1
                if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == -1:
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0 not in new_list_of_pes:
                        new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0)
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1 not in new_list_of_pes:
                        new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1)
                elif bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 0 and pe_in==0 or \
                    bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 1 and pe_in==1:
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0 not in new_list_of_pes:
                        new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0)
                else:
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1 not in new_list_of_pes:
                        new_list_of_pes.append(bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1)
            list_of_pes = new_list_of_pes[:]
        for e in list_of_pes:
            out_ports.append(e[0])
    '''

    if in_port_found: path_exists = 1
    else: path_exists = 0

    if debug:
        print ('out ports  ', out_ports)
        print ('in ports ', in_ports)
        print (port_num, '-->', port_dem, 'path exist=', path_exists)
    return path_exists

##############################################
# Set path
##############################################
def set_path(sqrt_N, port_num, port_dem):
    changes = []
    cur_pe = [[port_num // sqrt_N, 0], [(port_num % sqrt_N) // 2, 0], port_num % 2] # start PE
    for stage in range (3*(2*int(math.log(sqrt_N,2))-1)):
        bsw_r = cur_pe[0][0]
        bsw_c = cur_pe[0][1]
        pe_row = cur_pe[1][0]
        pe_col = cur_pe[1][1]
        pe_in = cur_pe[2]
        changes.append([stage, cur_pe])
        bsw[bsw_r][bsw_c].pe[pe_row][pe_col].count += 1
        # last stage
        if stage == 3*(2*int(math.log(sqrt_N,2))-1)-1:
            if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == -1:
                if pe_in==0 and port_dem%2==0 or pe_in==1 and port_dem%2==1:
                    bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state = 0
                else:
                    bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state = 1
            if debug: print ('set path', stage, '\t', cur_pe, ' || ',  'new state', bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state)
        else:
            # set up/down options
            up = bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0
            down = bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1
            usw_r, usw_c, upe_r, upe_c, uupdown = up[0][0], up[0][1], up[1][0], up[1][1], up[2]
            dsw_r, dsw_c, dpe_r, dpe_c, dupdown = down[0][0], down[0][1], down[1][0], down[1][1], down[2]
            up_ok = bsw[usw_r][usw_c].pe[upe_r][upe_c].backward == 1# and bsw[usw_r][usw_c].pe[upe_r][upe_c].forward==1
            down_ok = bsw[dsw_r][dsw_c].pe[dpe_r][dpe_c].backward == 1# and bsw[dsw_r][dsw_c].pe[dpe_r][dpe_c].forward==1
            if debug: ('set path', stage, '\t', cur_pe, ' || ',  up, up_ok, ' | ', down, down_ok)
            # set state of current PE
            if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == -1:
                if up_ok:
                    bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state = pe_in
                    cur_pe = up
                elif down_ok:
                    bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state = (1 + pe_in) % 2
                    cur_pe = down
                else: print ('ERROR1', port_num, port_dem)
            elif bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 0:
                if pe_in == 0   and up_ok:   cur_pe = up
                elif pe_in == 1 and down_ok: cur_pe = down
                else: print ('ERROR2', port_num, port_dem)
            elif bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 1:
                if pe_in == 1   and up_ok:   cur_pe = up
                elif pe_in == 0 and down_ok: cur_pe = down
                else: print ('ERROR3', port_num, port_dem)
            else: print ('ERROR4', port_num, port_dem)
    return changes

##############################################
# Clear path
##############################################
def clear_path(sqrt_N, port_num, port_dem):
    changes = []
    cur_pe = [[port_num // sqrt_N, 0], [(port_num % sqrt_N) // 2, 0], port_num % 2] # start PE
    for stage in range (3*(2*int(math.log(sqrt_N,2))-1)):
        bsw_r = cur_pe[0][0]
        bsw_c = cur_pe[0][1]
        pe_row = cur_pe[1][0]
        pe_col = cur_pe[1][1]
        pe_in = cur_pe[2]
        changes.append([stage, cur_pe])
        # set up/down options
        up = bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0
        down = bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1
        # follow the state of current PE
        if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 0:
            if pe_in == 0:   cur_pe = up
            elif pe_in == 1: cur_pe = down
            else: print ('ERROR2', port_num, port_dem)
        elif bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 1:
            if pe_in == 1:   cur_pe = up
            elif pe_in == 0: cur_pe = down
            else: print ('ERROR3', port_num, port_dem)
        else: print ('ERROR4', port_num, port_dem)
        bsw[bsw_r][bsw_c].pe[pe_row][pe_col].count -= 1
        if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].count == 0: bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state = -1
    return changes

###################################################
# clear forward/backward indications
###################################################
def clear_fb_flags(sqrt_N):
    for col in range(3):
        for row in range(sqrt_N):
            for k in range (Row):
                for j in range (Column):
                    bsw[row][col].pe[k][j].forward = 0
                    bsw[row][col].pe[k][j].backward = 0

####################################################
# Find CLOS path
#NO NEED TO CALCULATE, INSTEAD USE THE CONNECTIVITY ALREASY DEFINED IN THE LAST STAGE OF THE BENES
#               sw                          inPort                  outPort
# 1st stage:     [CLOS_port_i//sqrt_N][0]    CLOS_port_i%sqrt_N      x
# 2nd stage:     [x][1]                      [CLOS_port_i//sqrt_N]   CLOS_port_o//sqrt_N
# 3rd stage:     [CLOS_port_o//sqrt_N][2]    x                       CLOS_port_o%sqrt_N
####################################################
def ADD_CLOS_PATH(sqrt_N, CLOS_port_i, CLOS_port_o):
    # search for path
    if debug: print ('Add   :', CLOS_port_i, 'to', CLOS_port_o, end='\t')
    path_exists = find_path(sqrt_N, CLOS_port_i, CLOS_port_o)
    # if path is found, set the new states
    if path_exists:
        changes = set_path(sqrt_N, CLOS_port_i, CLOS_port_o)
        if debug: print (changes, end='\t')
    if debug: print (path_exists)
    clear_fb_flags(sqrt_N)
    return path_exists

####################################################
# Remove path
####################################################
def REMOVE_CLOS_PATH(sqrt_N, CLOS_port_i, CLOS_port_o):
    # search for path
    if debug: print ('Remove:', CLOS_port_i, 'to', CLOS_port_o, end='\t')
    path_exists = find_path(sqrt_N, CLOS_port_i, CLOS_port_o)
    # if path is found, set the new states
    if path_exists:
        changes = clear_path(sqrt_N, CLOS_port_i, CLOS_port_o)
        if debug: print (changes, end='\t')
    if debug: print (path_exists)
    clear_fb_flags(sqrt_N)
    return path_exists

########################################################################################################################
########################################################################################################################

##############################################
# Main
##############################################
StartTime = time.time()
#random.seed(23)

Samples     = 100000     # number of time units
warmup      = 10         # percentage of time for warmupdebug       = 0
debug = 0
f = open("data.txt", "w")
results = 'N\tLoad\tUtil\tLatency\n'

setup = []
for N in range(6, 11, 2):
    for INLoad in range(25, 101, 25):
        setup.append([2**N, INLoad])

print('CLOS')
print('N\t   Load\t   succ rate\t\t#perm')# \t %   \tHistogram')

for s in setup:
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

    ####################################################
    # Setup variables
    ####################################################
    CLOS_Row = N//2
    CLOS_Column = int(2*math.log(N,2)-1)

    if N==16: sqrt_N = 4
    elif N==64: sqrt_N = 8
    elif N==256: sqrt_N = 16
    elif N==1024: sqrt_N = 32

    Column = int(2*math.log2(sqrt_N)-1)
    Row = sqrt_N//2
    #print('     N=\t', N, 'rows=', CLOS_Row, 'cols=', CLOS_Column)
    #print('sqrt_N=\t', sqrt_N, '\tRow=\t', Row, '\tColumn=\t', Column)

    ####################################################
    # Create 3xsqrt(N) sqrt(N)xsqrt(N) switches
    ####################################################
    # bsw indexing[row][column]
    bsw = [[0 for j in range(3)] for k in range(sqrt_N)]
    for r in range(sqrt_N):
        for c in range(3):
            bsw[r][c] = BenesSW([r, c], Row, Column)  # col and row of a single switch
            bsw[r][c].Build_conn(r, c, sqrt_N)

    ####################################################
    # Create 3 stages CLOS
    ####################################################
    # connect between switches

    # Forward connections
    # source is:      [Switch [row,col], PE [row,Last-1], output I0/I1]
    # destination is: [Switch [row,col], PE [row,0], input I0/I1]

    # connecting 1st col to 2nd col
    for rr in range(sqrt_N):  # output switch index [rr]
        for r in range(0, sqrt_N, 2): bsw[rr][0].pe[r // 2][Column - 1].fc0 = [[r, 1], [rr // 2, 0], rr % 2]
        for r in range(1, sqrt_N, 2): bsw[rr][0].pe[r // 2][Column - 1].fc1 = [[r, 1], [rr // 2, 0], rr % 2]
    # connecting 2nd col to 3rd col
    for rr in range(sqrt_N):  # output switch index [rr]
        for r in range(0, sqrt_N, 2): bsw[rr][1].pe[r // 2][Column - 1].fc0 = [[r, 2], [rr // 2, 0], rr % 2]
        for r in range(1, sqrt_N, 2): bsw[rr][1].pe[r // 2][Column - 1].fc1 = [[r, 2], [rr // 2, 0], rr % 2]
    # connecting 3rd to ports
    for rr in range(sqrt_N):  # output switch index [rr]
        for r in range(0, sqrt_N, 2): bsw[rr][2].pe[r // 2][Column - 1].fc0 = [sqrt_N * rr + r]
        for r in range(1, sqrt_N, 2): bsw[rr][2].pe[r // 2][Column - 1].fc1 = [sqrt_N * rr + r]

    # Backward connections
    # source is:      [Switch [row,col], PE [row,0], output I0/I1]
    # destination is: [Switch [row,col], PE [row,Column-1], input I0/I1]

    # connecting 1st to ports
    for rr in range(sqrt_N):  # output switch index [rr]
        for r in range(0, sqrt_N, 2): bsw[rr][0].pe[r // 2][0].bc0 = [sqrt_N * rr + r]
        for r in range(1, sqrt_N, 2): bsw[rr][0].pe[r // 2][0].bc1 = [sqrt_N * rr + r]
    # connecting 2nd col to 1st col
    for rr in range(sqrt_N):
        for r in range(0, sqrt_N, 2): bsw[rr][1].pe[r // 2][0].bc0 = [[r, 0], [rr // 2, Column - 1], rr % 2]
        for r in range(1, sqrt_N, 2): bsw[rr][1].pe[r // 2][0].bc1 = [[r, 0], [rr // 2, Column - 1], rr % 2]
    # connecting 3rd col to 2nd col
    for rr in range(sqrt_N):
        for r in range(0, sqrt_N, 2): bsw[rr][2].pe[r // 2][0].bc0 = [[r, 1], [rr // 2, Column - 1], rr % 2]
        for r in range(1, sqrt_N, 2): bsw[rr][2].pe[r // 2][0].bc1 = [[r, 1], [rr // 2, Column - 1], rr % 2]

    if debug: print_conn(sqrt_N, Row, Column)

    # ##################################################################################################
    # ##################################################################################################

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
    if debug: print('in_timingwheel\t', in_timingwheel)
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
            able = ADD_CLOS_PATH(sqrt_N, in_p, out_p)
            if able == 1:
                count_connected += 1
                add_vec.pop(0)
                out_timingwheel[dur-1].append([in_p, out_p, dur])
            else:
                add_vec[0][1] = out_p
                next_entry = add_vec.pop(0)        # <<<<<<<<<<<<<<<< RAMI IMPROVEMENT
                add_vec.insert(1,next_entry)       # <<<<<<<<<<<<<<<< RAMI IMPROVEMENT
            if debug: print(t, '\tAdd\t', in_p, '-->', out_p, 'able=', able, '\tdur', dur, '\t#connected', count_connected, iport_time[in_p])

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
            if REMOVE_CLOS_PATH(sqrt_N, in_p, out_p) == 1:
                o_vec.append(out_p)
                count_connected -= 1
                if debug: print (t, '\tRem\t', in_p, '-->', out_p, '\t#connected', count_connected, 'latency', latency, end='\t')#o_vec, 'iportTime', iport_time[in_p], end='\t')
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
                if debug: print('\tFuture\t', in_p, '-->', out_p, 'wait', 'NOW', 'new dur', duration, '\t', 'port glb time', iport_time[in_p])
            else:
                in_timingwheel[wait_time-1].append([in_p, out_p, duration])
                if debug: print('\tFuture\t', in_p, '-->', out_p, 'wait', wait_time, 'new dur', duration, '\t', 'port glb time', iport_time[in_p])

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
    if debug: print_state(4,Row, Column)

    results += str(N) + '\t' + str(in_load) + '\t' + str(round(100*total_count_connected/N/(Samples-Samples*warmup//100),2)) + '\t' + str(round(total_latency/total_con,2)) + '\n'

# end of loop over N
###################################################
print('exec time', round(time.time()-StartTime,3))
print(results)
f.write(results)
f.close()
######################################################################################
