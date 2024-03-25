import os, sys, re
import argparse
from tqdm import tqdm
import numpy as np
import open3d as o3d
from PIL import Image


#读取一个 PCD 文件并返回该文件的内容和一个坐标系网格
def read_pcd(pcd_path):
    source = o3d.io.read_triangle_mesh(pcd_path, enable_post_processing=False, print_progress=False)
    mesh_frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
    size=0.3, origin=[0, 0, 0])
    return source, mesh_frame

def set_up_pcd(vis, pcd_path):
    source, axis_obj = read_pcd(pcd_path)
    #将 PCD 文件中的几何数据显示在可视化窗口中
    vis.add_geometry(source)
    return source

def capture_image(image_path):
    #捕获当前窗口的图像，并将其存储在变量 image 中。这个图像是浮点数形式的，范围在 0 到 1 之间
    image = vis.capture_screen_float_buffer()
    #将捕获的浮点数形式的图像转换为 numpy 数组，并将其乘以 255，以便将其转换为整数形式的像素值
    image = np.asarray(image) * 255
    #将 numpy 数组转换为 PIL 图像对象
    pil_img = Image.fromarray(image.astype(np.uint8))
    pil_img.save(image_path)
    return False

def capture_image_from_pose(vis, scans, scene, output):
    pcd_path = os.path.join(scans, scene, scene + '_vh_clean_2.ply')
    print(pcd_path)
    source = set_up_pcd(vis, pcd_path)
    vis.update_geometry(source)
    #用于处理窗口事件，例如键盘和鼠标输入。在可视化期间，这可以确保窗口响应用户的交互操作
    vis.poll_events()
    #更新渲染器，将更新后的几何体数据渲染到屏幕上
    vis.update_renderer()
    capture_image(os.path.join(output,  scene + '.jpg'))
    vis.update_geometry(source)
    vis.poll_events()
    vis.update_renderer()
    vis.clear_geometries()
    vis.close()                


if __name__=="__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--scene', type=str, default='scene0000_00', help='scene_id')
    parser.add_argument('--scans', type=str, help='directory having scan_data')
    parser.add_argument('--output', help='directory for saving a top-down image')
    args = parser.parse_args()
    
    #创建一个可视化器对象，该对象可以捕获键盘回调事件
    vis = o3d.visualization.VisualizerWithKeyCallback()
    vis.create_window(width=640, height=420)
    #设置窗口的背景颜色为白色
    vis.get_render_option().background_color = np.asarray([256,256,256])
    ctr = vis.get_view_control()
    # 改变视图的视野（Field of View），使其增加 90 度
    ctr.change_field_of_view(step=90)
    
    capture_image_from_pose(vis, args.scans, args.scene, args.output)

    
