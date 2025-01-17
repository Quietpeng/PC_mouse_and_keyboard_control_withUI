import cv2
import numpy as np
from PIL import ImageGrab
from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Controller as KeyboardController, Key
import pyperclip
import time
import json
import random
from screeninfo import get_monitors
import ctypes
import tkinter as tk
from tkinter import ttk

PROCESS_PER_MONITOR_DPI_AWARE = 2
ctypes.windll.shcore.SetProcessDpiAwareness(PROCESS_PER_MONITOR_DPI_AWARE)

# 校正类
class Calibration:
    def __init__(self, file_path=r".\offset_params.txt"):
        self.file_path = file_path
        self.mouse = MouseController()
        self.keyboard = KeyboardController()
        self.offset_x, self.offset_y = self.read_offset_params()

    def read_offset_params(self):
        try:
            with open(self.file_path, "r") as file:
                lines = file.readlines()
                offset_x = float(lines[0].strip())
                offset_y = float(lines[1].strip())
        except FileNotFoundError:
            offset_x, offset_y = 0.0, 0.0
        return offset_x, offset_y

    def save_offset_params(self):
        with open(self.file_path, "w") as file:
            file.write(f"{self.offset_x}\n")
            file.write(f"{self.offset_y}\n")

    def get_mouse_position(self):
        return self.mouse.position

    def calibrate(self, learning_rate=0.1, iterations=10):
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        for i in range(iterations):
            print(f'当前屏幕分辨率为{screen_width}x{screen_height}')
            target_x = random.randint(0, screen_width)
            target_y = random.randint(0, screen_height)
            self.mouse.position = (target_x, target_y)
            time.sleep(0.1)  # 等待鼠标移动完成
            actual_x, actual_y = self.get_mouse_position()
            error_x = actual_x - target_x
            error_y = actual_y - target_y
            self.offset_x -= learning_rate * error_x
            self.offset_y -= learning_rate * error_y
            print(f"迭代 {i+1}: 目标坐标=({target_x}, {target_y}), 实际坐标=({actual_x}, {actual_y}), "
                  f"偏差=({error_x}, {error_y}), 修正后偏差参数=({self.offset_x}, {self.offset_y})")
        self.save_offset_params()
        print(f"校正完成，偏差值: ({self.offset_x}, {self.offset_y})")

    def test_click(self):
        self.mouse.click(Button.left)

    def test_keyboard_input(self, text):
        pyperclip.copy(text)
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)

