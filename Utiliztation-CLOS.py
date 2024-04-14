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

##############################################
##############################################

##############################################
# Find path
##############################################
def find_path(sqrt_N, port_num, port_dem):
    in_port_found = 0
    out_port_found = 0
    path_exists = 0
    ###################################################
    # find backward paths
    ###################################################
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
        if port_num == e[0]: in_port_found = 1

    ###################################################
    # find forward paths, if forward path exists
    # if reaching the input port, establish a path
    ###################################################
    if in_port_found:
        '''
        list_of_pes = [[[port_num // sqrt_N, 0], [(port_num % sqrt_N) // 2, 0], port_num % 2]]  # start PE
        for stage in range (3 * (2 * int (math.log (sqrt_N, 2)) - 1)):
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
                        new_list_of_pes.append (bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0)
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1 not in new_list_of_pes:
                        new_list_of_pes.append (bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1)
                elif bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 0 and pe_in == 0 or \
                        bsw[bsw_r][bsw_c].pe[pe_row][pe_col].state == 1 and pe_in == 1:
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0 not in new_list_of_pes:
                        new_list_of_pes.append (bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc0)
                else:
                    if bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1 not in new_list_of_pes:
                        new_list_of_pes.append (bsw[bsw_r][bsw_c].pe[pe_row][pe_col].fc1)
            list_of_pes = new_list_of_pes[:]
        for e in list_of_pes:
            if port_dem==e[0]: out_port_found = 1

        if out_port_found and in_port_found: path_exists = 1
        else: path_exists = 0
        '''
        path_exists = 1
    else: path_exists = 0

    if debug:
        print ('out port  ', out_port_found)
        print ('in port ', in_port_found)
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
            up_ok = bsw[usw_r][usw_c].pe[upe_r][upe_c].backward == 1 #and bsw[usw_r][usw_c].pe[upe_r][upe_c].forward==1
            down_ok = bsw[dsw_r][dsw_c].pe[dpe_r][dpe_c].backward == 1 #and bsw[dsw_r][dsw_c].pe[dpe_r][dpe_c].forward==1
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
def ADD_CLOS_path(sqrt_N, CLOS_port_i, CLOS_port_o):
    # search for path
    if debug: print ('Add   :', CLOS_port_i, 'to', CLOS_port_o, end='\t')
    path_exists = find_path (sqrt_N, CLOS_port_i, CLOS_port_o)
    # if path is found, set the new states
    if path_exists:
        changes = set_path(sqrt_N, CLOS_port_i, CLOS_port_o)
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

#random.seed(223)

Samples     = 100      # number of time units
mode        = 3         # 0: Random, 1: LLA, 2: TTA, 3: NEW
debug       = 0
debug1      = 0
debug2      = 0
f = open("data.txt", "w")
results = 'mode=' + str(mode) + '\n' + 'N\tLoad\tORate\tUtil\tAvgDly\tRelDly\n'

if mode==0: print ('Random')
elif mode==1: print ('LLA')
elif mode==2: print ('TTA')
elif mode==3: print ('NEW')
else:
    print ('Unknown mode', mode)
    exit(0)
print ('N\tSamples\t%Out\tHistogram\t\t inload = 100')

setup = []
for N in (6, 8, 10):
    for INLoad in range(100, 101, 10):
        setup.append([2**N, INLoad])

