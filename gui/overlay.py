
import ctypes
from ctypes import wintypes

from PIL import Image, ImageDraw

from engine.capture import RobloxCapture
from engine.vision import detect_green_target


# ==========================================
# WINDOWS CONSTANTS
# ==========================================

WS_POPUP = 0x80000000

WS_EX_LAYERED = 0x00080000
WS_EX_TRANSPARENT = 0x00000020
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_NOACTIVATE = 0x08000000

HWND_TOPMOST = wintypes.HWND(-1)

SW_HIDE = 0

SWP_NOACTIVATE = 0x0010
SWP_SHOWWINDOW = 0x0040

ULW_ALPHA = 0x00000002
AC_SRC_OVER = 0
AC_SRC_ALPHA = 1

BI_RGB = 0
DIB_RGB_COLORS = 0

VK_F8 = 0x77

CLASS_NAME = "ForgeSightNativeOverlay"


# ==========================================
# WINDOWS STRUCTURES
# ==========================================

class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG)
    ]


class SIZE(ctypes.Structure):
    _fields_ = [
        ("cx", wintypes.LONG),
        ("cy", wintypes.LONG)
    ]


class BLENDFUNCTION(ctypes.Structure):
    _fields_ = [
        ("BlendOp", ctypes.c_ubyte),
        ("BlendFlags", ctypes.c_ubyte),
        ("SourceConstantAlpha", ctypes.c_ubyte),
        ("AlphaFormat", ctypes.c_ubyte)
    ]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD)
    ]


class RGBQUAD(ctypes.Structure):
    _fields_ = [
        ("rgbBlue", ctypes.c_ubyte),
        ("rgbGreen", ctypes.c_ubyte),
        ("rgbRed", ctypes.c_ubyte),
        ("rgbReserved", ctypes.c_ubyte)
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [
        ("bmiHeader", BITMAPINFOHEADER),
        ("bmiColors", RGBQUAD * 1)
    ]


class WNDCLASSW(ctypes.Structure):
    pass


WNDPROC = ctypes.WINFUNCTYPE(
    ctypes.c_ssize_t,
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
)

WNDCLASSW._fields_ = [
    ("style", wintypes.UINT),
    ("lpfnWndProc", WNDPROC),
    ("cbClsExtra", ctypes.c_int),
    ("cbWndExtra", ctypes.c_int),
    ("hInstance", wintypes.HINSTANCE),
    ("hIcon", wintypes.HANDLE),
    ("hCursor", wintypes.HANDLE),
    ("hbrBackground", wintypes.HANDLE),
    ("lpszMenuName", wintypes.LPCWSTR),
    ("lpszClassName", wintypes.LPCWSTR)
]


# ==========================================
# WINDOWS API
# ==========================================

user32 = ctypes.WinDLL(
    "user32",
    use_last_error=True
)

gdi32 = ctypes.WinDLL(
    "gdi32",
    use_last_error=True
)

kernel32 = ctypes.WinDLL(
    "kernel32",
    use_last_error=True
)

dwmapi = ctypes.WinDLL(
    "dwmapi",
    use_last_error=True
)


GetModuleHandleW = kernel32.GetModuleHandleW
GetModuleHandleW.argtypes = [wintypes.LPCWSTR]
GetModuleHandleW.restype = wintypes.HINSTANCE

RegisterClassW = user32.RegisterClassW
RegisterClassW.argtypes = [
    ctypes.POINTER(WNDCLASSW)
]
RegisterClassW.restype = wintypes.ATOM

DefWindowProcW = user32.DefWindowProcW
DefWindowProcW.argtypes = [
    wintypes.HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
]
DefWindowProcW.restype = ctypes.c_ssize_t

CreateWindowExW = user32.CreateWindowExW
CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HWND,
    wintypes.HMENU,
    wintypes.HINSTANCE,
    ctypes.c_void_p
]
CreateWindowExW.restype = wintypes.HWND

DestroyWindow = user32.DestroyWindow
DestroyWindow.argtypes = [wintypes.HWND]
DestroyWindow.restype = wintypes.BOOL

ShowWindow = user32.ShowWindow
ShowWindow.argtypes = [
    wintypes.HWND,
    ctypes.c_int
]
ShowWindow.restype = wintypes.BOOL

SetWindowPos = user32.SetWindowPos
SetWindowPos.argtypes = [
    wintypes.HWND,
    wintypes.HWND,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.UINT
]
SetWindowPos.restype = wintypes.BOOL

GetAsyncKeyState = user32.GetAsyncKeyState
GetAsyncKeyState.argtypes = [ctypes.c_int]
GetAsyncKeyState.restype = ctypes.c_short

GetDC = user32.GetDC
GetDC.argtypes = [wintypes.HWND]
GetDC.restype = wintypes.HDC

ReleaseDC = user32.ReleaseDC
ReleaseDC.argtypes = [
    wintypes.HWND,
    wintypes.HDC
]
ReleaseDC.restype = ctypes.c_int

