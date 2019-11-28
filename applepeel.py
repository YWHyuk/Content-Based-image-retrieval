import os
import gdal
import numpy as np
def image_projection(reference_image, input_image,outfile):
    band = reference_image.RasterCount
    width = reference_image.RasterXSize
    height = reference_image.RasterYSize

    trans = reference_image.GetGeoTransform()
    proj = reference_image.GetProjection()

    outdriver = gdal.GetDriverByName('GTiff')


    outdata = outdriver.Create(outfile, width, height, band, gdal.GDT_Byte)
    outdata.SetGeoTransform(trans)
    outdata.SetProjection(proj)

    outdata.GetRasterBand(1).WriteArray(input_image.GetRasterBand(1).ReadAsArray())
    outdata.GetRasterBand(2).WriteArray(input_image.GetRasterBand(2).ReadAsArray())
    outdata.GetRasterBand(3).WriteArray(input_image.GetRasterBand(3).ReadAsArray())
def run_matlab(path,reference_name,reference_dir,source_dir,dest_dir,white_name,edge_dir):
    # refernect image, raw_image, 를 받고 moved_image를 리턴하는 프로그램을 실행시킨다.
    reference =reference_name
    white = white_name
    path = path  # 현재 경로
    # 영상 폴더 저정 방식은 한 디렉토리 안에 싸그리 들어있는 상태로 생각한다.
    command = ""
    ref_path = path + "\\"+reference_dir+"\\"
    source_path = path + "\\"+source_dir+"\\"
    dest_path = path + "\\"+dest_dir+"\\"
    edge_path = path + "\\"+edge_dir+"\\"
    # check dest_path
    if not(os.path.isdir(dest_dir)):
        os.mkdir(dest_dir)
    # iterating source files
    file_list = os.listdir(source_path)
    a=1
    for source in file_list:
        if source == reference:
            continue
        command = command + "RotationFeatureMatching('" + ref_path + reference + \
                  "','" + source_path + source + \
                  "','" + dest_path + source + \
                  "','" + ref_path + white + \
                  "','" + edge_path + source + "');"
        if a%10 ==0:
            command = command + "exit"
            print(command)
            os.system('matlab -wait -nosplash -nodesktop -r ' + command)
            command=""
        a=a+1
    command = command + "exit"
    print(command)
    # matlab으로 파일들을 처리..
    a= os.system('matlab -wait -nosplash -nodesktop -r ' + command)
    print(a)
def findRasterIntersect(raster1, raster2):
    # load data
    band1 = raster1.GetRasterBand(2)
    band2 = raster2.GetRasterBand(2)
    gt1 = raster1.GetGeoTransform()
    gt2 = raster2.GetGeoTransform()

    # find each image's bounding box
    # r1 has left, top, right, bottom of dataset's bounds in geospatial coordinates.
    r1 = [gt1[0], gt1[3], gt1[0] + (gt1[1] * raster1.RasterXSize), gt1[3] + (gt1[5] * raster1.RasterYSize)]
    r2 = [gt2[0], gt2[3], gt2[0] + (gt2[1] * raster2.RasterXSize), gt2[3] + (gt2[5] * raster2.RasterYSize)]
    print('\t1 bounding box: %s' % str(r1))
    print('\t2 bounding box: %s' % str(r2))

    # find intersection between bounding boxes
    intersection = [max(r1[0], r2[0]), min(r1[1], r2[1]), min(r1[2], r2[2]), max(r1[3], r2[3])]
    if r1 != r2:
        print('\t** different bounding boxes **')
        # check for any overlap at all...
        if (intersection[2] < intersection[0]) or (intersection[1] < intersection[3]):
            intersection = None
            print('\t***no overlap***')
            return
        else:
            print
            '\tintersection:', intersection
            left1 = int(round((intersection[0] - r1[0]) / gt1[1]))  # difference divided by pixel dimension
            top1 = int(round((intersection[1] - r1[1]) / gt1[5]))
            col1 = int(round((intersection[2] - r1[0]) / gt1[1])) - left1  # difference minus offset left
            row1 = int(round((intersection[3] - r1[1]) / gt1[5])) - top1

            left2 = int(round((intersection[0] - r2[0]) / gt2[1]))  # difference divided by pixel dimension
            top2 = int(round((intersection[1] - r2[1]) / gt2[5]))
            col2 = int(round((intersection[2] - r2[0]) / gt2[1])) - left2  # difference minus new left offset
            row2 = int(round((intersection[3] - r2[1]) / gt2[5])) - top2

            # print '\tcol1:',col1,'row1:',row1,'col2:',col2,'row2:',row2
            if col1 != col2 or row1 != row2:
                print("*** MEGA ERROR *** COLS and ROWS DO NOT MATCH ***")
            # these arrays should now have the same spatial geometry though NaNs may differ
            array1 = band1.ReadAsArray(left1, top1, col1, row1)
            array2 = band2.ReadAsArray(left2, top2, col2, row2)

    else:  # same dimensions from the get go
        col1 = raster1.RasterXSize  # = col2
        row1 = raster1.RasterYSize  # = row2
        array1 = band1.ReadAsArray()
        array2 = band2.ReadAsArray()

    return array1, array2, col1, row1, intersection