for s in setup:
    N = s[0]                # network size
    in_load = s[1]          # input load 0-100

    if N==16: Samples = 1000
    elif N==64: Samples = 10000
    elif N==256: Samples = 5000
    elif N==1024: Samples = 500

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

    # ##################################################################################################
    # ##################################################################################################

    success_hist = [0 for x in range (N + 1)]
    cnt_input_load = 0
    routed = 0

    ####################################################
    # run multiple input permutations
    ####################################################
    for i in range (Samples):

        if debug1: print(i, end=' ')

        ####################################################
        # Create 3xsqrt(N) sqrt(N)xsqrt(N) switches
        ####################################################
        # bsw indexing[row][column]
        bsw = [[0 for j in range(3)] for k in range(sqrt_N)]
        for r in range(sqrt_N):
            for c in range(3):
                bsw[r][c] = BenesSW([r,c], Row, Column) # col and row of a single switch
                bsw[r][c].Build_conn (r, c, sqrt_N)
            #    print(k,j, end='\t\t')
            #print()

        ####################################################
        # Create 3 stages CLOS
        ####################################################
        # connect between switches

        # Forward connections
        # source is:      [Switch [row,col], PE [row,Last-1], output I0/I1]
        # destination is: [Switch [row,col], PE [row,0], input I0/I1]

        # connecting 1st col to 2nd col
        for rr in range(sqrt_N): # output switch index [rr]
            for r in range(0,sqrt_N,2): bsw[rr][0].pe[r//2][Column-1].fc0 = [[r,1], [rr//2,0], rr%2]
            for r in range(1,sqrt_N,2): bsw[rr][0].pe[r//2][Column-1].fc1 = [[r,1], [rr//2,0], rr%2]
        # connecting 2nd col to 3rd col
        for rr in range(sqrt_N): # output switch index [rr]
            for r in range(0,sqrt_N,2): bsw[rr][1].pe[r//2][Column-1].fc0 = [[r,2], [rr//2,0], rr%2]
            for r in range(1,sqrt_N,2): bsw[rr][1].pe[r//2][Column-1].fc1 = [[r,2], [rr//2,0], rr%2]
        # connecting 3rd to ports
        for rr in range(sqrt_N): # output switch index [rr]
            for r in range(0,sqrt_N,2): bsw[rr][2].pe[r//2][Column-1].fc0 = [sqrt_N*rr+r]
            for r in range(1,sqrt_N,2): bsw[rr][2].pe[r//2][Column-1].fc1 = [sqrt_N*rr+r]

        # Backward connections
        # source is:      [Switch [row,col], PE [row,0], output I0/I1]
        # destination is: [Switch [row,col], PE [row,Column-1], input I0/I1]

        # connecting 1st to ports
        for rr in range(sqrt_N): # output switch index [rr]
            for r in range(0,sqrt_N,2): bsw[rr][0].pe[r//2][0].bc0 = [sqrt_N*rr+r]
            for r in range(1,sqrt_N,2): bsw[rr][0].pe[r//2][0].bc1 = [sqrt_N*rr+r]
        # connecting 2nd col to 1st col
        for rr in range(sqrt_N):
            for r in range(0,sqrt_N,2): bsw[rr][1].pe[r//2][0].bc0 = [[r,0], [rr//2,Column-1], rr%2]
            for r in range(1,sqrt_N,2): bsw[rr][1].pe[r//2][0].bc1 = [[r,0], [rr//2,Column-1], rr%2]
        # connecting 3rd col to 2nd col
        for rr in range(sqrt_N):
            for r in range(0,sqrt_N,2): bsw[rr][2].pe[r//2][0].bc0 = [[r,1], [rr//2,Column-1], rr%2]
            for r in range(1,sqrt_N,2): bsw[rr][2].pe[r//2][0].bc1 = [[r,1], [rr//2,Column-1], rr%2]

        if debug: print_conn(sqrt_N, Row, Column)

        ####################################################
        # generate permutation
        ####################################################
        i_vec = random.sample ([x for x in range (N)], N)
        o_vec = random.sample ([x for x in range (N)], N)

        # reduce demands based on in_load
        if in_load < 100:
            cnt_input_load += N - N * in_load / 100
            while cnt_input_load > 0:
                x = random.randint (0, N - 1)
                while (o_vec[x] == -1):
                    x = random.randint (0, N - 1)
                o_vec[x] = -1
                cnt_input_load -= 1

        if debug: print (i_vec, o_vec)
        list_of_paths = []

        ####################################################
        # loop over demands of current permutation
        ####################################################
        success = 0
        #print(o_vec)
        for ind in range (N):
            if debug1: print('.', end='')
            port_num = i_vec[ind]
            port_dem = o_vec[ind]
            # find path
            if port_dem != -1:
            #    success -= 1
            #else:
                able = ADD_CLOS_path (sqrt_N, port_num, port_dem)
                #print ('MAIN', port_num, '-->',  port_dem, '\t', able)
                if able==1: success += 1

        # End of loop on samples
        routed += success
        success_hist[success] += 1
        if debug1: print()

    ####################################################
    # Statistics
    ####################################################
    print (N, '\t', Samples, '\t', round (100 * routed / Samples / N, 2), end='\t')
    for i in range(len(success_hist)):
        #print(round(100*success_hist[i]/Samples/N, 3), end='\t')
        print (success_hist[i], end='\t')
    print ()
# end of loop on N