CreateCompatibleDC = gdi32.CreateCompatibleDC
CreateCompatibleDC.argtypes = [wintypes.HDC]
CreateCompatibleDC.restype = wintypes.HDC

DeleteDC = gdi32.DeleteDC
DeleteDC.argtypes = [wintypes.HDC]
DeleteDC.restype = wintypes.BOOL

CreateDIBSection = gdi32.CreateDIBSection
CreateDIBSection.argtypes = [
    wintypes.HDC,
    ctypes.POINTER(BITMAPINFO),
    wintypes.UINT,
    ctypes.POINTER(ctypes.c_void_p),
    wintypes.HANDLE,
    wintypes.DWORD
]
CreateDIBSection.restype = wintypes.HBITMAP

SelectObject = gdi32.SelectObject
SelectObject.argtypes = [
    wintypes.HDC,
    wintypes.HGDIOBJ
]
SelectObject.restype = wintypes.HGDIOBJ

DeleteObject = gdi32.DeleteObject
DeleteObject.argtypes = [wintypes.HGDIOBJ]
DeleteObject.restype = wintypes.BOOL

UpdateLayeredWindow = user32.UpdateLayeredWindow
UpdateLayeredWindow.argtypes = [
    wintypes.HWND,
    wintypes.HDC,
    ctypes.POINTER(POINT),
    ctypes.POINTER(SIZE),
    wintypes.HDC,
    ctypes.POINTER(POINT),
    wintypes.DWORD,
    ctypes.POINTER(BLENDFUNCTION),
    wintypes.DWORD
]
UpdateLayeredWindow.restype = wintypes.BOOL

DwmFlush = dwmapi.DwmFlush
DwmFlush.argtypes = []
DwmFlush.restype = ctypes.c_long


# ==========================================
# WINDOW CLASS
# ==========================================

_window_proc = WNDPROC(
    lambda hwnd, msg, wparam, lparam:
        DefWindowProcW(
            hwnd,
            msg,
            wparam,
            lparam
        )
)


def register_overlay_class():

    instance = GetModuleHandleW(None)

    window_class = WNDCLASSW()
    window_class.lpfnWndProc = _window_proc
    window_class.hInstance = instance
    window_class.lpszClassName = CLASS_NAME

    atom = RegisterClassW(
        ctypes.byref(window_class)
    )

    if not atom:
        error = ctypes.get_last_error()

        # ERROR_CLASS_ALREADY_EXISTS
        if error != 1410:
            raise ctypes.WinError(error)

    return instance


# ==========================================
# FORGESIGHT OVERLAY
# ==========================================

