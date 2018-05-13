import numpy as np
from scipy import signal as sg
dim = 56
dim_p=dim + 2
dep = 16
ker = 64
sq_ker = 16
pool_en = 0
av_pool_en = 0
random = 1 #TODO
sq_rep = 0 # repete squze kernl for last layer

#######################         Input image
in_l = np.zeros(dim_p*dim_p*dep, dtype='uint8').reshape((dim_p,dim_p,dep))
if random == 0:
    in_ori = np.arange(dim*dim*dep, dtype='uint8').reshape((dim,dim,dep))
else:
    in_ori = np.random.randint(low = 0, high = 255, size = (dim,dim,dep), dtype='uint8')
in_l[1:-1,1:-1,:] = in_ori
# print(in_l[:,:,0]); print("_____________________-")
f_in = open("input_layer.txt","w")
f_in_b = open("input_layer.bin","wb")
for z in range(0,dim):
    for y in range(0,dep):
        for x in range(0,dim):
            lis = in_l[z:z+3,x:x+3,y].flatten().tolist()
            for rep in range(0,ker,4):
                f_in.write(str(lis)[1:-1]+'\n')
                f_in_b.write(bytearray(lis))

f_in_c = open("input_layer_c.txt","w")
f_in_c_b = open("input_layer_c.bin","wb")
for d in range(0,dep):
    for z in range(0,dim):
        for y in range(0,dim):
            lis = in_ori[z,y,d].flatten().tolist()
            f_in_c.write(str(lis)[1:-1]+'\n')
            f_in_c_b.write(bytearray(lis))
########################        expand kernels 
# ker_l_1 =np.zeros(ker*dep, dtype='uint8').reshape((ker,dep))
ker_l_1 =np.random.randint(100,size=ker*dep, dtype='uint8').reshape((ker,dep))
# print(ker_l_1);print("________")
f_k_1 = open("ker_1x1.txt","w")
f_k_1_b = open("ker_1x1.bin","wb")
# for z in range(0,dep):
#     lis = ker_l_1[:,z]
#     f_k_1_b.write(bytearray(lis))
#     f_k_1.write(str(lis)[1:-1]+'\n')
for z in range(0,dep):
    for x in range(0,ker,8):
        lis = ker_l_1[x:x+4,z][::-1]
        f_k_1_b.write(bytearray(lis))
        f_k_1.write(str(lis)[1:-1]+'\n')

        lis = ker_l_1[x+4:x+8,z][::-1]
        f_k_1_b.write(bytearray(lis))
        f_k_1.write(str(lis)[1:-1]+'\n')

# ker_l_3 = np.asarray(list(range(0,9))*ker*dep, dtype='uint8').reshape((ker,dep,9))
# ker_l_3 = np.ones(ker*dep*9, dtype='uint8').reshape((ker,dep,9))
ker_l_3 = np.random.randint(100,size=ker*dep*9, dtype='uint8').reshape((ker,dep,9))
# print(ker_l_3[0:8,0,:]);print("________")
f_k_3 = open("ker_3x3.txt","w")
f_k_3_b = open("ker_3x3.bin","wb")
# for m in range(0,dim): # repet 3x3 kernel # removed repeating
# ordering 78 345 012 ## 6
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

########################        exapnd bias
# bis_1 = np.arange(ker,dtype='uint8')
bis_1 = np.random.randint(low = 0, high = 255, size=ker,dtype='uint8')
# bis_3 = np.ones(ker,dtype='uint8')
bis_3 = np.random.randint(low = 0, high = 255, size=ker,dtype='uint8')
b_bis = open("bias.txt","w")
b_bis_b = open("bias.bin","wb")
# print(bis_1)
for i in range(0,ker,4):
    lis_b3 = bis_3[i:i+4][::-1] # reverse
    lis_b1 = bis_1[i:i+4][::-1] #reverst
    b_bis.write(str(lis_b1)[1:-1]+'\n')
    b_bis.write(str(lis_b3)[1:-1]+'\n')
    b_bis_b.write(bytearray(lis_b1))
    b_bis_b.write(bytearray(lis_b3))

