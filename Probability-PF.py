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
        self.tmp_state = 0
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


##############################################
# Main
##############################################

#N       = 32      # must be 8 or greater for the recursion
#Row     = N//2
#Column  = int(2*math.log(N,2)-1)
Samples = 100000
debug   = 0
StartTime = time.time()

print('Sample\t', Samples)
print('PathFinder')
print('N\t   Load\t   succ%\t#perm\trouted')

for NN in range(5, 11):
    N = 2**NN
    for ld in range(1,8):
        Load =ld * (N//8)
        Row = N//2
        Column = int(2*math.log(N,2)-1)

        ###################################################
        # build switch: matrix of PEs
        ###################################################
        pe = [[0 for j in range(Column)] for i in range(Row)]
        for i in range(Row):
            for j in range(Column):
                pe[i][j] = PE ([i, j])

        ###################################################
        # build connectivity into the matrix
        ###################################################
        Build_conn(N)
        if debug: print_connectivity()

        routed = 0
        perm_cnt = 0
        # run multiple input permutations
        for i in range(Samples):
            ###################################################
            # clear PEs
            ###################################################
            for k in range (Row):
                for j in range (Column):
                    pe[k][j].state = -1
                    pe[k][j].forward = 0
                    pe[k][j].backward = 0
                    pe[k][j].tmp_state = -1

            ###################################################
            # generate permutation
            ###################################################
            i_vec = random.sample ([x for x in range (N)], N)
            o_vec = random.sample ([x for x in range (N)], N)

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
                             [cur_pe, input_from] = pe[cur_pe][stage].fc0
                        else: [cur_pe, input_from] = pe[cur_pe][stage].fc1

                if pe[cur_pe][stage].state==0 and input_from==0 or pe[cur_pe][stage].state==1 and input_from==1:
                    port_dem = cur_pe*2
                else: port_dem = cur_pe*2+1
                #print('***', port_dem)
                o_vec.remove(port_dem)
            success_cnt = Load

            ########################################################################################################
            '''
            ###################################################
            # loop over demands of current permutation
            ###################################################
            success_cnt = 0
            for ind in range(N):
                out_ports = []
                in_ports = []
                port_num = random.choice (i_vec)
                port_dem = random.choice (o_vec)
                #port_num = i_vec[ind]
                #port_dem = o_vec[ind]

                ###################################################
                # find forward paths
                ###################################################
                list_of_pes = [[port_num//2, port_num%2]]
                for stage in range(2*int(math.log(N,2))-1):
                    new_list_of_pes = []
                    for cur_pe in list_of_pes:
                        pe[cur_pe[0]][stage].forward = 1
                        if pe[cur_pe[0]][stage].state == -1:
                            if pe[cur_pe[0]][stage].fc0 not in new_list_of_pes:
                                new_list_of_pes.append(pe[cur_pe[0]][stage].fc0)
                            if pe[cur_pe[0]][stage].fc1 not in new_list_of_pes:
                                new_list_of_pes.append(pe[cur_pe[0]][stage].fc1)
                        elif pe[cur_pe[0]][stage].state == 0:
                            if cur_pe[1]%2==0:
                                if pe[cur_pe[0]][stage].fc0 not in new_list_of_pes:
                                    new_list_of_pes.append(pe[cur_pe[0]][stage].fc0)
                            else:
                                if pe[cur_pe[0]][stage].fc1 not in new_list_of_pes:
                                    new_list_of_pes.append(pe[cur_pe[0]][stage].fc1)
                        else:
                            if cur_pe[1]%2==0:
                                if pe[cur_pe[0]][stage].fc1 not in new_list_of_pes:
                                    new_list_of_pes.append(pe[cur_pe[0]][stage].fc1)
                            else:
                                if pe[cur_pe[0]][stage].fc0 not in new_list_of_pes:
                                    new_list_of_pes.append(pe[cur_pe[0]][stage].fc0)
                    list_of_pes = new_list_of_pes[:]
                for e in list_of_pes:
                    out_ports.append(e[0])

                ###################################################
                # find backward paths, if forward path exists
                ###################################################
                if port_dem in out_ports:
                    list_of_pes = [[port_dem//2, port_dem%2]]
                    for stage in range(2*int(math.log(N,2))-2, -1, -1):
                        new_list_of_pes = []
                        for cur_pe in list_of_pes:
                            pe[cur_pe[0]][stage].backward = 1
                            if pe[cur_pe[0]][stage].state == -1:
                                if pe[cur_pe[0]][stage].bc0 not in new_list_of_pes:
                                    new_list_of_pes.append (pe[cur_pe[0]][stage].bc0)
                                if pe[cur_pe[0]][stage].bc1 not in new_list_of_pes:
                                    new_list_of_pes.append (pe[cur_pe[0]][stage].bc1)
                            elif pe[cur_pe[0]][stage].state == 0:
                                if cur_pe[1]%2==0:  # odd
                                    if pe[cur_pe[0]][stage].bc0 not in new_list_of_pes:
                                        new_list_of_pes.append (pe[cur_pe[0]][stage].bc0)
                                else:
                                    if pe[cur_pe[0]][stage].bc1 not in new_list_of_pes:
                                        new_list_of_pes.append (pe[cur_pe[0]][stage].bc1)
                            else:
                                if cur_pe[1]%2==0:
                                    if pe[cur_pe[0]][stage].bc1 not in new_list_of_pes:
                                        new_list_of_pes.append (pe[cur_pe[0]][stage].bc1)
                                else:
                                    if pe[cur_pe[0]][stage].bc0 not in new_list_of_pes:
                                        new_list_of_pes.append (pe[cur_pe[0]][stage].bc0)
                        list_of_pes = new_list_of_pes[:]
                    for e in list_of_pes:
                        in_ports.append (e[0])

                    if debug:
                        print ('out ports  ', out_ports)
                        print ('in ports ', in_ports)
                        print(port_num, '-->', port_dem, 'path exist=', port_num in out_ports and port_dem in in_ports)
                        print('\tout ports', out_ports, 'in ports', in_ports)

                ###################################################
                # select path if exists
                ###################################################
                if port_dem in out_ports and port_num in in_ports:
                    i_vec.remove(port_num)
                    o_vec.remove(port_dem)
                    success_cnt += 1
                    cur_pe = [port_num//2, port_num%2]
                    for stage in range (2*int(math.log(N,2))-1):
                        # last stage
                        if stage == 2*int(math.log(N,2))-2:
                            if pe[cur_pe[0]][stage].state == -1:
                                if cur_pe[1]==0 and port_dem%2==0 or cur_pe[1]==1 and port_dem%2==1:
                                    pe[cur_pe[0]][stage].state = 0
                                else:
                                    pe[cur_pe[0]][stage].state = 1
                            if debug: print('\t-->', 'stage:', stage, 'cur pe:', cur_pe, 'state', pe[cur_pe[0]][stage].state)
                        else:
                            # set up/down options
                            up = pe[cur_pe[0]][stage].fc0
                            down = pe[cur_pe[0]][stage].fc1
                            up_ok = pe[up[0]][stage + 1].forward == 1 and pe[up[0]][stage + 1].backward == 1
                            down_ok = pe[down[0]][stage + 1].forward == 1 and pe[down[0]][stage + 1].backward == 1
                            if debug: print('\t-->', 'stage:', stage, 'cur pe:', cur_pe, 'up ok:', up_ok, 'down ok:', down_ok)
                            # set state of current PE
                            if pe[cur_pe[0]][stage].state == -1:
                                if up_ok:
                                    pe[cur_pe[0]][stage].state = cur_pe[1]
                                    cur_pe = up
                                elif down_ok:
                                    pe[cur_pe[0]][stage].state = (1+cur_pe[1])%2
                                    cur_pe = down
                                else:
                                    print('ERROR1', i_vec, o_vec)
                            elif pe[cur_pe[0]][stage].state == 0:
                                if cur_pe[1]==0 and up_ok: cur_pe = up
                                elif cur_pe[1]==1 and down_ok: cur_pe = down
                                else: print('ERROR2', i_vec, o_vec)
                            elif pe[cur_pe[0]][stage].state == 1:
                                if cur_pe[1]==1 and up_ok: cur_pe = up
                                elif cur_pe[1]==0 and down_ok: cur_pe = down
                                else: print('ERROR3', i_vec, o_vec)
                            else: print('ERROR4', i_vec, o_vec)
                            if debug: print('\t\t\t' , 'up:', up, 'down', down, 'selected:', stage+1, cur_pe)

                if debug:
                    for i in range (Row):
                        for j in range (Column):
                            print (i, ':  stt', pe[i][j].state, 'f', pe[i][j].forward, 'b', pe[i][j].backward, end='|\t')
                        print ()
                        if i == Row // 2 - 1: print ()
                ###################################################
                # clear forward/backward indications
                ###################################################
                for k in range (Row):
                    for j in range (Column):
                        pe[k][j].forward = 0
                        pe[k][j].backward = 0
                if debug:
                    print('success:', success_cnt)
                    print('----------------------------------------------------------')

                if success_cnt == Load: break
            # end of loop over permutation
            '''

            ####################################################
            # try 1 demand
            ####################################################
            out_ports = []
            in_ports = []
            add_cnt = 0
            if success_cnt == Load:
                perm_cnt += 1
                port_num = random.choice (i_vec)
                port_dem = random.choice (o_vec)

                ########
                ###################################################
                # find forward paths
                ###################################################
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
                ########
                if port_dem in out_ports and port_num in in_ports:
                    add_cnt += 1
                    i_vec.remove (port_num)
                    o_vec.remove (port_dem)
                    routed += 1

        ###################################################
        # Statistics
        ###################################################

        #if perm_cnt==0: print(N, '  \t', Load, '  \t', 0)
        #else: print(N, '  \t', Load, '  \t', round(100*routed/Samples,2), '\t', round(100*routed/perm_cnt,2), '\t', routed, '\t', perm_cnt, '\t', Samples)
        #else: print(N, '  \t', Load, '  \t', round(100*routed/perm_cnt,2), '\t\t', perm_cnt, '\t', Samples)

        print(N, '  \t', Load, '  \t', round(100*routed/Samples,2), '\t', perm_cnt, '\t', routed)

# end of loops over N over load
###################################################

print('exec time', round(time.time()-StartTime,3))