class ForgeSightOverlay:

    def __init__(self, root, settings=None):

        self.root = root
        self.settings = settings

        self.capture = RobloxCapture()

        self.running = True
        self.visible = False
        self.f8_was_down = False

        self.last_render_key = None

        self.memory_dc = None
        self.bitmap = None
        self.bitmap_bits = None
        self.bitmap_size = None

        self.instance = None
        self.hwnd = None

        try:

            self.instance = register_overlay_class()

            self.hwnd = CreateWindowExW(
                WS_EX_LAYERED
                | WS_EX_TRANSPARENT
                | WS_EX_TOOLWINDOW
                | WS_EX_NOACTIVATE,

                CLASS_NAME,
                "ForgeSight Overlay",
                WS_POPUP,

                0, 0, 1, 1,

                None,
                None,
                self.instance,
                None
            )

            if not self.hwnd:
                raise ctypes.WinError(
                    ctypes.get_last_error()
                )

            print("[ForgeSight] Native overlay initialized.")

            self.root.after(
                100,
                self.update_overlay
            )

        except Exception:
            self.cleanup()
            raise

    # --------------------------------------
    # HIDE BEFORE CAPTURE
    # --------------------------------------

    def hide_overlay(self):

        if not self.hwnd or not self.visible:
            return

        ShowWindow(
            self.hwnd,
            SW_HIDE
        )

        self.visible = False

        # Flush the compositor so the hidden overlay
        # is not included in the next screen capture.
        DwmFlush()

    # --------------------------------------
    # BITMAP MANAGEMENT
    # --------------------------------------

    def ensure_bitmap(self, width, height):

        if self.bitmap_size == (width, height):
            return

        self.release_bitmap()

        self.memory_dc = CreateCompatibleDC(None)

        if not self.memory_dc:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        info = BITMAPINFO()

        info.bmiHeader.biSize = ctypes.sizeof(
            BITMAPINFOHEADER
        )

        info.bmiHeader.biWidth = width
        info.bmiHeader.biHeight = -height
        info.bmiHeader.biPlanes = 1
        info.bmiHeader.biBitCount = 32
        info.bmiHeader.biCompression = BI_RGB

        bits = ctypes.c_void_p()

        self.bitmap = CreateDIBSection(
            self.memory_dc,
            ctypes.byref(info),
            DIB_RGB_COLORS,
            ctypes.byref(bits),
            None,
            0
        )

        if not self.bitmap or not bits.value:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        SelectObject(
            self.memory_dc,
            self.bitmap
        )

        self.bitmap_bits = bits
        self.bitmap_size = (width, height)

    def release_bitmap(self):

        if self.memory_dc:
            DeleteDC(self.memory_dc)

        if self.bitmap:
            DeleteObject(self.bitmap)

        self.memory_dc = None
        self.bitmap = None
        self.bitmap_bits = None
        self.bitmap_size = None

    # --------------------------------------
    # RENDER FRAME
    # --------------------------------------

    def render(self, width, height, box):

        self.ensure_bitmap(width, height)

        image = Image.new(
            "RGBA",
            (width, height),
            (0, 0, 0, 0)
        )

        if box is not None:

            x, y, box_width, box_height = box

            padding = 3

            # Keep the rectangle inside the image.
            left = max(0, x - padding)
            top = max(0, y - padding)
            right = min(
                width - 1,
                x + box_width + padding - 1
            )
            bottom = min(
                height - 1,
                y + box_height + padding - 1
            )

            draw = ImageDraw.Draw(image)

            draw.rectangle(
                (left, top, right, bottom),
                outline=(255, 255, 255, 255),
                width=2
            )

        raw_pixels = image.tobytes(
            "raw",
            "BGRA"
        )

        ctypes.memmove(
            self.bitmap_bits,
            raw_pixels,
            len(raw_pixels)
        )

    # --------------------------------------
    # DISPLAY OVERLAY
    # --------------------------------------

    def present(self, bounds, box):

        width = bounds["width"]
        height = bounds["height"]

        key = (
            bounds["left"],
            bounds["top"],
            width,
            height,
            box
        )

        # Only redraw the bitmap if something changed.
        if key != self.last_render_key:

            self.render(
                width,
                height,
                box
            )

            self.last_render_key = key

        destination = POINT(
            bounds["left"],
            bounds["top"]
        )

        source = POINT(0, 0)

        size = SIZE(
            width,
            height
        )

        blend = BLENDFUNCTION(
            AC_SRC_OVER,
            0,
            255,
            AC_SRC_ALPHA
        )

        screen_dc = GetDC(None)

        if not screen_dc:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        try:

            success = UpdateLayeredWindow(
                self.hwnd,
                screen_dc,
                ctypes.byref(destination),
                ctypes.byref(size),
                self.memory_dc,
                ctypes.byref(source),
                0,
                ctypes.byref(blend),
                ULW_ALPHA
            )

            if not success:
                raise ctypes.WinError(
                    ctypes.get_last_error()
                )

        finally:
            ReleaseDC(None, screen_dc)

        success = SetWindowPos(
            self.hwnd,
            HWND_TOPMOST,
            bounds["left"],
            bounds["top"],
            width,
            height,
            SWP_NOACTIVATE | SWP_SHOWWINDOW
        )

        if not success:
            raise ctypes.WinError(
                ctypes.get_last_error()
            )

        self.visible = True

    # --------------------------------------
    # UPDATE LOOP
    # --------------------------------------

    def update_overlay(self):

        if not self.running:
            return

        try:

            # F8 emergency shutdown.
            f8_down = bool(
                GetAsyncKeyState(VK_F8) & 0x8000
            )

            if f8_down and not self.f8_was_down:
                self.close()
                return

            self.f8_was_down = f8_down

            window = self.capture.find_roblox_window()

            if window is None:

                self.hide_overlay()
                self.last_render_key = None

            else:

                # IMPORTANT:
                # Hide the overlay before MSS captures Roblox.
                self.hide_overlay()

                frame = self.capture.capture_frame(window)

                if frame is None:

                    self.last_render_key = None

                else:

                    detection = detect_green_target(frame)

                    box = (
                        detection["box"]
                        if detection is not None
                        else None
                    )

                    bounds = {
                        "left": window["left"],
                        "top": window["top"],
                        "width": window["width"],
                        "height": window["height"]
                    }

                    self.present(
                        bounds,
                        box
                    )

        except Exception:

            import traceback

            print("\n[ForgeSight Overlay Error]")
            traceback.print_exc()

            self.close()
            return

        if self.running:

            self.root.after(
                100,
                self.update_overlay
            )

    # --------------------------------------
    # CLEANUP
    # --------------------------------------

    def cleanup(self):

        if self.hwnd:

            ShowWindow(
                self.hwnd,
                SW_HIDE
            )

            DestroyWindow(self.hwnd)
            self.hwnd = None

        self.visible = False

        self.release_bitmap()

        if self.capture:
            self.capture.close()

    def close(self):

        if not self.running:
            return

        self.running = False

        self.cleanup()

        print("[ForgeSight] Overlay stopped.")


# ==========================================
# OPEN OVERLAY
# ==========================================

def open_overlay(root, settings=None):

    return ForgeSightOverlay(root, settings)