#######################        expand convolution
out_1 = np.zeros(ker*dep*dim*dim, dtype='uint8').reshape((ker,dep,dim,dim))
for k in range(0,ker):
    for l in range(0,dep):
        res = sg.convolve(in_l[:,:,l],[[ker_l_1[k,l]]] , "valid").astype(int)
        res = np.bitwise_and(res, 0xff)
        out_1[k,l,:,:]=res[1:-1,1:-1]
# print(out_1[1,1,:,:]);print('______')
f_out_1 = open("out_1x1.txt","w")
f_out_1_b = open("out_1x1.bin","wb")
# out_1 = np.arange(ker*dep*dim*dim, dtype='uint8').reshape((ker,dep,dim,dim))
for r in range(0,dim):
    for d in range(0,dep):
        for c in range(0,dim):
            lis = out_1[:,d,r,c]
            f_out_1_b.write(bytearray(lis))
            f_out_1.write(str(lis)[1:-1]+'\n')


out_3 = np.zeros(ker*dep*dim*dim, dtype='uint8').reshape((ker,dep,dim,dim))
for k in range(0,ker):
    for l in range(0,dep):
        kk = np.rot90(ker_l_3[k,l].reshape((3,3)),2)
        res = sg.convolve(in_l[:,:,l],kk , "valid").astype(int) # addre lus
        res = np.bitwise_and(res, 0xff)
        out_3[k,l,:,:]=res
# print(out_3[1,1,:,:]);print('______')
# out_3 = np.arange(ker*dep*dim*dim, dtype='uint8').reshape((ker,dep,dim,dim))

f_out_3 = open("out_3x3.txt","w")
f_out_3_b = open("out_3x3.bin","wb")
for r in range(0,dim):
    for d in range(0,dep):
        for c in range(0,dim):
            lis = out_3[:,d,r,c]
            f_out_3_b.write(bytearray(lis))
            f_out_3.write(str(lis)[1:-1]+'\n')

############################ add bias and relu

out_1 = np.sum(out_1,1,dtype='uint8') 
for i in range(0,ker):
    out_1[i,:,:] = out_1[i,:,:] + bis_1[i]
out_1[out_1 > 127] = 0 # no need for positive
exp_out_1 = open("exp_1.txt","w")
exp_out_1_b = open("exp_1.bin","wb")
for x in range(0,dim):
    for y in range(0,dim):
        lis=out_1[:,x,y]
        exp_out_1_b.write(bytearray(lis))
        exp_out_1.write(str(lis)[1:-1]+'\n')


out_3 = np.sum(out_3,1,dtype='uint8')
for i in range(0,ker):
    out_3[i,:,:] = out_3[i,:,:] + bis_3[i]
out_3[out_3 > 127] = 0
exp_out_3 = open("exp_3.txt","w")
exp_out_3_b = open("exp_3.bin","wb")
for x in range(0,dim):
    for y in range(0,dim):
        lis=out_3[:,x,y]
        exp_out_3_b.write(bytearray(lis))
        exp_out_3.write(str(lis)[1:-1]+'\n')

############################# pooling
dim_o = (dim - 1)//2
# out_1 = np.arange(ker*dim*dim, dtype='uint8').reshape((ker,dim,dim)) #test pool
# print(out_1)
pool_1 = np.zeros((ker,dim_o,dim_o), dtype = 'uint8') #initialize
for x in range(0,dim_o):
    xx = x*2
    for y in range(0,dim_o):
        yy = y*2
        pool_1[:,x,y]= np.amax(out_1[:,xx:xx+3,yy:yy+3],(1,2))
