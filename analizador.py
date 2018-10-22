import binascii
import os
import struct



def abrir_leer_n_bytes(init_byte, read_n_bytes):
    data_n = []
    with open("bts_canal_10_20180903.ts", 'rb') as f:
        f.seek(init_byte)
        data_n = f.read(read_n_bytes)
    
    f.close()
    return data_n

def segments_intlen_codrate_modscheme(a):
    res = []
    res.append(a & 15)
    a = a >> 4
    for i in range(3):
        res.append(a & 3)
        a = a >> 3
    return res

def mostrar_ISDBT_info(data, print_TSPs_list, show_parity_bits):
    '''
    data:               lista que contiene los bytes agregados a cada paquete por el ISDBT Remux (8 bits ISDBT info y 8 bits paridad)
    print_TSPs_list:    lista con los indices de los TSPs que se desean analizar  
    show_parity_bits:   0 no, 1 si   
    '''
    print("*******************************************")
    print("********** ISDBT Information **************")
    print("*******************************************")

    for j in print_TSPs_list:
        
        if show_parity_bits == True :
            print "Packet ", j, " ISDBT Info + Parity:"
            print ""
            print(binascii.hexlify(data[j]).upper())
        else:
            print "Packet ", j, " ISDBT Info:"
            print ""
            isdbt_info = []
            isdbt_info = struct.unpack(b'BBBBBBBBBBBBBBBB', data[j])
            isdbt_info = list(isdbt_info[0:8])
            isdbt_info = struct.pack('B'*len(isdbt_info), *isdbt_info)
            print(binascii.hexlify(isdbt_info).upper())
        print("___________________________________________")
#def mostrar_BTS_crudo():

