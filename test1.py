# this is for float hardware verfification
# only support dimension is divided by 4 in hardware
import numpy as np
from scipy import signal as sg
dim = 3; dep = 4; ker = 32
dim = 3;dep = 3;ker=64
dim_p=dim + 2
sq_ker = 16
pool_en = 0
av_pool_en = 0
random = 0 #TODO
sq_rep = 0 # repete squze kernl for last layer

###########quantization weight###########
from ctypes import *
# def q(x):
#     bits = cast(pointer(c_float(x)), POINTER(c_int32)).contents.value
#     bits = bits + 0x100000; # round off
#     bits=(bits>>21)<<21
#     return cast(pointer(c_int32(bits)), POINTER(c_float)).contents.value
# q8 = np.vectorize(q)
# def qq(x):
#     bits = cast(pointer(c_float(x)), POINTER(c_int32)).contents.value
#     e = ((bits&0x7F800000)>>23) - 112
#     if e<0:
#         bits=0
#     if e>31:
#         bits = bits & 0x807fffff
#         bits = bits | ((31+112)<<23)
#     # bits = bits + 0x010000;
#     # bits=(bits>>17)<<17
#     bits=bits&0xfffe0000
#     return cast(pointer(c_int32(bits)), POINTER(c_float)).contents.value
# q12 = np.vectorize(qq)

def dq(x):
    bits = cast(pointer(c_double(x)), POINTER(c_int64)).contents.value
    e = ((bits&0x7FF0000000000000)>>52) - 1008
    man = bits&0x000FC00000000000
    if e==0 and man==0:
        bits = 0
    if e<0:
        bits=0
    if e>31:
        bits = bits & 0x800fffffffffffff
        bits = bits | ((31+1008)<<52)
    # bits = bits + 0x010000;
    # bits=(bits>>17)<<17
    bits=bits&0xFFFFC00000000000
    return cast(pointer(c_int64(bits)), POINTER(c_double)).contents.value
dqv = np.vectorize(dq)

def d2b(x):
    x = cast(pointer(c_double(x)), POINTER(c_int64)).contents.value
    # print(hex(x))
    e = ((x&0x7FF0000000000000)>>52) - 1008
    man = x&0x000C000000000000
    sgn = x&0x8000000000000000
    if e<0:
        e = 0
        man = 0
        sgn = 0
    if e>31:
        e = 31
    bits = sgn>>56 | e<<2 | man>> 50# 64-8,2,52-2
    return np.uint8(bits)
d2bv = np.vectorize(d2b)

def b2d(x):
    ee = ((x&0x7c)>>2)+1008
    if((x&0x7c) == 0):
        if x&0x3==0:
            ee=0
        else:
            ee=1008
    bits = ((x&0x80)<<56) | (ee)<<52 | (x&0x3)<<50
    # print(hex(bits))
    return cast(pointer(c_int64(bits)), POINTER(c_double)).contents.value
b2dv = np.vectorize(b2d) 
# def byt_flt(x):
#     ee = ((x&0x7c)>>2)+112
#     if((x&0x7c) == 0):
#         if x&0x3==0:
#             ee=0
#         else:
#             ee=112
#     bits = ((x&0x80)<<24) | (ee)<<23 | (x&0x3)<<21
#     # print(hex(bits))
#     return cast(pointer(c_int32(bits)), POINTER(c_float)).contents.value
# b2f = np.vectorize(byt_flt)

# def flt_byt(x):
#     x = cast(pointer(c_float(x)), POINTER(c_int32)).contents.value
#     # print(hex(x))
#     e = ((x&0x7F800000)>>23) - 112
#     man = x&0x00600000
#     sgn = x&0x80000000
#     if e<0:
#         e = 0
#         man = 0
#         sgn = 0
#     if e>31:
#         e = 31
#     bits = sgn>>24 | e<<2 | man>>21
#     return np.uint8(bits)
# f2b = np.vectorize(flt_byt)

# def add(x):
#     while len(x)!=1:#hiearchical addition
#         t=[]
#         for a in range(0,len(x),2):
#             if a+1>=len(x):
#                 t.append(dq(x[a]))
#                 continue
#             t.append(dq(x[a])+dq(x[a+1]))
#         x=t
#     return x[0]

