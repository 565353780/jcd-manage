import struct
import numpy as np
from abc import ABC, abstractmethod
from typing import BinaryIO


class BaseData(ABC):
    """所有数据类的基类"""
    
    @abstractmethod
    def from_stream(self, jcd_file: BinaryIO):
        """从二进制流中读取数据
        
        Args:
            jcd_file: 二进制文件流
        """
        pass
    
    @staticmethod
    def read_int(jcd_file: BinaryIO) -> int:
        """读取4字节整数"""
        return int.from_bytes(jcd_file.read(4), 'little')
    
    @staticmethod
    def read_float(jcd_file: BinaryIO) -> float:
        """读取4字节浮点数"""
        return struct.unpack('<f', jcd_file.read(4))[0]
    
    @staticmethod
    def read_byte(jcd_file: BinaryIO) -> int:
        """读取1字节整数"""
        return int.from_bytes(jcd_file.read(1), 'little')
    
    @staticmethod
    def read_string(jcd_file: BinaryIO) -> str:
        """读取字符串（前4字节为长度）"""
        length = BaseData.read_int(jcd_file)
        return jcd_file.read(length).decode('utf-8')
    
    @staticmethod
    def read_points(jcd_file: BinaryIO) -> np.ndarray:
        """读取点数组（4D点：x, y, z, w）
        
        Returns:
            numpy数组，形状为(n, 4)
        """
        point_count = BaseData.read_int(jcd_file)
        if point_count == 0:
            return np.array([]).reshape(0, 4)
        
        points = np.zeros((point_count, 4), dtype=np.float32)
        for i in range(point_count):
            points[i] = struct.unpack('<ffff', jcd_file.read(16))
        return points
    
    @staticmethod
    def read_points_3d(jcd_file: BinaryIO) -> np.ndarray:
        """读取3D点数组（x, y, z）
        
        Returns:
            numpy数组，形状为(n, 3)
        """
        point_count = BaseData.read_int(jcd_file)
        if point_count == 0:
            return np.array([]).reshape(0, 3)
        
        points = np.zeros((point_count, 3), dtype=np.float32)
        for i in range(point_count):
            points[i] = struct.unpack('<fff', jcd_file.read(12))
        return points
    
    @staticmethod
    def read_int_points(jcd_file: BinaryIO) -> np.ndarray:
        """读取整数点数组（4D整数点）
        
        Returns:
            numpy数组，形状为(n, 4)
        """
        point_count = BaseData.read_int(jcd_file)
        if point_count == 0:
            return np.array([]).reshape(0, 4)
        
        points = np.zeros((point_count, 4), dtype=np.int32)
        for i in range(point_count):
            points[i] = struct.unpack('<iiii', jcd_file.read(16))
        return points
    
    @staticmethod
    def read_matrix(jcd_file: BinaryIO) -> np.ndarray:
        """读取单个4x4矩阵
        
        Returns:
            numpy数组，形状为(4, 4)
        """
        matrix = np.zeros((4, 4), dtype=np.float32)
        for i in range(4):
            for j in range(4):
                matrix[i, j] = BaseData.read_float(jcd_file)
        return matrix
    
    @staticmethod
    def read_matrices(jcd_file: BinaryIO, count: int) -> np.ndarray:
        """读取多个4x4矩阵（矩阵间有4字节间隔）
        
        Args:
            count: 矩阵数量
            
        Returns:
            numpy数组，形状为(count, 4, 4)
        """
        if count == 0:
            return np.array([]).reshape(0, 4, 4)
        
        matrices = np.zeros((count, 4, 4), dtype=np.float32)
        for i in range(count):
            matrices[i] = BaseData.read_matrix(jcd_file)
            # 两个矩阵之间间隔4个字节
            if i != count - 1:
                jcd_file.read(4)  # 跳过间隔数据
        return matrices
