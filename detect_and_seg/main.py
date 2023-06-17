import configparser
from tkinter import filedialog, END
from tkinter import messagebox as mb
import codecs
import tkinter
import customtkinter
from ultralytics import YOLO
import detect_w as detect


config = configparser.ConfigParser()
config.read_file(codecs.open("config.ini", 'r', 'utf8'))


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title(config['Main']['title'])
        self.geometry('550x380')

        self.tabview = customtkinter.CTkTabview(self, height=370, width=530)
        self.tabview.pack()

        self.tabview.add("Сегментация")
        self.tabview.add("Настройки")

        self.source = ''

        # Сегментация
        self.label2 = customtkinter.CTkLabel(self.tabview.tab('Сегментация'),
                                             text=config['Main']['title_con'],
                                             font=('', 18))
        self.label2.grid(row=2, column=1, pady=[10, 20], padx=[0, 0])

        self.label3 = customtkinter.CTkLabel(self.tabview.tab('Сегментация'), text=config['Main']['link_title'])
        self.label3.grid(row=4, column=1, padx=[0, 0])

        self.entry = customtkinter.CTkTextbox(self.tabview.tab('Сегментация'), width=500, height=40)
        self.entry.grid(row=5, column=0, columnspan=3, pady=[0, 30], padx=[10, 0])
        self.entry.insert("0.0", config['Main']['in_add'])

        self.label4 = customtkinter.CTkLabel(self.tabview.tab('Сегментация'), text=config['Main']['open_title'])
        self.label4.grid(row=6, column=1, padx=[0, 0])

        self.open_button = customtkinter.CTkButton(self.tabview.tab('Сегментация'),
                                                   text=config['Main']['open'],
                                                   # fg_color='green',
                                                   command=self.open)
        self.open_button.grid(row=7, column=1)

        self.connect_b = customtkinter.CTkButton(self.tabview.tab('Сегментация'),
                                                 text=config['Main']['connect'],
                                                 fg_color='green',
                                                 command=self.connect)
        self.connect_b.grid(row=8, column=1, pady=[60, 0])

        # Настройки
        self.settings_frame_1 = EntryFrame(self.tabview.tab('Настройки'),
                                           header_name=config['Stream']['window_size'],
                                           label_h='Высота',
                                           label_w='Ширина')
        self.settings_frame_1.grid(row=0, column=0, padx=20, pady=20)

        self.settings_frame_2 = ButtonFrame(self.tabview.tab('Настройки'), header_name=config['FPS']['fps_title'])
        self.settings_frame_2.grid(row=0, column=2, padx=20, pady=20)

        self.settings_frame_3 = SaveFrame(self.tabview.tab('Настройки'), header_name=config['Save']['save_title'])
        self.settings_frame_3.grid(row=0, column=4, padx=20, pady=20)

        self.frame_1_button = customtkinter.CTkButton(self.tabview.tab('Настройки'),
                                                      text="Применить",
                                                      command=lambda: self.set_size(self.settings_frame_1,
                                                                                    'window_size_h',
                                                                                    'window_size_w'))
        self.frame_1_button.grid(row=1, column=0, padx=20, pady=10)

        self.frame_2_button = customtkinter.CTkButton(self.tabview.tab('Настройки'),
                                                      text="Применить", command=self.set_fps)
        self.frame_2_button.grid(row=1, column=2, padx=20, pady=10)

        self.frame_3_button = customtkinter.CTkButton(self.tabview.tab('Настройки'),
                                                      text="Применить", command=self.set_save)
        self.frame_3_button.grid(row=1, column=4, padx=20, pady=10)

    def open(self):
        self.source = filedialog.askopenfilename()

    def set_size(self, settings_frame, arg_h, arg_w):
        try:
            height, width = settings_frame.get_value()
            if height is not None and width is not None:
                config['Stream'][arg_h] = str(height)
                config['Stream'][arg_w] = str(width)
                with open('config.ini', 'w', encoding='utf-8') as configfile:
                    config.write(configfile)
        except Exception:
            # print('Wrong input')
            print()

    def set_fps(self):
        if (fps := self.settings_frame_2.set_value()) != '':
            config['Stream']['fps_f'] = fps
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)

    def set_save(self):
        if (save := self.settings_frame_3.set_value()) != '':
            config['Stream']['save_state'] = save
            with open('config.ini', 'w', encoding='utf-8') as configfile:
                config.write(configfile)

    def connect(self):
        if self.source != '':
            program.destroy()
            detect.detect(self.source)

            # main(self.source)
        else:
            address = self.entry.get('0.0', END).rstrip()
            if address not in [' Add address', '', 'Add address']:
                # print(f'connect to: {address}')
                program.destroy()
                # main(address)

            else:
                mb.showerror("Ошибка", "Неправильный ввод")


class EntryFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="EntryFrame", label_h='label1', label_w='label2', **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name
        self.label1 = label_h
        self.label2 = label_w

        self.header = customtkinter.CTkLabel(self, text=self.header_name)
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.label_height = customtkinter.CTkLabel(self, text=self.label1)
        self.label_height.grid(row=1, padx=10, pady=[10, 0])

        self.entry_set = customtkinter.CTkEntry(self, width=100)
        self.entry_set.grid(row=2, column=0, padx=10, pady=[5, 10])

        self.label_width = customtkinter.CTkLabel(self, text=self.label2)
        self.label_width.grid(row=3, padx=10, pady=[10, 0])

        self.entry_set2 = customtkinter.CTkEntry(self, width=100)
        self.entry_set2.grid(row=4, column=0, padx=10, pady=[5, 10])

    def get_value(self):
        try:
            return int(self.entry_set.get()), int(self.entry_set2.get())
        except Exception:
            # print('Wrong input')
            print()


class ButtonFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="ButtonFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name

        self.radio_button_var = customtkinter.StringVar(value="")
        self.header = customtkinter.CTkLabel(self, text=self.header_name)
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.radio_button_var = customtkinter.StringVar(value="")

        self.radio_button_1 = customtkinter.CTkRadioButton(self, text=config['FPS']['default'], value="Option 1",
                                                           variable=self.radio_button_var)
        self.radio_button_1.grid(row=1, column=0, padx=10, pady=10)
        self.radio_button_2 = customtkinter.CTkRadioButton(self, text=config['FPS']['2d'], value="Option 2",
                                                           variable=self.radio_button_var)
        self.radio_button_2.grid(row=2, column=0, padx=10, pady=10)
        self.radio_button_3 = customtkinter.CTkRadioButton(self, text=config['FPS']['5d'], value="Option 3",
                                                           variable=self.radio_button_var)
        self.radio_button_3.grid(row=3, column=0, padx=10, pady=(10, 45))

    def set_value(self):
        return self.radio_button_var.get()


class SaveFrame(customtkinter.CTkFrame):
    def __init__(self, *args, header_name="ButtonFrame", **kwargs):
        super().__init__(*args, **kwargs)

        self.header_name = header_name

        self.radio_button_var = customtkinter.StringVar(value="")
        self.header = customtkinter.CTkLabel(self, text=self.header_name)
        self.header.grid(row=0, column=0, padx=10, pady=10)

        self.radio_button_var = customtkinter.StringVar(value="")

        self.radio_button_1 = customtkinter.CTkRadioButton(self, text=config['Save']['yes'], value="Yes",
                                                           variable=self.radio_button_var)
        self.radio_button_1.grid(row=1, column=0, padx=10, pady=10)
        self.radio_button_2 = customtkinter.CTkRadioButton(self, text=config['Save']['no'], value="No",
                                                           variable=self.radio_button_var)
        self.radio_button_2.grid(row=2, column=0, padx=10, pady=10)

    def set_value(self):
        return self.radio_button_var.get()


def close_window():
    program.destroy()



if __name__ == '__main__':
    customtkinter.set_appearance_mode("light")
    customtkinter.set_default_color_theme("green")
    program = App()
    program.protocol('WM_DELETE_WINDOW', close_window)
    program.mainloop()

