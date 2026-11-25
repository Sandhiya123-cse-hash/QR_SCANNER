import qrcode

# One fixed message inside the QR
qr_data = "ROTATION-QR-01"

qr = qrcode.QRCode(
    version=None,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=12,
    border=4
)

qr.add_data(qr_data)
qr.make(fit=True)

image = qr.make_image(
    fill_color="black",
    back_color="white"
)

image.save("my_qr.png")

print("QR code created: my_qr.png")
print("QR data:", qr_data)