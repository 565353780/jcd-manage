"""JCD数据可视化模块

使用Open3D进行JCD数据的通用可视化
"""
import numpy as np
import open3d as o3d
from typing import List, Union, Optional, Tuple
from jcd_manage.Data.jcd_base import JCDBaseData
from jcd_manage.Data.jcd_curve import JCDCurve
from jcd_manage.Data.jcd_surface import JCDSurface
from jcd_manage.Data.jcd_diamond import JCDDiamond
from jcd_manage.Data.jcd_font_surface import JCDFontSurface
from jcd_manage.Data.jcd_guide_line import JCDGuideLine
from jcd_manage.Data.jcd_bool_surface import JCDBoolSurface
from jcd_manage.Data.jcd_quad_type import JCDQuadType


class JCDRenderer:
    """JCD数据渲染器
    
    使用Open3D对各种JCD数据类型进行可视化
    """
    
    # 颜色方案
    COLORS = {
        'curve': [1.0, 0.0, 0.0],        # 红色
        'surface': [0.0, 0.5, 1.0],      # 蓝色
        'diamond': [1.0, 0.84, 0.0],     # 金色
        'font_surface': [0.0, 1.0, 0.0], # 绿色
        'guide_line': [0.5, 0.5, 0.5],   # 灰色
        'bool_surface': [1.0, 0.0, 1.0], # 洋红色
        'quad_type': [0.0, 1.0, 1.0],    # 青色
        'control_point': [1.0, 0.5, 0.0],# 橙色
        'normal': [0.8, 0.8, 0.8],       # 浅灰色
    }
    
    def __init__(self):
        """初始化渲染器"""
        self.geometries: List[o3d.geometry.Geometry] = []
        self.coordinate_frame = None
        
    def clear(self):
        """清空所有几何体"""
        self.geometries.clear()
        self.coordinate_frame = None
    
    def add_coordinate_frame(self, size: float = 10.0, origin: Optional[np.ndarray] = None):
        """添加坐标系
        
        Args:
            size: 坐标轴长度
            origin: 坐标系原点，默认为(0,0,0)
        """
        if origin is None:
            origin = np.array([0.0, 0.0, 0.0])
        
        self.coordinate_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=size, origin=origin
        )
        self.geometries.append(self.coordinate_frame)
    
    def _create_curve_geometry(self, curve: JCDCurve, color: Optional[List[float]] = None) -> List[o3d.geometry.Geometry]:
        """创建曲线几何体
        
        Args:
            curve: JCDCurve对象
            color: 颜色RGB，默认使用预设颜色
            
        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['curve']
        
        geometries = []
        
        points_3d = curve.get_points()
        if points_3d is None or len(points_3d) < 2:
            return geometries
        
        # 创建LineSet
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points_3d)
        
        # 创建线段索引
        lines = [[i, i + 1] for i in range(len(points_3d) - 1)]
        
        # 如果是闭合曲线，连接首尾
        if curve.is_closed() and len(points_3d) > 2:
            lines.append([len(points_3d) - 1, 0])
        
        line_set.lines = o3d.utility.Vector2iVector(lines)
        
        # 设置颜色
        colors = [color for _ in range(len(lines))]
        line_set.colors = o3d.utility.Vector3dVector(colors)
        
        geometries.append(line_set)
        
        return geometries
    
    def _create_surface_geometry(self, surface: JCDSurface, color: Optional[List[float]] = None,
                                show_wireframe: bool = True) -> List[o3d.geometry.Geometry]:
        """创建曲面几何体

        Args:
            surface: JCDSurface对象
            color: 颜色RGB，默认使用预设颜色
            show_wireframe: 是否显示网格线

        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['surface']

        geometries = []

        all_points = surface.get_points()
        bbox_min, bbox_max = surface.get_bounding_box()

        bbox_bound = np.max(bbox_max - bbox_min)
        if bbox_bound < 22:
            return geometries
        print(bbox_bound)

        if all_points is None or surface.u_count() == 0 or surface.v_count() == 0:
            return geometries

        # 重构网格结构
        grid = all_points.reshape(surface.u_count(), surface.v_count(), 3)

        # 创建网格线（U方向和V方向）
        if show_wireframe:
            # U方向曲线
            for i in range(surface.u_count()):
                points_3d = grid[i, :, :]
                line_set = o3d.geometry.LineSet()
                line_set.points = o3d.utility.Vector3dVector(points_3d)
                lines = [[j, j + 1] for j in range(len(points_3d) - 1)]
                line_set.lines = o3d.utility.Vector2iVector(lines)
                line_set.paint_uniform_color(color)
                geometries.append(line_set)

            # V方向曲线
            for j in range(surface.v_count()):
                points_3d = grid[:, j, :]
                line_set = o3d.geometry.LineSet()
                line_set.points = o3d.utility.Vector3dVector(points_3d)
                lines = [[i, i + 1] for i in range(len(points_3d) - 1)]
                line_set.lines = o3d.utility.Vector2iVector(lines)
                line_set.paint_uniform_color(color)
                geometries.append(line_set)

        return geometries

    def _create_diamond_geometry(self, diamond: JCDDiamond, color: Optional[List[float]] = None) -> List[o3d.geometry.Geometry]:
        """创建钻石几何体

        Args:
            diamond: JCDDiamond对象
            color: 颜色RGB，默认使用预设颜色

        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['diamond']

        geometries = []

        # 根据钻石类型创建不同的几何体
        # 这里使用简化的表示：一个球体
        sphere = o3d.geometry.TriangleMesh.create_sphere(radius=1.0, resolution=20)
        sphere.paint_uniform_color(color)
        sphere.compute_vertex_normals()

        # 应用钻石的完整变换矩阵
        transform_matrix = diamond.matrix.T
        sphere.transform(transform_matrix)

        geometries.append(sphere)

        return geometries

    def _create_font_surface_geometry(self, font_surface: JCDFontSurface, 
                                     color: Optional[List[float]] = None) -> List[o3d.geometry.Geometry]:
        """创建字体面片几何体

        Args:
            font_surface: JCDFontSurface对象
            color: 颜色RGB，默认使用预设颜色

        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['font_surface']

        geometries = []
        
        all_points = font_surface.get_points()
        if all_points is None or len(all_points) == 0:
            return geometries
        
        # 按轮廓分割点
        outline_sizes = font_surface.outline_sizes
        start_idx = 0
        
        for size in outline_sizes:
            if start_idx + size > len(all_points):
                break
            
            outline = all_points[start_idx:start_idx + size]
            start_idx += size
            
            if len(outline) < 2:
                continue
            
            # 创建闭合轮廓线
            line_set = o3d.geometry.LineSet()
            line_set.points = o3d.utility.Vector3dVector(outline)
            
            # 创建闭合轮廓
            lines = [[i, i + 1] for i in range(len(outline) - 1)]
            lines.append([len(outline) - 1, 0])  # 闭合
            
            line_set.lines = o3d.utility.Vector2iVector(lines)
            line_set.paint_uniform_color(color)
            
            geometries.append(line_set)
        
        return geometries
    
    def _create_guide_line_geometry(self, guide_line: JCDGuideLine, 
                                   color: Optional[List[float]] = None,
                                   length: float = 10.0) -> List[o3d.geometry.Geometry]:
        """创建辅助线几何体
        
        Args:
            guide_line: JCDGuideLine对象
            color: 颜色RGB，默认使用预设颜色
            length: 线段长度（该参数已由get_points()内部处理）
            
        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['guide_line']
        
        geometries = []
        
        points = guide_line.get_points()
        if points is None or len(points) < 2:
            return geometries
        
        line_set = o3d.geometry.LineSet()
        line_set.points = o3d.utility.Vector3dVector(points)
        line_set.lines = o3d.utility.Vector2iVector([[0, 1]])
        line_set.paint_uniform_color(color)
        
        geometries.append(line_set)
        
        return geometries
    
    def _create_bool_surface_geometry(self, bool_surface: JCDBoolSurface, 
                                     color: Optional[List[float]] = None) -> List[o3d.geometry.Geometry]:
        """创建布尔曲面几何体
        
        Args:
            bool_surface: JCDBoolSurface对象
            color: 颜色RGB，默认使用预设颜色
            
        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['bool_surface']
        
        geometries = []
        
        points = bool_surface.get_points()
        if points is not None and len(points) > 0:
            # 创建点云表示
            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(points)
            pcd.paint_uniform_color(color)
            geometries.append(pcd)
        
        return geometries
    
    def _create_quad_type_geometry(self, quad_type: JCDQuadType, 
                                  color: Optional[List[float]] = None,
                                  show_wireframe: bool = True) -> List[o3d.geometry.Geometry]:
        """创建四边形面片几何体
        
        Args:
            quad_type: JCDQuadType对象
            color: 颜色RGB，默认使用预设颜色
            show_wireframe: 是否显示线框
            
        Returns:
            几何体列表
        """
        if color is None:
            color = self.COLORS['quad_type']
        
        geometries = []
        
        if quad_type.num_vertices() == 0 or quad_type.num_quads() == 0:
            return geometries
        
        vertices = quad_type.get_points()
        if vertices is None:
            return geometries
        
        # 将四边形分解为三角形
        triangles = []
        for i in range(quad_type.num_quads()):
            quad_indices = quad_type.indices[i]
            # 将四边形分为两个三角形
            triangles.append([quad_indices[0], quad_indices[1], quad_indices[2]])
            triangles.append([quad_indices[0], quad_indices[2], quad_indices[3]])
        
        # 创建TriangleMesh
        mesh = o3d.geometry.TriangleMesh()
        mesh.vertices = o3d.utility.Vector3dVector(vertices)
        mesh.triangles = o3d.utility.Vector3iVector(triangles)
        mesh.paint_uniform_color(color)
        mesh.compute_vertex_normals()
        
        geometries.append(mesh)
        
        # 添加线框
        if show_wireframe:
            line_set = o3d.geometry.LineSet.create_from_triangle_mesh(mesh)
            line_set.paint_uniform_color([0.3, 0.3, 0.3])
            geometries.append(line_set)
        
        return geometries
    
    def add_data(self, data: Union[JCDBaseData, List[JCDBaseData]], 
                 color: Optional[List[float]] = None,
                 **kwargs):
        """添加JCD数据到渲染器
        
        Args:
            data: JCDBaseData对象或对象列表
            color: 自定义颜色RGB，默认使用类型对应的颜色
            **kwargs: 其他渲染参数
        """
        # 处理列表
        if isinstance(data, list):
            for item in data:
                self.add_data(item, color, **kwargs)
            return
        
        # 跳过隐藏对象
        if data.hide:
            return
        
        # 根据类型创建几何体
        if isinstance(data, JCDCurve):
            geometries = self._create_curve_geometry(data, color)
        elif isinstance(data, JCDSurface):
            geometries = self._create_surface_geometry(
                data, color, 
                show_wireframe=kwargs.get('show_wireframe', True)
            )
        elif isinstance(data, JCDDiamond):
            geometries = self._create_diamond_geometry(data, color)
        elif isinstance(data, JCDFontSurface):
            geometries = self._create_font_surface_geometry(data, color)
        elif isinstance(data, JCDGuideLine):
            geometries = self._create_guide_line_geometry(
                data, color, 
                length=kwargs.get('guide_line_length', 10.0)
            )
        elif isinstance(data, JCDBoolSurface):
            geometries = self._create_bool_surface_geometry(data, color)
        elif isinstance(data, JCDQuadType):
            geometries = self._create_quad_type_geometry(
                data, color,
                show_wireframe=kwargs.get('show_wireframe', True)
            )
        else:
            print(f"警告: 不支持的数据类型 {type(data)}")
            return
        
        self.geometries.extend(geometries)
    
    def render(self, window_name: str = "JCD Viewer", 
               width: int = 1024, height: int = 768,
               show_coordinate_frame: bool = True,
               coordinate_frame_size: float = 10.0):
        """渲染所有几何体
        
        Args:
            window_name: 窗口名称
            width: 窗口宽度
            height: 窗口高度
            show_coordinate_frame: 是否显示坐标系
            coordinate_frame_size: 坐标系大小
        """
        if len(self.geometries) == 0:
            print("警告: 没有几何体可以渲染")
            return
        
        # 添加坐标系
        if show_coordinate_frame and self.coordinate_frame is None:
            self.add_coordinate_frame(size=coordinate_frame_size)
        
        # 创建可视化窗口
        vis = o3d.visualization.Visualizer()
        vis.create_window(window_name=window_name, width=width, height=height)
        
        # 添加所有几何体
        for geom in self.geometries:
            vis.add_geometry(geom)
        
        # 设置渲染选项
        opt = vis.get_render_option()
        opt.background_color = np.asarray([0.1, 0.1, 0.1])  # 深灰色背景
        opt.point_size = 5.0
        opt.line_width = 2.0
        
        # 运行可视化
        vis.run()
        vis.destroy_window()
    
    def save_view(self, filename: str):
        """保存当前视图为图片
        
        Args:
            filename: 保存的文件名（支持png, jpg等格式）
        """
        if len(self.geometries) == 0:
            print("警告: 没有几何体可以保存")
            return
        
        vis = o3d.visualization.Visualizer()
        vis.create_window(visible=False)
        
        for geom in self.geometries:
            vis.add_geometry(geom)
        
        vis.capture_screen_image(filename)
        vis.destroy_window()
        print(f"视图已保存到: {filename}")
    
    def get_bounding_box(self) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """计算所有几何体的总边界框
        
        Returns:
            (min_point, max_point) 或 None
        """
        if len(self.geometries) == 0:
            return None
        
        all_points = []
        
        for geom in self.geometries:
            if isinstance(geom, o3d.geometry.PointCloud):
                all_points.extend(np.asarray(geom.points))
            elif isinstance(geom, o3d.geometry.LineSet):
                all_points.extend(np.asarray(geom.points))
            elif isinstance(geom, o3d.geometry.TriangleMesh):
                all_points.extend(np.asarray(geom.vertices))
        
        if len(all_points) == 0:
            return None
        
        all_points = np.array(all_points)
        min_point = np.min(all_points, axis=0)
        max_point = np.max(all_points, axis=0)
        
        return min_point, max_point