# 指令编辑类
class CommandEditor:
    def __init__(self, file_path=r".\rule.json"):
        self.file_path = file_path
        self.commands = self.read_commands()

    def read_commands(self):
        try:
            with open(self.file_path, "r") as file:
                commands = json.load(file)
        except FileNotFoundError:
            commands = []
        return commands

    def save_commands(self):
        with open(self.file_path, "w") as file:
            json.dump(self.commands, file, indent=4)

    def add_command(self, command):
        self.commands.append(command)
        self.commands.sort(key=lambda x: x['order'])
        self.save_commands()

    def edit_command(self, index, command):
        self.commands[index] = command
        self.commands.sort(key=lambda x: x['order'])
        self.save_commands()

    def delete_command(self, index):
        del self.commands[index]
        self.save_commands()

    def show_ui(self):
        def add_command():
            command_type = command_type_var.get()
            order = int(order_entry.get())
            if command_type == "mouse_move":
                position = [int(x_entry.get()), int(y_entry.get())]
                command = {"type": command_type, "position": position, "order": order}
            elif command_type == "mouse_click":
                clicks = int(clicks_entry.get())
                command = {"type": command_type, "clicks": clicks, "order": order}
            elif command_type == "keyboard_input":
                text = text_entry.get()
                command = {"type": command_type, "text": text, "order": order}
            elif command_type == "keyboard_shortcut":
                keys = [special_key_var.get()] + keys_entry.get().split(',')
                command = {"type": command_type, "keys": keys, "order": order}
            self.add_command(command)
            update_command_list()

        def update_command_list():
            command_list.delete(0, tk.END)
            for command in self.commands:
                command_list.insert(tk.END, command)

        def delete_command():
            selected_index = command_list.curselection()
            if selected_index:
                self.delete_command(selected_index[0])
                update_command_list()

        def confirm_and_run():
            root.destroy()
            executor = OperationExecutor(calibration, command_editor)
            print("执行命令...")
            executor.execute_commands()
            print("命令执行完成")

        def update_input_fields(*args):
            for widget in input_frame.winfo_children():
                widget.grid_forget()
            command_type = command_type_var.get()
            if command_type == "mouse_move":
                tk.Label(input_frame, text="X 坐标").grid(row=0, column=0)
                x_entry.grid(row=0, column=1)
                tk.Label(input_frame, text="Y 坐标").grid(row=1, column=0)
                y_entry.grid(row=1, column=1)
                tk.Label(input_frame, text="或图片路径").grid(row=2, column=0)
                image_path_entry.grid(row=2, column=1)
            elif command_type == "mouse_click":
                tk.Label(input_frame, text="点击次数").grid(row=0, column=0)
                clicks_entry.grid(row=0, column=1)
            elif command_type == "keyboard_input":
                tk.Label(input_frame, text="输入文本").grid(row=0, column=0)
                text_entry.grid(row=0, column=1)
            elif command_type == "keyboard_shortcut":
                tk.Label(input_frame, text="特殊按键").grid(row=0, column=0)
                special_key_menu.grid(row=0, column=1)
                tk.Label(input_frame, text="常规按键 (逗号分隔)").grid(row=1, column=0)
                keys_entry.grid(row=1, column=1)

        def validate_inputs():
            command_type = command_type_var.get()
            if command_type == "mouse_move":
                if image_path_entry.get():
                    if not os.path.exists(image_path_entry.get()):
                        tk.messagebox.showerror("错误", "图片路径不存在")
                        return False
                else:
                    try:
                        int(x_entry.get())
                        int(y_entry.get())
                    except ValueError:
                        tk.messagebox.showerror("错误", "坐标必须是整数")
                        return False
            elif command_type == "mouse_click":
                try:
                    int(clicks_entry.get())
                except ValueError:
                    tk.messagebox.showerror("错误", "点击次数必须是整数")
                    return False
            elif command_type == "keyboard_input":
                if not text_entry.get():
                    tk.messagebox.showerror("错误", "输入文本不能为空")
                    return False
            elif command_type == "keyboard_shortcut":
                if not special_key_var.get() or not keys_entry.get():
                    tk.messagebox.showerror("错误", "特殊按键和常规按键不能为空")
                    return False
            return True

        root = tk.Tk()
        root.title("命令编辑器")

        frame = tk.Frame(root)
        frame.pack(padx=10, pady=10)

        command_type_var = tk.StringVar()
        command_type_var.trace("w", update_input_fields)
        command_type_label = tk.Label(frame, text="命令类型")
        command_type_label.grid(row=0, column=0)
        command_type_menu = ttk.Combobox(frame, textvariable=command_type_var)
        command_type_menu['values'] = ("mouse_move", "mouse_click", "keyboard_input", "keyboard_shortcut")
        command_type_menu.grid(row=0, column=1)

        order_label = tk.Label(frame, text="顺序")
        order_label.grid(row=1, column=0)
        order_entry = tk.Entry(frame)
        order_entry.grid(row=1, column=1)

        input_frame = tk.Frame(frame)
        input_frame.grid(row=2, column=0, columnspan=2)

        x_entry = tk.Entry(input_frame)
        y_entry = tk.Entry(input_frame)
        image_path_entry = tk.Entry(input_frame)
        clicks_entry = tk.Entry(input_frame)
        text_entry = tk.Entry(input_frame)
        keys_entry = tk.Entry(input_frame)

        special_key_var = tk.StringVar()
        special_key_menu = ttk.Combobox(input_frame, textvariable=special_key_var)
        special_key_menu['values'] = ("Ctrl", "Alt", "Shift")

        add_button = tk.Button(frame, text="添加命令", command=lambda: validate_inputs() and add_command())
        add_button.grid(row=3, column=0, columnspan=2)

        command_list = tk.Listbox(frame, height=10, width=50)
        command_list.grid(row=4, column=0, columnspan=2)

        delete_button = tk.Button(frame, text="删除命令", command=delete_command)
        delete_button.grid(row=5, column=0, columnspan=2)

        confirm_button = tk.Button(frame, text="确认并运行", command=confirm_and_run)
        confirm_button.grid(row=6, column=0, columnspan=2)

        exit_button = tk.Button(frame, text="退出", command=root.quit)
        exit_button.grid(row=7, column=0, columnspan=2)

        update_command_list()

        root.mainloop()

# 操作执行类
class OperationExecutor:
    def __init__(self, calibration, command_editor):
        self.calibration = calibration
        self.command_editor = command_editor
        self.mouse = MouseController()
        self.keyboard = KeyboardController()

    def find_image_on_screen(self, template_path, threshold=0.8):
        screenshot = ImageGrab.grab()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        template = cv2.imread(template_path, cv2.IMREAD_COLOR)
        if template is None:
            raise ValueError(f"无法加载目标图像: {template_path}")
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return center_x, center_y
        else:
            return None

    def execute_commands(self):
        for command in self.command_editor.commands:
            if command['type'] == 'mouse_move':
                x, y = command['position']
                self.mouse.position = (x + self.calibration.offset_x, y + self.calibration.offset_y)
                print(f'目标{x},{y},实际{self.mouse.position}')
            elif command['type'] == 'mouse_click':
                self.mouse.click(Button.left, command['clicks'])
            elif command['type'] == 'keyboard_input':
                self.paste_text(command['text'])
            elif command['type'] == 'keyboard_shortcut':
                for key in command['keys']:
                    self.keyboard.press(key)
                for key in command['keys']:
                    self.keyboard.release(key)
            time.sleep(command.get('delay', 0.1))

    def paste_text(self, text):
        pyperclip.copy(text)
        self.keyboard.press(Key.ctrl)
        self.keyboard.press('v')
        self.keyboard.release('v')
        self.keyboard.release(Key.ctrl)

# 示例
if __name__ == "__main__":
    try:
        calibration = Calibration()
        # print("开始校正...")
        # calibration.calibrate()
        # calibration.test_click()
        # calibration.test_keyboard_input("测试文本")
        # print("校正完成")

        command_editor = CommandEditor()
        command_editor.show_ui()
        print("添加命令...")

        # executor = OperationExecutor(calibration, command_editor)
        # print("执行命令...")
        # executor.execute_commands()
        # print("命令执行完成")
    except Exception as e:
        print(f"发生错误: {e}")