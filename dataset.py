from __future__ import annotations
import numpy as np
import cv2
import pandas as pd




class CitySimDataSet():
    """ `CitySim` 数据集

    `method:`
    >>> len(dataset): 返回该数据集中车辆数
        dataset[i]: 返回该数据集中第[i]条车辆轨迹, pandas.DataFrame
        dataset_3 = dataset_1 + dataset_2: 合并数据集

    `attribute:`
    >>> dataset.id_list: 数据集中每条车辆轨迹的车辆ID list[str]
    """
    COLUMNS = [
        "frameNum",
        "carId",
        "carCenterX",
        "carCenterY",
        "headX",
        "headY",
        "tailX",
        "tailY",
        "boundingBox1X",
        "boundingBox1Y",
        "boundingBox2X",
        "boundingBox2Y",
        "boundingBox3X",
        "boundingBox3Y",
        "boundingBox4X",
        "boundingBox4Y",
        "carCenterXft",
        "carCenterYft",
        "headXft",
        "headYft",
        "tailXft",
        "tailYft",
        "boundingBox1Xft",
        "boundingBox1Yft",
        "boundingBox2Xft",
        "boundingBox2Yft",
        "boundingBox3Xft",
        "boundingBox3Yft",
        "boundingBox4Xft",
        "boundingBox4Yft",
        "carCenterLat",
        "carCenterLon",
        "headLat",
        "headLon",
        "tailLat",
        "tailLon",
        "boundingBox1Lat",
        "boundingBox1Lon",
        "boundingBox2Lat",
        "boundingBox2Lon",
        "boundingBox3Lat",
        "boundingBox3Lon",
        "boundingBox4Lat",
        "boundingBox4Lon",
        "speed",
        "heading",
        "course",
        "laneId"]
    """数据集字段
    """
    def __init__(self, path: str, columns: list[str] = None):
        """从 `.csv` 文件初始化一个数据集

            注：`*.csv` 文件中的字段 `["speed"]` 在导入时单位已经由 mile/h -> km/h

        Args:
            path (str): `*.csv` 文件的位置

            columns (list[str], optional): 要从 `*.csv` 格式文件中读取的字段, 若留空则默认全部读取. Defaults to None.
                注意：`"carId"`, `"frameNum"` 为 `columns` 必选项
        """
        if path is None:

            self.data:pd.DataFrame = None
            """原始数据"""
            self.id_list:list = None
            """车辆 ID 列表"""
            self.__start_index__:np.ndarray = None
            """车辆轨迹起始 索引

                注：不包括结尾索引
            """
        else:
            self.data = CitySimDataSet.__readcsv__(path, columns)
            self.data["speed"] = self.data["speed"] * 0.44704 # mile/h TO km/h
            self.id_list, self.__start_index__ = CitySimDataSet.__splitdata__(self.data)
        pass

    def __getitem__(self, index: int) -> pd.DataFrame:
        # start_idx = self.__start_index__[index] + 1
        start_idx = self.__start_index__[index]
        if index != len(self) -1:
            # end_idx = self.__start_index__[index+1] + 1
            end_idx = self.__start_index__[index+1]
        else:
            # end_idx = self.data.shape[0]-1
            end_idx = self.data.shape[0]
        return self.data[start_idx:end_idx]
    

    def __len__(self) -> int:
        return len(self.__start_index__)

    def __readcsv__(filepath: str, usecols: list[str]) -> pd.DataFrame:
        datatable = pd.read_csv(filepath, usecols=usecols)
        datatable.sort_values(by=["carId", "frameNum"], inplace=True)
        return datatable

    def __splitdata__(data: pd.DataFrame) -> tuple[list,np.ndarray]:
        frameNum = np.array(data["frameNum"])
        carId = np.array(data["carId"])
        id_list = [data["carId"][0]]

        start_index = [0,]
        l = frameNum.shape[0]
        for i in range(l-2):
            if carId[i] != carId[i+1]:

                start_index.append(i+1)
                id_list.append(carId[i+1])
        start_index = np.array(start_index,dtype="int32")
        return id_list, start_index

    def __add__(self, other:CitySimDataSet) -> CitySimDataSet:
        new = CitySimDataSet(None)
        new.__start_index__ = np.concatenate((self.__start_index__, other.__start_index__ + other.data.shape[0]+1),axis=0)
        new.data = pd.concat([self.data,other.data])
        new.id_list = self.id_list + other.id_list
        return new