def renderData(data: Union[JCDBaseData, List[JCDBaseData]], 
               color: Optional[List[float]] = None,
               window_name: str = "JCD Viewer",
               width: int = 1024,
               height: int = 768,
               show_coordinate_frame: bool = True,
               coordinate_frame_size: float = 10.0,
               **kwargs):
    """通用的JCD数据渲染函数
    
    这是一个便捷函数，用于快速可视化JCD数据。
    
    Args:
        data: JCDBaseData对象或对象列表
        color: 自定义颜色RGB (0-1范围)，例如 [1.0, 0.0, 0.0] 为红色
        window_name: 窗口标题
        width: 窗口宽度（像素）
        height: 窗口高度（像素）
        show_coordinate_frame: 是否显示坐标系
        coordinate_frame_size: 坐标系大小
        **kwargs: 其他渲染参数
            - show_wireframe: bool, 是否显示网格线（用于曲面和四边形）
            - guide_line_length: float, 辅助线长度
    
    示例:
        >>> from jcd_manage.Module.jcd_loader import JCDLoader
        >>> loader = JCDLoader()
        >>> loader.loadJCDFile("model.jcd")
        >>> 
        >>> # 渲染所有对象
        >>> renderData(loader.objects)
        >>> 
        >>> # 只渲染曲线，使用自定义颜色
        >>> curves = loader.get_curves()
        >>> renderData(curves, color=[1.0, 0.0, 0.0])
        >>> 
        >>> # 渲染曲面，不显示网格线
        >>> surfaces = loader.get_surfaces()
        >>> renderData(surfaces, show_wireframe=False)
    """
    renderer = JCDRenderer()
    renderer.add_data(data, color, **kwargs)
    renderer.render(
        window_name=window_name,
        width=width,
        height=height,
        show_coordinate_frame=show_coordinate_frame,
        coordinate_frame_size=coordinate_frame_size
    )


