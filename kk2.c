#include <stdio.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/mman.h>

#define ALT_LWFPGASLVS_OFST 0xFF200000
#define ddr3_fpga 0x30000000
#define LED_PIO_BASE             0x3000
#define REG_SPAN            0x100
#define DDR3_SPAN            0x1000000

int main(void)
{
          unsigned char *lw_addr, *ddr3_common;
          int fd;
          int i, j, k;

          fd = open("/dev/mem", (O_RDWR | O_SYNC));

          //Map LED_PIO Physical Address to Virtual Address Space
          lw_addr = mmap( NULL, REG_SPAN, ( PROT_READ | PROT_WRITE ), MAP_SHARED, fd, (ALT_LWFPGASLVS_OFST) );


          ddr3_common = mmap( NULL, DDR3_SPAN, ( PROT_READ | PROT_WRITE ), MAP_SHARED, fd, (ddr3_fpga) );

          FILE *f = fopen("input_layer_c.bin", "rb");
          for(k = 0; k < 16; k++){
			  for(i = 0; i < 56; i++){
				  fread((ddr3_common+ k * 4096 + (i * 64)), 1, 56,f);
			   }
          }
          fclose(f);
          f = fopen("ker_3x3.bin", "rb");
          fread(ddr3_common + 0x80000, 1, 0x2400,f);
          fclose(f);

          f = fopen("ker_1x1.bin", "rb");
          fread(ddr3_common + 0x83000, 1, 0x400,f);
          fclose(f);

          f = fopen("bias.bin", "rb");
          fread(ddr3_common + 0x83500, 1, 0x80,f);
          fclose(f);

          f = fopen("sq_ker.bin", "rb");
          fread(ddr3_common + 0x84000, 1, 0x800,f);
          fclose(f);

          f = fopen("sq_bias.bin", "rb");
          fread(ddr3_common + 0x84900, 1, 0x10,f);
          fclose(f);

//          for(k = 0; k < 0x1000; k++){
//        	  *(ddr3_common+ 0x80000 + k) =  k%10;
//          }
          // common parameters
          unsigned int row_0 = 0x0010010d;
          unsigned int row_1 = 0x00380038;
          unsigned int row_2 = 0x00100040;
          unsigned int row_3 = 0x2FFFFFC0;
          unsigned int row_4 = 0x70010040;

          // kernel loader paramter
          unsigned int row_8 = 0x00000001;
          unsigned int row_9 =  0x30080000;
          unsigned int row_10 = 0x30082400;

          unsigned int row_12 = 0x00000000;
          unsigned int row_13 = 0x30083000;
          unsigned int row_14 = 0x30083400;

          unsigned int row_16 = 0x00000000;
          unsigned int row_17 = 0x30083500;
          unsigned int row_18 = 0x30083580;

          unsigned int row_20 = 0x00000000;
          unsigned int row_21 = 0x30084000;
          unsigned int row_22 = 0x30084800;

          unsigned int row_24 = 0x00000000;
          unsigned int row_25 = 0x30084900;
          unsigned int row_26 = 0x30084910;

          // output layer parameters
          unsigned int row_32 = 0x00000010;
          unsigned int row_33 = 0x00380038;
          unsigned int row_34 = 0x30040000;
          unsigned int row_35 = 0x70010040;

          // fire configuration
          unsigned int row_36 = 0x00370f10;
          unsigned int row_37 = 0x037f00ff;
          unsigned int row_38 = 0x0f202f0f;

          unsigned int row_39 = 0x01ae037e;

          unsigned int row_40 = 0x000800ff;

          unsigned int row_41 = 0x000f0380;

          unsigned int row_42 = 0x000f01bf;

          unsigned int row_43 = 0x00370040;

          // common parameter
          memcpy(lw_addr+4, &row_1, 4);
          memcpy(lw_addr+8, &row_2, 4);
          memcpy(lw_addr+12, &row_3, 4);
          memcpy(lw_addr+16, &row_4, 4);


          // kernel loader
          memcpy(lw_addr+32, &row_8, 4);
          memcpy(lw_addr+36, &row_9, 4);
          memcpy(lw_addr+40, &row_10, 4);

          memcpy(lw_addr+48, &row_12, 4);
          memcpy(lw_addr+52, &row_13, 4);
          memcpy(lw_addr+56, &row_14, 4);

          memcpy(lw_addr+64, &row_16, 4);
          memcpy(lw_addr+68, &row_17, 4);
          memcpy(lw_addr+72, &row_18, 4);

          memcpy(lw_addr+80, &row_20, 4);
          memcpy(lw_addr+84, &row_21, 4);
          memcpy(lw_addr+88, &row_22, 4);

          memcpy(lw_addr+96, &row_24, 4);
          memcpy(lw_addr+100, &row_25, 4);
          memcpy(lw_addr+104, &row_26, 4);

//
//          //output layer
          memcpy(lw_addr+128, &row_32, 4);
          memcpy(lw_addr+132, &row_33, 4);
          memcpy(lw_addr+136, &row_34, 4);
          memcpy(lw_addr+140, &row_35, 4);

          // fire module
          memcpy(lw_addr+144, &row_36, 4);
          memcpy(lw_addr+148, &row_37, 4);
          memcpy(lw_addr+152, &row_38, 4);
          memcpy(lw_addr+156, &row_39, 4);
          memcpy(lw_addr+160, &row_40, 4);
          memcpy(lw_addr+164, &row_41, 4);
          memcpy(lw_addr+168, &row_42, 4);
          memcpy(lw_addr+172, &row_43, 4);

          // issue start signal
          memcpy(lw_addr+4, &row_1, 4);
          memcpy(lw_addr, &row_0, 4);



          //int a = 100;
//          printf("writing value:%d in ddr3 space", a);
//          memcpy(ddr3_common, &a, 4);
          usleep(10000);
          unsigned int * ptr = (unsigned int *)lw_addr;
          printf("reading value in ddr3 output address space\n");
          //int i = 0;

          for(k = 0; k < 16; k++){
			  for(i = 0; i < 56; i++){
				  for(j = 0; j < 56; j++){
					 printf("%d ", *(ddr3_common+ 0x40000 + 4096 * k + (i * 64) + j)) ;
				 }
				  printf("\n");
			  }
			  printf("\n");
          }

//          for(i = 0; i < 100; i = i + 1){
//                  	  usleep(1);
//                  	  printf("%i %x  \n", i, *(ptr));
//           }

          munmap(lw_addr, REG_SPAN);
          munmap(ddr3_common, DDR3_SPAN);
          close(fd);
          return(0);
}