def identificar_layers_en_frame(data, n_TSP_packets, return_IIP_info):
    '''
    Muestra si los paquetes TSP dentro del multiplex frame corresponden a Layer A, B, C, NULL o IIP.
    '''
    a = 0
    b = 0
    c = 0
    nul = 0
    iip = 0
    for i in range(n_TSP_packets):
        isdbt_info_parity = struct.unpack(b'BBBBBBBBBBBBBBBB', data[i])
        isdbt_info = list(isdbt_info_parity[0:8])
        layer_indicator = (isdbt_info[1] & 240) >> 4
        
 

        if layer_indicator == 0:
            # Null
            nul = nul +1
            if ((iip +a +b+c+nul) > 2304) & ((iip +a +b+c+nul) < 2500):
                print("En el cuadro multiplex hay NUL (menos 1)", nul)
            #print("NULL"),
        elif layer_indicator == 1:
            # A
            a = a +1
            #if ((iip +a +b+c+nul) > 2304) & ((iip +a +b+c+nul) < 2500):
            #    print("En el cuadro multiplex hay (menos 1)", a)
            #print("A"),
            
        elif layer_indicator == 2:
            # B
            b = b+1
            #if ((iip +a +b+c+nul) > 2304) & ((iip +a +b+c+nul) < 2500):
            #    print("En el cuadro multiplex hay B (menos 1)", b)
            #print("B"),
        elif layer_indicator == 3:
            # C
            c = c+1
            if ((iip +a +b+c+nul) > 2304) & ((iip +a +b+c+nul) < 2500):
                print("En el cuadro multiplex hay C (menos 1)", c)
            print("C"),
        elif layer_indicator == 4:
            # AC
            print("AuxCha"),
        elif layer_indicator == 8:
            # IIP Packet
            # byte 6, leo 160 bits de la mod scheme information, 20 bytes leo
            print ("VALOR DE i para el paquete IIP+++++++++++++++++++++++++++++++++++++", i)
            iip = iip +1
            print ("IIP+null+weas", iip +a +b+c+nul)
            if (iip +a +b+c+nul) > 2304:
                print("En el cuadro multiplex hay IIP (menos 1)", iip)
            if return_IIP_info == 1:

                mod_ctrl_config_info = struct.unpack(b'BBBBBBBBBBBBBBBBBBBB', abrir_leer_n_bytes(i*204 + 6, 20)) #En estos 20 bytes tengo la modulation_control_configuration_information( ). ME resta desmenuzarlo
                
                # en el mode_GI_information van datos como el MODO y CP length 
                mode = (mod_ctrl_config_info[1] & 190) >> 6
                cp_length = (mod_ctrl_config_info[1] >> 4) & 3               
                # print("Modo: ", mode)
                # print("CP_LENGTH: ", cp_length)

                # bit 24 comienzan los parametros del layer A
                transmission_param_A = list(mod_ctrl_config_info[3:5])
                transmission_param_B = list(mod_ctrl_config_info[4:7])
                transmission_param_C = list(mod_ctrl_config_info[6:8])

                transmission_param_A = (transmission_param_A[0] << 5)|(transmission_param_A[1] >> 3) # ahora transmission_param_A es un entero de 13bits
                transmission_param_B = (((transmission_param_B[0] & 7) << 11) | (transmission_param_B[1] << 2)) | ((transmission_param_B[2]&192) >> 6)
                transmission_param_C = ((transmission_param_C[0]&63) << 7) | ((transmission_param_C[1]&254) >> 1)

                param_A = segments_intlen_codrate_modscheme(transmission_param_A)
                param_B = segments_intlen_codrate_modscheme(transmission_param_B)
                param_C = segments_intlen_codrate_modscheme(transmission_param_C)
                # print("Layer A: ")
                # print '         Segments: ', param_A[0]
                # print '         Interleaving Length: ', param_A[1]
                # print '         Convolution coding rate: ', param_A[2]
                # print '         Modulation scheme: ', param_A[3]
                # print("Layer B: ")
                # print '         Segments: ', param_B[0]
                # print '         Interleaving Length: ', param_B[1]
                # print '         Convolution coding rate: ', param_B[2]
                # print '         Modulation scheme: ', param_B[3]
                # print("Layer C: ")
                # print '         Segments: ', param_C[0]
                # print '         Interleaving Length: ', param_C[1]
                # print '         Convolution coding rate: ', param_C[2]
                # print '         Modulation scheme: ', param_C[3]

            print("**IIP**"),
        else:
            print("...Another layer indicator... \n \n", layer_indicator)
    # print("a = ",a)
    # print("b = ",b)
    # print("c = ",c)
    # print("Cantidad de Paquetes de capa A: ", a)
    # print("Cantidad de Paquetes de capa B: ", b)
    # print("Cantidad de Paquetes de capa C: ", c)
    # print("Cantidad de Paquetes NULL: ", nul)
    # print("Cantidad de Paquetes IIP: ", iip)
    # print("---------------------------------")
    # print("TOTAL DE PAQUETES CONTADOS", iip+a+b+c+nul)
#def reconocer_patron_multiplex():

#def detectar_patron_incorrecto():



file_size = os.path.getsize("bts_canal_10_20180903.ts") # tamanio del archivo en bytes
i = 1
data = []


with open("bts_canal_10_20180903.ts", 'rb') as f:     # usar with open tiene la ventaja de que automaticamente se cierra el file
        while (i*(204-16)<file_size):
            f.seek(i*204-16)   # se posiciona en el byte i*204-16 - esimo
            data.append(f.read(16)) #reads the 16 bytes of ISDBT info(8) + parity(8)
            i = i+1
f.close()


print_TSPs_list = (1, 2, 3, 4, 4608)          # Indices de paquetes que queremos que se consideren
mostrar_ISDBT_info(data, print_TSPs_list, 1)

n_TSP_packets =  file_size/(204) # paquetes que quiero analizar: primeros 2000    
identificar_layers_en_frame(data, n_TSP_packets, 1) # 

print("Cantidad de cuadros multiplex:", file_size/(204.0*2304.0))

#print(binascii.hexlify(data).upper()), # .upper() prints hexa in uppercase (0xFF)
