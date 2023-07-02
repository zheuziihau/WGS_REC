# -*- coding: utf-8 -*-import arcpyimport mathimport warningsfrom typing import Callablearcpy.env.overwriteOutput = Truex_pi = 3.14159265358979324 * 3000.0 / 180.0pi = 3.1415926535897932384626  # πa = 6378245.0  # 长半轴ee = 0.00669342162296594323  # 扁率# 百度墨卡托投影纠正矩阵class CoordTrans:    def __init__(self):        pass    @staticmethod    def bd09togcj02(bd_lon, bd_lat):        """        百度坐标系(BD09)转火星坐标系(GCJ02)        :param bd_lat:百度坐标纬度        :param bd_lon:百度坐标经度        :return:转换后的坐标列表形式        """        x = bd_lon - 0.0065        y = bd_lat - 0.006        z = math.sqrt(x * x + y * y) - 0.00002 * math.sin(y * x_pi)        theta = math.atan2(y, x) - 0.000003 * math.cos(x * x_pi)        gg_lng = z * math.cos(theta)        gg_lat = z * math.sin(theta)        return [gg_lng, gg_lat]    @staticmethod    def gcj02towgs84(lng, lat):        """        GCJ02(火星坐标系)转GPS84        :param lng:火星坐标系的经度        :param lat:火星坐标系纬度        :return:        """        dlat = CoordTrans.transformlat(lng - 105.0, lat - 35.0)        dlng = CoordTrans.transformlng(lng - 105.0, lat - 35.0)        radlat = lat / 180.0 * pi        magic = math.sin(radlat)        magic = 1 - ee * magic * magic        sqrtmagic = math.sqrt(magic)        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)        mglat = lat + dlat        mglng = lng + dlng        return [lng * 2 - mglng, lat * 2 - mglat]    @staticmethod    def bd09towgs84(lng, lat):        lng, lat = CoordTrans.bd09togcj02(lng, lat)        return CoordTrans.gcj02towgs84(lng, lat)    @staticmethod    def wgs84togcj02(lng, lat):        """        WGS84转GCJ02(火星坐标系)        :param lng:WGS84坐标系的经度        :param lat:WGS84坐标系的纬度        :return:        """        dlat = CoordTrans.transformlat(lng - 105.0, lat - 35.0)        dlng = CoordTrans.transformlng(lng - 105.0, lat - 35.0)        radlat = lat / 180.0 * pi        magic = math.sin(radlat)        magic = 1 - ee * magic * magic        sqrtmagic = math.sqrt(magic)        dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * pi)        dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * pi)        mglat = lat + dlat        mglng = lng + dlng        return [mglng, mglat]    @staticmethod    def transformlat(lng, lat):        ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \            0.1 * lng * lat + 0.2 * math.sqrt(math.fabs(lng))        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *                math.sin(2.0 * lng * pi)) * 2.0 / 3.0        ret += (20.0 * math.sin(lat * pi) + 40.0 *                math.sin(lat / 3.0 * pi)) * 2.0 / 3.0        ret += (160.0 * math.sin(lat / 12.0 * pi) + 320 *                math.sin(lat * pi / 30.0)) * 2.0 / 3.0        return ret    @staticmethod    def transformlng(lng, lat):        ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \            0.1 * lng * lat + 0.1 * math.sqrt(math.fabs(lng))        ret += (20.0 * math.sin(6.0 * lng * pi) + 20.0 *                math.sin(2.0 * lng * pi)) * 2.0 / 3.0        ret += (20.0 * math.sin(lng * pi) + 40.0 *                math.sin(lng / 3.0 * pi)) * 2.0 / 3.0        ret += (150.0 * math.sin(lng / 12.0 * pi) + 300.0 *                math.sin(lng / 30.0 * pi)) * 2.0 / 3.0        return ret#def point_trans_arcpy(i_cursor, correct_func: Callable, spa_ref):    for row in i_cursor:        if row[0] is None:            continue        p = row[0][0]        new_x, new_y = correct_func(p.X, p.Y)        new_p = arcpy.PointGeometry(arcpy.Point(new_x, new_y), spatial_reference=spa_ref)        row[0] = new_p        i_cursor.updateRow(row)def polyline_trans_arcpy(i_cursor, correct_func: Callable, spa_ref):    for row in i_cursor:        if row[0] is None:            continue        all_parts_new = arcpy.Array()        for part in row[0]:            points_new = arcpy.Array()            for p in part:                new_x, new_y = correct_func(p.X, p.Y)                new_p = arcpy.Point(new_x, new_y)                points_new.append(new_p)            all_parts_new.append(points_new)        new_line = arcpy.Polyline(all_parts_new, spatial_reference=spa_ref)        row[0] = new_line        i_cursor.updateRow(row)def polygon_trans_arcpy(i_cursor, correct_func: Callable, spa_ref):    for row in i_cursor:        if row[0] is None:            continue        all_parts_new = arcpy.Array()        for part in row[0]:            points_new = arcpy.Array()            for p in part:                new_x, new_y = correct_func(p.X, p.Y)                new_p = arcpy.Point(new_x, new_y)                points_new.append(new_p)            all_parts_new.append(points_new)        new_plg = arcpy.Polygon(all_parts_new, spatial_reference=spa_ref)        row[0] = new_plg        i_cursor.updateRow(row)def correct_core(input_shp:str, output_shp:str, tran_func: Callable):    # attribution check    feature_type = arcpy.Describe(input_shp).shapeType    spa_ref = arcpy.Describe(input_shp).spatialReference    print(spa_ref.name)    if spa_ref.name not in ['GCS_WGS_1984', 'WGS_1984', 'WGS1984']:        warnings.warn('incorrect spatial reference, only WGS 1984 is supported')    # create new featureclass    try:        arcpy.CopyFeatures_management(input_shp, output_shp, 'DEFAULTS')    except Exception as e:        print(e)        raise RuntimeError('failed to create new feature class')    # coord transformation    try:        i_cursor = arcpy.da.UpdateCursor(output_shp, ['SHAPE@'])        if feature_type == 'Point':            point_trans_arcpy(i_cursor, tran_func, spa_ref)        elif feature_type == 'Polyline':            polyline_trans_arcpy(i_cursor, tran_func, spa_ref)        elif feature_type == 'Polygon':            polygon_trans_arcpy(i_cursor, tran_func, spa_ref)        else:            raise NotImplementedError('Unknown feature type')    except Exception as e:        raise RuntimeError('failed to conduct coordinate transformation')def correct(input_shp:str, output_shp:str, correct_type: str = 'bd'):    if correct_type == 'bd':        tran_func = CoordTrans.bd09towgs84    elif correct_type == 'gd':        tran_func = CoordTrans.gcj02towgs84    else:        raise NotImplementedError('Unknown rectification type')    correct_core(input_shp, output_shp, tran_func)class Toolbox(object):    def __init__(self):        """Define the toolbox (the name of the toolbox is the name of the        .pyt file)."""        self.label = "Toolbox"        self.alias = "toolbox"        # List of tool classes associated with this toolbox        self.tools = [WGS_correct]class WGS_correct(object):    def __init__(self):        """Define the tool (tool name is the name of the class)."""        self.label = "WGS_correct"        self.description = ""        self.canRunInBackground = False    def getParameterInfo(self):        # """Define parameter definitions"""        param_input_shp = arcpy.Parameter(            displayName = u'input shp',            name = 'input_shp',            datatype = "GPFeatureLayer",            parameterType ='Required',            direction ='Input')        param_input_shp.filter.list = ['Point', 'Polyline', 'Polygon']        param_output_shp = arcpy.Parameter(            displayName = u'output shp',            name = u'output_shp',            datatype = "GPFeatureLayer",            parameterType ='Required',            direction ='Output')        param_correction_type = arcpy.Parameter(            displayName = u'correction type',            name = u'correction type',            datatype = "GPString",            parameterType ='Required',            direction ='Input')        param_correction_type.filter.list = ['gd', 'bd']        params = [param_input_shp, param_output_shp, param_correction_type]        return params    def isLicensed(self):        """Set whether tool is licensed to execute."""        return True    def updateParameters(self, parameters):        """Modify the values and properties of parameters before internal        validation is performed.  This method is called whenever a parameter        has been changed."""        return    def updateMessages(self, parameters):        """Modify the messages created by internal validation for each tool        parameter.  This method is called after internal validation."""        return    def execute(self, parameters, messages):        """The source code of the tool."""        input_shp = parameters[0].valueAsText        output_shp = parameters[1].valueAsText        correct_type = parameters[2].valueAsText        correct(input_shp, output_shp, correct_type)    def postExecute(self, parameters):        """This method takes place after outputs are processed and        added to the display."""        returnif __name__ == '__main__':    # rec_core('./data/rec/route_1.shp', './data/rec/route_rec.shp',  CoordTrans.gcj02towgs84)    # rec_core('./data/rec/county0.shp', './data/rec/county_rec.shp', CoordTrans.gcj02towgs84)    correct_core('./rec.gdb/route_1_WGS_REC7', './data/rec/county_rec2.shp', CoordTrans.gcj02towgs84)