def add(x):
    np.set_printoptions(linewidth=np.inf)
    assert(x.size%128 == 0)
    prt = np.split(x,x.size//128)
    ans = []
    for i in prt:
        ii = i
        assert(ii.size==128)
        # print(ii)
        for n in range(0,3):#64-64 to 8-8 (1x1-3x3)
            t=[]
            for a in range(0,len(ii),2):
                t.append(dq(ii[a])+dq(ii[a+1]))
            ii = np.array(t)
        assert(ii.size==16)
        # print(ii)
        t=[]
        for a in range(0,8):
            t.append(dq(ii[a])+dq(ii[a+8]))
        ii=np.array(t)
        assert(ii.size==8)
        # print(ii)
        for n in range(0,3):
            t=[]
            for a in range(0,len(ii),2):
                t.append(dq(ii[a])+dq(ii[a+1]))
            ii = np.array(t)
        assert(ii.size==1)
        # print(ii)
        ans.append(ii[0])
    res = 0
    for a in ans:
        res = dq(res)+dq(a)
    return dq(res)

#######################         Input image
in_l = np.zeros(dim_p*dim_p*dep, dtype='uint8').reshape((dim_p,dim_p,dep))
if random == 0:
    in_ori = np.full(dim*dim*dep,0, dtype='uint8').reshape((dim,dim,dep))
    in_ori[:,:,0] = np.arange(dim*dim,dtype='uint8').reshape(dim,dim)
    # in_ori[:,:,1] = np.arange(dim*dim,dtype='uint8').reshape(dim,dim)
    # in_ori = np.random.randint(low = 0, high = 255, size = (dim*dim*dep),dtype='uint8').reshape((dim,dim,dep))
    # in_ori = np.full(dim*dim*dep,60,dtype='uint8').reshape((dim,dim,dep))
else:
    in_ori = np.random.randint(low = 0, high = 255, size = (dim,dim,dep), dtype='uint8')
in_l[1:-1,1:-1,:] = in_ori
f_in = open("input_layer.txt","w")
f_in_b = open("input_layer.bin","wb")
for z in range(0,dim):
    for y in range(0,dep):
        for x in range(0,dim):
            lis = in_l[z:z+3,x:x+3,y].flatten().tolist()
            for rep in range(0,ker,4):
                f_in.write(str(lis)[1:-1]+'\n')# already in byte
                f_in_b.write(bytearray(lis))
f_in_c = open("input_layer_c.txt","w")
f_in_c_b = open("input_layer_c.bin","wb")
for d in range(0,dep):
    for z in range(0,dim):
        for y in range(0,dim):
            lis = in_ori[z,y,d].flatten().tolist()
            f_in_c.write(str(lis)[1:-1]+'\n')
            f_in_c_b.write(bytearray(lis))
in_l = b2dv(in_l)
print("input layer");print(in_l[:,:,0]); 
########################        expand kernels 
# ker_l_1 = np.zeros(ker*dep, dtype='uint8').reshape((ker,dep))
ker_l_1 = np.full(ker*dep,0,dtype='uint8').reshape((ker,dep))
# ker_l_1 = np.random.randint(low = 0, high = 255, size = (ker*dep),dtype='uint8').reshape((ker,dep))
f_k_1 = open("ker_1x1.txt","w")
f_k_1_b = open("ker_1x1.bin","wb")
for z in range(0,dep):
    for x in range(0,ker,8):
        lis = ker_l_1[x:x+4,z][::-1]
        f_k_1_b.write(bytearray(lis))
        f_k_1.write(str(lis)[1:-1]+'\n')

        lis = ker_l_1[x+4:x+8,z][::-1]
        f_k_1_b.write(bytearray(lis))
        f_k_1.write(str(lis)[1:-1]+'\n')

# ker_l_3 = np.arange(ker*dep*9, dtype='uint8').reshape((ker,dep,9))
ker_l_3 = np.full(ker*dep*9,0,dtype='uint8').reshape((ker,dep,9))
ker_l_3[0,0,4]=60
# ker_l_3 = np.random.randint(low = 0, high = 255, size = (ker,dep,9),dtype='uint8').reshape((ker,dep,9))
# print(ker_l_3[0,0,:]);print("________")
f_k_3 = open("ker_3x3.txt","w")
f_k_3_b = open("ker_3x3.bin","wb")
for z in range(0,dep):
    lis = ker_l_3[:,z,:]
    for x in range(0,ker,8):
        for a in range(0,8):
            eig = lis[x+a,[7,8,3,4,5,0,1,2]] #reversed
            f_k_3_b.write(bytearray(eig))
            f_k_3.write(str(eig)[1:-1]+'\n')
        nin = lis[x:x+8,6].flatten() #no reversed 6 means 
        f_k_3_b.write(bytearray(nin))
        f_k_3.write(str(nin)[1:-1]+'\n')
ker_l_1 = b2dv(ker_l_1)
ker_l_3 = b2dv(ker_l_3)
print("expand kernel 1");print(ker_l_1[0,:])
print("expand kernel 3");print(ker_l_3[11, 0,:])
########################        exapnd bias
bis_1 = np.full(ker,0x00,dtype='uint8') #one
# bis_1 = np.random.randint(low = 0, high = 255, size = (ker),dtype='uint8')
bis_3 = np.full(ker,0x00,dtype='uint8')
# bis_3 = np.random.randint(low = 0, high = 255, size = (ker),dtype='uint8')
b_bis = open("bias.txt","w")
b_bis_b = open("bias.bin","wb")
for i in range(0,ker,4):
    lis_b3 = bis_3[i:i+4][::-1] # reverse
    lis_b1 = bis_1[i:i+4][::-1] #reverst
    b_bis.write(str(lis_b1)[1:-1]+'\n')
    b_bis.write(str(lis_b3)[1:-1]+'\n')
    b_bis_b.write(bytearray(lis_b1))
    b_bis_b.write(bytearray(lis_b3))
bis_1 = b2dv(bis_1) ######### convert to float
# print(sum(bis_1))
bis_3 = b2dv(bis_3)
print("exp1 bias");print(bis_1)
print("exp3 bias");print(bis_3)
#######################        expand convolution
out_1 = np.zeros(ker*dep*dim*dim, dtype='float64').reshape((ker,dep,dim,dim))
for k in range(0,ker):
    for l in range(0,dep):
        res = sg.convolve(in_l[:,:,l],[[ker_l_1[k,l]]] , "valid").astype(float)
        out_1[k,l,:,:]=dqv(res[1:-1,1:-1])

f_out_1 = open("out_1x1.txt","w")
f_out_1_b = open("out_1x1.bin","wb")
# out_1 = np.arange(ker*dep*dim*dim, dtype='uint8').reshape((ker,dep,dim,dim))
for r in range(0,dim):
    for d in range(0,dep):
        for c in range(0,dim):
            lis = d2bv( out_1[:,d,r,c])
            f_out_1_b.write(bytearray(lis))
            f_out_1.write(str(lis)[1:-1]+'\n')
print("exp1 add bf add")
print(out_1[0,0,:,:])

out_3 = np.zeros(ker*dep*dim*dim, dtype='float64').reshape((ker,dep,dim,dim))
for k in range(0,ker):
    for l in range(0,dep):
        # kk = np.rot90(ker_l_3[k,l].reshape((3,3)),2)
        kk = ker_l_3[k,l]
        for a in range(0,dim):
            for b in range(0,dim):
                ll = in_l[a:a+3,b:b+3,l].flatten()
                ll = np.multiply(kk,ll)
                l1 = dq(ll[0]) + dq(ll[1])
                l2 = dq(ll[5]) + dq(ll[4])
                l3 = dq(ll[3]) + dq(ll[8])
                l4 = dq(ll[7]) + dq(ll[6])
                l1 = dq(l1) + dq(l2)
                l2 = dq(l3) + dq(l4)
                l1 = dq(l1) + dq(l2)
                ll = dq(dq(l1) + dq(ll[2]) )
                out_3[k,l,a,b]=ll
        # res = sg.convolve(in_l[:,:,l],kk , "valid").astype(float) # addre lus #################### change to 12bit
        # out_3[k,l,:,:]=res
print("exp3 out bef add")
print(out_3[0,0,:,:])
# out_3 = np.arange(ker*dep*dim*dim, dtype='uint8').reshape((ker,dep,dim,dim))

f_out_3 = open("out_3x3.txt","w")
f_out_3_b = open("out_3x3.bin","wb")
for r in range(0,dim):
    for d in range(0,dep):
        for c in range(0,dim):
            lis = d2bv(out_3[:,d,r,c])
            f_out_3_b.write(bytearray(lis))
            f_out_3.write(str(list(lis))[1:-1]+'\n')

############################ add bias and relu
out_1_tmp = np.zeros(ker*dim*dim, dtype='float64').reshape((ker,dim,dim))
for a in range(0,ker):# for exp kernel addition is sequential
    for b in range(0,dim):
        for c in range(0,dim):
            ans = 0.0
            for i in range(dep):
                ans = dq(ans + dq(out_1[a,i,b,c]))
            out_1_tmp[a,b,c]=ans
# print(out_1_tmp[0,:,:])
out_1 = out_1_tmp
# out_1 = np.sum(out_1,1,dtype='float64') ########change to 12 bit
# print(out_1[0,:,:])
for i in range(0,ker):
    out_1[i,:,:] = dqv(dqv(out_1[i,:,:]) + dqv(bis_1[i]))
print("after expan1");print(out_1[0,:,:])
out_1[out_1 < 0] = 0.0 # no need for positive
exp_out_1 = open("exp_1.txt","w")
exp_out_1_b = open("exp_1.bin","wb")
for x in range(0,dim):
    for y in range(0,dim):
        lis=d2bv(out_1[:,x,y])
        exp_out_1_b.write(bytearray(lis))
        exp_out_1.write(str(lis)[1:-1]+'\n')


out_3_tmp = np.zeros(ker*dim*dim, dtype='float64').reshape((ker,dim,dim))
for a in range(0,ker):# for exp kernel addition is sequential
    for b in range(0,dim):
        for c in range(0,dim):
            ans = 0.0
            for i in range(dep):
                ans = dq(ans + dq(out_3[a,i,b,c]))
            out_3_tmp[a,b,c]=ans
out_3 = out_3_tmp
print("after expan3 add");print(out_3[0,:,:])
# out_3 = np.sum(out_3,1,dtype='float64') ############# change
for i in range(0,ker):
    out_3[i,:,:] = dqv(dqv(out_3[i,:,:]) + dqv(bis_3[i]))
out_3[out_3 < 0] = 0.0
exp_out_3 = open("exp_3.txt","w")
exp_out_3_b = open("exp_3.bin","wb")
for x in range(0,dim):
    for y in range(0,dim):
        lis=d2bv(out_3[:,x,y])
        exp_out_3_b.write(bytearray(lis))
        exp_out_3.write(str(lis)[1:-1]+'\n')

############################# pooling
dim_o = (dim - 1)//2
# out_1 = np.arange(ker*dim*dim, dtype='float64').reshape((ker,dim,dim)) #test pool
# print(out_1)
pool_1 = np.zeros((ker,dim_o,dim_o), dtype = 'float64') #initialize
for x in range(0,dim_o):
    xx = x*2
    for y in range(0,dim_o):
        yy = y*2
        pool_1[:,x,y]= np.amax(out_1[:,xx:xx+3,yy:yy+3],(1,2))

# print("before pool 1")
# print(out_1[0,:,:]);
# print("after pool 1")
# print(pool_1[0,:,:]) # pool checking 

pool_out_1 = open("pool_1.txt","w")
pool_out_1_b = open("pool_1.bin","wb")
# print(pool_1)
for x in range(0,dim_o):
    for y in range(0,dim_o):
        lis=pool_1[:,x,y]
        pool_out_1_b.write(bytearray(lis))
        pool_out_1.write(str(lis)[1:-1]+'\n')

# out_3 = np.arange(ker*dim*dim, dtype='float64').reshape((ker,dim,dim)) #test pool
# print(out_3)
pool_3 = np.zeros((ker,dim_o,dim_o), dtype = 'float64')
for x in range(0,dim_o):
    xx = x*2
    for y in range(0,dim_o):
        yy = y*2
        pool_3[:,x,y]= np.amax(out_3[:,xx:xx+3,yy:yy+3],(1,2))

# print("before pool 3")
# print(out_3[0,:,:]);
# print("after pool 3")
# print(pool_3[0,:,:]) # pool checking 

pool_out_3 = open("pool_3.txt","w")
pool_out_3_b = open("pool_3.bin","wb")
# print(pool_3)
for x in range(0,dim_o):
    for y in range(0,dim_o):
        lis=pool_3[:,x,y]
        pool_out_3_b.write(bytearray(lis))
        pool_out_3.write(str(lis)[1:-1]+'\n')

########################## squeeze
sq_in=[] # dep*dim*dim
dep = ker*2 # TODO firs layer no ned 2
if pool_en == 1: # ########TODO add first layer heere
    sq_in = np.concatenate((pool_1, pool_3), axis=0)
    dim_sq = dim_o
else:
    sq_in = np.concatenate((out_1, out_3), axis=0)
    dim_sq = dim

# print(out_1[31,:,:])
# print(out_3[0,:,:])
# print(sq_in[31:33,:,:])
# sq_in = np.rollaxis(sq_in,0,3)

########################   squ kernel
if random == 0:
    #sq_ker_l = np.full(sq_ker*dep,65,dtype='uint8').reshape((sq_ker,dep))
    # sq_ker_l = np.random.randint(low=0, high=255, size = (sq_ker*dep),dtype='uint8').reshape((sq_ker,dep))
    sq_ker_l = np.full(sq_ker*dep,0, dtype='uint8').reshape((sq_ker,dep))
    # sq_ker_l[0,0]=60
    sq_ker_l[0,dep//2]=60
else:
    sq_ker_l = np.random.randint(low = 0, high = 255, size = (sq_ker,dep), dtype='uint8')

sq_k_1 = open("sq_ker.txt","w")
sq_k_1_b = open("sq_ker.bin","wb")
dep_h = dep//2

rep_no = 1
if(sq_rep == 1):
    rep_no = dim_sq
for r in range(0,rep_no):
    for x in range(0,sq_ker):
        for z in range(0,dep_h,8):
            lis = sq_ker_l[x,z+dep_h:z+dep_h+8][::-1]#kerle of 3x3 part # reverse added
            sq_k_1.write(str(lis)[1:-1]+'\n')
            sq_k_1_b.write(bytearray(lis))

            lis = sq_ker_l[x,z:z+8][::-1] #reverse added
            sq_k_1.write(str(lis)[1:-1]+'\n')
            sq_k_1_b.write(bytearray(lis))
    
sq_ker_l = b2dv(sq_ker_l) #########converting to float
print("sqeeze kernel");print(sq_ker_l[0,:])
# #######################    squ bias
sq_bis_1 = np.full(sq_ker,0x00,dtype='uint8')
# sq_bis_1 = np.random.randint(low = 0, high = 255, size = (sq_ker),dtype='uint8')
# print(sq_bis_1)
f_sq_bis = open("sq_bias.txt","w")
f_sq_bis_b = open("sq_bias.bin","wb")
for x in range(0,sq_ker,8):
    lis = sq_bis_1[x:x+8]
    # lis = lis[::-1] #reverse
    f_sq_bis.write(str(lis)[1:-1]+'\n')
    f_sq_bis_b.write(bytearray(lis))

sq_bis_1 = b2dv(sq_bis_1)# converting to float
# ######################    squ convoluve
sq_out = np.zeros((sq_ker,dep,dim_sq,dim_sq), dtype='float64')
for k in range(0,sq_ker):
    for l in range(0,dep):
        res = sg.convolve(sq_in[l,:,:],[[sq_ker_l[k,l]]] , "valid").astype(float)
        sq_out[k,l,:,:]=dqv(res)

print("squ input before add")
inkk=dep//2
print("layer " + str(inkk))
print(sq_in[inkk,:,:])
print("kernel")
print(sq_ker_l[0,inkk])
print("output ")
print(sq_out[0,inkk,:,:])
# print("single pixe")
# print(sq_out[0,:,0,0])

squ_out_tmp = np.zeros((sq_ker,dim_sq,dim_sq), dtype='float64')
for a in range(0,sq_ker):
    for b in range(0,dim_sq):
        for c in range(0,dim_sq):
            squ_out_tmp[a,b,c]=add(sq_out[a,:,b,c])
sq_out = squ_out_tmp
# print("after addition single pixel")
# print(sq_out[:,0,0])
# print(sq_bis_1)
for i in range(0,sq_ker):
    sq_out[i,:,:] = sq_out[i,:,:] + sq_bis_1[i]
sq_out[sq_out < 0] = 0 # no need for positive
# print(sq_out[:,0,0])

# sq_out = np.arange(sq_ker*dim_sq*dim_sq, dtype='uint8').reshape((sq_ker,dim_sq,dim_sq)) # test ouptu
# print(sq_out[0,:,:]);print('______')
f_sq_out_1 = open("sq_out.txt","w")
f_sq_out_1_b = open("sq_out.bin","wb")
for r in range(0,dim_sq):
    for d in range(0,sq_ker):
        lis = d2bv(sq_out[d,r,:])
        f_sq_out_1_b.write(bytearray(lis))
        f_sq_out_1.write(str(lis)[1:-1]+'\n')

f_sq_out_1_c = open("sq_out_c.txt","w")
for r in range(0,sq_ker):
    for d in range(0,dim_sq):
        lis = d2bv(sq_out[r,d,:])
        lisStr = ' '.join(map(str,list(lis)))
        f_sq_out_1_c.write(lisStr+'\n')
########################     avg pool
sq_bis_1 = np.ones(sq_ker,dtype='uint8') # actual value for convoution
if av_pool_en == 1:
    av_pool = np.sum(sq_out,axis = (1,2), dtype = 'uint8')
    f_av_out_1 = open("av_pool_out.txt","w")
    f_av_out_1_b = open("av_pool_out.bin","wb")
    f_av_out_1_b.write(bytearray(av_pool))
    f_av_out_1.write(str(av_pool)[1:-1]+'\n')