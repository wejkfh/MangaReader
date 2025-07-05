import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
import time
from pathlib import Path
import re
from datetime import datetime
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("警告: OpenCV未安装，视频功能将受限")

class EnhancedMangaReader:
    def __init__(self, root):
        self.root = root
        self.root.title("增强版漫画阅读器")
        self.root.geometry("1400x900")
        
        # 当前状态
        self.current_directory = ""
        self.root_directory = ""
        self.image_files = []
        self.video_files = []
        self.current_index = 0
        self.is_playing_video = False
        self.video_cap = None
        self.video_thread = None
        self.is_fullscreen = False
        
        # 显示设置
        self.align_mode = tk.StringVar(value="width")  # width, height, fit
        self.reading_mode = tk.StringVar(value="page")  # page, continuous
        
        # 支持的文件格式
        self.image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff', '.tif'}
        self.video_extensions = {'.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv'}
        
        # 缩放设置
        self.zoom_factor = 1.0
        self.original_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主框架
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 顶部控制面板
        self.setup_control_panel()
        
        # 中间内容区域
        content_frame = ttk.Frame(self.main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # 左侧面板（文件树和缩略图）
        self.setup_left_panel(content_frame)
        
        # 右侧显示区域
        self.setup_display_area(content_frame)
        
        # 底部状态栏
        self.setup_status_bar()
        
        # 绑定事件
        self.bind_events()
        
    def setup_control_panel(self):
        control_frame = ttk.Frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 第一行：目录操作
        row1 = ttk.Frame(control_frame)
        row1.pack(fill=tk.X, pady=(0, 2))
        
        ttk.Button(row1, text="选择根目录", command=self.select_root_directory).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="递归查找图片", command=self.recursive_find_images).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="后续目录查找", command=self.find_subsequent_directories).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(row1, text="刷新", command=self.refresh_current_directory).pack(side=tk.LEFT, padx=(0, 5))
        
        # 当前目录显示
        self.dir_label = ttk.Label(row1, text="未选择目录")
        self.dir_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 第二行：显示设置
        row2 = ttk.Frame(control_frame)
        row2.pack(fill=tk.X, pady=(2, 0))
        
        # 对齐模式
        ttk.Label(row2, text="对齐:").pack(side=tk.LEFT)
        ttk.Radiobutton(row2, text="宽度", variable=self.align_mode, value="width", command=self.update_display_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(row2, text="高度", variable=self.align_mode, value="height", command=self.update_display_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(row2, text="适应", variable=self.align_mode, value="fit", command=self.update_display_mode).pack(side=tk.LEFT, padx=(0, 10))
        
        # 阅读模式
        ttk.Label(row2, text="模式:").pack(side=tk.LEFT)
        ttk.Radiobutton(row2, text="翻页", variable=self.reading_mode, value="page", command=self.update_reading_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(row2, text="连续", variable=self.reading_mode, value="continuous", command=self.update_reading_mode).pack(side=tk.LEFT, padx=(0, 10))
        
        # 全屏按钮
        ttk.Button(row2, text="全屏", command=self.toggle_fullscreen).pack(side=tk.LEFT, padx=(0, 5))
        
        # 视频控制
        self.play_button = ttk.Button(row2, text="播放视频", command=self.toggle_video)
        self.play_button.pack(side=tk.LEFT, padx=(0, 5))
        
    def setup_left_panel(self, parent):
        # 左侧面板
        left_panel = ttk.Frame(parent)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        
        # 文件树
        tree_frame = ttk.LabelFrame(left_panel, text="目录树")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        # 创建文件树
        self.file_tree = ttk.Treeview(tree_frame)
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # 缩略图面板
        thumbnail_frame = ttk.LabelFrame(left_panel, text="缩略图")
        thumbnail_frame.pack(fill=tk.BOTH, expand=True)
        
        # 缩略图滚动区域
        self.thumbnail_canvas = tk.Canvas(thumbnail_frame)
        thumbnail_scrollbar = ttk.Scrollbar(thumbnail_frame, orient="vertical", command=self.thumbnail_canvas.yview)
        self.thumbnail_frame_inner = ttk.Frame(self.thumbnail_canvas)
        
        self.thumbnail_canvas.configure(yscrollcommand=thumbnail_scrollbar.set)
        self.thumbnail_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        thumbnail_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.thumbnail_canvas.create_window((0, 0), window=self.thumbnail_frame_inner, anchor="nw")
        
    def setup_display_area(self, parent):
        # 右侧显示区域
        display_frame = ttk.Frame(parent)
        display_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # 导航按钮框架
        nav_frame = ttk.Frame(display_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(nav_frame, text="上一张", command=self.previous_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="下一张", command=self.next_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="第一张", command=self.first_image).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="最后一张", command=self.last_image).pack(side=tk.LEFT, padx=(0, 5))
        
        # 缩放控制
        ttk.Button(nav_frame, text="放大", command=self.zoom_in).pack(side=tk.LEFT, padx=(10, 5))
        ttk.Button(nav_frame, text="缩小", command=self.zoom_out).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(nav_frame, text="原始大小", command=self.original_size).pack(side=tk.LEFT, padx=(0, 5))
        
        # 图片显示区域
        self.display_canvas = tk.Canvas(display_frame, bg="black")
        display_scrollbar_v = ttk.Scrollbar(display_frame, orient="vertical", command=self.display_canvas.yview)
        display_scrollbar_h = ttk.Scrollbar(display_frame, orient="horizontal", command=self.display_canvas.xview)
        
        self.display_canvas.configure(yscrollcommand=display_scrollbar_v.set, xscrollcommand=display_scrollbar_h.set)
        
        self.display_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        display_scrollbar_v.pack(side=tk.RIGHT, fill=tk.Y)
        display_scrollbar_h.pack(side=tk.BOTTOM, fill=tk.X)
        
    def setup_status_bar(self):
        # 底部状态栏
        status_frame = ttk.Frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.status_label = ttk.Label(status_frame, text="就绪")
        self.status_label.pack(side=tk.LEFT)
        
        # 进度信息
        self.progress_label = ttk.Label(status_frame, text="")
        self.progress_label.pack(side=tk.RIGHT)
        
    def bind_events(self):
        # 绑定键盘事件
        self.root.bind('<Key>', self.on_key_press)
        self.root.focus_set()
        
        # 绑定鼠标滚轮事件
        self.display_canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.display_canvas.bind("<Button-1>", self.on_canvas_click)
        
        # 绑定窗口事件
        self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self.exit_fullscreen())
        
    def select_root_directory(self):
        """选择根目录"""
        directory = filedialog.askdirectory(title="选择漫画根目录")
        if directory:
            self.root_directory = directory
            self.current_directory = directory
            self.dir_label.config(text=f"根目录: {os.path.basename(directory)}")
            self.populate_file_tree()
            self.load_files_from_directory(directory)
            
    def populate_file_tree(self):
        """填充文件树"""
        # 清空文件树
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
            
        if not self.root_directory:
            return
            
        # 添加根节点
        root_name = os.path.basename(self.root_directory)
        root_item = self.file_tree.insert("", "end", text=root_name, values=[self.root_directory])
        
        # 递归添加子目录
        self._add_tree_children(root_item, self.root_directory)
        
        # 展开根节点
        self.file_tree.item(root_item, open=True)
        
    def _add_tree_children(self, parent_item, directory):
        """递归添加文件树子节点"""
        try:
            items = os.listdir(directory)
            # 按目录名排序（考虑日期格式）
            dirs = [item for item in items if os.path.isdir(os.path.join(directory, item))]
            dirs.sort(key=self._extract_date_from_dirname)
            
            for item in dirs:
                item_path = os.path.join(directory, item)
                tree_item = self.file_tree.insert(parent_item, "end", text=item, values=[item_path])
                
                # 检查是否有子目录
                try:
                    sub_items = os.listdir(item_path)
                    has_subdirs = any(os.path.isdir(os.path.join(item_path, sub)) for sub in sub_items)
                    if has_subdirs:
                        self._add_tree_children(tree_item, item_path)
                except PermissionError:
                    pass
                    
        except PermissionError:
            pass
            
    def _extract_date_from_dirname(self, dirname):
        """从目录名提取日期用于排序"""
        # 匹配 yyyy-mm-dd 格式
        date_pattern = r'(\d{4}-\d{2}-\d{2})'
        match = re.search(date_pattern, dirname)
        if match:
            try:
                return datetime.strptime(match.group(1), '%Y-%m-%d')
            except ValueError:
                pass
        
        # 如果没有日期格式，按字母顺序
        return datetime.min
        
    def on_tree_select(self, event):
        """文件树选择事件"""
        selection = self.file_tree.selection()
        if selection:
            item = selection[0]
            values = self.file_tree.item(item, 'values')
            if values:
                directory = values[0]
                self.current_directory = directory
                self.dir_label.config(text=f"当前: {os.path.basename(directory)}")
                self.load_files_from_directory(directory)
                
    def load_files_from_directory(self, directory):
        """从目录加载文件"""
        self.image_files = []
        self.video_files = []
        
        try:
            files = os.listdir(directory)
            for file in files:
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    ext = Path(file).suffix.lower()
                    
                    if ext in self.image_extensions:
                        self.image_files.append(file_path)
                    elif ext in self.video_extensions:
                        self.video_files.append(file_path)
            
            # 智能排序
            self.image_files.sort(key=self._smart_sort_key)
            self.video_files.sort(key=self._smart_sort_key)
            
            self.current_index = 0
            self.update_thumbnails()
            self.display_current_item()
            self.update_status()
            
        except Exception as e:
            messagebox.showerror("错误", f"加载目录失败: {str(e)}")
            
    def _smart_sort_key(self, filepath):
        """智能排序键"""
        filename = os.path.basename(filepath)
        
        # 尝试提取数字
        numbers = re.findall(r'\d+', filename)
        if numbers:
            # 如果有数字，按第一个数字排序
            try:
                return (0, int(numbers[0]), filename)
            except ValueError:
                pass
        
        # 按文件修改时间排序
        try:
            mtime = os.path.getmtime(filepath)
            return (1, mtime, filename)
        except OSError:
            return (2, 0, filename)
            
    def recursive_find_images(self):
        """递归查找当前目录下所有图片"""
        if not self.current_directory:
            messagebox.showwarning("警告", "请先选择目录")
            return
            
        self.image_files = []
        self.video_files = []
        
        # 获取所有子目录并排序
        all_dirs = []
        for root, dirs, files in os.walk(self.current_directory):
            all_dirs.append(root)
            
        # 按目录路径中的日期排序
        all_dirs.sort(key=lambda d: self._extract_date_from_path(d))
        
        # 从每个目录收集文件
        for directory in all_dirs:
            try:
                files = os.listdir(directory)
                dir_images = []
                dir_videos = []
                
                for file in files:
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path):
                        ext = Path(file).suffix.lower()
                        
                        if ext in self.image_extensions:
                            dir_images.append(file_path)
                        elif ext in self.video_extensions:
                            dir_videos.append(file_path)
                
                # 对每个目录内的文件排序
                dir_images.sort(key=self._smart_sort_key)
                dir_videos.sort(key=self._smart_sort_key)
                
                self.image_files.extend(dir_images)
                self.video_files.extend(dir_videos)
                
            except PermissionError:
                continue
        
        self.current_index = 0
        self.update_thumbnails()
        self.display_current_item()
        self.update_status()
        
    def _extract_date_from_path(self, path):
        """从路径提取日期"""
        # 从路径的各个部分提取日期
        parts = path.split(os.sep)
        for part in parts:
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', part)
            if date_match:
                try:
                    return datetime.strptime(date_match.group(1), '%Y-%m-%d')
                except ValueError:
                    pass
        return datetime.min
        
    def find_subsequent_directories(self):
        """查找当前目录后续的同级目录"""
        if not self.current_directory or not self.root_directory:
            messagebox.showwarning("警告", "请先选择根目录")
            return
            
        # 获取当前目录的父目录
        parent_dir = os.path.dirname(self.current_directory)
        if not parent_dir or parent_dir == self.current_directory:
            parent_dir = self.root_directory
            
        try:
            # 获取同级目录
            all_dirs = []
            for item in os.listdir(parent_dir):
                item_path = os.path.join(parent_dir, item)
                if os.path.isdir(item_path):
                    all_dirs.append(item_path)
                    
            # 按日期排序
            all_dirs.sort(key=lambda d: self._extract_date_from_dirname(os.path.basename(d)))
            
            # 找到当前目录的位置
            current_index = -1
            for i, dir_path in enumerate(all_dirs):
                if os.path.samefile(dir_path, self.current_directory):
                    current_index = i
                    break
                    
            if current_index == -1:
                messagebox.showwarning("警告", "无法找到当前目录在同级目录中的位置")
                return
                
            # 获取后续目录
            subsequent_dirs = all_dirs[current_index + 1:]
            
            if not subsequent_dirs:
                messagebox.showinfo("信息", "没有后续目录")
                return
                
            # 从后续目录递归收集图片
            self.image_files = []
            self.video_files = []
            
            for directory in subsequent_dirs:
                for root, dirs, files in os.walk(directory):
                    dir_images = []
                    dir_videos = []
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        ext = Path(file).suffix.lower()
                        
                        if ext in self.image_extensions:
                            dir_images.append(file_path)
                        elif ext in self.video_extensions:
                            dir_videos.append(file_path)
                    
                    dir_images.sort(key=self._smart_sort_key)
                    dir_videos.sort(key=self._smart_sort_key)
                    
                    self.image_files.extend(dir_images)
                    self.video_files.extend(dir_videos)
                    
            self.current_index = 0
            self.update_thumbnails()
            self.display_current_item()
            self.update_status()
            
            messagebox.showinfo("信息", f"已加载 {len(subsequent_dirs)} 个后续目录的内容")
            
        except Exception as e:
            messagebox.showerror("错误", f"查找后续目录失败: {str(e)}")
            
    def refresh_current_directory(self):
        """刷新当前目录"""
        if self.current_directory:
            self.load_files_from_directory(self.current_directory)
        else:
            messagebox.showwarning("警告", "请先选择目录")
            
    def update_thumbnails(self):
        """更新缩略图"""
        # 清除现有缩略图
        for widget in self.thumbnail_frame_inner.winfo_children():
            widget.destroy()
            
        # 创建新缩略图
        for i, file_path in enumerate(self.image_files[:50]):  # 限制显示数量以提高性能
            try:
                # 创建缩略图
                img = Image.open(file_path)
                img.thumbnail((120, 120), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # 创建缩略图按钮
                frame = ttk.Frame(self.thumbnail_frame_inner)
                frame.pack(fill=tk.X, pady=1)
                
                # 高亮当前选中的缩略图
                bg_color = "lightblue" if i == self.current_index else "white"
                btn = tk.Button(frame, image=photo, command=lambda idx=i: self.jump_to_image(idx), bg=bg_color)
                btn.image = photo  # 保持引用
                btn.pack(side=tk.LEFT)
                
                # 添加序号和文件名
                info_frame = ttk.Frame(frame)
                info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
                
                ttk.Label(info_frame, text=f"{i+1}", font=("Arial", 8, "bold")).pack(anchor="w")
                filename = os.path.basename(file_path)
                if len(filename) > 20:
                    filename = filename[:17] + "..."
                ttk.Label(info_frame, text=filename, font=("Arial", 7)).pack(anchor="w")
                
            except Exception as e:
                print(f"创建缩略图失败: {file_path}, {str(e)}")
                
        # 更新滚动区域
        self.thumbnail_frame_inner.update_idletasks()
        self.thumbnail_canvas.configure(scrollregion=self.thumbnail_canvas.bbox("all"))
        
    def jump_to_image(self, index):
        """跳转到指定图片"""
        self.current_index = index
        self.display_current_item()
        self.update_status()
        self.update_thumbnails()
        
    def display_current_item(self):
        """显示当前项目"""
        if not self.image_files and not self.video_files:
            return
            
        # 停止当前视频播放
        self.stop_video()
        
        if self.current_index < len(self.image_files):
            self.display_image(self.image_files[self.current_index])
        elif self.current_index - len(self.image_files) < len(self.video_files):
            video_index = self.current_index - len(self.image_files)
            self.display_video_thumbnail(self.video_files[video_index])
            
    def display_image(self, image_path):
        """显示图片"""
        try:
            # 加载原始图片
            self.original_image = Image.open(image_path)
            
            # 根据阅读模式显示
            if self.reading_mode.get() == "continuous":
                self.display_continuous_image()
            else:
                self.display_page_image()
                
        except Exception as e:
            messagebox.showerror("错误", f"显示图片失败: {str(e)}")
            
    def display_page_image(self):
        """翻页模式显示图片"""
        if not self.original_image:
            return
            
        # 清除画布
        self.display_canvas.delete("all")
        
        # 获取画布尺寸
        canvas_width = self.display_canvas.winfo_width()
        canvas_height = self.display_canvas.winfo_height()
        
        if canvas_width <= 1 or canvas_height <= 1:
            self.root.after(100, self.display_page_image)
            return
            
        # 计算缩放
        img = self.original_image.copy()
        img_width, img_height = img.size
        
        if self.align_mode.get() == "width":
            # 按宽度对齐
            scale = (canvas_width * 0.95) / img_width
        elif self.align_mode.get() == "height":
            # 按高度对齐
            scale = (canvas_height * 0.95) / img_height
        else:
            # 适应窗口
            scale_x = (canvas_width * 0.95) / img_width
            scale_y = (canvas_height * 0.95) / img_height
            scale = min(scale_x, scale_y)
            
        # 应用用户缩放
        scale *= self.zoom_factor
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 高质量缩放
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.current_photo = ImageTk.PhotoImage(img)
        
        # 居中显示
        x = max(0, (canvas_width - new_width) // 2)
        y = max(0, (canvas_height - new_height) // 2)
        
        self.display_canvas.create_image(x, y, anchor="nw", image=self.current_photo)
        
        # 更新滚动区域
        self.display_canvas.configure(scrollregion=(0, 0, max(canvas_width, new_width), max(canvas_height, new_height)))
        
    def display_continuous_image(self):
        """连续模式显示图片（显示所有图片）"""
        # 清除画布
        self.display_canvas.delete("all")
        
        canvas_width = self.display_canvas.winfo_width()
        if canvas_width <= 1:
            self.root.after(100, self.display_continuous_image)
            return
            
        y_offset = 0
        
        # 显示所有图片，不限制数量
        start_index = 0
        end_index = len(self.image_files)
        
        # 清空之前的图片引用
        if hasattr(self, 'continuous_photos'):
            self.continuous_photos.clear()
        else:
            self.continuous_photos = []
            
        # 记录每张图片的位置，用于滚动定位
        self.image_positions = {}
            
        for i in range(start_index, end_index):
            try:
                # 记录当前图片的Y位置
                self.image_positions[i] = y_offset
                
                img = Image.open(self.image_files[i])
                img_width, img_height = img.size
                
                # 按宽度缩放
                scale = (canvas_width * 0.95) / img_width
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                
                # 添加到画布
                x = (canvas_width - new_width) // 2
                self.display_canvas.create_image(x, y_offset, anchor="nw", image=photo)
                
                # 保存引用
                self.continuous_photos.append(photo)
                
                # 添加图片序号标识
                self.display_canvas.create_text(
                    10, y_offset + 10, 
                    text=f"{i+1}", 
                    fill="white", 
                    font=("Arial", 12, "bold"),
                    anchor="nw"
                )
                
                # 高亮当前图片
                if i == self.current_index:
                    self.display_canvas.create_rectangle(
                        x-2, y_offset-2, x+new_width+2, y_offset+new_height+2,
                        outline="red", width=3
                    )
                
                y_offset += new_height
                
                # 添加分隔线
                if i < end_index - 1:
                    y_offset += 10
                    self.display_canvas.create_line(
                        0, y_offset - 5, canvas_width, y_offset - 5, 
                        fill="gray", width=2
                    )
                    
            except Exception as e:
                print(f"连续模式显示图片失败: {self.image_files[i]}, {str(e)}")
                
        # 更新滚动区域
        self.display_canvas.configure(scrollregion=(0, 0, canvas_width, y_offset))
        
        # 滚动到当前图片位置
        self.scroll_to_current_image()
        
    def scroll_to_current_image(self):
        """滚动到当前图片位置"""
        if hasattr(self, 'image_positions') and self.current_index in self.image_positions:
            # 获取当前图片的Y位置
            current_y = self.image_positions[self.current_index]
            
            # 获取滚动区域的总高度
            scroll_region = self.display_canvas.cget('scrollregion')
            if scroll_region:
                total_height = float(scroll_region.split()[3])
                if total_height > 0:
                    # 计算滚动比例
                    scroll_ratio = current_y / total_height
                    # 滚动到该位置
                    self.display_canvas.yview_moveto(scroll_ratio)
        
    def display_video_thumbnail(self, video_path):
        """显示视频缩略图"""
        canvas_width = self.display_canvas.winfo_width()
        canvas_height = self.display_canvas.winfo_height()
        
        if CV2_AVAILABLE:
            try:
                cap = cv2.VideoCapture(video_path)
                ret, frame = cap.read()
                cap.release()
                
                if ret:
                    # 转换颜色格式
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    img = Image.fromarray(frame)
                    
                    # 缩放图片
                    if canvas_width > 1 and canvas_height > 1:
                        img_width, img_height = img.size
                        scale_x = canvas_width / img_width
                        scale_y = canvas_height / img_height
                        scale = min(scale_x, scale_y, 1.0)
                        
                        new_width = int(img_width * scale)
                        new_height = int(img_height * scale)
                        
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    self.current_photo = ImageTk.PhotoImage(img)
                    
                    # 显示缩略图
                    x = (canvas_width - img.width) // 2 if canvas_width > img.width else 0
                    y = (canvas_height - img.height) // 2 if canvas_height > img.height else 0
                    
                    self.display_canvas.create_image(x, y, anchor="nw", image=self.current_photo)
                else:
                    self._show_video_placeholder(canvas_width, canvas_height, video_path)
                    
            except Exception as e:
                print(f"显示视频缩略图失败: {str(e)}")
                self._show_video_placeholder(canvas_width, canvas_height, video_path)
        else:
            self._show_video_placeholder(canvas_width, canvas_height, video_path)
            
        # 添加播放按钮提示
        self.display_canvas.create_text(
            canvas_width // 2, canvas_height - 50,
            text="点击'播放视频'按钮观看" if CV2_AVAILABLE else "需要安装OpenCV才能播放视频", 
            fill="white", font=("Arial", 16)
        )
        
    def _show_video_placeholder(self, canvas_width, canvas_height, video_path):
        """显示视频占位符"""
        # 清除画布
        self.display_canvas.delete("all")
        
        # 创建一个简单的视频图标
        self.display_canvas.create_rectangle(
            canvas_width//4, canvas_height//4, 
            3*canvas_width//4, 3*canvas_height//4,
            fill="gray", outline="white", width=2
        )
        
        # 播放按钮图标
        center_x, center_y = canvas_width//2, canvas_height//2
        triangle_size = 30
        self.display_canvas.create_polygon(
            center_x - triangle_size//2, center_y - triangle_size//2,
            center_x - triangle_size//2, center_y + triangle_size//2,
            center_x + triangle_size//2, center_y,
            fill="white"
        )
        
        # 文件名
        filename = os.path.basename(video_path)
        self.display_canvas.create_text(
            canvas_width // 2, canvas_height // 2 + 60,
            text=filename, fill="white", font=("Arial", 12)
        )
        
    def update_display_mode(self):
        """更新显示模式"""
        self.display_current_item()
        
    def update_reading_mode(self):
        """更新阅读模式"""
        if hasattr(self, 'continuous_photos'):
            self.continuous_photos = []
        self.display_current_item()
        
    def toggle_fullscreen(self):
        """切换全屏模式"""
        self.is_fullscreen = not self.is_fullscreen
        self.root.attributes('-fullscreen', self.is_fullscreen)
        
        if self.is_fullscreen:
            # 隐藏控制面板和状态栏
            self.main_frame.pack_forget()
            
            # 创建全屏显示
            self.fullscreen_canvas = tk.Canvas(self.root, bg="black")
            self.fullscreen_canvas.pack(fill=tk.BOTH, expand=True)
            
            # 绑定全屏事件
            self.fullscreen_canvas.bind("<Button-1>", self.on_fullscreen_click)
            self.fullscreen_canvas.bind("<MouseWheel>", self.on_mousewheel)
            self.fullscreen_canvas.bind("<Key>", self.on_key_press)
            self.fullscreen_canvas.focus_set()
            
            # 确保画布可以接收键盘事件
            self.fullscreen_canvas.config(highlightthickness=0)
            self.root.bind("<Key>", self.on_key_press)
            
            # 显示当前图片
            self.display_fullscreen_image()
        else:
            self.exit_fullscreen()
            
    def exit_fullscreen(self):
        """退出全屏模式"""
        if self.is_fullscreen:
            self.is_fullscreen = False
            self.root.attributes('-fullscreen', False)
            
            # 解绑全屏模式的键盘事件
            self.root.unbind("<Key>")
            
            # 销毁全屏画布
            if hasattr(self, 'fullscreen_canvas'):
                self.fullscreen_canvas.destroy()
                
            # 恢复主界面
            self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.root.focus_set()
            
            # 重新绑定正常模式的键盘事件
            self.root.bind("<Key>", self.on_key_press)
            
            # 重新显示当前图片
            self.display_current_item()
            
    def display_fullscreen_image(self):
        """全屏显示图片"""
        if not hasattr(self, 'fullscreen_canvas'):
            return
            
        # 确保当前索引有效且是图片
        if self.current_index >= len(self.image_files):
            return
            
        try:
            # 重新加载当前图片
            self.original_image = Image.open(self.image_files[self.current_index])
        except Exception as e:
            print(f"加载图片失败: {str(e)}")
            return
            
        # 清除画布
        self.fullscreen_canvas.delete("all")
        
        # 获取屏幕尺寸
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # 高质量缩放到全屏
        img = self.original_image.copy()
        img_width, img_height = img.size
        
        scale_x = screen_width / img_width
        scale_y = screen_height / img_height
        scale = min(scale_x, scale_y)  # 保持比例
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # 使用最高质量缩放
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        self.fullscreen_photo = ImageTk.PhotoImage(img)
        
        # 居中显示
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        
        self.fullscreen_canvas.create_image(x, y, anchor="nw", image=self.fullscreen_photo)
        
        # 显示图片信息
        filename = os.path.basename(self.image_files[self.current_index])
        info_text = f"{self.current_index + 1}/{len(self.image_files)} - {filename}"
        self.fullscreen_canvas.create_text(
            screen_width // 2, screen_height - 30,
            text=info_text, fill="white", font=("Arial", 14)
        )
        
    def on_fullscreen_click(self, event):
        """全屏模式点击事件"""
        if hasattr(self, 'fullscreen_canvas'):
            canvas_width = self.fullscreen_canvas.winfo_width()
            if event.x < canvas_width // 2:
                self.previous_image()
            else:
                self.next_image()
                
    # 视频相关方法（与之前相同）
    def toggle_video(self):
        """切换视频播放状态"""
        if not CV2_AVAILABLE:
            messagebox.showwarning("警告", "需要安装OpenCV才能播放视频\n请运行: pip install opencv-python")
            return
            
        if self.current_index >= len(self.image_files):
            video_index = self.current_index - len(self.image_files)
            if video_index < len(self.video_files):
                if self.is_playing_video:
                    self.stop_video()
                else:
                    self.play_video(self.video_files[video_index])
                    
    def play_video(self, video_path):
        """播放视频"""
        if not CV2_AVAILABLE:
            messagebox.showwarning("警告", "需要安装OpenCV才能播放视频")
            return
            
        try:
            self.stop_video()  # 停止当前播放
            
            self.video_cap = cv2.VideoCapture(video_path)
            self.is_playing_video = True
            self.play_button.config(text="停止视频")
            
            # 启动视频播放线程
            self.video_thread = threading.Thread(target=self._play_video_thread)
            self.video_thread.daemon = True
            self.video_thread.start()
            
        except Exception as e:
            messagebox.showerror("错误", f"播放视频失败: {str(e)}")
            
    def _play_video_thread(self):
        """视频播放线程"""
        if not CV2_AVAILABLE or not self.video_cap:
            return
            
        fps = self.video_cap.get(cv2.CAP_PROP_FPS)
        delay = 1.0 / fps if fps > 0 else 1.0 / 30
        
        while self.is_playing_video and self.video_cap.isOpened():
            ret, frame = self.video_cap.read()
            if not ret:
                break
                
            # 转换颜色格式
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            
            # 缩放图片
            canvas_width = self.display_canvas.winfo_width()
            canvas_height = self.display_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                img_width, img_height = img.size
                scale_x = canvas_width / img_width
                scale_y = canvas_height / img_height
                scale = min(scale_x, scale_y, 1.0)
                
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # 更新显示
            self.current_photo = ImageTk.PhotoImage(img)
            
            def update_frame():
                if self.is_playing_video:
                    self.display_canvas.delete("all")
                    x = (canvas_width - img.width) // 2 if canvas_width > img.width else 0
                    y = (canvas_height - img.height) // 2 if canvas_height > img.height else 0
                    self.display_canvas.create_image(x, y, anchor="nw", image=self.current_photo)
            
            self.root.after(0, update_frame)
            time.sleep(delay)
            
        self.stop_video()
        
    def stop_video(self):
        """停止视频播放"""
        self.is_playing_video = False
        self.play_button.config(text="播放视频")
        
        if self.video_cap:
            self.video_cap.release()
            self.video_cap = None
            
    # 导航方法
    def previous_image(self):
        """上一张"""
        if self.current_index > 0:
            self.current_index -= 1
            if self.is_fullscreen:
                # 全屏模式下只显示图片，不显示视频
                if self.current_index < len(self.image_files):
                    self.display_fullscreen_image()
                else:
                    # 如果是视频，退出全屏模式
                    self.exit_fullscreen()
                    self.display_current_item()
            else:
                # 在连续阅读模式下，只需要滚动到对应位置
                if self.reading_mode.get() == "continuous":
                    self.scroll_to_current_image()
                    # 重新绘制以更新高亮
                    self.display_current_item()
                else:
                    self.display_current_item()
            self.update_status()
            if not self.is_fullscreen:
                self.update_thumbnails()
            
    def next_image(self):
        """下一张"""
        total_items = len(self.image_files) + len(self.video_files)
        if self.current_index < total_items - 1:
            self.current_index += 1
            if self.is_fullscreen:
                # 全屏模式下只显示图片，不显示视频
                if self.current_index < len(self.image_files):
                    self.display_fullscreen_image()
                else:
                    # 如果是视频，退出全屏模式
                    self.exit_fullscreen()
                    self.display_current_item()
            else:
                # 在连续阅读模式下，只需要滚动到对应位置
                if self.reading_mode.get() == "continuous":
                    self.scroll_to_current_image()
                    # 重新绘制以更新高亮
                    self.display_current_item()
                else:
                    self.display_current_item()
            self.update_status()
            if not self.is_fullscreen:
                self.update_thumbnails()
            
    def first_image(self):
        """第一张"""
        if self.image_files or self.video_files:
            self.current_index = 0
            if self.is_fullscreen:
                if self.current_index < len(self.image_files):
                    self.display_fullscreen_image()
                else:
                    self.exit_fullscreen()
                    self.display_current_item()
            else:
                self.display_current_item()
            self.update_status()
            if not self.is_fullscreen:
                self.update_thumbnails()
            
    def last_image(self):
        """最后一张"""
        total_items = len(self.image_files) + len(self.video_files)
        if total_items > 0:
            self.current_index = total_items - 1
            if self.is_fullscreen:
                if self.current_index < len(self.image_files):
                    self.display_fullscreen_image()
                else:
                    self.exit_fullscreen()
                    self.display_current_item()
            else:
                self.display_current_item()
            self.update_status()
            if not self.is_fullscreen:
                self.update_thumbnails()
            
    # 缩放方法
    def zoom_in(self):
        """放大"""
        self.zoom_factor *= 1.2
        if self.is_fullscreen:
            self.display_fullscreen_image()
        else:
            self.display_current_item()
        
    def zoom_out(self):
        """缩小"""
        self.zoom_factor /= 1.2
        if self.is_fullscreen:
            self.display_fullscreen_image()
        else:
            self.display_current_item()
        
    def original_size(self):
        """原始大小"""
        self.zoom_factor = 1.0
        if self.is_fullscreen:
            self.display_fullscreen_image()
        else:
            self.display_current_item()
            
    def update_status(self):
        """更新状态信息"""
        total_items = len(self.image_files) + len(self.video_files)
        if total_items > 0:
            current_type = "图片" if self.current_index < len(self.image_files) else "视频"
            filename = ""
            if self.current_index < len(self.image_files):
                filename = os.path.basename(self.image_files[self.current_index])
            elif self.current_index - len(self.image_files) < len(self.video_files):
                video_index = self.current_index - len(self.image_files)
                filename = os.path.basename(self.video_files[video_index])
                
            zoom_percent = int(self.zoom_factor * 100)
            self.status_label.config(
                text=f"{current_type} {self.current_index + 1}/{total_items} | {filename} | 缩放: {zoom_percent}%"
            )
            
            # 更新进度
            progress = (self.current_index + 1) / total_items * 100
            self.progress_label.config(text=f"进度: {progress:.1f}%")
        else:
            self.status_label.config(text="无文件")
            self.progress_label.config(text="")
            
    # 事件处理
    def on_key_press(self, event):
        """键盘事件处理"""
        if event.keysym == 'Left' or event.keysym == 'a':
            self.previous_image()
        elif event.keysym == 'Right' or event.keysym == 'd':
            self.next_image()
        elif event.keysym == 'Up' or event.keysym == 'w':
            self.previous_image()
        elif event.keysym == 'Down' or event.keysym == 's':
            self.next_image()
        elif event.keysym == 'Home':
            self.first_image()
        elif event.keysym == 'End':
            self.last_image()
        elif event.keysym == 'plus' or event.keysym == 'equal':
            self.zoom_in()
        elif event.keysym == 'minus':
            self.zoom_out()
        elif event.keysym == '0':
            self.original_size()
        elif event.keysym == 'F11':
            self.toggle_fullscreen()
        elif event.keysym == 'Escape':
            if self.is_fullscreen:
                self.exit_fullscreen()
        elif event.keysym == 'space':
            self.toggle_video()
            
    def on_mousewheel(self, event):
        """鼠标滚轮事件处理"""
        # Ctrl + 滚轮进行缩放
        if event.state & 0x4:  # Ctrl键按下
            if event.delta > 0:
                self.zoom_in()
            else:
                self.zoom_out()
        else:
            # 在连续阅读模式下，滚轮用于滚动画布
            if self.reading_mode.get() == "continuous" and not self.is_fullscreen:
                # 连续模式下的滚动处理
                if event.delta > 0:
                    # 向上滚动
                    self.display_canvas.yview_scroll(-3, "units")
                else:
                    # 向下滚动
                    self.display_canvas.yview_scroll(3, "units")
            else:
                # 普通翻页模式或全屏模式下的翻页
                if event.delta > 0:
                    self.previous_image()
                else:
                    self.next_image()
                
    def _check_continuous_scroll_bounds(self):
        """检查连续滚动的边界，自动翻页"""
        # 在连续阅读模式下不需要自动翻页，因为已经显示了多张图片
        # 这个方法暂时禁用，避免滚动异常
        pass
    
    def on_canvas_click(self, event):
        """画布点击事件处理"""
        # 点击左半部分上一张，右半部分下一张
        canvas_width = self.display_canvas.winfo_width()
        if event.x < canvas_width / 2:
            self.previous_image()
        else:
            self.next_image()
            
    def __del__(self):
        """析构函数"""
        self.stop_video()

def main():
    root = tk.Tk()
    app = EnhancedMangaReader(root)
    root.mainloop()

if __name__ == "__main__":
    main()