def renderMultipleGroups(data_groups: List[Tuple[Union[JCDBaseData, List[JCDBaseData]], List[float]]],
                        window_name: str = "JCD Viewer",
                        width: int = 1024,
                        height: int = 768,
                        show_coordinate_frame: bool = True,
                        coordinate_frame_size: float = 10.0,
                        **kwargs):
    """渲染多组数据，每组使用不同的颜色
    
    Args:
        data_groups: 数据组列表，每个元素为 (data, color) 元组
        window_name: 窗口标题
        width: 窗口宽度
        height: 窗口高度
        show_coordinate_frame: 是否显示坐标系
        coordinate_frame_size: 坐标系大小
        **kwargs: 其他渲染参数
    
    示例:
        >>> from jcd_manage.Module.jcd_loader import JCDLoader
        >>> loader = JCDLoader()
        >>> loader.loadJCDFile("model.jcd")
        >>> 
        >>> # 不同类型使用不同颜色
        >>> groups = [
        ...     (loader.get_curves(), [1.0, 0.0, 0.0]),      # 红色曲线
        ...     (loader.get_surfaces(), [0.0, 1.0, 0.0]),    # 绿色曲面
        ...     (loader.get_diamonds(), [1.0, 0.84, 0.0]),   # 金色钻石
        ... ]
        >>> renderMultipleGroups(groups)
    """
    renderer = JCDRenderer()
    
    for data, color in data_groups:
        renderer.add_data(data, color, **kwargs)
    
    renderer.render(
        window_name=window_name,
        width=width,
        height=height,
        show_coordinate_frame=show_coordinate_frame,
        coordinate_frame_size=coordinate_frame_size
    )
