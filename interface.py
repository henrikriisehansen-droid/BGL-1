import json
import webbrowser
import flet as ft
from encryption import encrypt
from decryption import decrypt, DecryptionError, EncodingError, IntegrityError, PaddingError, JSONFormatError
from utils import is_base64

BASE_URL = "https://www.trustpilot.com/evaluate-bgl/"
DEFAULT_PAYLOAD = {
    "email": "",
    "name": "",
    "ref": "",
    "skus": ["sku1", "sku2", "sku3"],
    "tags": ["tag1", "tag2", "tag3"]
}

def main(page: ft.Page):
    page.title = "Business Generated Link (BGL)"
    page.window_width = 1000
    page.window_height = 800
    page.window_icon = "bgl_icon.png" # Set application icon
    
    # Darker Theme Section
    page.theme_mode = ft.ThemeMode.DARK
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)
    page.bgcolor = ft.Colors.BLACK  # Even darker background
    page.padding = 20

    # --- State Variables (Controls) ---
    # Encryption Section
    enc_key_entry = ft.TextField(label="Encryption Key", label_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    auth_key_entry = ft.TextField(label="Authentication Key", label_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    domain_entry = ft.TextField(label="Domain", label_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    payload_textbox = ft.TextField(
        label="Payload (JSON)", 
        multiline=True, 
        min_lines=10, 
        max_lines=15,
        value=json.dumps(DEFAULT_PAYLOAD, indent=2)
    )
    link_entry = ft.TextField(label="Resulting Link", read_only=True)

    # Decryption Section
    decrypt_payload_entry = ft.TextField(label="Payload to Decrypt", label_style=ft.TextStyle(weight=ft.FontWeight.BOLD))
    output_textbox = ft.TextField(
        label="Decrypted Payload / Error Message", 
        multiline=True, 
        min_lines=10, 
        max_lines=15, 
        read_only=True
    )

    # --- Helper Functions ---
    def display_message(message: str, is_error: bool = False):
        output_textbox.value = message
        output_textbox.color = ft.Colors.RED if is_error else ft.Colors.WHITE
        page.update()

    def validate_inputs_for_encryption() -> bool:
        enc_key = enc_key_entry.value.strip()
        auth_key = auth_key_entry.value.strip()
        domain = domain_entry.value.strip()
        payload_str = payload_textbox.value.strip()

        if not all([enc_key, auth_key, domain, payload_str]):
            display_message("All encryption fields must be filled.", is_error=True)
            return False

        if not is_base64(enc_key):
            display_message("Encryption Key must be valid Base64.", is_error=True)
            return False
        
        if not is_base64(auth_key):
            display_message("Authentication Key must be valid Base64.", is_error=True)
            return False

        try:
            json.loads(payload_str)
        except json.JSONDecodeError as e:
            display_message(f"Payload is not valid JSON: {e}", is_error=True)
            return False

        return True

    # --- Event Handlers ---
    def on_encrypt_click(e):
        if not validate_inputs_for_encryption():
            return

        payload_str = payload_textbox.value
        enc_key = enc_key_entry.value.strip()
        auth_key = auth_key_entry.value.strip()
        domain = domain_entry.value.strip()

        try:
            encrypted_msg = encrypt(payload_str.encode("utf-8"), enc_key, auth_key)
            link = f"{BASE_URL}{domain}?p={encrypted_msg}"
            
            link_entry.value = link
            decrypt_payload_entry.value = encrypted_msg
            display_message("Encryption successful.", is_error=False)
        except Exception as err:
            display_message(f"Encryption failed: {err}", is_error=True)
        page.update()

    def on_decrypt_click(e):
        encrypted_payload = decrypt_payload_entry.value.strip()
        enc_key = enc_key_entry.value.strip()
        auth_key = auth_key_entry.value.strip()

        if not all([encrypted_payload, enc_key, auth_key]):
            display_message("Encrypted payload and both keys are required for decryption.", is_error=True)
            return

        try:
            decrypted_bytes = decrypt(encrypted_payload, enc_key, auth_key)
            decrypted_text = decrypted_bytes.decode('utf-8')
            display_message(f"Decryption Successful:\n{decrypted_text}", is_error=False)
        except (EncodingError, IntegrityError, PaddingError, JSONFormatError) as err:
            display_message(f"Decryption Error: {err}", is_error=True)
        except Exception as err:
            display_message(f"An unexpected error occurred: {err}", is_error=True)
        page.update()

    def on_clear_click(e):
        decrypt_payload_entry.value = ""
        output_textbox.value = ""
        page.update()

    def on_copy_click(e):
        if link_entry.value:
            page.set_clipboard(link_entry.value)
            page.show_snack_bar(ft.SnackBar(ft.Text("Link copied to clipboard!")))

    def on_open_click(e):
        if link_entry.value:
            webbrowser.open_new(link_entry.value)

    # --- Layout Setup ---
    encrypt_view = ft.ListView(
        controls=[
            ft.Text("Encryption", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
            ft.ElevatedButton("Encrypt", on_click=on_encrypt_click, icon=ft.Icons.LOCK),
            enc_key_entry,
            auth_key_entry,
            domain_entry,
            payload_textbox,
            ft.Row([
                ft.ElevatedButton("Copy Link", on_click=on_copy_click, expand=True, icon=ft.Icons.COPY),
                ft.ElevatedButton("Open Link", on_click=on_open_click, expand=True, icon=ft.Icons.OPEN_IN_BROWSER),
            ], spacing=10),
            link_entry,
        ],
        expand=True,
        spacing=20,
        padding=ft.padding.only(right=40, top=10, bottom=10)
    )

    decrypt_view = ft.ListView(
        controls=[
            ft.Text("Decryption", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_200),
            ft.ElevatedButton("Decrypt", on_click=on_decrypt_click, icon=ft.Icons.LOCK_OPEN),
            decrypt_payload_entry,
            ft.ElevatedButton("Clear", on_click=on_clear_click, icon=ft.Icons.CLEAR),
            output_textbox,
        ],
        expand=True,
        spacing=20,
        padding=ft.padding.only(right=40, top=10, bottom=10)
    )

    page.add(
        ft.Row(
            controls=[
                ft.Container(content=encrypt_view, padding=20, expand=True, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE_200), border_radius=10),
                ft.VerticalDivider(width=1, color=ft.Colors.BLUE_900),
                ft.Container(content=decrypt_view, padding=20, expand=True, bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE), border_radius=10)
            ],
            expand=True,
            vertical_alignment=ft.CrossAxisAlignment.START
        )
    )

if __name__ == "__main__":
    ft.run(main, assets_dir=".")