# print(out_1[:,:,:]);print(pool_1[:,:,:]) # pool checking 
pool_out_1 = open("pool_1.txt","w")
pool_out_1_b = open("pool_1.bin","wb")
# print(pool_1)
for x in range(0,dim_o):
    for y in range(0,dim_o):
        lis=pool_1[:,x,y]
        pool_out_1_b.write(bytearray(lis))
        pool_out_1.write(str(lis)[1:-1]+'\n')

# out_3 = np.arange(ker*dim*dim, dtype='uint8').reshape((ker,dim,dim)) #test pool
# print(out_3)
pool_3 = np.zeros((ker,dim_o,dim_o), dtype = 'uint8')
for x in range(0,dim_o):
    xx = x*2
    for y in range(0,dim_o):
        yy = y*2
        pool_3[:,x,y]= np.amax(out_3[:,xx:xx+3,yy:yy+3],(1,2))

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
    sq_ker_l = np.ones(sq_ker*dep, dtype='uint8').reshape((sq_ker,dep))
else:
    # sq_ker_l = np.ones(sq_ker*dep, dtype='uint8').reshape((sq_ker,dep))
    sq_ker_l = np.random.randint(low = 0, high = 255, size = (sq_ker,dep), dtype='uint8')

sq_k_1 = open("sq_ker.txt","w")
sq_k_1_b = open("sq_ker.bin","wb")
# print(sq_ker_l[0,:])
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
    

#######################    squ bias
sq_bis_1 = np.random.randint(10,size=sq_ker,dtype='uint8')
# sq_bis_1 = np.zeros(sq_ker,dtype='uint8')
f_sq_bis = open("sq_bias.txt","w")
f_sq_bis_b = open("sq_bias.bin","wb")

for x in range(0,sq_ker,8):
    lis = sq_bis_1[x:x+8]
    # lis = lis[::-1] #reverse
    f_sq_bis.write(str(lis)[1:-1]+'\n')
    f_sq_bis_b.write(bytearray(lis))

######################    squ convoluve
sq_out = np.zeros((sq_ker,dep,dim_sq,dim_sq), dtype='uint8')
for k in range(0,sq_ker):
    for l in range(0,dep):
        res = sg.convolve(sq_in[l,:,:],[[sq_ker_l[k,l]]] , "valid").astype(int)
        res = np.bitwise_and(res, 0xff)
        sq_out[k,l,:,:]=res

# print(sq_in[2,:,:])
# print(sq_ker_l[0,2])
# print(sq_out[0,2,:,:])

sq_out = np.sum(sq_out,1,dtype='uint8') 
for i in range(0,sq_ker):
    sq_out[i,:,:] = sq_out[i,:,:] + sq_bis_1[i]
sq_out[sq_out > 127] = 0 # no need for positive

# sq_out = np.arange(sq_ker*dim_sq*dim_sq, dtype='uint8').reshape((sq_ker,dim_sq,dim_sq)) # test ouptu
# print(sq_out[0,:,:]);print('______')
f_sq_out_1 = open("sq_out.txt","w")
f_sq_out_1_b = open("sq_out.bin","wb")
for r in range(0,dim_sq):
    for d in range(0,sq_ker):
        lis = sq_out[d,r,:]
        f_sq_out_1_b.write(bytearray(lis))
        f_sq_out_1.write(str(lis)[1:-1]+'\n')

f_sq_out_1_c = open("sq_out_c.txt","w")
for r in range(0,sq_ker):
    for d in range(0,dim_sq):
        lis = sq_out[r,d,:]
        lisStr = ' '.join(map(str,list(lis)))
        f_sq_out_1_c.write(lisStr+'\n')

########################     avg pool
if av_pool_en == 1:
    av_pool = np.sum(sq_out,axis = (1,2), dtype = 'uint8')
    f_av_out_1 = open("av_pool_out.txt","w")
    f_av_out_1_b = open("av_pool_out.bin","wb")
    f_av_out_1_b.write(bytearray(av_pool))
    f_av_out_1.write(str(av_pool)[1:-1]+'\n')