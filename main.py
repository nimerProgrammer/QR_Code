import qrcode
import cv2
import numpy as np
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.textinput import TextInput
from kivy.graphics.texture import Texture
from PIL import Image as PILImage


class MainScreen(Screen):
    """Main Screen with buttons to navigate to Generate or Scan QR Code."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)

        # Title Label
        layout.add_widget(Label(text="QR Code App", font_size=30, size_hint=(1, 0.2)))

        # Buttons Layout
        button_layout = BoxLayout(orientation='vertical', spacing=20, size_hint=(0.5, None), height=140)

        # Generate QR Button
        btn_generate = Button(text="Generate QR Code", size_hint=(2, None), height=50)
        btn_generate.bind(on_press=self.go_to_generate)
        button_layout.add_widget(btn_generate)

        # Scan QR Button
        btn_scan = Button(text="Scan QR Code", size_hint=(2, None), height=50)
        btn_scan.bind(on_press=self.go_to_scan)
        button_layout.add_widget(btn_scan)

        layout.add_widget(button_layout)
        self.add_widget(layout)

    def go_to_generate(self, instance):
        self.manager.current = 'generate_qr'

    def go_to_scan(self, instance):
        self.manager.current = 'scan_qr'


class GenerateQRScreen(Screen):
    """Screen for Generating QR Codes with user input."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        # Input field for name
        self.name_input = TextInput(hint_text="Enter Name", size_hint=(0.8, None), height=50, multiline=False)
        layout.add_widget(self.name_input)

        # QR Code Display
        self.qr_image = Image(size_hint=(None, None), size=(200, 200))
        layout.add_widget(self.qr_image)

        # Generate QR Button
        btn_generate = Button(text="Generate QR Code", size_hint=(1, None), height=50)
        btn_generate.bind(on_press=self.generate_qr)
        layout.add_widget(btn_generate)

        # Back Button
        btn_back = Button(text="Back to Home", size_hint=(1, None), height=50)
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def generate_qr(self, instance):
        name = self.name_input.text.strip()
        if not name:
            self.name_input.hint_text = "Please enter a name!"
            return

        qr = qrcode.make(name)
        qr.save("qr_code.png")

        # Load QR image into Kivy
        pil_image = PILImage.open("qr_code.png").convert("RGBA")
        texture = Texture.create(size=pil_image.size, colorfmt='rgba')
        texture.blit_buffer(pil_image.tobytes(), colorfmt='rgba', bufferfmt='ubyte')

        self.qr_image.texture = texture

    def go_back(self, instance):
        self.manager.current = 'main'


class ScanQRScreen(Screen):
    """Screen for Scanning QR Codes."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)

        self.result_label = Label(text="Scan Result: ", font_size=20, size_hint=(1, 0.2))
        layout.add_widget(self.result_label)

        # Scan QR Button
        btn_scan = Button(text="Start Scanning", size_hint=(1, None), height=50)
        btn_scan.bind(on_press=self.scan_qr)
        layout.add_widget(btn_scan)

        # Back Button
        btn_back = Button(text="Back to Home", size_hint=(1, None), height=50)
        btn_back.bind(on_press=self.go_back)
        layout.add_widget(btn_back)

        self.add_widget(layout)

    def scan_qr(self, instance):
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            data, bbox, _ = detector.detectAndDecode(frame)
            if data:
                self.result_label.text = f"Scan Result: {data}"
                break

            cv2.imshow("QR Scanner", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

    def go_back(self, instance):
        self.manager.current = 'main'


class QRApp(App):
    """Main Application for the QR Code App."""

    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(GenerateQRScreen(name='generate_qr'))
        sm.add_widget(ScanQRScreen(name='scan_qr'))
        return sm


if __name__ == "__main__":
    QRApp().run()