def apple_peeling(input_image):
    XSize=input_image.RasterXSize
    YSize=input_image.RasterYSize
    input_array=input_image.GetRasterBand(1).ReadAsArray()
    up= {'value':0,'fixed':False}
    down= {'value':YSize-1,'fixed':False}
    left= {'value':0,'fixed':False}
    right= {'value':XSize-1,'fixed':False}
    while up['value']<down['value'] and left['value']<right['value']:
        if right['fixed'] and left['fixed'] and up['fixed'] and down['fixed']:
            break
        else:
            if not up['fixed']:
                buff_array1=input_array[up['value']:up['value']+1,left['value']:right['value']].ravel()
                if np.all(buff_array1):
                    up['fixed']=True
            if not left['fixed']:
                buff_array2 = input_array[up['value']:down['value'], left['value']:left['value']+1].ravel()
                if np.all(buff_array2):
                    left['fixed']=True
            if not down['fixed']:
                buff_array3 = input_array[down['value']-1:down['value'], left['value']:right['value']].ravel()
                if np.all(buff_array3):
                    down['fixed']=True
            if not right['fixed']:
                buff_array4 = input_array[up['value']:down['value'], right['value']-1:right['value']].ravel()
                if np.all(buff_array4):
                    right['fixed']=True
            side= min(buff_array1.sum(),buff_array2.sum(),buff_array3.sum(),buff_array4.sum())
            if side==buff_array1.sum():
                up['value'] += 1
            if side==buff_array2.sum():
                left['value'] += 1
            if side==buff_array3.sum():
                down['value'] -= 1
            if side==buff_array4.sum():
                right['value'] -= 1
    return up['value'], down['value'], left['value'], right['value']
if __name__=="__main__":
    # edge: 패턴 매칭 과정 중 함께 나오는 테두리 표시 영상
    # total_edge: 테두리 표시 영상을 모두 합친 영상
    # processed: 패턴 매칭이 끝난후 저장되는 장소
    # coordinate: 좌표를 지정한 후 저장되는 장소(legacy) 시간나면 삭제
    # source: 매칭을 시행할 영상 모음
    # reference: 기준이 되는 영상과, white 이미지
    # 1. Coordinate featurematched images
    reference_image = gdal.Open(".\\reference\\site1.JPG")
    XSize =reference_image.RasterXSize
    YSize =reference_image.RasterYSize
    # 2. Making white image..
    white_image = gdal.GetDriverByName('GTiff').Create(".\\reference\\white.tif",XSize,YSize,1,gdal.GDT_Byte);
    raster = np.full((YSize, XSize),255, dtype=np.uint8)
    white_image.GetRasterBand(1).WriteArray(raster)
    white_image=None;
    # 이 과정은 과거의 잔재.. 지우기 귀찮아서 놔둠
    if False:
        for source in os.listdir('.\\source'):
            input_image=gdal.Open(".\\source\\"+source)
            image_projection(reference_image,input_image,".\\coordinated\\"+source.split(".")[0]+".tif")
        # 3. FeatureMatching various images
        run_matlab('.', 'site1.JPG', "reference", "coordinated", "processed","white.tif","edge")
    # 4. integrate edge images
    white_image=gdal.Open(".\\reference\\white.tif")
    white_array=white_image.GetRasterBand(1).ReadAsArray()
    for source in os.listdir('.\\edge'):
        input_image=gdal.Open('.\\edge\\'+source)
        input_array = input_image.GetRasterBand(1).ReadAsArray()
        white_array = np.bitwise_and(white_array, input_array)
        #for index_y in range(0,YSize):
        #    white_array[index_y] = np.bitwise_and(white_array[index_y], input_array[index_y])
    total_edge_image = gdal.GetDriverByName('GTiff').Create(".\\total_edge\\site1.JPG", XSize, YSize, 1, gdal.GDT_Byte);
    total_edge_image.GetRasterBand(1).WriteArray(white_array)
    total_edge_image=None
    # 5. get intersected square
    # by. 사과 껍질 짜르기 알고리즘. 이것의 성능은 테스트, 증명되지 않음.. 더 좋은 알고리즘으로 개선해야함..
    total_edge_image=gdal.Open(".\\total_edge\\site1.JPG")
    up, down, left, right = apple_peeling(total_edge_image)
    for source in os.listdir('.\\processed'):
        input_image = gdal.Open('.\\processed\\' + source)
        band_size= input_image.RasterCount
        output_image= gdal.GetDriverByName('GTiff').Create('.\\peeled\\'+source,right-left,down-up,band_size,gdal.GDT_Byte )
        for i in range(1,band_size+1):
            input_array=input_image.GetRasterBand(i).ReadAsArray()
            input_array=input_array[up:down,left:right]
            output_image.GetRasterBand(i).WriteArray(input_array)
        output_image=None
    # 6. setting all images in same square

