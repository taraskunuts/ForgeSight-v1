
import ctypes
import ntpath
from ctypes import wintypes

import mss
from PIL import Image


# ==========================================
# WINDOWS API
# ==========================================

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG)
    ]


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG)
    ]


WNDENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HWND,
    wintypes.LPARAM
)


# ==========================================
# WINDOW FUNCTIONS
# ==========================================

EnumWindows = user32.EnumWindows
EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]
EnumWindows.restype = wintypes.BOOL

IsWindow = user32.IsWindow
IsWindow.argtypes = [wintypes.HWND]
IsWindow.restype = wintypes.BOOL

IsWindowVisible = user32.IsWindowVisible
IsWindowVisible.argtypes = [wintypes.HWND]
IsWindowVisible.restype = wintypes.BOOL

IsIconic = user32.IsIconic
IsIconic.argtypes = [wintypes.HWND]
IsIconic.restype = wintypes.BOOL

GetWindowTextW = user32.GetWindowTextW
GetWindowTextW.argtypes = [
    wintypes.HWND,
    wintypes.LPWSTR,
    ctypes.c_int
]
GetWindowTextW.restype = ctypes.c_int

GetWindowTextLengthW = user32.GetWindowTextLengthW
GetWindowTextLengthW.argtypes = [wintypes.HWND]
GetWindowTextLengthW.restype = ctypes.c_int

GetClientRect = user32.GetClientRect
GetClientRect.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(RECT)
]
GetClientRect.restype = wintypes.BOOL

ClientToScreen = user32.ClientToScreen
ClientToScreen.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(POINT)
]
ClientToScreen.restype = wintypes.BOOL

GetWindowThreadProcessId = user32.GetWindowThreadProcessId
GetWindowThreadProcessId.argtypes = [
    wintypes.HWND,
    ctypes.POINTER(wintypes.DWORD)
]
GetWindowThreadProcessId.restype = wintypes.DWORD


# ==========================================
# PROCESS DETECTION
# ==========================================

PROCESS_QUERY_LIMITED_INFORMATION = 0x1000

OpenProcess = kernel32.OpenProcess
OpenProcess.argtypes = [
    wintypes.DWORD,
    wintypes.BOOL,
    wintypes.DWORD
]
OpenProcess.restype = wintypes.HANDLE

QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
QueryFullProcessImageNameW.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPWSTR,
    ctypes.POINTER(wintypes.DWORD)
]
QueryFullProcessImageNameW.restype = wintypes.BOOL

CloseHandle = kernel32.CloseHandle
CloseHandle.argtypes = [wintypes.HANDLE]
CloseHandle.restype = wintypes.BOOL


# ==========================================
# GET PROCESS NAME
# ==========================================

def get_process_name(hwnd):

    process_id = wintypes.DWORD()

    GetWindowThreadProcessId(
        hwnd,
        ctypes.byref(process_id)
    )

    if not process_id.value:
        return None

    handle = OpenProcess(
        PROCESS_QUERY_LIMITED_INFORMATION,
        False,
        process_id.value
    )

    if not handle:
        return None

    try:
        buffer = ctypes.create_unicode_buffer(1024)
        size = wintypes.DWORD(len(buffer))

        success = QueryFullProcessImageNameW(
            handle,
            0,
            buffer,
            ctypes.byref(size)
        )

        if not success:
            return None

        return ntpath.basename(buffer.value).lower()

    finally:
        CloseHandle(handle)


# ==========================================
# GET CLIENT AREA
# ==========================================

def get_client_bounds(hwnd):

    rect = RECT()

    if not GetClientRect(
        hwnd,
        ctypes.byref(rect)
    ):
        return None

    width = rect.right - rect.left
    height = rect.bottom - rect.top

    if width <= 0 or height <= 0:
        return None

    top_left = POINT(0, 0)
    bottom_right = POINT(width, height)

    if not ClientToScreen(hwnd, ctypes.byref(top_left)):
        return None

    if not ClientToScreen(hwnd, ctypes.byref(bottom_right)):
        return None

    return {
        "left": top_left.x,
        "top": top_left.y,
        "width": bottom_right.x - top_left.x,
        "height": bottom_right.y - top_left.y
    }


# ==========================================
# ROBLOX CAPTURE
# ==========================================

class RobloxCapture:

    ROBLOX_PROCESS = "robloxplayerbeta.exe"

    def __init__(self):
        self.sct = mss.mss()

    # --------------------------------------
    # FIND ROBLOX WINDOW
    # --------------------------------------

    def find_roblox_window(self):

        windows = []

        def callback(hwnd, lparam):

            if not IsWindowVisible(hwnd):
                return True

            if IsIconic(hwnd):
                return True

            process_name = get_process_name(hwnd)

            # STRICT PROCESS VALIDATION
            if process_name != self.ROBLOX_PROCESS:
                return True

            title_length = GetWindowTextLengthW(hwnd)

            title_buffer = ctypes.create_unicode_buffer(
                title_length + 1
            )

            GetWindowTextW(
                hwnd,
                title_buffer,
                title_length + 1
            )

            bounds = get_client_bounds(hwnd)

            if bounds is None:
                return True

            windows.append({
                "handle": hwnd,
                "title": title_buffer.value,
                "process": process_name,
                **bounds
            })

            return True

        callback_ref = WNDENUMPROC(callback)

        EnumWindows(callback_ref, 0)

        if not windows:
            return None

        return max(
            windows,
            key=lambda window:
                window["width"] * window["height"]
        )

    # --------------------------------------
    # CAPTURE FRAME
    # --------------------------------------

    def capture_frame(self, window):

        if window is None:
            return None

        hwnd = window["handle"]

        if not IsWindow(hwnd):
            return None

        if not IsWindowVisible(hwnd) or IsIconic(hwnd):
            return None

        # Verify that the window still belongs to Roblox
        if get_process_name(hwnd) != self.ROBLOX_PROCESS:
            return None

        # Refresh coordinates in case Roblox moved
        bounds = get_client_bounds(hwnd)

        if bounds is None:
            return None

        screenshot = self.sct.grab(bounds)

        return Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.rgb
        )

    # --------------------------------------
    # CLOSE CAPTURE
    # --------------------------------------

    def close(self):
        self.sct.close()
